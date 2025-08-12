#!/bin/bash
#
# Fenrir Updater Script (Robust Version)
# This script automates updating Fenrir by finding and using the correct
# Python interpreter from the project's virtual environment.
#
# Usage: ./update_fenrir.sh

# --- Style Functions for better output ---
bold=$(tput bold)
normal=$(tput sgr0)
green=$(tput setaf 2)
yellow=$(tput setaf 3)
red=$(tput setaf 1)

# --- Error Logging ---
error_log=""

echo "${bold}${green}--- Starting Fenrir Update ---${normal}"

# 1. Check for prerequisite commands
if ! command -v git &> /dev/null || ! command -v poetry &> /dev/null; then
    echo "${bold}${red}Fatal Error: 'git' or 'poetry' is not installed. Please install them to continue.${normal}"
    exit 1
fi

# 2. Fetch latest changes from the repository
echo "\n${yellow}Step 1: Pulling latest changes from Git...${normal}"
git pull
if [ $? -ne 0 ]; then
    echo "${bold}${yellow}Warning: 'git pull' failed. This might be because you are not in a git repository. Continuing...${normal}"
    error_log+=" - 'git pull' failed to fetch updates.\n"
else
    echo "Git pull successful."
fi

# 3. Find the correct Python interpreter from the Poetry environment
echo "\n${yellow}Step 2: Locating and configuring project's Python 3.12 environment...${normal}"
# Ensure the environment is configured for python3.12. This is safe to run multiple times.
poetry env use python3.12 > /dev/null 2>&1
# Get the full path to the python executable inside the virtual environment
PYTHON_EXEC=$(poetry env info --path)/bin/python

if [ ! -f "$PYTHON_EXEC" ]; then
    echo "${bold}${red}Error: Could not find the Python executable in the virtual environment.${normal}"
    echo "Please ensure Python 3.12 is installed and that 'poetry env use python3.12' was successful."
    error_log+=" - Could not locate the project's Python interpreter.\n"
else
    echo "Found correct Python interpreter at: $PYTHON_EXEC"
fi

# 4. Lock and Install dependencies using the correct interpreter
echo "\n${yellow}Step 3: Resolving and installing dependencies...${normal}"
if [ -z "$error_log" ]; then # Only proceed if we found the python executable
    # Use the specific python executable to run poetry's module commands.
    # This bypasses any system path issues.
    "$PYTHON_EXEC" -m poetry lock
    if [ $? -ne 0 ]; then
        echo "${bold}${red}Error: 'poetry lock' failed. There is a dependency conflict in pyproject.toml.${normal}"
        error_log+=" - 'poetry lock' failed to resolve dependencies.\n"
    else
        echo "Dependencies locked successfully. Now installing..."
        "$PYTHON_EXEC" -m poetry install
        if [ $? -ne 0 ]; then
            echo "${bold}${red}Error: 'poetry install' failed. The application may not be runnable.${normal}"
            error_log+=" - 'poetry install' failed.\n"
        else
            echo "Installation complete."
        fi
    fi
fi

# 5. Final Summary
echo "\n${bold}${green}--- Fenrir Update Process Finished ---${normal}"

if [ -n "$error_log" ]; then
    echo "${bold}${red}Update completed with errors. Please review the summary below:${normal}"
    echo -e "${red}${error_log}${normal}"
    echo "The application might be in an unstable state."
else
    echo "${bold}${green}Fenrir has been successfully updated!${normal}"
    echo "You can now run the scanner with: ${bold}poetry run fenrir --help${normal}"
fi
