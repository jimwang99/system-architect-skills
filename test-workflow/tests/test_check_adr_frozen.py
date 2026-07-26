#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "..", "write-adr", "scripts", "check_adr_frozen.py")

PROPOSED = """---
status: proposed
created: 2026-07-25
---

# Sample decision

## Context

c

## Decision

d

## Alternatives Considered

- **Other** — rejected because reasons.

## Consequences

q
"""


def run(repo, *cmd):
    subprocess.run(cmd, cwd=repo, check=True, capture_output=True)


def git(repo, *args):
    run(repo, "git", *args)


def init_repo(repo):
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    os.makedirs(os.path.join(repo, "docs", "adr"))


def write(repo, rel, text):
    p = os.path.join(repo, rel)
    # git prunes an emptied working-tree dir after `git rm`; recreate parents so the
    # delete-and-recreate case can rewrite the file where its directory used to be.
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def accept(text):
    return text.replace("status: proposed", "status: accepted\ndecided: 2026-07-25")


def check(path):
    r = subprocess.run([sys.executable, SCRIPT, path], capture_output=True, text=True)
    return r.returncode, r.stderr


class TestFrozenCheck(unittest.TestCase):
    def scratch(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        init_repo(d.name)
        return d.name

    def test_proposed_file_passes(self):
        repo = self.scratch()
        p = write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        self.assertEqual(check(p)[0], 0)

    def test_clean_frozen_via_rename_passes(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        self.assertEqual(check(os.path.join(repo, "docs/adr/adr-001-x.md"))[0], 0)

    def test_post_freeze_body_edit_fails(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED).replace("## Decision\n\nd", "## Decision\n\nEDITED"))
        code, err = check(os.path.join(repo, "docs/adr/adr-001-x.md"))
        self.assertEqual(code, 1)
        self.assertIn("body", err)

    def test_supersession_frontmatter_edit_passes(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        flipped = accept(PROPOSED).replace(
            "status: accepted", "status: superseded").replace(
            "decided: 2026-07-25", "decided: 2026-07-25\nsuperseded-by: adr-002-y.md")
        write(repo, "docs/adr/adr-001-x.md", flipped)
        self.assertEqual(check(os.path.join(repo, "docs/adr/adr-001-x.md"))[0], 0)

    def test_born_frozen_fails_closed(self):
        repo = self.scratch()
        p = write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "born frozen")
        code, err = check(p)
        self.assertEqual(code, 1)
        self.assertIn("proposed ancestor", err)

    def test_delete_and_recreate_fails(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        git(repo, "rm", "-q", "docs/adr/adr-001-x.md")
        git(repo, "commit", "-qm", "delete")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED).replace("## Decision\n\nd", "## Decision\n\nREWRITTEN"))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "recreate")
        self.assertEqual(check(os.path.join(repo, "docs/adr/adr-001-x.md"))[0], 1)

    def test_post_freeze_edit_on_merged_branch_fails(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        git(repo, "checkout", "-qb", "side")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED).replace("q\n", "q edited\n"))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "sneaky edit")
        git(repo, "checkout", "-q", "main")
        git(repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
        self.assertEqual(check(os.path.join(repo, "docs/adr/adr-001-x.md"))[0], 1)

    def test_shallow_clone_fails_closed(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        clone_parent = tempfile.TemporaryDirectory()
        self.addCleanup(clone_parent.cleanup)
        clone = os.path.join(clone_parent.name, "clone")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + repo, clone],
                       check=True, capture_output=True)
        code, err = check(os.path.join(clone, "docs/adr/adr-001-x.md"))
        self.assertEqual(code, 1)
        self.assertIn("shallow", err)

    def test_not_a_repo_exits_2(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p = write(d.name, "adr-001-x.md", accept(PROPOSED))
        self.assertEqual(check(p)[0], 2)

    def test_defrosted_status_with_freeze_point_fails(self):
        # D1 regression: freeze, then flip frontmatter back to proposed and edit the body.
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        write(repo, "docs/adr/adr-001-x.md", PROPOSED.replace("## Decision\n\nd", "## Decision\n\nREWRITTEN"))
        code, err = check(os.path.join(repo, "docs/adr/adr-001-x.md"))
        self.assertEqual(code, 1)
        self.assertIn("freeze point", err)

    def test_proposed_after_freeze_is_not_an_ancestor(self):
        # Rm12: the only proposed version sits AFTER the freeze point; lineage is unproven.
        repo = self.scratch()
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "born frozen")
        write(repo, "docs/adr/adr-001-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "defrost")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "refreeze")
        code, err = check(os.path.join(repo, "docs/adr/adr-001-x.md"))
        self.assertEqual(code, 1)
        self.assertIn("proposed ancestor", err)

    def test_proposed_worktree_in_shallow_clone_fails_closed(self):
        # Worktree status is untrusted, so shallowness fails closed for every status.
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "pad", "--allow-empty")
        clone_parent = tempfile.TemporaryDirectory()
        self.addCleanup(clone_parent.cleanup)
        clone = os.path.join(clone_parent.name, "clone")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + repo, clone],
                       check=True, capture_output=True)
        code, err = check(os.path.join(clone, "docs/adr/adr-draft-x.md"))
        self.assertEqual(code, 1)
        self.assertIn("shallow", err)

    def _frozen_repo(self):
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept")
        return repo, os.path.join(repo, "docs/adr/adr-001-x.md")

    def test_trailing_blank_line_fails(self):
        repo, p = self._frozen_repo()
        with open(p, "a", encoding="utf-8") as fh:
            fh.write("\n")
        code, err = check(p)
        self.assertEqual(code, 1)
        self.assertRegex(err, r"body line \d+")

    def test_crlf_rewrite_fails(self):
        repo, p = self._frozen_repo()
        with open(p, "rb") as fh:
            data = fh.read()
        with open(p, "wb") as fh:
            fh.write(data.replace(b"\n", b"\r\n"))
        code, err = check(p)
        self.assertEqual(code, 1)
        self.assertRegex(err, r"body line \d+")

    def test_missing_file_exits_2(self):
        repo = self.scratch()
        code, err = check(os.path.join(repo, "docs/adr/absent.md"))
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertTrue(err.strip())

    def test_rename_across_merge_outcome_documented(self):
        """Spec 02 requires this case exercised and its outcome documented.

        The accept-rename happens on a side branch merged --no-ff into main, so
        `git log --follow` must bridge the rename across a merge commit. Git's
        documentation calls --follow's handling of non-linear history limited;
        either outcome is safe under fail-closed semantics:
        exit 0 = lineage found through the merge (rename tracked);
        exit 1 = lineage lost => no proposed ancestor => fail closed.
        The assertion below pins the outcome OBSERVED on first run; if a git
        upgrade flips it, this test documents exactly what changed.

        Observed on branch 'main' with git version 2 (Apple Git-155, 2.50.1):
        exit 0 — git --follow successfully tracks the rename across the merge
        commit, so the proposed ancestor is found and the check passes.
        """
        repo = self.scratch()
        write(repo, "docs/adr/adr-draft-x.md", PROPOSED)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "draft")
        git(repo, "checkout", "-qb", "side")
        git(repo, "mv", "docs/adr/adr-draft-x.md", "docs/adr/adr-001-x.md")
        write(repo, "docs/adr/adr-001-x.md", accept(PROPOSED))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "accept on side")
        git(repo, "checkout", "-q", "main")
        write(repo, "README.md", "unrelated\n")
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "unrelated mainline work")
        git(repo, "merge", "-q", "--no-ff", "-m", "merge side", "side")
        code, err = check(os.path.join(repo, "docs/adr/adr-001-x.md"))
        self.assertEqual(code, 0)  # observed: exit 0 on git 2.50.1


if __name__ == "__main__":
    unittest.main()
