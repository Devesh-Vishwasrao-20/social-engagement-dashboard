
"""
Main Pipeline
Project: Data-Driven Social Engagement Initiative

Purpose:
Coordinate the project's analysis modules.
This file does not start or modify the Streamlit dashboard.
"""

from pathlib import Path
import importlib.util
import logging

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Folder containing the analysis modules
SOURCE_DIR = PROJECT_ROOT / "01_Source_Code"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Modules in the intended execution order
MODULES = [
    "module1_data_extraction.py",
    "module2_cleaning_sentiment.py",
    "module3_engagement_analysis.py",
    "module4_virality_model.py",
    "module5_statistical_tests.py",
    "module6_recommendations.py",
    "module7_visualizations.py",
]


def check_modules():
    """Check whether the expected source files exist."""
    missing = []

    for filename in MODULES:
        module_path = SOURCE_DIR / filename

        if module_path.is_file():
            logging.info("Found: %s", filename)
        else:
            missing.append(filename)
            logging.warning("Not found: %s", module_path)

    if missing:
        logging.warning(
            "Setup is incomplete. Create or locate the missing modules "
            "before running the full analysis."
        )
        return False

    return True


def main():
    """Main entry point for the project pipeline."""
    logging.info("Starting Social Engagement Initiative pipeline.")

    if not check_modules():
        logging.error("Pipeline stopped: required files are missing.")
        return

    logging.info(
        "All expected module files are present. "
        "Their execution functions must be connected next."
    )

    # IMPORTANT:
    # File presence alone does not run the analysis.
    # Add module function calls only after checking the actual
    # functions and input/output paths in each module.

    logging.info("Pipeline setup check completed.")


if __name__ == "__main__":
    main()
