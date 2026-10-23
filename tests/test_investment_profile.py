import unittest

from planner.funds.investment_profile import (
    AVIVA_UNIVERSAL_2027,
    SKY_NEW_DRAWDOWN_LIFESTYLE,
    InvestmentProfile,
    InvestmentProfileRegistry,
)


class InvestmentProfileTests(unittest.TestCase):
    def test_aviva_profile_has_real_identifier(self):
        self.assertEqual(AVIVA_UNIVERSAL_2027.identifier, "GB00BRDCMN86:GBP")
        self.assertEqual(AVIVA_UNIVERSAL_2027.provider, "Aviva")
        self.assertTrue(AVIVA_UNIVERSAL_2027.glide_path)

    def test_aviva_profile_records_target_year(self):
        self.assertEqual(AVIVA_UNIVERSAL_2027.target_retirement_year, 2027)
        self.assertEqual(AVIVA_UNIVERSAL_2027.investment_type, "target_retirement_fund")

    def test_sky_profile_records_underlying_investments(self):
        self.assertTrue(SKY_NEW_DRAWDOWN_LIFESTYLE.glide_path)
        self.assertEqual(len(SKY_NEW_DRAWDOWN_LIFESTYLE.underlying_investments), 3)

    def test_profiles_are_internal_metadata_not_allocations(self):
        self.assertFalse(hasattr(AVIVA_UNIVERSAL_2027, "allocation"))
        self.assertFalse(hasattr(SKY_NEW_DRAWDOWN_LIFESTYLE, "allocation"))

    def test_registry_retrieves_profile(self):
        registry = InvestmentProfileRegistry([AVIVA_UNIVERSAL_2027])
        self.assertIs(registry.get("GB00BRDCMN86:GBP"), AVIVA_UNIVERSAL_2027)

    def test_registry_rejects_duplicate_identifier(self):
        registry = InvestmentProfileRegistry([AVIVA_UNIVERSAL_2027])
        with self.assertRaises(ValueError):
            registry.add(AVIVA_UNIVERSAL_2027)

    def test_registry_reports_missing_profile(self):
        registry = InvestmentProfileRegistry()
        with self.assertRaises(KeyError):
            registry.get("missing")

    def test_negative_charge_is_rejected(self):
        profile = InvestmentProfile("A", "Provider", "Fund", annual_charge=-0.01)
        with self.assertRaises(ValueError):
            profile.validate()

    def test_invalid_asset_allocation_is_rejected(self):
        profile = InvestmentProfile(
            "A", "Provider", "Fund", asset_allocation=(("equity", 0.75),)
        )
        with self.assertRaises(ValueError):
            profile.validate()

    def test_registry_accepts_both_test_profiles(self):
        registry = InvestmentProfileRegistry(
            [AVIVA_UNIVERSAL_2027, SKY_NEW_DRAWDOWN_LIFESTYLE]
        )
        self.assertEqual(len(registry), 2)


if __name__ == "__main__":
    unittest.main()
