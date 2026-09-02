import unittest

from planner.simulation.sequence_risk import SequenceRiskAnalyzer


class SequenceRiskTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = SequenceRiskAnalyzer()

    def test_same_returns_in_different_order_can_change_outcome_with_withdrawals(self):
        result = self.analyzer.compare(
            1000.0,
            [-0.20, 0.20],
            [0.20, -0.20],
            withdrawals=[100.0, 100.0],
        )
        self.assertNotEqual(result.first_terminal_value, result.second_terminal_value)
        self.assertGreater(result.absolute_difference, 0.0)

    def test_same_sequence_produces_zero_difference(self):
        returns = [-0.10, 0.05, 0.08]
        result = self.analyzer.compare(1000.0, returns, returns)
        self.assertEqual(result.absolute_difference, 0.0)
        self.assertEqual(result.percentage_difference, 0.0)

    def test_return_sets_must_match(self):
        with self.assertRaises(ValueError):
            self.analyzer.compare(1000.0, [0.1, 0.2], [0.1, 0.3])

    def test_withdrawals_must_match_return_count(self):
        with self.assertRaises(ValueError):
            self.analyzer.terminal_value(1000.0, [0.1, 0.1], [50.0])

    def test_negative_withdrawal_is_rejected(self):
        with self.assertRaises(ValueError):
            self.analyzer.terminal_value(1000.0, [0.1], [-1.0])

    def test_negative_starting_value_is_rejected(self):
        with self.assertRaises(ValueError):
            self.analyzer.terminal_value(-1.0, [0.1])

    def test_depletion_is_floored_at_zero(self):
        self.assertEqual(
            self.analyzer.terminal_value(100.0, [-0.5], [100.0]),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
