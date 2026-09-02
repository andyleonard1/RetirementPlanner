"""
PDF helper functions.
"""

from reportlab.platypus import Table
from reportlab.platypus import TableStyle

from reportlab.lib import colors


def financial_table(rows):

    table = Table(rows, colWidths=[220, 120])

    table.setStyle(

        TableStyle(

            [

                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),

                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

                ("TOPPADDING", (0, 0), (-1, -1), 6),

                ("LEFTPADDING", (0, 0), (-1, -1), 8),

                ("RIGHTPADDING", (0, 0), (-1, -1), 8),

            ]

        )

    )

    return table