import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_window import ScenarioProjectionWindow
from planner.gui.testability import RecordingDialog, RecordingFileDialog
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication


class _FakeButton:
    def __init__(self):
        self.states = []

    def configure(self, **kwargs):
        self.states.append(kwargs.get("state"))


class Sprint206GuiReportPackTests(unittest.TestCase):
    def _window(self):
        application = ScenarioProjectionApplication(Assumptions())
        view_model = application.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        window = ScenarioProjectionWindow(
            view_model,
            application=application,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        window._run_projection()
        return window

    def test_gui_report_pack_reuses_current_workflow_result_and_publishes_pack(self):
        window = self._window()
        dialog = RecordingDialog()
        with tempfile.TemporaryDirectory() as directory:
            file_dialog = RecordingFileDialog(directory)
            captured = {}

            def suite_exporter(**kwargs):
                captured.update(kwargs)
                return {"scenario_projection": Path(directory) / "scenario.pdf"}

            def pack_exporter(suite_result, output):
                captured["suite_result"] = suite_result
                captured["pack_output"] = output
                return output

            window._dialog = dialog
            window._file_dialog = file_dialog
            window._report_suite_exporter = suite_exporter
            window._report_pack_exporter = pack_exporter
            window.application.run_report_workflow = lambda **_: (_ for _ in ()).throw(
                AssertionError("GUI report pack export must not recalculate the published projection")
            )

            self.assertTrue(window._export_pdf_report_pack())

            self.assertIs(captured["scenario_result"].view_model, window.view_model)
            self.assertEqual(captured["pack_output"], Path(directory) / "RetirementPlanner_Report_Pack.pdf")
            self.assertEqual(len(file_dialog.calls), 1)
            self.assertEqual(dialog.errors, [])
            self.assertEqual(len(dialog.infos), 1)

    def test_gui_report_pack_blocks_existing_pack_before_suite_generation(self):
        window = self._window()
        dialog = RecordingDialog()
        with tempfile.TemporaryDirectory() as directory:
            pack_path = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
            pack_path.write_bytes(b"existing")
            file_dialog = RecordingFileDialog(directory)
            called = []

            def suite_exporter(**kwargs):
                called.append(True)
                return {}

            window._dialog = dialog
            window._file_dialog = file_dialog
            window._report_suite_exporter = suite_exporter
            window._report_pack_exporter = lambda *_args, **_kwargs: None

            self.assertFalse(window._export_pdf_report_pack())
            self.assertEqual(called, [])
            self.assertEqual(pack_path.read_bytes(), b"existing")
            self.assertEqual(len(dialog.errors), 1)

    def test_gui_report_pack_button_tracks_current_result_state(self):
        window = self._window()
        button = _FakeButton()
        window._report_pack_button = button
        window._refresh_status()
        self.assertIn("normal", button.states)

        window._pension_var = type("Var", (), {"get": lambda self: "700000"})()
        window._retirement_age_var = type("Var", (), {"get": lambda self: "64"})()
        window._end_age_var = type("Var", (), {"get": lambda self: "90"})()
        window._scenario_vars = {
            name: type("Var", (), {"get": lambda self, name=name: name in {"conservative", "central", "optimistic"}})()
            for name in window.selected_scenarios
        }
        window._refresh_status()
        self.assertEqual(button.states[-1], "disabled")


if __name__ == "__main__":
    unittest.main()
