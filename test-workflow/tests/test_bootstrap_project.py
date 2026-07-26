#!/usr/bin/env python3
"""Tests for bootstrap_project.py — state-table classifier/applier (spec 03)."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "write-prd", "scripts", "bootstrap_project.py")
TX = os.path.join(HERE, "..", "..", "scripts", "session_tx.py")

CANONICAL_SECTION = (
    "## Doc-driven workflow\n"
    "\n"
    "Before any workflow task, read and follow\n"
    "@~/.agents/skills/system-architect-skills/WORKFLOW.md.\n"
)
CLAUDE_LINE = "@AGENTS.md"

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
}


def git_init(d):
    subprocess.run(
        ["git", "init", d],
        check=True,
        capture_output=True,
        env=GIT_ENV,
    )


def git_commit(d, msg, files):
    """Stage files and commit in repo at d."""
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false",
         "add", "--"] + files,
        cwd=d, check=True, capture_output=True, env=GIT_ENV,
    )
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false",
         "commit", "-m", msg],
        cwd=d, check=True, capture_output=True, env=GIT_ENV,
    )


def run_bootstrap(repo, subcommand, workflow_file, extra_args=None):
    """Run bootstrap_project.py with --workflow-path pointing to workflow_file."""
    cmd = [sys.executable, TOOL, subcommand, "--workflow-path", workflow_file]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, cwd=repo, capture_output=True, text=True, env=GIT_ENV)


def run_tx(repo, *args):
    return subprocess.run(
        [sys.executable, TX] + list(args),
        cwd=repo, capture_output=True, text=True, env=GIT_ENV,
    )


class TestBootstrap(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tmp = os.path.realpath(self._tmp)
        # Create a fake workflow file for --workflow-path
        self.workflow = os.path.join(self.tmp, "WORKFLOW.md")
        with open(self.workflow, "w") as f:
            f.write("# Fake workflow\n")
        # Separate scratch repo dir (created per test that needs it)
        self.repo = None

    def tearDown(self):
        # Restore permissions so tempfile cleanup works
        for root_dir, dirs, files in os.walk(self.tmp):
            for name in files:
                fp = os.path.join(root_dir, name)
                try:
                    os.chmod(fp, 0o644)
                except OSError:
                    pass
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_repo(self, subdir="repo"):
        repo = os.path.realpath(os.path.join(self.tmp, subdir))
        os.makedirs(repo, exist_ok=True)
        git_init(repo)
        # Need at least one commit so git commands work
        readme = os.path.join(repo, "README.md")
        with open(readme, "w") as f:
            f.write("# Test repo\n")
        git_commit(repo, "init", ["README.md"])
        self.repo = repo
        return repo

    # -----------------------------------------------------------------------
    # Case 1: not a git repo → plan exits 1, stderr contains "git init"
    # -----------------------------------------------------------------------
    def test_case_01_not_a_git_repo(self):
        plain = os.path.realpath(os.path.join(self.tmp, "plain"))
        os.makedirs(plain)
        before = set(os.listdir(plain))
        r = run_bootstrap(plain, "plan", self.workflow)
        self.assertEqual(r.returncode, 1, "expected exit 1 for non-git dir")
        self.assertIn("git init", r.stderr)
        after = set(os.listdir(plain))
        self.assertEqual(before, after, "dir contents must be unchanged")

    # -----------------------------------------------------------------------
    # Case 2: workflow path missing → exit 1, stderr contains "broken"
    # -----------------------------------------------------------------------
    def test_case_02_workflow_path_missing(self):
        repo = self.make_repo()
        r = run_bootstrap(repo, "plan", os.path.join(self.tmp, "nonexistent.md"))
        self.assertEqual(r.returncode, 1, "expected exit 1 for missing workflow")
        self.assertIn("broken", r.stderr)

    # -----------------------------------------------------------------------
    # Case 3: both files absent → plan exits 3 (two creates); apply exits 3;
    #         AGENTS.md == canonical; CLAUDE.md == "@AGENTS.md\n"; idempotent
    # -----------------------------------------------------------------------
    def test_case_03_both_absent(self):
        repo = self.make_repo()
        # plan
        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("AGENTS.md", r.stdout)
        self.assertIn("CLAUDE.md", r.stdout)
        self.assertIn("create", r.stdout)

        # apply
        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)

        agents_path = os.path.join(repo, "AGENTS.md")
        claude_path = os.path.join(repo, "CLAUDE.md")
        with open(agents_path) as f:
            agents_content = f.read()
        with open(claude_path) as f:
            claude_content = f.read()
        self.assertEqual(agents_content, CANONICAL_SECTION)
        self.assertEqual(claude_content, CLAUDE_LINE + "\n")

        # idempotent: re-run plan → exit 0
        r2 = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r2.returncode, 0, r2.stderr + r2.stdout)

    # -----------------------------------------------------------------------
    # Case 4: AGENTS.md present without section → append planned;
    #         after apply, original preserved as prefix, canonical section
    #         appended, exactly one blank line between.
    # -----------------------------------------------------------------------
    def test_case_04_agents_present_no_section(self):
        repo = self.make_repo()
        original = "# Existing content\n\nSome text here.\n"
        agents_path = os.path.join(repo, "AGENTS.md")
        with open(agents_path, "w") as f:
            f.write(original)

        # plan
        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("append", r.stdout)

        # apply
        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)

        with open(agents_path) as f:
            result = f.read()
        # original content preserved as prefix
        self.assertTrue(result.startswith(original), "original must be prefix")
        # canonical section appended
        self.assertTrue(result.endswith(CANONICAL_SECTION), "must end with canonical section")
        # exactly one blank line between original and canonical
        # original ends with "\n", separator should be "\n" (one blank line = two newlines total)
        between = result[len(original):]
        self.assertTrue(between.startswith("\n"), "must have blank line separator before canonical section")

    # -----------------------------------------------------------------------
    # Case 5: AGENTS.md with section heading + intact reference line → no-op
    # -----------------------------------------------------------------------
    def test_case_05_agents_section_intact(self):
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        with open(agents_path, "w") as f:
            f.write(CANONICAL_SECTION)
        # CLAUDE.md also present with reference so overall exit is 0 (no writes)
        claude_path = os.path.join(repo, "CLAUDE.md")
        with open(claude_path, "w") as f:
            f.write(CLAUDE_LINE + "\n")

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        # AGENTS.md row must be no-op
        self.assertIn("no-op", r.stdout)

    # -----------------------------------------------------------------------
    # Case 6: AGENTS.md with section heading, reference line altered → exit 1,
    #         stderr contains "malformed"
    # -----------------------------------------------------------------------
    def test_case_06_agents_section_malformed(self):
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        # Drop the ".md" from the reference line
        malformed = (
            "## Doc-driven workflow\n"
            "\n"
            "Before any workflow task, read and follow\n"
            "@~/.agents/skills/system-architect-skills/WORKFLOW\n"  # no .md
        )
        with open(agents_path, "w") as f:
            f.write(malformed)

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("malformed", r.stderr)

    # -----------------------------------------------------------------------
    # Case 7: AGENTS.md is a symlink → exit 1; target file untouched
    # -----------------------------------------------------------------------
    def test_case_07_agents_is_symlink(self):
        repo = self.make_repo()
        target = os.path.join(repo, "actual_agents.md")
        original_target = "# Target file\n"
        with open(target, "w") as f:
            f.write(original_target)
        agents_path = os.path.join(repo, "AGENTS.md")
        os.symlink(target, agents_path)

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 1, r.stdout)

        # Target file untouched
        with open(target) as f:
            self.assertEqual(f.read(), original_target)

    # -----------------------------------------------------------------------
    # Case 8: CLAUDE.md symlink → AGENTS.md → no-op row for CLAUDE.md
    # -----------------------------------------------------------------------
    def test_case_08_claude_symlink_to_agents(self):
        repo = self.make_repo()
        # Create AGENTS.md with canonical section (so it's no-op)
        agents_path = os.path.join(repo, "AGENTS.md")
        with open(agents_path, "w") as f:
            f.write(CANONICAL_SECTION)
        # CLAUDE.md → AGENTS.md
        claude_path = os.path.join(repo, "CLAUDE.md")
        os.symlink(agents_path, claude_path)

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("no-op", r.stdout)

    # -----------------------------------------------------------------------
    # Case 9: CLAUDE.md symlink → other.md → exit 1; other.md byte-identical
    # -----------------------------------------------------------------------
    def test_case_09_claude_symlink_elsewhere(self):
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        with open(agents_path, "w") as f:
            f.write(CANONICAL_SECTION)
        other = os.path.join(repo, "other.md")
        original_other = "# Other file\n"
        with open(other, "w") as f:
            f.write(original_other)
        claude_path = os.path.join(repo, "CLAUDE.md")
        os.symlink(other, claude_path)

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 1, r.stdout)

        with open(other) as f:
            self.assertEqual(f.read(), original_other, "other.md must be byte-identical")

    # -----------------------------------------------------------------------
    # Case 10: CLAUDE.md regular without reference → append planned;
    #          after apply, file ends with "@AGENTS.md\n", original intact
    # -----------------------------------------------------------------------
    def test_case_10_claude_regular_no_reference(self):
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        with open(agents_path, "w") as f:
            f.write(CANONICAL_SECTION)
        claude_path = os.path.join(repo, "CLAUDE.md")
        original = "# My Claude config\n\nSome settings.\n"
        with open(claude_path, "w") as f:
            f.write(original)

        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("append", r.stdout)

        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr)

        with open(claude_path) as f:
            result = f.read()
        self.assertTrue(result.endswith(CLAUDE_LINE + "\n"), "must end with @AGENTS.md\\n")
        self.assertIn(original.rstrip("\n"), result, "original content must be intact")

    # -----------------------------------------------------------------------
    # Case 11: append-then-fail rollback: AGENTS.md needs append, CLAUDE.md
    #          needs append but is unwritable (chmod 0o444, non-root) →
    #          apply exits 1, AGENTS.md byte-identical to pre-apply content
    # -----------------------------------------------------------------------
    @unittest.skipIf(os.geteuid() == 0, "root ignores mode bits")
    def test_case_11_rollback_on_write_failure(self):
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        original_agents = "# Pre-existing agents\n"
        with open(agents_path, "w") as f:
            f.write(original_agents)

        claude_path = os.path.join(repo, "CLAUDE.md")
        original_claude = "# Pre-existing claude\n"
        with open(claude_path, "w") as f:
            f.write(original_claude)
        # Make CLAUDE.md unwritable
        os.chmod(claude_path, 0o444)

        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

        # AGENTS.md must be byte-identical to pre-apply content (rolled back)
        with open(agents_path) as f:
            self.assertEqual(f.read(), original_agents, "AGENTS.md must be rolled back")
        # CLAUDE.md must be untouched (failed before writing)
        with open(claude_path) as f:
            self.assertEqual(f.read(), original_claude, "CLAUDE.md must be untouched")

    # -----------------------------------------------------------------------
    # Case 12: composition with session transaction:
    #   begin → track AGENTS.md CLAUDE.md → apply → abandon
    #   → both paths back to pre-session state
    # -----------------------------------------------------------------------
    def test_case_12_composition_with_session_tx(self):
        repo = self.make_repo()

        # Pre-existing AGENTS.md (needs append) — must be committed so
        # session_tx abandon can restore from HEAD
        agents_path = os.path.join(repo, "AGENTS.md")
        original_agents = "# Pre-existing agents\n"
        with open(agents_path, "w") as f:
            f.write(original_agents)
        git_commit(repo, "add agents", ["AGENTS.md"])

        # CLAUDE.md absent (will be created by apply)
        claude_path = os.path.join(repo, "CLAUDE.md")
        self.assertFalse(os.path.exists(claude_path))

        # Begin session
        r = run_tx(repo, "begin")
        self.assertEqual(r.returncode, 0, r.stderr)

        # Track both paths (AGENTS.md tracked, CLAUDE.md absent → "created")
        r = run_tx(repo, "track", "AGENTS.md", "CLAUDE.md")
        self.assertEqual(r.returncode, 0, r.stderr)

        # Apply bootstrap
        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)

        # Verify both written
        self.assertTrue(os.path.exists(agents_path))
        self.assertTrue(os.path.exists(claude_path))

        # Abandon the session → rollback
        r = run_tx(repo, "abandon")
        self.assertEqual(r.returncode, 0, r.stderr)

        # AGENTS.md: restored to pre-session state (byte-identical)
        with open(agents_path) as f:
            self.assertEqual(f.read(), original_agents, "AGENTS.md must be restored")
        # CLAUDE.md: created by session → must be gone
        self.assertFalse(os.path.exists(claude_path), "CLAUDE.md created by session must be deleted")

    # -----------------------------------------------------------------------
    # Exit-code contract: explicit checks
    # -----------------------------------------------------------------------
    def test_exit_code_0_no_op(self):
        """Exit 0 when fully installed (no writes needed)."""
        repo = self.make_repo()
        agents_path = os.path.join(repo, "AGENTS.md")
        claude_path = os.path.join(repo, "CLAUDE.md")
        with open(agents_path, "w") as f:
            f.write(CANONICAL_SECTION)
        with open(claude_path, "w") as f:
            f.write(CLAUDE_LINE + "\n")
        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_exit_code_2_usage(self):
        """Exit 2 for bad usage (no subcommand)."""
        repo = self.make_repo()
        r = subprocess.run(
            [sys.executable, TOOL, "--workflow-path", self.workflow],
            cwd=repo, capture_output=True, text=True, env=GIT_ENV,
        )
        self.assertEqual(r.returncode, 2, r.stderr + r.stdout)

    def test_exit_code_3_plan_writes(self):
        """Exit 3 for plan when writes are planned."""
        repo = self.make_repo()
        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)

    def test_exit_code_3_apply_writes(self):
        """Exit 3 for apply when writes are performed."""
        repo = self.make_repo()
        r = run_bootstrap(repo, "apply", self.workflow)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)

    def test_exit_code_1_stop_state(self):
        """Exit 1 for stop state (symlink AGENTS.md)."""
        repo = self.make_repo()
        target = os.path.join(repo, "actual.md")
        with open(target, "w") as f:
            f.write("# target\n")
        os.symlink(target, os.path.join(repo, "AGENTS.md"))
        r = run_bootstrap(repo, "plan", self.workflow)
        self.assertEqual(r.returncode, 1, r.stdout)


if __name__ == "__main__":
    unittest.main()
