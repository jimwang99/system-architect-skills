"""Show writeback, redirect, and ALU-select paths in an in-order pipeline."""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HELPER_DIR = (
    SCRIPT_DIR if (SCRIPT_DIR / "uarch.py").is_file() else SCRIPT_DIR.parent / "scripts"
)
sys.path.insert(0, str(HELPER_DIR))

from uarch import Figure  # noqa: E402


def build() -> Figure:
    figure = Figure(
        "Five-stage in-order pipeline",
        question="Where do writeback, redirect, and ALU-select paths go?",
        omit=["clock/reset", "cache internals", "exception details"],
    )
    pipeline = figure.pipeline(registers=True)

    fetch = pipeline.stage("IF", group="Frontend")
    decode = pipeline.stage("ID", group="Frontend")
    execute = pipeline.stage("EX", group="Backend")
    memory = pipeline.stage("MEM", group="Backend")
    writeback = pipeline.stage("WB", group="Backend")

    instruction_cache = fetch.mem(
        "I$ + Fetch", inputs="pc", outputs="instruction", sub="32 KiB"
    )
    register_file = decode.mem(
        "Decode + RegFile",
        inputs=["instruction", "writeback"],
        outputs="operands",
        sub="32 × 64b, 2R1W",
    )
    alu = execute.unit(
        "ALU + Branch",
        inputs="operands",
        outputs=["result", "redirect"],
        bottom="select",
    )
    hazard = execute.control("Hazard control", top="select").accent()
    data_cache = memory.mem(
        "D$ / MEM path",
        inputs="result",
        outputs=["alu_result", "load_data"],
        sub="32 KiB D$",
    )
    result_mux = writeback.mux(
        "Result mux", inputs=["alu_result", "load_data"], outputs="writeback"
    )

    figure.bus(instruction_cache.instruction, register_file.instruction, width=32)
    figure.bus(register_file.operands, alu.operands, width=128)
    figure.bus(alu.result, data_cache.result, width=64)
    figure.bus(data_cache.alu_result, result_mux.alu_result, width=64)
    figure.bus(data_cache.load_data, result_mux.load_data, width=64)
    figure.ctrl(hazard.select, alu.select)
    figure.ctrl(alu.redirect, instruction_cache.pc, label="redirect", back=True)
    figure.bus(
        result_mux.writeback,
        register_file.writeback,
        width=64,
        label="writeback",
        back=True,
    )
    return figure


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=SCRIPT_DIR / "pipeline5")
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()
    build().render(args.out, png=args.png)


if __name__ == "__main__":
    main()
