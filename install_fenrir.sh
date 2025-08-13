#!/bin/bash
#
# Fenrir All-in-One Installer (with automatic dependency installation)
# This script clones the Fenrir repository, installs prerequisites, sets up the
# environment, and makes the 'fenrir' command available system-wide.
#
# Usage:
# 1. Save this script as install_fenrir.sh
# 2. Make it executable: chmod +x install_fenrir.sh
# 3. Run it: sudo ./install_fenrir.sh

# --- Style Functions for better output ---
bold=$(tput bold)
normal=$(tput sgr0)
green=$(tput setaf 2)
yellow=$(tput setaf 3)
red=$(tput setaf 1)

# --- Configuration ---
# !!! IMPORTANT !!!
# Replace this URL with the actual URL of your Fenrir GitHub repository.
REPO_URL="https://github.com/kj-droid/Project_fenrirv2.git"
PROJECT_DIR="Project_fenrirv2"
COMMAND_NAME="fenrir"

echo "${bold}${green}--- Starting Fenrir Installation ---${normal}"

# --- Step 1: Install Prerequisites ---
echo "\n${yellow}Step 1: Checking for prerequisites (git, poetry)...${normal}"

# Check for Git
if ! command -v git &> /dev/null; then
    echo "Git not found. Attempting to install..."
    apt-get update && apt-get install git -y
    if [ $? -ne 0 ]; then
        echo "${bold}${red}Fatal Error: Failed to install git. Please install it manually and run this script again.${normal}"
        exit 1
    fi
    echo "${green}Git installed successfully.${normal}"
else
    echo "Git is already installed."
fi

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Attempting to install..."
    if ! command -v curl &> /dev/null || ! command -v pip3 &> /dev/null; then
        echo "Installing curl and python3-pip..."
        apt-get update && apt-get install curl python3-pip -y
        if [ $? -ne 0 ]; then
            echo "${bold}${red}Fatal Error: Failed to install curl/pip3. Please install them manually and run this script again.${normal}"
            exit 1
        fi
    fi
    curl -sSL https://install.python-poetry.org | python3 -
    if [ $? -ne 0 ]; then
        echo "${bold}${red}Fatal Error: Failed to install Poetry. Please try installing it manually from https://python-poetry.org/docs/${normal}"
        exit 1
    fi
    export PATH="$HOME/.local/bin:$PATH"
    echo "${green}Poetry installed successfully.${normal}"
else
    echo "Poetry is already installed."
fi


# --- Step 2: Clone the Repository ---
if [ -d "$PROJECT_DIR" ]; then
    echo "\n${yellow}Project directory '${PROJECT_DIR}' already exists. Skipping clone.${normal}"
else
    echo "\n${yellow}Step 2: Cloning repository from GitHub...${normal}"
    git clone "$REPO_URL"
    if [ $? -ne 0 ]; then
        echo "${bold}${red}Error: 'git clone' failed. Please check the repository URL and your connection.${normal}"
        exit 1
    fi
fi

# --- Step 3: Run the Internal Updater/Installer ---
cd "$PROJECT_DIR" || exit
echo "\n${yellow}Step 3: Setting up environment and installing dependencies...${normal}"
if [ -f "update_fenrir.sh" ]; then
    chmod +x update_fenrir.sh
    ./update_fenrir.sh
    if [ $? -ne 0 ]; then
        echo "${bold}${red}Error: The update script failed. Please check the output above for errors.${normal}"
        exit 1
    fi
else
    echo "${bold}${red}Error: 'update_fenrir.sh' not found in the repository.${normal}"
    exit 1
fi

# --- Step 4: Set File Permissions ---
echo "\n${yellow}Step 4: Setting file permissions for the current user...${normal}"
# Use SUDO_USER to get the name of the user who invoked sudo
if [ -n "$SUDO_USER" ]; then
    chown -R "$SUDO_USER":"$SUDO_USER" .
    echo "Ownership of all project files set to user '${SUDO_USER}'."
else
    echo "${yellow}Warning: Not running with sudo. Skipping ownership change.${normal}"
fi
# Grant read, write, and execute permissions to the owner
chmod -R u+rwx .
echo "User permissions (read/write/execute) set for all project files."

# --- Step 5: Create the System-Wide Command ---
echo "\n${yellow}Step 5: Creating the system-wide '${COMMAND_NAME}' command...${normal}"
RUN_SCRIPT_PATH="$(pwd)/run.sh"
INSTALL_PATH="/usr/local/bin/$COMMAND_NAME"

# Use -f to force overwrite the link if it already exists
echo "Creating symbolic link from ${RUN_SCRIPT_PATH} to ${INSTALL_PATH}"
ln -sf "$RUN_SCRIPT_PATH" "$INSTALL_PATH"
if [ $? -ne 0 ]; then
    echo "${bold}${red}Error: Failed to create symbolic link. This usually requires sudo privileges.${normal}"
    exit 1
fi
echo "Symbolic link created successfully."

# --- Final Summary ---
echo "\n${bold}${green}--- Fenrir Installation Complete! ---${normal}"
echo "You can now run the scanner from anywhere on your system by simply typing:"
echo "${bold}${COMMAND_NAME} --help${normal}"
