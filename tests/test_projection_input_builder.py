import unittest

from planner.funds.investment_profile import (
    AVIVA_UNIVERSAL_2027,
    SKY_NEW_DRAWDOWN_LIFESTYLE,
    InvestmentProfile,
)
from planner.funds.projection_input_builder import ProjectionInputBuilder


class ProjectionInputBuilderTests(unittest.TestCase):
    def setUp(self):
        self.builder = ProjectionInputBuilder()

    def test_aviva_profile_is_eligible_with_limited_confidence(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertTrue(result.projection_eligible)
        self.assertEqual(result.confidence, "limited")

    def test_aviva_historical_data_is_classified_as_available(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertTrue(result.historical_return_available)

    def test_aviva_charge_is_available(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertTrue(result.charges_available)

    def test_aviva_missing_volatility_is_reported(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertFalse(result.volatility_available)
        self.assertIn("Volatility data is unavailable.", result.limitations)

    def test_aviva_missing_asset_weights_are_not_inferred(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertFalse(result.asset_allocation_available)
        self.assertIn("Asset allocation data is unavailable.", result.limitations)

    def test_sky_snapshot_is_historically_available(self):
        result = self.builder.build(SKY_NEW_DRAWDOWN_LIFESTYLE)
        self.assertTrue(result.projection_eligible)
        self.assertTrue(result.historical_return_available)

    def test_sky_missing_charge_is_reported(self):
        result = self.builder.build(SKY_NEW_DRAWDOWN_LIFESTYLE)
        self.assertFalse(result.charges_available)
        self.assertIn("Fund charge data is unavailable.", result.limitations)

    def test_sky_underlying_names_do_not_create_fake_asset_weights(self):
        result = self.builder.build(SKY_NEW_DRAWDOWN_LIFESTYLE)
        self.assertFalse(result.asset_allocation_available)
        self.assertIn("Asset allocation data is unavailable.", result.limitations)

    def test_identity_and_retirement_details_are_preserved(self):
        result = self.builder.build(AVIVA_UNIVERSAL_2027)
        self.assertEqual(result.fund_identifier, "GB00BRDCMN86:GBP")
        self.assertEqual(result.provider, "Aviva")
        self.assertEqual(
            result.fund_name,
            "Aviva Insured Funds Universal 2027 Retirement S14",
        )
        self.assertTrue(result.glide_path)
        self.assertEqual(result.target_retirement_year, 2027)

    def test_unknown_data_quality_is_ineligible(self):
        profile = InvestmentProfile(
            identifier="TEST",
            provider="Test",
            name="Test Fund",
            data_quality="unknown",
        )
        result = self.builder.build(profile)
        self.assertFalse(result.projection_eligible)
        self.assertFalse(result.historical_return_available)
        self.assertEqual(result.confidence, "ineligible")

    def test_complete_profile_can_reach_high_confidence(self):
        profile = InvestmentProfile(
            identifier="COMPLETE",
            provider="Test",
            name="Complete Fund",
            annual_charge=0.01,
            data_quality="complete_history",
            asset_allocation=(
                ("Global equity", 0.60),
                ("Bonds", 0.40),
            ),
        )
        result = self.builder.build(profile)
        self.assertTrue(result.projection_eligible)
        self.assertTrue(result.historical_return_available)
        self.assertTrue(result.charges_available)
        self.assertTrue(result.asset_allocation_available)
        self.assertFalse(result.volatility_available)
        self.assertEqual(result.confidence, "limited")

    def test_build_many_preserves_order(self):
        result = self.builder.build_many(
            [AVIVA_UNIVERSAL_2027, SKY_NEW_DRAWDOWN_LIFESTYLE]
        )
        self.assertEqual(
            [item.fund_identifier for item in result],
            ["GB00BRDCMN86:GBP", "SKY_NEW_DRAWDOWN_LIFESTYLE"],
        )

    def test_missing_data_is_not_fabricated(self):
        result = self.builder.build(SKY_NEW_DRAWDOWN_LIFESTYLE)
        self.assertFalse(result.volatility_available)
        self.assertFalse(result.asset_allocation_available)


if __name__ == "__main__":
    unittest.main()
