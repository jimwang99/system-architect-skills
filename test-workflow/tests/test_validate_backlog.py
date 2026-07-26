#!/usr/bin/env python3
import os, subprocess, sys, tempfile, shutil, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "..", "write-prd", "scripts", "validate_backlog.py")
FIX = os.path.join(HERE, "..", "fixtures", "backlog")

def run(path):
    return subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True)

class TestGood(unittest.TestCase):
    def test_good_fixtures_pass(self):
        for name in os.listdir(FIX):
            if name.startswith("good"):
                with self.subTest(name):
                    r = run(os.path.join(FIX, name))
                    self.assertEqual(r.returncode, 0, r.stderr)

class TestBad(unittest.TestCase):
    def test_bad_fixtures_fail_with_location(self):
        for name in os.listdir(FIX):
            if name.startswith("bad"):
                with self.subTest(name):
                    r = run(os.path.join(FIX, name))
                    self.assertEqual(r.returncode, 1, "%s: %s" % (name, r.stderr))
                    self.assertRegex(r.stderr, r"\.md:\d+: ")

class TestCli(unittest.TestCase):
    def test_missing_arg_exits_2(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
    def test_unreadable_exits_2(self):
        r = run(os.path.join(FIX, "no-such-file.md"))
        self.assertEqual(r.returncode, 2)

class TestSlugFilename(unittest.TestCase):
    def test_illegal_slug_filenames_exit_1(self):
        good = os.path.join(FIX, "good-product.md")
        tmp = tempfile.mkdtemp()
        try:
            for bad_name in ("Trailing-.md", "a--b.md"):
                dst = os.path.join(tmp, bad_name)
                shutil.copy(good, dst)
                r = run(dst)
                with self.subTest(bad_name):
                    self.assertEqual(r.returncode, 1, r.stderr)
                    self.assertIn(bad_name, r.stderr)
        finally:
            shutil.rmtree(tmp)

class TestMetadataPlacement(unittest.TestCase):
    def test_type_under_options_mentions_between(self):
        r = run(os.path.join(FIX, "bad-type-under-options.md"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("between", r.stderr)

if __name__ == "__main__":
    unittest.main()
