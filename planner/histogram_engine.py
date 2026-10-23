"""
Histogram Engine

Converts Monte Carlo results into histogram buckets
ready for charting.
"""

import logging

from planner.results import HistogramResult

logger = logging.getLogger(__name__)


class HistogramEngine:

    def build(self, values, buckets=20):

        logger.info(
            "Building histogram (%s buckets)",
            buckets,
        )

        minimum = min(values)
        maximum = max(values)

        if minimum == maximum:
            return HistogramResult(
                labels=[f"£{minimum:,.0f}"],
                counts=[len(values)],
            )

        bucket_size = (maximum - minimum) / buckets
        counts = [0] * buckets

        for value in values:
            index = int((value - minimum) / bucket_size)
            if index >= buckets:
                index = buckets - 1
            counts[index] += 1

        labels = []
        for i in range(buckets):
            lower = minimum + (i * bucket_size)
            labels.append(f"£{lower/1000000:.1f}M")

        return HistogramResult(
            labels=labels,
            counts=counts,
        )
