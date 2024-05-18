#!/usr/bin/env python3

"""Helper script for merging in upstream changes to the cookiecutter template.

Generates a new Django cookiecutter output project using my original options, checks
what has changed between my original cookiecutter output project and this project,
and then launches the "meld" tool against the latest version of my project's versions
of those files, to help me grab and merge in the latest upstream changes to the
cookiecutter.
"""

import logging
import os
import shutil
import subprocess  # nosec
import sys
import tempfile
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_command(
    command: list[str],
    *,
    ignore_errors: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run the referenced command, check the result, and return the result.

    Args:
        command (list[str]): The command to run as a list of arguments.
        ignore_errors (bool): If set to True then don't terminate on errors.

    Returns:
        subprocess.CompletedProcess[str]: The result of the command execution.
    """
    result2 = subprocess.run(  # nosec
        command,  # noqa: S603
        check=False,
        text=True,
        capture_output=True,
    )
    if result2.returncode != 0:
        logging.error("Command failed: %s\n%s", " ".join(command), result2.stderr)
        if not ignore_errors:
            sys.exit(1)
    return result2


def md5sum(path: Path) -> str:
    """Return md5sum hash of the referenced file.

    Args:
        path (Path): The path to the file.

    Returns:
        str: The md5sum hash.
    """
    result2 = run_command(["md5sum", str(path)])
    md5 = result2.stdout.split()[0]
    md5sum_num_chars = 32
    if len(md5) != md5sum_num_chars:
        logging.error("Doesn't look like an md5sum: %s", md5)
        sys.exit(1)
    return md5


def md5sum_end_stripped(path: Path) -> str:
    """Return md5sum of a file after the end of it has its whitespace stripped off.

    Args:
        path (Path): The path to the file.

    Returns:
        str: The md5sum hash of the stripped file.
    """
    with path.open(encoding="utf-8") as f:
        s1 = f.read()
        s2 = s1.rstrip()
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(s2)
        stripped_path = Path(tmp.name)
    return md5sum(stripped_path)


# Variables
TEMPLATE_REPO = "gh:cookiecutter/cookiecutter-django"
ORIGINAL_TEMPLATE_BRANCH = "original_template"
CURRENT_PROJECT_DIR = Path.cwd()
NEW_TEMPLATE_BRANCH = "updated_template"
COOKIECUTTER_DIR = Path("/home/david/.cookiecutters/cookiecutter-django")

# Use tempfile for new template directory
NEW_TEMPLATE_DIR = Path(tempfile.mkdtemp(prefix="new_template_project_"))

# Step 0: Tidy up previous runs
logging.info("Tidying up from previous runs...")
run_command(["git", "checkout", "main"])
shutil.rmtree(COOKIECUTTER_DIR, ignore_errors=True)
shutil.rmtree(NEW_TEMPLATE_DIR, ignore_errors=True)
run_command(["git", "remote", "remove", "new_template"], ignore_errors=True)

# Step 1: Create a new project using the latest Cookiecutter template
logging.info("Creating a new project using the latest Cookiecutter template...")
run_command(
    ["cookiecutter", "--replay", TEMPLATE_REPO, "--output-dir", str(NEW_TEMPLATE_DIR)],
)

# Step 2: Initialize and commit new template
logging.info(
    "Initializing Git in the new template directory and committing all files...",
)
new_template_project_dir = NEW_TEMPLATE_DIR / "manies_maintenance_manager"
os.chdir(new_template_project_dir)
run_command(["git", "init"])
run_command(["git", "add", "."])
run_command(["git", "commit", "-m", "Initial commit of new template"])

# Step 3: Add as a remote and fetch
logging.info("Adding new template as a remote and fetching it...")
os.chdir(CURRENT_PROJECT_DIR)
run_command(["git", "remote", "add", "new_template", str(new_template_project_dir)])
run_command(["git", "fetch", "new_template"])

# Get files that changed between original and new template
result = run_command(
    ["git", "diff", ORIGINAL_TEMPLATE_BRANCH, "new_template/main", "--name-only"],
)
changed_files = [p for p in result.stdout.split("\n") if p]

logging.info("Opening Meld for the changed template files...")
for name in changed_files:
    name2 = name.strip()

    original_file = new_template_project_dir / name2
    current_file = CURRENT_PROJECT_DIR / name2

    current_file = Path(str(current_file).replace("manie", "marnie"))

    if not original_file.is_file():
        sys.exit("File (1) not found: " + str(original_file))

    if not current_file.is_file():
        sys.exit("File (2) not found: " + str(current_file))

    if md5sum_end_stripped(original_file) == md5sum_end_stripped(current_file):
        continue

    run_command(["meld", str(original_file), str(current_file)])

# Cleanup
logging.info("Cleaning up...")
run_command(["git", "remote", "remove", "new_template"])