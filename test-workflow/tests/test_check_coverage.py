#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "prd-to-milestones", "scripts", "check_coverage.py")
FIX = os.path.join(HERE, "..", "fixtures", "coverage")

def run(tree):
    return subprocess.run([sys.executable, TOOL, os.path.join(FIX, tree, "ROADMAP.md")],
                          capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_trees_pass(self):
        for tree in ("good-single-prd", "good-multi-prd", "good-retired-uncited"):
            with self.subTest(tree):
                r = run(tree)
                self.assertEqual(r.returncode, 0, r.stderr)

class TestBad(unittest.TestCase):
    EXPECT = {
        "bad-unassigned-req": "not covered by any milestone",
        "bad-cites-retired": "cites retired",
        "bad-cites-missing-req": "cites nonexistent REQ",
        "bad-cites-missing-prd": "cites nonexistent PRD",
    }
    def test_bad_trees_fail_with_location(self):
        for tree, needle in self.EXPECT.items():
            with self.subTest(tree):
                r = run(tree)
                self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (tree, r.returncode, r.stderr))
                self.assertIn(needle, r.stderr)
                self.assertRegex(r.stderr, r"\.md:\d+: ")

class TestEnvironment(unittest.TestCase):
    def test_malformed_prd_exits_2(self):
        r = run("env-malformed-prd")
        self.assertEqual(r.returncode, 2)
        self.assertIn("prd-001-broken.md", r.stderr)

    def test_invalid_roadmap_exits_2(self):
        r = run("env-invalid-roadmap")
        self.assertEqual(r.returncode, 2)

    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

if __name__ == "__main__":
    unittest.main()
