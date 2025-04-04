import logging
import subprocess

logger = logging.getLogger(__name__)


def run_test(test_file, test_type: str, test_env: str = None):
    if test_type != "pytest":
        raise Exception(f"{test_type} not implemented use: pytest")

    result = subprocess.run(
        ["pytest", test_file, "-W", "ignore::DeprecationWarning"],
        capture_output=True,
        text=True,
        env=test_env,
    )

    logger.info(result.stdout)  # Print pytest output

    if result.returncode != 0:
        logger.warning("Tests failed or encountered errors.")
