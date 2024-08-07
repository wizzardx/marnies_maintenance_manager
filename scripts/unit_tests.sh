#!/bin/bash
set -euo pipefail

# Function to log messages
log() {
    echo "[INFO] $1"
}

# Check for --stop-on-first-error or -s argument
STOP_ON_FIRST_ERROR="no"
for arg in "$@";
do
    if [ "$arg" == "--stop-on-first-error" ] || [ "$arg" == "-s" ]; then
        STOP_ON_FIRST_ERROR="yes"
    else
        echo "Unknown argument: $arg"
        exit 1
    fi
done

# Setup Python version to use for the unit tests
log "Setting up Python version..."
pyenv local 3.12.4

# Setup the virtualenv dir.
log "Setup venv dir...."
scripts/setup_venv_dir.sh

# Activate the virtualenv
log "Activating virtual environment..."
VENV_DIR=$(scripts/print_venv_dir.sh)
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Clear out the pycached "lastfailed" marker if it refers to something besides the
# unit test tests:
log "Clearing out pycached 'lastfailed' marker..."
scripts/clear_functional_tests_pytest_lastfailed_marker.py

# Setup needed environment variables
log "Setting up environment variables..."
export DATABASE_URL=sqlite://:memory:  # Faster than PostgreSQL
export USE_DOCKER=no

TEST_USER_PASSWORD=$(scripts/print_test_user_password.sh)
export TEST_USER_PASSWORD

# The basic pytest command before we do any further alterations
log "Preparing pytest command..."
CMD=(
    pytest
        manies_maintenance_manager/jobs
        manies_maintenance_manager/users
        --doctest-modules
        --reuse-db
)

# If STOP_ON_FIRST_ERROR is set, then fail after the first error:
if [ "$STOP_ON_FIRST_ERROR" == "yes" ]; then
    CMD+=("--maxfail=1")
fi

# If there are no recently-failed tests, then we use the extra parallelizations to
# help run things super fast. (When there are recently-failed tests, then we
# don't use these options, because they make it a bit harder follow my TDD workflow).
if [ ! -f .pytest_cache/v/cache/lastfailed ]; then
    log "Adding parallel execution and DB migration-disabling options..."
    CMD+=("-n" "auto")
    CMD+=("--nomigrations")
else
    # Not running unit tests in parallel, so lets show the top 10 slowest unit tests.
    # In parallel mode these measurments are less useful.
    log "Adding options to show the slowest 10 tests"
    CMD+=("--durations=10")
fi

# Run the unit tests:
log "Running unit tests..."
# shellcheck disable=SC2068
"${CMD[@]}"

# If we got this far, then there were no test errors. Now we can clear some data from
# the pytest cache so that we don't -repeatedly get warnings like this:
# "run-last-failure: 16 known failures not in selected tests"
if [ -f .pytest_cache/v/cache/lastfailed ]; then
    log "Removing obsolete pytest cache file..."
    rm -vf .pytest_cache/v/cache/lastfailed
fi

log "Script execution completed successfully."
