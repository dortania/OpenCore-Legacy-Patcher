#!/bin/zsh --no-rcs
# ------------------------------------------------------
# OpenCore Legacy Patcher PKG Preinstall Script
# ------------------------------------------------------
# Remove old files, and prepare directories.
# ------------------------------------------------------


# MARK: Variables
# ---------------------------

filesToRemove=(
    "/Applications/OpenCore-Patcher.app"
    "/Library/Application Support/Dortania/Update.plist"
    "/Library/Application Support/Dortania/OpenCore-Patcher.app"
    "/Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
)


# MARK: Functions
# ---------------------------

function _removeFile() {
    local file=$1

    if [[ ! -e $file ]]; then
        # Check if file is a symbolic link
        if [[ -L $file ]]; then
            echo "  Removing symbolic link: $file"
            /bin/rm -f $file
        fi
        return
    fi

    echo "  Removing file: $file"

    # Check if file is a directory
    if [[ -d $file ]]; then
        /bin/rm -rf $file
    else
        /bin/rm -f $file
    fi
}

function _createParentDirectory() {
    local file=$1

    local parentDirectory=$(/usr/bin/dirname $file)

    # Check if parent directory exists
    if [[ ! -d $parentDirectory ]]; then
        echo "  Creating parent directory: $parentDirectory"
        /bin/mkdir -p $parentDirectory
    fi
}

function _main() {
    for file in $filesToRemove; do
        _removeFile $file
        _createParentDirectory $file
    done
}


# MARK: Main
# ---------------------------

echo "Starting preinstall script..."
_main