import json

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


planner = RetirementPlanner(
    Assumptions()
)

result = planner.run()

golden = []

for year in result.timeline:

    golden.append({

        "age": year.age,

        "calendar_year": year.calendar_year,

        "opening_pension": year.opening_pension,

        "closing_pension": year.closing_pension,

        "isa_opening": year.isa_opening,

        "isa_closing": year.isa_closing,

        "savings_opening": year.savings_opening,

        "savings_closing": year.savings_closing,

        "household_income": year.household_net_income,

        "total_assets": year.total_assets,

    })

with open(
    "tests/golden/baseline.json",
    "w",
    encoding="utf8",
) as f:

    json.dump(
        golden,
        f,
        indent=4,
    )

print("Golden Scenario created.")