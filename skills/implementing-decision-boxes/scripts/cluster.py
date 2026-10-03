#!/usr/bin/env python3
"""Cluster rows of text into a named taxonomy: Jev assigns every row, an LLM proposes a category only when Jev abstains.

cluster.py --proxy-url URL --api-key KEY --input rows.jsonl --purpose "Which failure does this feedback report?" --out labels.jsonl --taxonomy taxonomy.json
"""
import argparse
import json
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

OTHER = "other"
JEV_MODEL = "jev-latest"
MIGRATION_LIMIT = 0.5
CATEGORY_FIELDS = ("what", "not_for", "examples")

PROPOSER_PROMPT = """You maintain a taxonomy of categories for rows of text. A calibrated classifier could not place
the row below in the current taxonomy. Reply with exactly one action:
- add: a new category (snake_case key; what it covers; not_for: what it excludes; two short examples).
- widen: rewrite an existing category's what / not_for / examples so this row fits.
- assign: the row fits an existing key as written and the classifier was merely unsure.
Prefer widen over add when the row is a variant of an existing category. Keep categories mutually
exclusive and phrased so a literal reader can apply them without context."""

CONSOLIDATE_PROMPT = """You are finishing a taxonomy discovered one row at a time. Merge synonyms and tighten criteria.
Return every category that should survive, keeping its key; a category that absorbs another lists
the absorbed keys under `merged`. Never add a category that was not in the input."""

PROPOSAL_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["add", "widen", "assign"]},
        "key": {"type": "string"},
        "what": {"type": "string"},
        "not_for": {"type": "string"},
        "examples": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["action", "key", "what", "not_for", "examples"],
    "additionalProperties": False,
}

CATEGORY_SCHEMA = {
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "what": {"type": "string"},
        "not_for": {"type": "string"},
        "examples": {"type": "array", "items": {"type": "string"}},
        "merged": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["key", "what", "not_for", "examples", "merged"],
    "additionalProperties": False,
}

CONSOLIDATE_SCHEMA = {
    "type": "object",
    "properties": {"categories": {"type": "array", "items": CATEGORY_SCHEMA}},
    "required": ["categories"],
    "additionalProperties": False,
}


def choice_question(taxonomy, purpose):
    criteria = {key: {field: category.get(field, "" if field != "examples" else []) for field in CATEGORY_FIELDS}
                for key, category in taxonomy.items()}
    criteria[OTHER] = {"what": "None of the other options describes this row",
                       "not_for": "Anything one of the other options covers", "examples": []}
    return {"type": "choice", "instructions": purpose, "criteria": criteria}


def assign(answer, threshold):
    category, confidence = answer["choice"], answer["confidence"]
    return category, confidence, category == OTHER or confidence < threshold


def state_of(row, max_chars):
    state = {key: value for key, value in row.items() if key != "id"}
    return {key: value[:max_chars] if isinstance(value, str) else value for key, value in state.items()}


def ask(jev, row, taxonomy, purpose, max_chars):
    return jev(state_of(row, max_chars), {"assign": choice_question(taxonomy, purpose)})["assign"]


def load_labels(path):
    if not path or not os.path.exists(path):
        return {}
    labels = [json.loads(line) for line in open(path) if line.strip()]
    return {label["id"]: label for label in labels}


def append_label(path, label):
    with open(path, "a") as handle:
        handle.write(json.dumps(label) + "\n")


def category_entry(proposal):
    return {"what": proposal.get("what", ""), "not_for": proposal.get("not_for", ""), "examples": proposal.get("examples", [])}


def migrated(taxonomy, candidate, new_key, seen, jev, purpose, sample_size, max_chars):
    """The existing category whose sampled rows mostly move to new_key, or None."""
    for key, rows in seen.items():
        sample = rows[:sample_size]
        if not sample:
            continue
        moved = sum(ask(jev, row, candidate, purpose, max_chars)["choice"] == new_key for row in sample)
        if moved / len(sample) > MIGRATION_LIMIT:
            return key
    return None


def apply_proposal(taxonomy, proposal, *, jev, seen, purpose, sample_size, max_chars):
    action, key = proposal["action"], proposal["key"]
    if action == "add":
        if key in taxonomy or key == OTHER:
            raise ValueError(f"proposer added an existing key: {key}")
        candidate = {**taxonomy, key: category_entry(proposal)}
        absorbed_by = migrated(taxonomy, candidate, key, seen, jev, purpose, sample_size, max_chars)
        if absorbed_by:
            taxonomy[absorbed_by].setdefault("merged", []).append(key)
            return taxonomy
        return candidate
    if action == "widen":
        if key not in taxonomy:
            raise ValueError(f"proposer widened an unknown key: {key}")
        taxonomy[key] = {**taxonomy[key], **category_entry(proposal)}
        return taxonomy
    if action == "assign":
        if key not in taxonomy:
            raise ValueError(f"proposer assigned an unknown key: {key}")
        return taxonomy
    raise ValueError(f"unknown proposer action: {action}")


def run(rows, taxonomy, *, jev, propose, purpose, threshold, out_path, sample_size, max_categories=30, max_chars=20000):
    done = load_labels(out_path)
    seen = {key: [] for key in taxonomy}
    for row in rows:
        if row["id"] in done:
            continue
        answer = ask(jev, row, taxonomy, purpose, max_chars) if taxonomy else None
        category, confidence, gap = assign(answer, threshold) if answer else (OTHER, 0.0, True)
        if gap and len(taxonomy) < max_categories:
            proposal = propose({"purpose": purpose, "row": state_of(row, max_chars), "answer": answer, "taxonomy": taxonomy,
                                "examples": {key: [r.get("text") for r in rows_[:3]] for key, rows_ in seen.items()}})
            if proposal:
                taxonomy = apply_proposal(taxonomy, proposal, jev=jev, seen=seen, purpose=purpose,
                                          sample_size=sample_size, max_chars=max_chars)
                if proposal["action"] == "assign":
                    category, confidence, gap = proposal["key"], answer["probabilities"].get(proposal["key"], 0.0), False
                else:
                    answer = ask(jev, row, taxonomy, purpose, max_chars)
                    category, confidence, gap = assign(answer, threshold)
        label = {"id": row["id"], "category": category, "confidence": confidence, "gap": gap,
                 "probabilities": answer["probabilities"] if answer else {}}
        append_label(out_path, label)
        done[row["id"]] = label
        seen.setdefault(category, []).append(row)
    return taxonomy


def relabel(rows, taxonomy, *, jev, purpose, out_path, max_chars=20000):
    labels = []
    done = load_labels(out_path)
    for row in rows:
        if row["id"] in done:
            labels.append(done[row["id"]])
            continue
        answer = ask(jev, row, taxonomy, purpose, max_chars)
        label = {"id": row["id"], "category": answer["choice"], "confidence": answer["confidence"],
                 "probabilities": answer["probabilities"]}
        append_label(out_path, label)
        labels.append(label)
    return labels


def consolidate(taxonomy, counts, *, examples, propose):
    final = {category["key"]: category for category in propose({"taxonomy": taxonomy, "counts": counts, "examples": examples})["categories"]}
    invented = set(final) - set(taxonomy)
    if invented:
        raise ValueError(f"consolidation invented categories: {sorted(invented)}")
    absorbed = {key for category in final.values() for key in category.get("merged", [])}
    dropped = set(taxonomy) - set(final) - absorbed
    if dropped:
        raise ValueError(f"consolidation dropped categories without merging them: {sorted(dropped)}")
    return {key: {**category_entry(category), **({"merged": category["merged"]} if category.get("merged") else {})}
            for key, category in final.items()}


def build_request(proxy_url, api_key, path, body):
    return Request(proxy_url.rstrip("/") + path, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "hegl-plugin-cluster/1.0",
    })


def http_client(proxy_url, api_key):
    def post(path, body):
        try:
            with urlopen(build_request(proxy_url, api_key, path, body), timeout=300) as response:
                return json.load(response)
        except HTTPError as error:
            sys.exit(f"proxy returned {error.code} for {path}: {error.read().decode(errors='replace')}")
    return post


def jev_http(post):
    def jev(state, questions):
        return post("/typesafe/v1/systemone", {"model": JEV_MODEL, "state": state, "questions": questions})["answers"]
    return jev


def proposer_http(post, model, prompt, schema):
    def propose(context):
        body = {"model": model, "messages": [{"role": "system", "content": prompt},
                                             {"role": "user", "content": json.dumps(context, indent=1)}],
                "response_format": {"type": "json_schema", "json_schema": {"name": "proposal", "schema": schema}}}
        text = post("/v1/chat/completions", body)["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.strip("`").split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    return propose


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proxy-url", required=True, help="proxyUrl from issue_llm_proxy_credentials")
    parser.add_argument("--api-key", required=True, help="apiKey from issue_llm_proxy_credentials")
    parser.add_argument("--input", required=True, help="JSONL rows with an `id` and a `text` field; other fields join the state")
    parser.add_argument("--purpose", required=True, help="the Choice instructions, e.g. 'Which failure does this feedback report?'")
    parser.add_argument("--out", required=True, help="discovery labels (JSONL, appended per row; resumes on restart)")
    parser.add_argument("--taxonomy", required=True, help="taxonomy JSON: read as the seed if it exists, written at the end")
    parser.add_argument("--final", help="labels against the consolidated taxonomy (default: <out>.final.jsonl)")
    parser.add_argument("--proposer-model", default="anthropic/claude-opus-5-5")
    parser.add_argument("--threshold", type=float, default=0.6, help="confidence below which Jev's pick counts as a gap")
    parser.add_argument("--sample-size", type=int, default=5, help="rows per existing category re-checked before adding one")
    parser.add_argument("--max-categories", type=int, default=30)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    rows = [json.loads(line) for line in open(args.input) if line.strip()]
    taxonomy = json.load(open(args.taxonomy)) if os.path.exists(args.taxonomy) else {}
    post = http_client(args.proxy_url, args.api_key)
    jev = jev_http(post)
    propose = proposer_http(post, args.proposer_model, PROPOSER_PROMPT, PROPOSAL_SCHEMA)
    taxonomy = run(rows, taxonomy, jev=jev, propose=propose, purpose=args.purpose, threshold=args.threshold,
                   out_path=args.out, sample_size=args.sample_size, max_categories=args.max_categories)
    labels = load_labels(args.out)
    counts = {key: sum(label["category"] == key for label in labels.values()) for key in taxonomy}
    examples = {key: [row.get("text") for row in rows if labels[row["id"]]["category"] == key][:3] for key in taxonomy}
    taxonomy = consolidate(taxonomy, counts, examples=examples,
                           propose=proposer_http(post, args.proposer_model, CONSOLIDATE_PROMPT, CONSOLIDATE_SCHEMA))
    json.dump(taxonomy, open(args.taxonomy, "w"), indent=2)
    final = relabel(rows, taxonomy, jev=jev, purpose=args.purpose, out_path=args.final or f"{args.out}.final.jsonl")
    for key in taxonomy:
        print(f"{key}: {sum(label['category'] == key for label in final)}")
    print(f"{OTHER}: {sum(label['category'] == OTHER for label in final)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
