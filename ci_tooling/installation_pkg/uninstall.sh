#!/bin/zsh --no-rcs
# ------------------------------------------------------
# OpenCore Legacy Patcher PKG Uninstall Script
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

function _cleanLaunchService() {
    local domain="com.dortania.opencore-legacy-patcher"

    # Iterate over launch agents and daemons
    for launchServiceVariant in "/Library/LaunchAgents" "/Library/LaunchDaemons"; do
        # Check if directory exists
        if [[ ! -d $launchServiceVariant ]]; then
            continue
        fi

        # Iterate over launch service files
        for launchServiceFile in $(/bin/ls -1 $launchServiceVariant | /usr/bin/grep $domain); do
            local launchServicePath="$launchServiceVariant/$launchServiceFile"

            # Remove launch service file
            _removeFile $launchServicePath
        done
    done
}

function _main() {
    _cleanLaunchService
    for file in $filesToRemove; do
        _removeFile $file
    done
}


# MARK: Main
# ---------------------------

echo "Starting uninstall script..."
_main