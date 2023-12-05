#!/bin/bash
#
# NSO-RPC Bootstrap Script
# This should work with Ubuntu/Debian, Fedora and Arch Linux out of the box 
# Github: https://github.com/MCMi460/NSO-RPC
#

YELLOW_COLOR="\e[33m"
RESET_COLOR="\e[0m"

# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

package_managers=("apt-get" "dnf" "pacman")
package_manager_found=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--repo)
      github_repo="$2"
      shift 2
      ;;
    -b|--branch)
      branch="$2"
      shift 2
      ;;
    -n|--no-venv)
      no_venv=false
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Available options: -r/--repo, -b/--branch, -n/--no-venv"
      exit 1
      ;;
  esac
done

# Default values if not provided
github_repo="${github_repo:-MCMi460}"
branch="${branch:-main}"

# Iterate over package managers
for manager in "${package_managers[@]}"; do
  if command_exists "$manager"; then
    echo -e "${YELLOW_COLOR}[NSO-RPC: Bootstrap] Using $manager package manager.${RESET_COLOR}"
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

if [ ! -d './NSO-RPC' ]; then
    git clone --branch "$branch" "https://github.com/$github_repo/NSO-RPC"
fi

cd './NSO-RPC/scripts'
chmod +x './install.sh'

# Pass the use_venv flag to the install.sh script


if [ "$no_venv" = true ]; then
  ./install.sh --no-venv
else
  ./install.sh
fi