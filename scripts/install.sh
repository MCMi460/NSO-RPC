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
    sudo $PACKAGE_MANAGER install -y python3-pip
fi


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

install_python_bindings

cd ../client
python3 -m pip install -r requirements.txt
executableDir='/opt/NSO-RPC/'

# Check if installation directory already exists
if [ -d "$executableDir" ]; then
    echo "[NSO-RPC: Installer]: Installation directory already exists. Removing existing directory..."
    sudo rm -r "$executableDir"
fi

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

read -r -d '' content <<EOF
[Desktop Entry]
Type=Application
Name=Nintendo Switch Online Rich Presence
GenericName=NSO-RPC
Comment=Display your Nintendo Switch game status on Discord!
Exec=bash -c 'cd /opt/NSO-RPC && python3 app.py'
Icon=nso.svg
Terminal=false
Categories=Game;Application;Utility;
EOF

echo "$content" | sudo tee "$execFile" > /dev/null
sudo chmod +x "$execFile"
echo -e "${GREEN}Script finished executing successfully.${RESET}"
