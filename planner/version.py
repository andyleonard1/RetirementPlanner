"""
Application version information.

This file is the single source of truth for version
details displayed throughout the Retirement Planner.
"""

from datetime import date

# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APPLICATION_NAME = "Retirement Planner"

# Semantic Versioning
VERSION = "2.0.0-rc1"

# Build information
BUILD_DATE = date.today().isoformat()

# Friendly display string
FULL_VERSION = f"{APPLICATION_NAME} {VERSION}"

# Copyright
COPYRIGHT = "© 2026 Andy Leonard"

# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def banner():

    line = "=" * 60

    return (
        f"{line}\n"
        f"{APPLICATION_NAME}\n"
        f"Version : {VERSION}\n"
        f"Build   : {BUILD_DATE}\n"
        f"{COPYRIGHT}\n"
        f"{line}"
    )