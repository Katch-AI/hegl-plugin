import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = [".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "package.json"]
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def run(repo, *cmd):
    return subprocess.run(cmd, cwd=repo, env=ENV, check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    for path in [*MANIFESTS, "bin/set-version", "bin/prepare-release"]:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / path, tmp_path / path)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 1.2.3 — 2026-01-01\n\n- Old entry\n")
    run(tmp_path, "git", "init", "-q")
    run(tmp_path, "bin/set-version", "1.2.3")
    run(tmp_path, "git", "add", "-A")
    run(tmp_path, "git", "commit", "-qm", "Release 1.2.3")
    run(tmp_path, "git", "tag", "v1.2.3")
    return tmp_path


def versions(repo):
    return {json.loads((repo / m).read_text())["version"] for m in MANIFESTS} | {(repo / "VERSION").read_text().strip()}


def test_set_version_writes_version_file_and_every_manifest(repo):
    run(repo, "bin/set-version", "2.0.0")
    assert versions(repo) == {"2.0.0"}


def test_set_version_rejects_a_non_semver_version(repo):
    with pytest.raises(subprocess.CalledProcessError):
        run(repo, "bin/set-version", "banana")
    assert versions(repo) == {"1.2.3"}


def test_prepare_release_bumps_patch_and_logs_commits_since_the_last_tag(repo):
    run(repo, "git", "commit", "-qm", "Add a thing", "--allow-empty")
    run(repo, "git", "commit", "-qm", "Fix a thing", "--allow-empty")
    assert run(repo, "bin/prepare-release").stdout.strip() == "1.2.4"
    assert versions(repo) == {"1.2.4"}
    changelog = (repo / "CHANGELOG.md").read_text()
    head, old = changelog.split("## 1.2.3")
    assert head.startswith("# Changelog\n\n## 1.2.4 — ")
    assert "- Fix a thing\n- Add a thing\n" in head
    assert "- Old entry" in old
