class ValidationEngine:

    def validate(self, timeline):

        for year in timeline:

            if year.closing_pension < 0:
                print(f"WARNING: Pension below zero at age {year.age}")

            if year.savings_closing < 0:
                print(f"WARNING: Savings below zero at age {year.age}")

            if year.isa_closing < 0:
                print(f"WARNING: ISA below zero at age {year.age}")