from planner.assumptions import Assumptions
from planner.services.retirement_solver import RetirementSolver

solver = RetirementSolver(
    Assumptions()
)

results = solver.explore(55, 70)

print()

print(
    f"{'Age':<5}"
    f"{'Success':<10}"
    f"{'Assets':>15}"
)

for r in results:

    print(
        f"{r.age:<5}"
        f"{str(r.success):<10}"
        f"£{r.ending_assets:>14,.0f}"
    )