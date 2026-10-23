import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_window import ScenarioProjectionWindow
from planner.gui.testability import RecordingDialog, RecordingFileDialog
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication


class _FakeVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _FakeButton:
    def __init__(self):
        self.states = []

    def configure(self, **kwargs):
        self.states.append(kwargs.get("state"))


class Sprint203GuiReportSuiteTests(unittest.TestCase):
    def _window(self):
        application = ScenarioProjectionApplication(Assumptions())
        view_model = application.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        return ScenarioProjectionWindow(
            view_model,
            application=application,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )

    def test_gui_report_export_consumes_current_workflow_result(self):
        window = self._window()
        dialog = RecordingDialog()
        with tempfile.TemporaryDirectory() as directory:
            file_dialog = RecordingFileDialog(directory)
            captured = {}

            def exporter(**kwargs):
                captured.update(kwargs)
                return {"scenario_projection": Path(directory) / "scenario.pdf"}

            window._dialog = dialog
            window._file_dialog = file_dialog
            window._report_suite_exporter = exporter
            window.application.run_report_workflow = lambda **_: (_ for _ in ()).throw(
                AssertionError("GUI report export must not recalculate the published projection")
            )

            self.assertTrue(window._export_pdf_reports())

        self.assertIn("scenario_result", captured)
        self.assertIs(captured["scenario_result"].view_model, window.view_model)
        self.assertEqual(len(file_dialog.calls), 1)
        self.assertEqual(dialog.errors, [])
        self.assertEqual(len(dialog.infos), 1)

    def test_gui_report_export_blocks_stale_results(self):
        window = self._window()
        dialog = RecordingDialog()
        file_dialog = RecordingFileDialog("should-not-be-used")
        window._dialog = dialog
        window._file_dialog = file_dialog
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name in {"conservative", "central", "optimistic"}) for name in window.selected_scenarios}

        self.assertFalse(window._export_pdf_reports())
        self.assertEqual(len(file_dialog.calls), 0)
        self.assertEqual(len(dialog.errors), 1)
        self.assertIn("stale", dialog.errors[0][1])

    def test_gui_report_button_disables_when_results_are_stale(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name in window.selected_scenarios) for name in window.selected_scenarios}
        window._reports_button = _FakeButton()

        window._refresh_action_states()

        self.assertEqual(window._reports_button.states[-1], "disabled")


if __name__ == "__main__":
    unittest.main()
