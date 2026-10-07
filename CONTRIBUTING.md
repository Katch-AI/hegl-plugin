# Contributing

The skills here are read by a model, every turn. Brevity is the rule: teach only what a frontier model does not know (Hegl's behaviour, wire contracts, gotchas). Cut every sentence that explains JSON, HTTP or webhooks.

- Say **Hegl** for the product. Tool names, piece names and other identifiers stay as they are.
- Every tool a skill names must exist on the server. Check against `tools/list`.
- Text that lands on Hegl (requirements, flow descriptions, version and experiment descriptions, publish notes, artifacts) is written for a non-technical reader. Skills say so where it matters and nothing about how the harness talks in chat.
- `SKILL.md` frontmatter: `name` equals the directory, `description` starts with "Use when".
- These skills are also vendored into Hegl's hosted coding agent, so a change here ships to it on the next release.

To work against a development host, see README's "Developing against another Hegl host".

Run the lint locally: `node --test .opencode/hegl.test.mjs`, `python3 -m pytest skills/*/tests tests -q`, `claude plugin validate .`, and the checks in `.github/workflows/lint.yml`.

## Releases

Every merge to `main` is released. If `VERSION` has no tag yet, the merge is tagged with it. Otherwise a `Release x.y.z` pull request bumps the patch and merges itself, and that merge is tagged. For a minor or major release, run `bin/set-version <version>` in your pull request.

Label a pull request `automerge` to have it squash-merged once it is approved and lint is green.
