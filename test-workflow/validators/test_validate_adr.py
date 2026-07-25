#!/usr/bin/env python3
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "validate_adr.py")
sys.path.insert(0, HERE)
from validate_adr import validate  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "adr")
GOOD = os.path.join(FIX, "good")
BAD = os.path.join(FIX, "bad")


class TestGoodAdrFixtures(unittest.TestCase):
    def test_all_good_fixtures_pass(self):
        for name in sorted(os.listdir(GOOD)):
            with self.subTest(name):
                self.assertEqual(validate(os.path.join(GOOD, name)), [])


class TestBadAdrFixtures(unittest.TestCase):
    # bad/<dir> -> (file to validate, required error substring)
    EXPECT = {
        "unknown-key": ("adr-draft-log-format.md", "unknown key"),
        "dup-key": ("adr-draft-log-format.md", "duplicate key"),
        "name-status": ("adr-draft-log-format.md", "filename"),
        "bad-date": ("adr-draft-log-format.md", "ISO date"),
        "decided-on-proposed": ("adr-draft-log-format.md", "decided"),
        "missing-decided": ("adr-001-caching-strategy.md", "decided"),
        "missing-superseded-by": ("adr-002-sync-transport.md", "superseded-by"),
        "illegal-status": ("adr-draft-log-format.md", "illegal status"),
        "bad-resolves": ("adr-draft-log-format.md", "kebab-case"),
        "empty-section": ("adr-draft-log-format.md", "non-empty"),
        "section-order": ("adr-draft-log-format.md", "order"),
        "missing-section": ("adr-draft-log-format.md", "missing section"),
        "alt-no-reason": ("adr-draft-log-format.md", "rejection reason"),
        "no-alternatives": ("adr-draft-log-format.md", "alternative"),
        "dup-number": ("adr-001-a.md", "not unique"),
        "dangling-pointer": ("adr-004-orphan.md", "counterpart"),
        "unflipped-target": ("adr-004-new.md", "must be superseded"),
        "rejected-successor": ("adr-004-x.md", "filename grammar"),
        "undecodable-counterpart": ("adr-004-x.md", "unreadable"),
        "undecodable-primary": ("adr-001-x.md", "unreadable"),
        "impossible-date": ("adr-draft-log-format.md", "ISO date"),
        "compact-date": ("adr-draft-log-format.md", "ISO date"),
        "week-date": ("adr-draft-log-format.md", "ISO date"),
    }

    def test_bad_fixtures_fail_with_expected_error(self):
        for d, (fname, needle) in self.EXPECT.items():
            with self.subTest(d):
                errs = validate(os.path.join(BAD, d, fname))
                self.assertTrue(errs, "expected errors for " + d)
                self.assertTrue(any(needle in e for e in errs), errs)

    def test_every_error_is_line_referenced(self):
        for d, (fname, _) in self.EXPECT.items():
            for e in validate(os.path.join(BAD, d, fname)):
                self.assertRegex(e, r":\d+: ")


class TestCliContract(unittest.TestCase):
    def _run(self, *argv):
        return subprocess.run([sys.executable, SCRIPT] + list(argv), capture_output=True, text=True)

    def test_missing_file_exits_2(self):
        r = self._run(os.path.join(HERE, "no-such-file.md"))
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertTrue(r.stderr.strip())

    def test_no_args_exits_2(self):
        r = self._run()
        self.assertEqual(r.returncode, 2)

    def test_good_fixture_exits_0(self):
        r = self._run(os.path.join(GOOD, "adr-001-caching-strategy.md"))
        self.assertEqual(r.returncode, 0)

    def test_bad_fixture_exits_1(self):
        r = self._run(os.path.join(BAD, "illegal-status", "adr-draft-log-format.md"))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
