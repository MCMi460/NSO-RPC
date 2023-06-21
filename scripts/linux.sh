#!/bin/bash
#
# NSO-RPC Bootstrap Script
# This should work with Ubuntu/Debian, Fedora and Arch Linux out of the box 
# Github: https://github.com/MCMi460/NSO-RPC
#

YELLOW="\e[33m"
RESET="\e[0m"


# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

package_managers=("apt-get" "dnf" "pacman")
package_manager_found=false

# Iterate over package managers
for manager in "${package_managers[@]}"; do
  if command_exists "$manager"; then
    echo -e "${YELLOW}[NSO-RPC: Bootstrap] Using $manager package manager.${RESET}"
    if [ "$manager" = "pacman" ]; then
      sudo "$manager" -S --noconfirm git
    else
      sudo "$manager" install git -y
    fi
    package_manager_found=true
    break
  fi
done

if ! "$package_manager_found"; then
  echo "Unable to detect a supported package manager on your system."
  exit 1
fi

branch=${1:-main}

if [ ! -d './NSO-RPC' ]; then
    git clone --branch "$branch" 'https://github.com/MCMi460/NSO-RPC'
fi

cd './NSO-RPC/scripts'
chmod +x './install.sh'
./install.sh