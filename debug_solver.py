from planner.assumptions import Assumptions
from planner.services.retirement_solver import RetirementSolver

assumptions = Assumptions()

solver = RetirementSolver(assumptions)

age = solver.find_earliest_age()

print()
print("Returned age:", age)