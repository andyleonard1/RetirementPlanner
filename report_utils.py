"""
Shared report formatting utilities.
"""


def currency(value):

    return f"£{value:,.0f}"


def heading(title):

    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
    print()


def section(title):

    print()
    print(title)
    print("-" * len(title))