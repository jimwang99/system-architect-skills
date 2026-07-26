#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "review-milestone", "scripts", "validate_review.py")
FIX = os.path.join(HERE, "..", "fixtures", "review")

def run(path):
    return subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_fixtures_pass(self):
        good = os.path.join(FIX, "good")
        for d in sorted(os.listdir(good)):
            p = os.path.join(good, d)
            for name in sorted(os.listdir(p)):
                if name.endswith(".md"):
                    with self.subTest(d):
                        r = run(os.path.join(p, name))
                        self.assertEqual(r.returncode, 0, "%s: %s" % (d, r.stderr))

class TestBad(unittest.TestCase):
    def test_bad_fixtures_fail_with_location(self):
        bad = os.path.join(FIX, "bad")
        for d in sorted(os.listdir(bad)):
            p = os.path.join(bad, d)
            for name in sorted(os.listdir(p)):
                if name.endswith(".md"):
                    with self.subTest(d):
                        r = run(os.path.join(p, name))
                        self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (d, r.returncode, r.stderr))
                        self.assertRegex(r.stderr, r"\.md:\d+: ")

class TestCli(unittest.TestCase):
    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_unreadable_exits_2(self):
        r = run(os.path.join(FIX, "no-such.md"))
        self.assertEqual(r.returncode, 2)

if __name__ == "__main__":
    unittest.main()
