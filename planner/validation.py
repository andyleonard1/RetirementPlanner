"""Timeline validation warnings."""

import logging


logger = logging.getLogger(__name__)


class ValidationEngine:

    def validate(self, timeline):

        for year in timeline:

            if year.closing_pension < 0:
                logger.warning(
                    "Pension below zero at age %s",
                    year.age,
                )

            if year.savings_closing < 0:
                logger.warning(
                    "Savings below zero at age %s",
                    year.age,
                )

            if year.isa_closing < 0:
                logger.warning(
                    "ISA below zero at age %s",
                    year.age,
                )
