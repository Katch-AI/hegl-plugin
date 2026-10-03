import io
import json

import pytest

import cluster

TAXONOMY = {
    "wrong_total": {"what": "The reply says a number in the email is wrong", "not_for": "Complaints about tone", "examples": ["total should be 1200"]},
    "wrong_recipient": {"what": "The email went to the wrong person", "not_for": "Wrong numbers", "examples": ["this was meant for Dana"]},
}


def choice(option, confidence=0.95):
    probabilities = {key: 0.0 for key in ["wrong_total", "wrong_recipient", "other"]}
    probabilities[option] = confidence
    return {"assign": {"type": "choice", "choice": option, "confidence": confidence, "probabilities": probabilities}}


class ScriptedJev:
    """Returns one scripted answer per call and records the questions it saw."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, state, questions):
        self.calls.append((state, questions))
        return self.answers.pop(0)


def test_choice_question_lists_every_category_with_criteria_plus_other():
    question = cluster.choice_question(TAXONOMY, purpose="Which failure does this feedback report?")
    assert question["type"] == "choice"
    assert set(question["criteria"]) == {"wrong_total", "wrong_recipient", "other"}
    assert question["criteria"]["wrong_total"]["not_for"] == "Complaints about tone"
    assert "none of the" in question["criteria"]["other"]["what"].lower()


def test_assign_flags_a_gap_on_other_or_low_confidence():
    assert cluster.assign(choice("wrong_total")["assign"], threshold=0.6) == ("wrong_total", 0.95, False)
    assert cluster.assign(choice("other")["assign"], threshold=0.6) == ("other", 0.95, True)
    assert cluster.assign(choice("wrong_total", 0.4)["assign"], threshold=0.6) == ("wrong_total", 0.4, True)


def test_run_adds_the_proposed_category_and_labels_with_it(tmp_path):
    rows = [{"id": "1", "text": "the tone was too pushy"}, {"id": "2", "text": "way too aggressive an opener"}]
    proposals = [{"action": "add", "key": "tone", "what": "The reply objects to how the email sounds",
                  "not_for": "Wrong facts", "examples": ["too pushy"]}]
    pushy = {"assign": {"type": "choice", "choice": "tone", "confidence": 0.9,
                        "probabilities": {"wrong_total": 0.0, "wrong_recipient": 0.0, "tone": 0.9, "other": 0.1}}}
    jev = ScriptedJev([choice("other"), pushy, pushy])
    out = tmp_path / "labels.jsonl"

    taxonomy = cluster.run(rows, dict(TAXONOMY), jev=jev, propose=lambda ctx: proposals.pop(0),
                           purpose="p", threshold=0.6, out_path=out, sample_size=0)

    assert "tone" in taxonomy
    labels = [json.loads(line) for line in out.read_text().splitlines()]
    assert [(l["id"], l["category"]) for l in labels] == [("1", "tone"), ("2", "tone")]
    assert set(jev.calls[1][1]["assign"]["criteria"]) == {"wrong_total", "wrong_recipient", "tone", "other"}


def test_run_merges_a_proposal_that_steals_an_existing_category(tmp_path):
    rows = [{"id": "1", "text": "total should be 1500"}, {"id": "2", "text": "amount is off by 300"},
            {"id": "3", "text": "the sum is wrong again"}]
    steal = {"assign": {"type": "choice", "choice": "wrong_amount", "confidence": 0.9,
                        "probabilities": {"wrong_total": 0.1, "wrong_recipient": 0.0, "wrong_amount": 0.9, "other": 0.0}}}
    # rows 1-2 land in wrong_total; row 3 abstains, the proposer adds wrong_amount, both samples migrate.
    jev = ScriptedJev([choice("wrong_total"), choice("wrong_total"), choice("other"), steal, steal, choice("wrong_total")])
    proposal = {"action": "add", "key": "wrong_amount", "what": "A money amount is wrong", "not_for": "", "examples": []}

    taxonomy = cluster.run(rows, dict(TAXONOMY), jev=jev, propose=lambda ctx: proposal,
                           purpose="p", threshold=0.6, out_path=tmp_path / "l.jsonl", sample_size=2)

    assert "wrong_amount" not in taxonomy
    assert taxonomy["wrong_total"]["merged"] == ["wrong_amount"]


def test_run_widens_an_existing_category_when_the_proposer_says_so(tmp_path):
    rows = [{"id": "1", "text": "the subtotal is wrong"}]
    proposal = {"action": "widen", "key": "wrong_total", "what": "Any number in the email is wrong, including subtotals",
                "not_for": "Complaints about tone", "examples": ["total should be 1200", "subtotal is wrong"]}
    jev = ScriptedJev([choice("other"), choice("wrong_total")])

    taxonomy = cluster.run(rows, dict(TAXONOMY), jev=jev, propose=lambda ctx: proposal,
                           purpose="p", threshold=0.6, out_path=tmp_path / "l.jsonl", sample_size=0)

    assert taxonomy["wrong_total"]["what"].startswith("Any number")
    assert set(taxonomy) == {"wrong_total", "wrong_recipient"}


def test_run_resumes_from_the_checkpoint_file(tmp_path):
    out = tmp_path / "labels.jsonl"
    out.write_text(json.dumps({"id": "1", "category": "wrong_total", "confidence": 0.9}) + "\n")
    rows = [{"id": "1", "text": "done already"}, {"id": "2", "text": "sent to the wrong person"}]
    jev = ScriptedJev([choice("wrong_recipient")])

    cluster.run(rows, dict(TAXONOMY), jev=jev, propose=lambda ctx: None, purpose="p", threshold=0.6, out_path=out, sample_size=0)

    assert len(jev.calls) == 1
    assert [json.loads(l)["id"] for l in out.read_text().splitlines()] == ["1", "2"]


def test_relabel_scores_every_row_against_the_final_taxonomy(tmp_path):
    rows = [{"id": "1", "text": "a"}, {"id": "2", "text": "b"}]
    jev = ScriptedJev([choice("wrong_total"), choice("wrong_recipient", 0.7)])

    labels = cluster.relabel(rows, TAXONOMY, jev=jev, purpose="p", out_path=tmp_path / "final.jsonl")

    assert [(l["id"], l["category"], l["confidence"]) for l in labels] == [("1", "wrong_total", 0.95), ("2", "wrong_recipient", 0.7)]
    assert all(set(call[1]["assign"]["criteria"]) == {"wrong_total", "wrong_recipient", "other"} for call in jev.calls)


def test_consolidate_applies_merges_from_the_proposer():
    taxonomy = dict(TAXONOMY, wrong_amount={"what": "An amount is wrong", "not_for": "", "examples": []})
    counts = {"wrong_total": 30, "wrong_recipient": 4, "wrong_amount": 6}
    final = [{"key": "wrong_total", "what": "A number in the email is wrong", "not_for": "Tone", "examples": ["1200"], "merged": ["wrong_amount"]},
             {"key": "wrong_recipient", **TAXONOMY["wrong_recipient"], "merged": []}]

    result = cluster.consolidate(taxonomy, counts, examples={}, propose=lambda ctx: {"categories": final})

    assert set(result) == {"wrong_total", "wrong_recipient"}
    assert result["wrong_total"]["merged"] == ["wrong_amount"]
    assert "merged" not in result["wrong_recipient"]


def test_consolidate_rejects_a_proposer_that_invents_categories():
    with pytest.raises(ValueError):
        cluster.consolidate(dict(TAXONOMY), {"wrong_total": 1, "wrong_recipient": 1}, examples={},
                            propose=lambda ctx: {"categories": [{"key": key, **category, "merged": []} for key, category in TAXONOMY.items()]
                                                 + [{"key": "new_one", "what": "x", "not_for": "", "examples": [], "merged": []}]})


def test_run_asks_the_proposer_first_when_the_taxonomy_is_empty(tmp_path):
    rows = [{"id": "1", "text": "total should be 1500"}]
    proposal = {"action": "add", "key": "wrong_total", "what": "A number is wrong", "not_for": "", "examples": []}
    jev = ScriptedJev([{"assign": {"type": "choice", "choice": "wrong_total", "confidence": 0.9,
                                   "probabilities": {"wrong_total": 0.9, "other": 0.1}}}])

    taxonomy = cluster.run(rows, {}, jev=jev, propose=lambda ctx: proposal, purpose="p", threshold=0.6,
                           out_path=tmp_path / "l.jsonl", sample_size=0)

    assert set(taxonomy) == {"wrong_total"}
    assert len(jev.calls) == 1


REQUIRED = ["--input", "r.jsonl", "--purpose", "p", "--out", "o.jsonl", "--taxonomy", "t.json"]


@pytest.mark.parametrize("missing", ["--proxy-url", "--api-key"])
def test_proxy_flags_are_required(missing):
    flags = {"--proxy-url": "https://proxy.example", "--api-key": "sk-test"}
    del flags[missing]
    with pytest.raises(SystemExit):
        cluster.parse_args(REQUIRED + [arg for pair in flags.items() for arg in pair])


def test_request_targets_the_proxy_with_the_key():
    request = cluster.build_request("https://proxy.example/", "sk-test", "/v1/chat/completions", {"a": 1})
    assert request.full_url == "https://proxy.example/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer sk-test"
    assert request.get_header("User-agent") == "hegl-plugin-cluster/1.0"
    assert request.get_header("X-litellm-tags") is None
    assert json.loads(request.data) == {"a": 1}


def test_proxy_flags_parse():
    args = cluster.parse_args(REQUIRED + ["--proxy-url", "https://proxy.example", "--api-key", "sk-test"])
    assert (args.proxy_url, args.api_key) == ("https://proxy.example", "sk-test")


def test_a_proxy_error_exits_with_its_status_and_body(monkeypatch):
    def refuse(request, timeout):
        raise cluster.HTTPError(request.full_url, 401, "Unauthorized", {}, io.BytesIO(b"key expired"))
    monkeypatch.setattr(cluster, "urlopen", refuse)

    with pytest.raises(SystemExit) as exit_info:
        cluster.http_client("https://proxy.example", "sk-test")("/v1/chat/completions", {})

    assert "401" in str(exit_info.value.code) and "key expired" in str(exit_info.value.code)


def test_main_sends_every_call_through_the_flagged_proxy(tmp_path, monkeypatch):
    clients, paths = [], []

    def fake_client(proxy_url, api_key):
        clients.append((proxy_url, api_key))

        def post(path, body):
            paths.append(path)
            if path == "/typesafe/v1/systemone":
                return {"answers": choice("wrong_total")}
            categories = [{"key": key, **category, "merged": []} for key, category in TAXONOMY.items()]
            return {"choices": [{"message": {"content": json.dumps({"categories": categories})}}]}
        return post
    monkeypatch.setattr(cluster, "http_client", fake_client)
    (tmp_path / "rows.jsonl").write_text(json.dumps({"id": "1", "text": "total should be 1500"}) + "\n")
    (tmp_path / "t.json").write_text(json.dumps(TAXONOMY))

    cluster.main(["--proxy-url", "https://proxy.example", "--api-key", "sk-test", "--input", str(tmp_path / "rows.jsonl"),
                  "--purpose", "p", "--out", str(tmp_path / "o.jsonl"), "--taxonomy", str(tmp_path / "t.json")])

    assert clients == [("https://proxy.example", "sk-test")]
    assert set(paths) == {"/typesafe/v1/systemone", "/v1/chat/completions"}
