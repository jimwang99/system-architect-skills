#!/usr/bin/env python3
"""Tests for session_tx.py — stdlib unittest, scratch repos via subprocess."""
import os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "session_tx.py")

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
}

COMMIT_FLAGS = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"]


def git(repo, *args):
    return subprocess.run(
        ["git"] + list(args),
        cwd=repo,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def git_commit(repo, *args):
    """git commit with required identity flags."""
    return subprocess.run(
        ["git"] + COMMIT_FLAGS + ["commit"] + list(args),
        cwd=repo,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def tx(repo, *args):
    return subprocess.run(
        [sys.executable, TOOL] + list(args),
        cwd=repo,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def make_repo():
    """Create a scratch git repo with one committed file base.txt. Returns realpath."""
    d = tempfile.mkdtemp()
    d = os.path.realpath(d)
    git(d, "init")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    git(d, "config", "commit.gpgsign", "false")
    with open(os.path.join(d, "base.txt"), "w") as f:
        f.write("original content\n")
    git(d, "add", "base.txt")
    git_commit(d, "-m", "init")
    return d


class TestBeginDoubleBegin(unittest.TestCase):
    """Case 1: begin then begin again exits 1 mentioning an active session."""

    def setUp(self):
        self.repo = make_repo()

    def test_double_begin_exits_1(self):
        r1 = tx(self.repo, "begin")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        r2 = tx(self.repo, "begin")
        self.assertEqual(r2.returncode, 1, r2.stderr)
        self.assertIn("session", r2.stderr.lower())


class TestTrackCleanTracked(unittest.TestCase):
    """Case 2: track a clean tracked file → 0; manifest lists it via status."""

    def setUp(self):
        self.repo = make_repo()

    def test_track_clean_tracked(self):
        tx(self.repo, "begin")
        r = tx(self.repo, "track", "base.txt")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = tx(self.repo, "status")
        self.assertEqual(s.returncode, 0)
        self.assertIn("base.txt", s.stdout)


class TestTrackDirtyTracked(unittest.TestCase):
    """Case 3: track a dirty tracked file exits 1, manifest unchanged."""

    def setUp(self):
        self.repo = make_repo()

    def test_track_dirty_exits_1(self):
        # dirty the file before begin
        with open(os.path.join(self.repo, "base.txt"), "a") as f:
            f.write("extra\n")
        tx(self.repo, "begin")
        r = tx(self.repo, "track", "base.txt")
        self.assertEqual(r.returncode, 1, r.stderr)
        # manifest should not list base.txt
        s = tx(self.repo, "status")
        self.assertNotIn("base.txt", s.stdout)


class TestTrackExistingUntracked(unittest.TestCase):
    """Case 4: track new.md when new.md already exists untracked → exit 1."""

    def setUp(self):
        self.repo = make_repo()

    def test_track_existing_untracked_exits_1(self):
        with open(os.path.join(self.repo, "new.md"), "w") as f:
            f.write("already here\n")
        tx(self.repo, "begin")
        r = tx(self.repo, "track", "new.md")
        self.assertEqual(r.returncode, 1, r.stderr)


class TestPreviewNewAndModified(unittest.TestCase):
    """Case 5: track absent new.md (0), write it, preview shows contents + 'new file';
    modify base.txt after tracking, preview shows unified diff hunk."""

    def setUp(self):
        self.repo = make_repo()

    def test_preview_new_file_and_diff(self):
        tx(self.repo, "begin")
        # track both paths before writing
        r = tx(self.repo, "track", "new.md", "base.txt")
        self.assertEqual(r.returncode, 0, r.stderr)

        # now write new.md
        with open(os.path.join(self.repo, "new.md"), "w") as f:
            f.write("hello world\n")

        # modify base.txt after tracking
        with open(os.path.join(self.repo, "base.txt"), "a") as f:
            f.write("added line\n")

        p = tx(self.repo, "preview")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("new file", p.stdout)
        self.assertIn("hello world", p.stdout)
        # unified diff hunk for base.txt
        self.assertIn("@@", p.stdout)


class TestApproveCommit(unittest.TestCase):
    """Case 6: approve -m msg → exactly one new commit, git show lists manifest paths, manifest gone."""

    def setUp(self):
        self.repo = make_repo()

    def _commit_count(self):
        r = git(self.repo, "rev-list", "--count", "HEAD")
        return int(r.stdout.strip())

    def test_approve_creates_one_commit(self):
        before = self._commit_count()
        tx(self.repo, "begin")
        tx(self.repo, "track", "base.txt", "new.md")

        with open(os.path.join(self.repo, "new.md"), "w") as f:
            f.write("content\n")
        with open(os.path.join(self.repo, "base.txt"), "a") as f:
            f.write("change\n")

        r = tx(self.repo, "approve", "-m", "test commit")
        self.assertEqual(r.returncode, 0, r.stderr)

        after = self._commit_count()
        self.assertEqual(after - before, 1)

        # git show --name-only lists only the manifest paths
        show = git(self.repo, "show", "--name-only", "HEAD")
        shown_paths = [
            line for line in show.stdout.strip().splitlines()
            if line and not line.startswith("commit")
            and not line.startswith("Author")
            and not line.startswith("Date")
            and not line.startswith("    ")
        ]
        self.assertIn("base.txt", shown_paths)
        self.assertIn("new.md", shown_paths)

        # manifest file gone
        git_dir_r = git(self.repo, "rev-parse", "--git-dir")
        gd = git_dir_r.stdout.strip()
        if not os.path.isabs(gd):
            gd = os.path.join(self.repo, gd)
        manifest = os.path.join(gd, "session-tx.json")
        self.assertFalse(os.path.exists(manifest), "manifest file should be gone after approve")


class TestApproveStagedOutside(unittest.TestCase):
    """Case 7: pre-staged non-manifest change before approve → exits 1, no commit."""

    def setUp(self):
        self.repo = make_repo()

    def _commit_count(self):
        r = git(self.repo, "rev-list", "--count", "HEAD")
        return int(r.stdout.strip())

    def test_staged_outside_manifest_fails(self):
        tx(self.repo, "begin")
        tx(self.repo, "track", "base.txt")

        before = self._commit_count()

        # stage a non-manifest file
        with open(os.path.join(self.repo, "other.txt"), "w") as f:
            f.write("x\n")
        git(self.repo, "add", "other.txt")

        r = tx(self.repo, "approve", "-m", "should fail")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self._commit_count(), before)


class TestAbandon(unittest.TestCase):
    """Case 8: abandon restores tracked file, deletes created file, bystander untouched, manifest gone."""

    def setUp(self):
        self.repo = make_repo()

    def test_abandon(self):
        # modify bystander BEFORE begin (non-manifest dirty file)
        bystander = os.path.join(self.repo, "bystander.txt")
        with open(bystander, "w") as f:
            f.write("bystander original\n")
        git(self.repo, "add", "bystander.txt")
        git_commit(self.repo, "-m", "add bystander")

        # Now dirty bystander before begin — it should survive abandon
        with open(bystander, "a") as f:
            f.write("bystander modified\n")

        with open(bystander) as f:
            bystander_dirty_content = f.read()

        tx(self.repo, "begin")
        tx(self.repo, "track", "base.txt", "created.md")

        with open(os.path.join(self.repo, "base.txt")) as f:
            original_base = f.read()

        # modify tracked file
        with open(os.path.join(self.repo, "base.txt"), "a") as f:
            f.write("session change\n")
        # write created file
        with open(os.path.join(self.repo, "created.md"), "w") as f:
            f.write("new content\n")

        r = tx(self.repo, "abandon")
        self.assertEqual(r.returncode, 0, r.stderr)

        # tracked file restored byte-identical
        with open(os.path.join(self.repo, "base.txt")) as f:
            self.assertEqual(f.read(), original_base)
        # created file deleted
        self.assertFalse(os.path.exists(os.path.join(self.repo, "created.md")))
        # bystander still dirty and intact
        with open(bystander) as f:
            self.assertEqual(f.read(), bystander_dirty_content)
        # manifest gone
        git_dir_r = git(self.repo, "rev-parse", "--git-dir")
        gd = git_dir_r.stdout.strip()
        if not os.path.isabs(gd):
            gd = os.path.join(self.repo, gd)
        manifest = os.path.join(gd, "session-tx.json")
        self.assertFalse(os.path.exists(manifest))


class TestAbandonStagedMidSession(unittest.TestCase):
    """Case 10: abandon must reset the index too — mid-session `git add` of both a
    tracked and a created manifest path must not survive abandon."""

    def setUp(self):
        self.repo = make_repo()

    def test_abandon_resets_index(self):
        with open(os.path.join(self.repo, "base.txt")) as f:
            original_base = f.read()

        tx(self.repo, "begin")
        r = tx(self.repo, "track", "base.txt", "created.md")
        self.assertEqual(r.returncode, 0, r.stderr)

        # modify tracked file, write created file
        with open(os.path.join(self.repo, "base.txt"), "a") as f:
            f.write("session change\n")
        with open(os.path.join(self.repo, "created.md"), "w") as f:
            f.write("new content\n")

        # stage BOTH mid-session (e.g. a sub-step or a crashed/retried approve)
        git(self.repo, "add", "base.txt", "created.md")

        r = tx(self.repo, "abandon")
        self.assertEqual(r.returncode, 0, r.stderr)

        # index clean: no staged changes survive
        staged = git(self.repo, "diff", "--cached")
        self.assertEqual(staged.stdout, "", "index not clean after abandon:\n%s" % staged.stdout)
        # worktree clean for tracked paths
        unstaged = git(self.repo, "diff")
        self.assertEqual(unstaged.stdout, "", "worktree not clean after abandon:\n%s" % unstaged.stdout)
        # tracked file byte-identical to pre-session
        with open(os.path.join(self.repo, "base.txt")) as f:
            self.assertEqual(f.read(), original_base)
        # created file gone from disk and from the index (no ghost AD entry)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "created.md")))
        ls = git(self.repo, "ls-files", "--", "created.md")
        self.assertEqual(ls.stdout.strip(), "", "ghost index entry for created.md")
        # fully clean repo: nothing staged, nothing modified, nothing untracked
        status = git(self.repo, "status", "--porcelain")
        self.assertEqual(status.stdout, "", "repo not clean after abandon:\n%s" % status.stdout)


class TestDeletionFlow(unittest.TestCase):
    """Case 9: track base.txt, delete it, preview shows deletion diff, approve commits deletion."""

    def setUp(self):
        self.repo = make_repo()

    def _commit_count(self):
        r = git(self.repo, "rev-list", "--count", "HEAD")
        return int(r.stdout.strip())

    def test_deletion_flow(self):
        tx(self.repo, "begin")
        tx(self.repo, "track", "base.txt")

        base_path = os.path.join(self.repo, "base.txt")
        os.remove(base_path)

        # preview shows deletion diff
        p = tx(self.repo, "preview")
        self.assertEqual(p.returncode, 0, p.stderr)
        # git diff of a deleted file shows --- line and +++ /dev/null
        self.assertIn("---", p.stdout)

        before = self._commit_count()
        r = tx(self.repo, "approve", "-m", "delete base.txt")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self._commit_count() - before, 1)

        # show commit contents — assert path list, not exact output equality
        show = git(self.repo, "show", "--name-only", "HEAD")
        lines = show.stdout.strip().splitlines()
        path_lines = [
            l for l in lines
            if l and not l.startswith("commit")
            and not l.startswith("Author")
            and not l.startswith("Date")
            and not l.startswith(" ")
        ]
        self.assertIn("base.txt", path_lines)


if __name__ == "__main__":
    unittest.main()
