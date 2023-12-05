#!/bin/bash
#
# NSO-RPC Install Script
# This should work with Ubuntu/Debian, Fedora, and Arch Linux out of the box 
# Github: https://github.com/MCMi460/NSO-RPC
#

GREEN="\e[32;1m"
YELLOW="\e[33m"
RED="\e[31m"
RESET="\e[0m"

PACKAGE_MANAGERS=("apt-get" "dnf" "pacman")

# Function to check if a package is installed
function is_package_installed {
    if [ -n "$(command -v $1)" ]; then
        return 0
    else
        return 1
    fi
}

# Parse command-line options
NO_VENV=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-venv)
        NO_VENV=true
        shift
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done


# Set the package manager command based on availability
for pkg_manager in "${PACKAGE_MANAGERS[@]}"; do
    if command -v "$pkg_manager" &>/dev/null; then
        PACKAGE_MANAGER="$pkg_manager"
        break
    fi
done

# If no package manager found, exit
if [ -z "$PACKAGE_MANAGER" ]; then
    echo -e "${RED}[NSO-RPC: Installer] Unable to determine the package manager.${RESET}"
    echo -e "${RED}[NSO-RPC: Installer] Please install the required packages manually.${RESET}"
    exit 1
fi

echo -e "${YELLOW}[NSO-RPC: Installer] Using $PACKAGE_MANAGER package manager.${RESET}"

# Check if pip is installed
if ! is_package_installed pip; then
    case "$PACKAGE_MANAGER" in
        "apt-get" | "dnf")
            sudo $PACKAGE_MANAGER install -y python3-pip
            ;;
        "pacman")
            sudo $PACKAGE_MANAGER -S --noconfirm python-pip
            ;;
        *)
            echo -e "${RED}[NSO-RPC: Installer] Unsupported package manager.${RESET}"
            exit 1
            ;;
    esac
fi


# Function to check if venv is installed
function is_venv_installed {
    if [ -n "$(command -v python3 -m venv)" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if Qt is installed
function is_qt_installed {
    if [ -n "$(command -v pacman)" ]; then
        # Arch Linux
        if [ -n "$(pacman -Qs '^qt6' 2>/dev/null)" ]; then
            return 0
        elif [ -n "$(pacman -Qs '^qt5' 2>/dev/null)" ]; then
            return 0
        else
            return 1
        fi
    elif [ -n "$(command -v apt-get)" ]; then
        # Ubuntu
        if [ -n "$(dpkg -l | grep '^ii' | grep 'qt6' 2>/dev/null)" ]; then
            return 0
        elif [ -n "$(dpkg -l | grep '^ii' | grep 'qt5' 2>/dev/null)" ]; then
            return 0
        else
            return 1
        fi
    elif [ -n "$(command -v dnf)" ]; then
        # Fedora
        if [ -n "$(dnf list installed 'qt6*' 2>/dev/null)" ]; then
            return 0
        elif [ -n "$(dnf list installed 'qt5*' 2>/dev/null)" ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Check if Qt5 or Qt6 is installed
if ! is_qt_installed; then
    echo -e "${RED}[NSO-RPC: Installer] Qt5 or Qt6 libraries are not found. Please install them manually.${RESET}"
    exit 1
fi

# Function to install Python bindings based on Qt version
function install_python_bindings {
    if is_qt_installed; then
        if $PACKAGE_MANAGER -Qs '^qt6' >/dev/null 2>&1; then
            if ! is_package_installed python3-pyqt6; then
                if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
                    sudo $PACKAGE_MANAGER install -y python3-pyqt6
                elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
                    sudo $PACKAGE_MANAGER install -y python3-qt6
                elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
                    sudo $PACKAGE_MANAGER -S --noconfirm python-pyqt6
                fi
                python3 -m pip install pyqt6
            fi
        elif $PACKAGE_MANAGER -Qs '^qt5' >/dev/null 2>&1; then
            if ! is_package_installed python3-pyqt5; then
                if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
                    sudo $PACKAGE_MANAGER install -y python3-pyqt5
                elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
                    sudo $PACKAGE_MANAGER install -y python3-qt5
                elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
                    sudo $PACKAGE_MANAGER -S --noconfirm python-pyqt5
                fi
                python3 -m pip install pyqt5
            fi
        fi
    fi
}

cd ../client
executableDir='/opt/NSO-RPC/'

# Check if installation directory already exists
if [ -d "$executableDir" ]; then
    echo -e "${YELLOW}[NSO-RPC: Installer] Installation directory already exists. Removing existing directory..."
    sudo rm -r "$executableDir"
fi

# Check if venv is installed
if ! is_venv_installed; then
    sudo $PACKAGE_MANAGER install -y python3-venv
fi


# Check if venv is installed (if not disabled)
if [ "$NO_VENV" != true ] && ! is_venv_installed; then
    case "$PACKAGE_MANAGER" in
        "apt-get" | "dnf")
            sudo $PACKAGE_MANAGER install -y python3-venv
            ;;
        "pacman")
            # Skip venv installation on Arch Linux
            ;;
        *)
            echo -e "${RED}[NSO-RPC: Installer] Unsupported package manager.${RESET}"
            exit 1
            ;;
    esac
fi

# Create a virtual environment (if not disabled)
if [ "$NO_VENV" != true ]; then
    echo -e "${YELLOW}[NSO-RPC: Installer] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment (if not disabled)
if [ "$NO_VENV" != true ]; then
    echo -e "${YELLOW}[NSO-RPC: Installer] Activating virtual environment..."
    source venv/bin/activate
fi

# Install Python dependencies
pip install -r requirements.txt GitPython

# Install Python bindings
install_python_bindings

# Create version file
python3 _version.py

# Create the installation directory
sudo mkdir -p "$executableDir"

# Copy files to the installation directory
sudo cp -a './' "$executableDir"

# Begin creating .desktop alias
execDir='/usr/share/applications'
execFile="$execDir/nsorpc.desktop"
mkdir -p "$execDir"
sudo touch "$execFile"

iconDir='/usr/share/pixmaps'
mkdir -p "$iconDir"

sudo cp './icon.svg' "$iconDir/nso.svg"

# Determine the Python executable
PYTHON_EXECUTABLE="/opt/NSO-RPC/venv/bin/python"
if [ "$NO_VENV" = true ]; then
    PYTHON_EXECUTABLE="python3"
fi

read -r -d '' content <<EOF
[Desktop Entry]
Type=Application
Name=Nintendo Switch Online Rich Presence
GenericName=NSO-RPC
Comment=Display your Nintendo Switch game status on Discord!
Exec=/bin/sh -c 'cd /opt/NSO-RPC && exec $PYTHON_EXECUTABLE /opt/NSO-RPC/app.py'
Icon=nso.svg
Terminal=false
Categories=Game;Application;Utility;
EOF

echo "$content" | sudo tee "$execFile" > /dev/null
sudo chmod +x "$execFile"
echo -e "${GREEN}Script finished executing successfully.${RESET}"
