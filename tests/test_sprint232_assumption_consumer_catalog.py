import importlib
import unittest

from planner.assumption_consumer_catalog import (
    CONSUMERS,
    consumer_modules,
    unclassified_consumer_roles,
)
from planner.assumption_usage_catalog import ROLES, schema_paths


class Sprint232AssumptionConsumerCatalogTests(unittest.TestCase):
    def test_every_operational_role_has_a_consumer_boundary(self):
        self.assertEqual(unclassified_consumer_roles(), ())
        self.assertEqual(set(ROLES.values()), set(CONSUMERS))

    def test_every_schema_path_resolves_to_a_non_empty_consumer_boundary(self):
        for path in schema_paths():
            self.assertTrue(consumer_modules(path), path)

    def test_declared_consumer_modules_are_importable(self):
        for modules in CONSUMERS.values():
            for module_name in modules:
                importlib.import_module(module_name)

    def test_legacy_and_auxiliary_boundaries_remain_distinct(self):
        self.assertEqual(consumer_modules("inflation"), ("planner.assumption_resolver",))
        self.assertIn("planner.simulation.tax_free_cash", consumer_modules("target_net_income"))
        self.assertNotEqual(consumer_modules("target_net_income"), consumer_modules("inflation"))


if __name__ == "__main__":
    unittest.main()
