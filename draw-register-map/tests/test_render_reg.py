import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from render_reg import _field_table  # noqa: E402


class FieldTableTests(unittest.TestCase):
    def test_generic_attributes_are_preserved(self) -> None:
        table = _field_table(
            {},
            [
                {"name": "opcode", "bits": 7, "attr": "0010011"},
                {"name": "operation", "bits": 3, "attr": ["ADD", "SLT", "XOR"]},
            ],
        )

        self.assertIn("| Bits | Field | Attributes | Description |", table)
        self.assertIn("| [6:0] | opcode | 0010011 |", table)
        self.assertIn("ADD<br>SLT<br>XOR", table)
        self.assertNotIn("| Access |", table)

    def test_bit_offset_applies_to_every_table_row(self) -> None:
        table = _field_table(
            {},
            [{"name": "low", "bits": 1}, {"name": "high", "bits": 31}],
            bit_offset=32,
        )

        self.assertIn("| [63:33] | high |", table)
        self.assertIn("| [32] | low |", table)

    def test_register_table_uses_explicit_access_and_reset(self) -> None:
        table = _field_table(
            {"name": "CTRL", "kind": "register"},
            [
                {
                    "name": "EN",
                    "bits": 1,
                    "access": "RW",
                    "reset": "0",
                    "desc": "Enable.",
                }
            ],
        )

        self.assertIn("| Bits | Field | Access | Reset | Description |", table)
        self.assertIn("| [0] | EN | RW | 0 | Enable. |", table)

    def test_register_table_rejects_generic_attributes(self) -> None:
        with self.assertRaisesRegex(ValueError, "register fields use access/reset"):
            _field_table(
                {"name": "CTRL"},
                [{"name": "EN", "bits": 1, "attr": ["RW", "0"]}],
            )

    def test_explicit_zero_dimensions_are_rejected(self) -> None:
        script = SKILL_DIR / "scripts" / "render_reg.py"
        example = SKILL_DIR / "examples" / "dma_ctrl.json"
        for option in ("--bits", "--lanes"):
            with self.subTest(option=option):
                result = subprocess.run(
                    [sys.executable, str(script), str(example), option, "0"],
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must be", result.stderr)

    def test_invalid_field_mode_writes_no_outputs(self) -> None:
        script = SKILL_DIR / "scripts" / "render_reg.py"
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            source = directory_path / "invalid.json"
            output = directory_path / "result"
            source.write_text(
                json.dumps(
                    {
                        "name": "CTRL",
                        "width": 1,
                        "fields": [{"name": "EN", "bits": 1, "attr": ["RW", "0"]}],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(script), str(source), "--out", str(output)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(Path(f"{output}.svg").exists())
            self.assertFalse(Path(f"{output}.md").exists())


if __name__ == "__main__":
    unittest.main()
