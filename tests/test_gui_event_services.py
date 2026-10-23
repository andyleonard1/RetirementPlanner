import unittest

from planner.gui.event_services import RecordingEventService


class GuiEventServiceTests(unittest.TestCase):
    def test_recording_event_service_records_bindings(self):
        service = RecordingEventService()
        callback = lambda event: event
        service.bind("<Return>", callback)
        self.assertIs(service.bindings["<Return>"], callback)

    def test_recording_event_service_schedules_idle_callbacks(self):
        service = RecordingEventService()
        called = []
        service.after_idle(lambda: called.append(True))
        self.assertEqual(called, [])
        service.run_idle()
        self.assertEqual(called, [True])

    def test_idle_callbacks_are_consumed_once(self):
        service = RecordingEventService()
        called = []
        service.after_idle(lambda: called.append(True))
        service.run_idle()
        service.run_idle()
        self.assertEqual(called, [True])

    def test_window_keyboard_bindings_can_use_recording_service(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        from planner.assumptions import Assumptions

        app = ScenarioProjectionApplication(Assumptions())
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        service = RecordingEventService()
        window = ScenarioProjectionWindow(
            view,
            root=object(),
            application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            event_service=service,
        )
        window._bind_keyboard_shortcuts()
        self.assertEqual(set(service.bindings), {"<Return>", "<Escape>", "<Alt-r>", "<Alt-s>", "<Alt-t>", "<Alt-l>"})

    def test_focus_callback_is_safe_after_close(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel

        # The method is intentionally safe without Tk widgets.
        window = object.__new__(ScenarioProjectionWindow)
        window._closed = True
        window._entry_widgets = [object()]
        window._focus_pension_entry()


if __name__ == "__main__":
    unittest.main()
