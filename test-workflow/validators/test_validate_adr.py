#!/usr/bin/env python3
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
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


if __name__ == "__main__":
    unittest.main()
