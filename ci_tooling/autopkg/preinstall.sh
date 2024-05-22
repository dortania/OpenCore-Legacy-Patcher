#!/bin/zsh --no-rcs
# ------------------------------------------------------
# AutoPkg Assets Preinstall Script
# ------------------------------------------------------
# Remove old files, and prepare directories.
# ------------------------------------------------------


# MARK: Variables
# ---------------------------

filesToRemove=(
    "/Applications/OpenCore-Patcher.app"
    "/Library/Application Support/Dortania/Update.plist"
    "/Library/Application Support/Dortania/OpenCore-Patcher.app"
    "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"
    "/Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
)


# MARK: Functions
# ---------------------------

function _removeFile() {
    local currentFile=$1

    if [[ ! -e $currentFile ]]; then
        # Check if file is a symbolic link
        if [[ -L $currentFile ]]; then
            /bin/rm -f $currentFile
        fi
        return
    fi

    # Check if file is a directory
    if [[ -d $currentFile ]]; then
        /bin/rm -rf $currentFile
    else
        /bin/rm -f $currentFile
    fi
}

function _createParentDirectory() {
    local currentFile=$1

    local parentDirectory="$(/usr/bin/dirname $currentFile)"

    # Check if parent directory exists
    if [[ ! -d $parentDirectory ]]; then
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

_main