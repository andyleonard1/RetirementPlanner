import unittest

from planner.simulation.monte_carlo import MonteCarloEngine, SimulationConfig


class MonteCarloInfrastructureTests(unittest.TestCase):
    def test_seed_reproduces_paths(self):
        c = SimulationConfig(paths=3, years=4, seed=7)
        self.assertEqual(MonteCarloEngine(c).generate_return_paths(),
                         MonteCarloEngine(c).generate_return_paths())

    def test_different_seed_changes_paths(self):
        a = MonteCarloEngine(SimulationConfig(paths=2, years=3, seed=1))
        b = MonteCarloEngine(SimulationConfig(paths=2, years=3, seed=2))
        self.assertNotEqual(a.generate_return_paths(), b.generate_return_paths())

    def test_terminal_value(self):
        self.assertAlmostEqual(
            MonteCarloEngine.terminal_values(100.0, [[0.10, 0.10]])[0], 121.0)

    def test_zero_returns_preserve_value(self):
        self.assertEqual(
            MonteCarloEngine.terminal_values(100.0, [[0.0, 0.0]]), [100.0])

    def test_summary_counts(self):
        c = SimulationConfig(paths=20, years=5, seed=3)
        s = MonteCarloEngine(c).summarise(1000.0)
        self.assertEqual((s.paths, s.years), (20, 5))

    def test_success_probability_bounds(self):
        s = MonteCarloEngine(SimulationConfig(paths=50, years=5, seed=9)).summarise(1000.0, 500.0)
        self.assertGreaterEqual(s.success_probability, 0.0)
        self.assertLessEqual(s.success_probability, 1.0)

    def test_invalid_config_rejected(self):
        with self.assertRaises(ValueError):
            MonteCarloEngine(SimulationConfig(paths=0))

    def test_negative_start_rejected(self):
        e = MonteCarloEngine(SimulationConfig(paths=2, years=2))
        with self.assertRaises(ValueError):
            e.summarise(-1.0)


if __name__ == '__main__':
    unittest.main()
