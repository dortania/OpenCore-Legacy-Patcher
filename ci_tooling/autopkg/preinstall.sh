#!/bin/zsh --no-rcs
# ------------------------------------------------------
# AutoPkg Assets Preinstall Script
# ------------------------------------------------------
# Remove old files, and prepare directories.
# ------------------------------------------------------


# MARK: PackageKit Parameters
# ---------------------------

pathToScript=$0            # ex. /tmp/PKInstallSandbox.*/Scripts/*/preinstall
pathToPackage=$1           # ex. ~/Downloads/Installer.pkg
pathToTargetLocation=$2    # ex. '/', '/Applications', etc (depends on pkgbuild's '--install-location' argument)
pathToTargetVolume=$3      # ex. '/', '/Volumes/MyVolume', etc
pathToStartupDisk=$4       # ex. '/'


# MARK: Variables
# ---------------------------

filesToRemove=(
    "Applications/OpenCore-Patcher.app"
    "Library/Application Support/Dortania/Update.plist"
    "Library/Application Support/Dortania/OpenCore-Patcher.app"
    "Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"
    "Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
)


# MARK: Functions
# ---------------------------

function _removeFile() {
    local file=$1

    if [[ ! -e $file ]]; then
        # Check if file is a symbolic link
        if [[ -L $file ]]; then
            echo "Removing symbolic link: $file"
            /bin/rm -f $file
        fi
        return
    fi

    echo "Removing file: $file"

    # Check if file is a directory
    if [[ -d $file ]]; then
        /bin/rm -rf $file
    else
        /bin/rm -f $file
    fi
}

function _createParentDirectory() {
    local file=$1

    local parentDirectory="$(/usr/bin/dirname $file)"

    # Check if parent directory exists
    if [[ ! -d $parentDirectory ]]; then
        echo "Creating parent directory: $parentDirectory"
        /bin/mkdir -p $parentDirectory
    fi
}

function _main() {
    for file in $filesToRemove; do
        _removeFile $pathToTargetVolume/$file
        _createParentDirectory $pathToTargetVolume/$file
    done
}


# MARK: Main
# ---------------------------

echo "Starting preinstall script..."
_main