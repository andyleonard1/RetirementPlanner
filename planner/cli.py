"""Shared command-line helpers for loading retirement assumptions."""

import argparse

from planner.assumptions import Assumptions


def add_assumptions_argument(parser: argparse.ArgumentParser) -> None:
    """Add the optional assumptions-file argument to an application parser."""
    parser.add_argument(
        "--assumptions",
        metavar="PATH",
        default="data/assumptions.json",
        help="path to the assumptions JSON file (default: data/assumptions.json)",
    )


def load_assumptions(path: str) -> Assumptions:
    """Load one validated assumptions document for a public CLI entry point."""
    return Assumptions(filename=path)
