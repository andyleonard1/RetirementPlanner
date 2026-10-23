import importlib
import re
import unittest
from pathlib import Path

from planner.assumption_consumer_catalog import CONSUMERS, consumer_modules
from planner.assumption_usage_catalog import ROLES, schema_paths


class Sprint241AssumptionEndToEndConsumerTraceTests(unittest.TestCase):
    def _module_source(self, module_name):
        module = importlib.import_module(module_name)
        path = Path(module.__file__).with_suffix(".py")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _evidence_tokens(path):
        if path.startswith("goals["):
            return ("goals",)
        accessor_tokens = {
            "expected_return": ("monte_carlo_expected_return",),
            "platform_charge": ("platform_charge",),
            "fund_charge": ("fund_charge",),
            "investment_return_schedule_enabled": ("investment_return_schedule_enabled",),
            "investment_return_schedule": ("investment_return_schedule",),
            "isa_return_schedule_enabled": ("isa_return_schedule_enabled",),
            "isa_return_schedule": ("isa_return_schedule",),
        }
        return (path,) + accessor_tokens.get(path, ())

    def test_every_schema_assumption_has_runtime_consumer_evidence(self):
        missing = []
        for path in schema_paths():
            evidence = self._evidence_tokens(path)
            sources = {
                module_name: self._module_source(module_name)
                for module_name in consumer_modules(path)
            }
            if not any(
                any(re.search(rf"\b{re.escape(token)}\b", source) for token in evidence)
                for source in sources.values()
            ):
                missing.append(path)
        self.assertEqual([], missing)

    def test_legacy_aliases_trace_only_through_resolver(self):
        for path in ("inflation", "savings_interest", "pension_growth"):
            self.assertEqual(("planner.assumption_resolver",), consumer_modules(path))
            source = self._module_source("planner.assumption_resolver")
            self.assertIn(f'"{path}"', source)

    def test_projection_and_monte_carlo_boundaries_remain_distinct(self):
        self.assertNotEqual(CONSUMERS["projection"], CONSUMERS["monte_carlo"])
        self.assertIn("planner.monte_carlo_engine", CONSUMERS["monte_carlo"])
        self.assertIn("planner.planner", CONSUMERS["projection"])

    def test_consumer_catalog_covers_every_declared_operational_role(self):
        self.assertEqual(set(ROLES.values()), set(CONSUMERS))
        self.assertTrue(all(consumer_modules(path) for path in schema_paths()))


if __name__ == "__main__":
    unittest.main()
