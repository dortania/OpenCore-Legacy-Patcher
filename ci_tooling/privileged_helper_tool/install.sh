#!/bin/zsh --no-rcs
# ------------------------------------------------------
# Privileged Helper Tool Installer
# ------------------------------------------------------
# Moves to expected destination and sets SUID bit.
# ------------------------------------------------------
# Developed for internal testing, end users should be
# using the PKG installer when released.
# ------------------------------------------------------


# MARK: Variables
# ---------------------------
helperName="com.dortania.opencore-legacy-patcher.privileged-helper"
helperPath="/Library/PrivilegedHelperTools/$helperName"

# MARK: Functions
# ---------------------------

function _setSUIDBit() {
    local binaryPath=$1

    # Check if path is a directory
    if [[ -d $binaryPath ]]; then
        /bin/chmod -R +s $binaryPath
    else
        /bin/chmod +s $binaryPath
    fi
}

function _copyHelper() {
    local sourcePath=$1
    local destinationPath=$2

    # Check if destination path exists
    if [[ -e $destinationPath ]]; then
        # Check if destination path is a directory
        if [[ -d $destinationPath ]]; then
            /bin/rm -rf $destinationPath
        else
            /bin/rm -f $destinationPath
        fi
    fi

    # Copy source to destination
    /bin/cp -R $sourcePath $destinationPath
}


# MARK: Main
# ---------------------------

_copyHelper "./$helperName" $helperPath
_setSUIDBit $helperPath