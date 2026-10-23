import unittest


class TestSmoke(unittest.TestCase):

    def test_python_is_running(self):
        self.assertTrue(True)

    def test_can_import_planner(self):
        import planner.planner

    def test_can_import_pension_engine(self):
        import planner.pension_engine

    def test_can_import_tax_engine(self):
        import planner.tax_engine

    def test_can_import_cashflow_engine(self):
        import planner.cashflow_engine

    def test_can_import_monte_carlo_engine(self):
        import planner.monte_carlo_engine


if __name__ == "__main__":
    unittest.main()