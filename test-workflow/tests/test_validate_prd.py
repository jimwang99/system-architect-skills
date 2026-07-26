#!/usr/bin/env python3
import os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "write-prd", "scripts", "validate_prd.py")
FIX = os.path.join(HERE, "..", "fixtures", "prd")
GOOD = os.path.join(FIX, "good")
BAD = os.path.join(FIX, "bad")

def run(path):
    return subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True)


class TestGood(unittest.TestCase):
    def test_good_fixtures_pass(self):
        for root, dirs, files in os.walk(GOOD):
            dirs.sort()
            for name in sorted(files):
                if not name.endswith(".md"):
                    continue
                path = os.path.join(root, name)
                with self.subTest(path=os.path.relpath(path, FIX)):
                    r = run(path)
                    self.assertEqual(r.returncode, 0, r.stderr)


class TestBad(unittest.TestCase):
    def test_bad_fixtures_fail_with_location(self):
        for root, dirs, files in os.walk(BAD):
            dirs.sort()
            for name in sorted(files):
                if not name.endswith(".md"):
                    continue
                path = os.path.join(root, name)
                with self.subTest(path=os.path.relpath(path, FIX)):
                    r = run(path)
                    self.assertEqual(r.returncode, 1, "%s: exit=%d\n%s" % (path, r.returncode, r.stderr))
                    self.assertRegex(r.stderr, r"\.md:\d+: ", "no location in stderr for %s:\n%s" % (path, r.stderr))


class TestCli(unittest.TestCase):
    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_unreadable_exits_2(self):
        r = run(os.path.join(FIX, "no-such-file.md"))
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
