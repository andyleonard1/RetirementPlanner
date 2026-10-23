"""Console presentation for precomputed retirement-goal results."""


class GoalReport:

    def print(self, goals):

        print()

        print("=" * 60)
        print("RETIREMENT GOALS")
        print("=" * 60)
        print()

        for goal in goals:

            icon = "[OK]" if goal["passed"] else "[FAIL]"
            operator = goal.get("operator", "")
            constraint = f"{operator} {goal['target']}" if operator else str(goal["target"])

            print(f"{icon} {goal['name']}")
            print(f"    Constraint: {constraint}")
            print(f"    Target    : {goal['target']}")
            print(f"    Actual    : {goal['actual']}")
            print()

        passed = sum(1 for g in goals if g["passed"])

        print(f"Goals achieved: {passed}/{len(goals)}")
        print()
