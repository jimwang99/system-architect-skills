#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "act-learn-improve", "scripts", "validate_learning.py")
FIX = os.path.join(HERE, "..", "fixtures", "learning")
GOOD = os.path.join(FIX, "good")
BAD = os.path.join(FIX, "bad")

def run(path):
    return subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_fixtures_pass(self):
        for name in sorted(os.listdir(GOOD)):
            if name.endswith(".md"):
                with self.subTest(name):
                    r = run(os.path.join(GOOD, name))
                    self.assertEqual(r.returncode, 0, r.stderr)

class TestBad(unittest.TestCase):
    def test_bad_fixtures_fail_with_location(self):
        for cls in sorted(os.listdir(BAD)):
            d = os.path.join(BAD, cls)
            for name in sorted(os.listdir(d)):
                if name.endswith(".md"):
                    with self.subTest(cls):
                        r = run(os.path.join(d, name))
                        self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (cls, r.returncode, r.stderr))
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
