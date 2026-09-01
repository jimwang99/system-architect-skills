"""Regression tests for the hardware-specification contract validator."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_spec.py"

MODULE_SPEC = importlib.util.spec_from_file_location(
    "write_hardware_spec_validator", VALIDATOR_PATH
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = VALIDATOR
MODULE_SPEC.loader.exec_module(VALIDATOR)


def merged_spec(*, purpose_suffix: str = "", test_mapping: str = "FR-01, TR-01") -> str:
    """Return a minimal structurally complete merged specification."""
    text = textwrap.dedent(
        f"""\
        # Demo Specification
        ## Purpose
        Demonstrate validation.__PURPOSE_SUFFIX__
        ## Parameters
        None.
        ## Interfaces
        None.
        ## Functional Requirements
        | ID | Requirement |
        |---|---|
        | FR-01 | Produce a result. |
        ## Timing Requirements
        | ID | Requirement |
        |---|---|
        | TR-01 | Produce the result exactly 1 cycle after acceptance. |
        ## Reset-Visible Behavior
        No transfer occurs during reset; recovery takes exactly 1 cycle.
        ## Non-Goals
        - No buffering.
        ## Block Diagram
        ```mermaid
        flowchart LR
            input --> demo --> output
        ```
        ## Implementation Detail
        The output is registered.
        ## Sub-Block Decomposition
        One datapath block.
        ## Internal Signals and Storage
        One output register.
        ## Reset Behavior
        The output register resets to zero.
        ## Critical Timing Paths
        Input to the output-register D pin.
        ## Requirement Mapping
        FR-01 and TR-01 map to the datapath and output register.
        ## Test Plan
        | ID | Maps To | Check |
        |---|---|---|
        | T-01 | {test_mapping} | Observe the result at the required cycle. |
        """
    )
    suffix = f"\n{purpose_suffix}" if purpose_suffix else ""
    return text.replace("__PURPOSE_SUFFIX__", suffix)


class ValidatorBehaviorTest(unittest.TestCase):
    def validate_text(self, text: str):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "demo_spec.md"
            path.write_text(text)
            return VALIDATOR.validate(path, "merged")

    def test_rejects_mapping_to_undefined_requirement(self):
        report = self.validate_text(merged_spec(test_mapping="FR-99"))
        self.assertIn("UNKNOWN_MAPPING", {item.code for item in report.diagnostics})

    def test_rejects_common_angle_bracket_placeholder(self):
        report = self.validate_text(
            merged_spec(purpose_suffix="Replace <Block Name> before review.")
        )
        self.assertIn("UNRESOLVED_MARKER", {item.code for item in report.diagnostics})

    def test_rejects_unsupported_diagram_forms(self):
        fixtures = {
            "Markdown image": "![diagram](flow.webp)",
            "reference-style image": "![diagram][flow]\n\n[flow]: flow.svg",
            "HTML image": '<img src="flow.svg" alt="diagram">',
            "Graphviz fence": "```dot\ngraph G { a -- b }\n```",
            "unfenced Graphviz graph": "graph G { a -- b }",
        }
        for label, diagram in fixtures.items():
            with self.subTest(label=label):
                report = self.validate_text(merged_spec(purpose_suffix=diagram))
                self.assertIn(
                    "FORBIDDEN_DIAGRAM", {item.code for item in report.diagnostics}
                )

    def test_accepts_mermaid_diagram(self):
        report = self.validate_text(
            merged_spec(
                purpose_suffix="```mermaid\nflowchart LR\n  a --> b\n```"
            )
        )
        self.assertNotIn(
            "FORBIDDEN_DIAGRAM", {item.code for item in report.diagnostics}
        )

    def test_rejects_ascii_block_diagram(self):
        text = merged_spec().replace(
            "```mermaid\nflowchart LR\n    input --> demo --> output\n```",
            "```text\ninput -> demo -> output\n```",
        )
        report = self.validate_text(text)
        self.assertIn(
            "MISSING_MERMAID_DIAGRAM",
            {item.code for item in report.diagnostics},
        )

    def test_rejects_ascii_pipeline_diagram(self):
        report = self.validate_text(
            merged_spec(
                purpose_suffix="## Pipeline Diagram\n```text\nS0 -> S1\n```"
            )
        )
        self.assertIn(
            "MISSING_MERMAID_DIAGRAM",
            {item.code for item in report.diagnostics},
        )

    def test_rejects_ascii_common_flow_and_fsm_sections(self):
        for heading in ("FSM Sketch", "Control Flow", "Data Flow"):
            with self.subTest(heading=heading):
                report = self.validate_text(
                    merged_spec(
                        purpose_suffix=f"## {heading}\n```text\nIdle -> Run\n```"
                    )
                )
                self.assertIn(
                    "MISSING_MERMAID_DIAGRAM",
                    {item.code for item in report.diagnostics},
                )

    def test_allows_merged_pipeline(self):
        report = self.validate_text(
            merged_spec(purpose_suffix="## Pipeline Stages\nA two-stage pipeline.")
        )
        self.assertNotIn(
            "COMPLEX_REQUIRES_SPLIT",
            {item.code for item in report.diagnostics},
        )

    def test_rejects_unmapped_fsm_transition(self):
        report = self.validate_text(
            merged_spec(
                purpose_suffix=(
                    "## FSM Transitions\n"
                    "| ID | From | To | Condition |\n"
                    "|---|---|---|---|\n"
                    "| FSM-CTRL-01 | Idle | Run | start_i |"
                )
            )
        )
        self.assertIn(
            "UNCOVERED_TRANSITION",
            {item.code for item in report.diagnostics},
        )

    def test_fsm_transition_may_map_to_assertion_or_coverage(self):
        for heading, item in (
            ("Assertions", "- ASSERT_START maps to FSM-CTRL-01."),
            ("Coverage", "- CVR_START covers FSM-CTRL-01."),
        ):
            with self.subTest(heading=heading):
                report = self.validate_text(
                    merged_spec(
                        purpose_suffix=(
                            "## FSM Transitions\n"
                            "| ID | From | To | Condition |\n"
                            "|---|---|---|---|\n"
                            "| FSM-CTRL-01 | Idle | Run | start_i |\n"
                            f"### {heading}\n{item}"
                        )
                    )
                )
                self.assertNotIn(
                    "UNCOVERED_TRANSITION",
                    {item.code for item in report.diagnostics},
                )


class ContractAlignmentTest(unittest.TestCase):
    def test_contract_declares_merged_implementation_detail_heading(self):
        contract = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn(
            "In merged format, place these sections under a REQUIRED "
            "`Implementation Detail` heading.",
            contract,
        )

    def test_contract_covers_illegal_fsm_encodings(self):
        contract = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn(
            "Define recovery or assertion behavior for illegal state encodings.",
            contract,
        )

    def test_contract_requires_referenced_local_files_to_exist(self):
        contract = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("Every referenced local file exists.", contract)

    def test_contract_resolves_or_accepts_important_findings(self):
        contract = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn(
            "Important findings are resolved or explicitly accepted by the user.",
            contract,
        )


if __name__ == "__main__":
    unittest.main()
