"""
Goal Report
"""


class GoalReport:

    def print(self, goals):

        print()

        print("=" * 60)
        print("RETIREMENT GOALS")
        print("=" * 60)
        print()

        for goal in goals:

            icon = "[OK]" if goal["passed"] else "[FAIL]"

            print(
                f"{icon} {goal['name']}"
            )

            print(
                f"    Target : {goal['target']}"
            )

            print(
                f"    Actual : {goal['actual']}"
            )

            print()

        passed = sum(
            1 for g in goals if g["passed"]
        )

        print(
            f"Goals achieved: {passed}/{len(goals)}"
        )

        print()