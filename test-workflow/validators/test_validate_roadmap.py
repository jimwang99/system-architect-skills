#!/usr/bin/env python3
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_roadmap import validate  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def fixture(name):
    return os.path.join(FIX, name)


class TestGoodFixtures(unittest.TestCase):
    def test_all_good_fixtures_pass(self):
        for name in sorted(os.listdir(FIX)):
            if name.startswith("good-"):
                with self.subTest(name):
                    self.assertEqual(validate(fixture(name)), [])


class TestBadFixtures(unittest.TestCase):
    # fixture name -> substring that must appear in at least one error
    EXPECT = {
        "bad-missing-status.md": "Current Workflow Status",
        "bad-duplicate-key.md": "duplicate key",
        "bad-next-action-placeholder.md": "Next action",
        "bad-feature-status.md": "illegal feature status",
        "bad-milestone-state.md": "illegal milestone state",
        "bad-duplicate-feature-id.md": "duplicate feature ID",
        "bad-duplicate-milestone-id.md": "duplicate milestone ID",
        "bad-tuple-state-none.md": "illegal summary tuple",
        "bad-tuple-review-ready-wip.md": "illegal summary tuple",
        "bad-agreement-state.md": "does not match summary",
        "bad-agreement-active-feature.md": "active feature",
        "bad-ordering-past-not-accepted.md": "before the current milestone",
        "bad-evidence-missing-field.md": "missing evidence field",
        "bad-evidence-tests-failed.md": "Tests must begin 'pass'",
        "bad-evidence-verdict-reject.md": "Verdict must be",
        "bad-evidence-findings-unresolved.md": "Findings must be",
        "bad-sequence-done-after-todo.md": "out of order",
        "bad-two-wip.md": "more than one WIP",
        "bad-failed-no-learning.md": "Learning",
        "bad-review-ready-unfinished.md": "must be done",
        "bad-malformed-milestone-heading.md": "malformed milestone heading",
        "bad-malformed-feature-heading.md": "malformed feature heading",
        "bad-duplicate-status-section.md": "duplicate '## Current Workflow Status' section",
    }

    def test_bad_fixtures_fail_with_expected_error(self):
        for name, needle in self.EXPECT.items():
            with self.subTest(name):
                errs = validate(fixture(name))
                self.assertTrue(errs, "expected errors for " + name)
                self.assertTrue(any(needle in e for e in errs), errs)

    def test_every_error_is_line_referenced(self):
        for name in self.EXPECT:
            for e in validate(fixture(name)):
                self.assertRegex(e, r":\d+: ")


if __name__ == "__main__":
    unittest.main()
