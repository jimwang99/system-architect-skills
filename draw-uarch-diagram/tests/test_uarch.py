import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from uarch import Figure  # noqa: E402


class FigureTests(unittest.TestCase):
    def test_manual_layout_expands_canvas_and_reports_cost(self) -> None:
        figure = Figure("Flow", question="Where does data move?")
        frame = figure.columns()
        source = frame.column("Source").io("Host", outputs="request")
        destination = frame.column("Destination").unit("Engine", inputs="request")
        destination.at(100, 100)
        figure.bus(source.request, destination.request, width=64).via((50, 90))

        with tempfile.TemporaryDirectory() as directory:
            path = figure.render(Path(directory) / "manual")
            root = ElementTree.parse(path).getroot()

        self.assertGreater(float(root.attrib["width"]), 2_000)
        self.assertGreater(float(root.attrib["height"]), 2_000)
        self.assertTrue(
            any("manual layout cost" in finding.message for finding in figure.lint())
        )

    def test_route_leaves_and_enters_declared_port_sides(self) -> None:
        figure = Figure("Control", question="Where does select go?")
        stage = figure.pipeline(registers=False).stage("EX")
        destination = stage.unit("ALU", bottom="select")
        source = stage.control("Hazard", top="select")
        edge = figure.ctrl(source.select, destination.select)

        figure._layout()
        points = figure._route(edge, 0)
        source_point = source.select.point()
        destination_point = destination.select.point()

        self.assertLess(points[1][1], source_point[1])
        self.assertGreater(points[-2][1], destination_point[1])
        self.assertNotEqual(points[-2], points[-1])

    def test_skip_stage_edge_needs_an_explicit_route(self) -> None:
        figure = Figure("Bypass", question="Where does the bypass go?")
        frame = figure.columns()
        source = frame.column("A").unit("Source", outputs="data")
        frame.column("B").unit("Occupied")
        destination = frame.column("C").unit("Destination", inputs="data")
        edge = figure.bus(source.data, destination.data, width=32)

        self.assertTrue(
            any(
                finding.severity == "error"
                and "skips an occupied stage" in finding.message
                for finding in figure.lint()
            )
        )
        edge.via((12, 16), (34, 16))
        self.assertFalse(any(finding.severity == "error" for finding in figure.lint()))

        figure._layout()
        points = figure._route(edge, 0)
        self.assertTrue(
            all(
                first[0] == second[0] or first[1] == second[1]
                for first, second in zip(points, points[1:])
            )
        )
        middle_box = frame.stages[1].blocks[0]._box
        self.assertFalse(
            any(
                self._segment_crosses_box(first, second, middle_box)
                for first, second in zip(points, points[1:])
            )
        )

    def test_same_stage_non_facing_edge_needs_an_explicit_route(self) -> None:
        figure = Figure("Stage internals", question="How does data cross the stage?")
        stage = figure.pipeline(registers=False).stage("EX")
        source = stage.unit("A", outputs="data")
        stage.unit("B")
        destination = stage.unit("C", inputs="data")
        edge = figure.wire(source.data, destination.data)

        self.assertTrue(
            any(
                finding.severity == "error" and "same-stage edge" in finding.message
                for finding in figure.lint()
            )
        )
        edge.via((12, 16), (12, 24))
        self.assertFalse(any(finding.severity == "error" for finding in figure.lint()))

    @staticmethod
    def _segment_crosses_box(
        first: tuple[float, float],
        second: tuple[float, float],
        box: tuple[float, float, float, float],
    ) -> bool:
        x, y, width, height = box
        if first[1] == second[1]:
            low, high = sorted((first[0], second[0]))
            return y < first[1] < y + height and low < x + width and high > x
        low, high = sorted((first[1], second[1]))
        return x < first[0] < x + width and low < y + height and high > y


if __name__ == "__main__":
    unittest.main()
