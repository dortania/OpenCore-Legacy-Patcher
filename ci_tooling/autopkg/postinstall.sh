#!/bin/zsh --no-rcs
# ------------------------------------------------------
# AutoPkg Assets Postinstall Script
# ------------------------------------------------------
# Create alias for app, start patching and reboot.
# ------------------------------------------------------


# MARK: Variables
# ---------------------------

mainAppPath="/Library/Application Support/Dortania/OpenCore-Patcher.app"
shimAppPath="/Applications/OpenCore-Patcher.app"
executablePath="$mainAppPath/Contents/MacOS/OpenCore-Patcher"


# MARK: Functions
# ---------------------------

function _createAlias() {
    local mainPath=$1
    local aliasPath=$2

    # Check if alias path exists
    if [[ -e $aliasPath ]]; then
        # Check if alias path is a symbolic link
        if [[ -L $aliasPath ]]; then
            /bin/rm -f $aliasPath
        else
            /bin/rm -rf $aliasPath
        fi
    fi

    # Create symbolic link
    /bin/ln -s $mainPath $aliasPath
}

function _startPatching() {
    local executable=$1
    local logPath=$(_logFile)

    # Start patching
    "$executable" "--patch_sys_vol" &> $logPath
}

function _logFile() {
    echo "/Users/Shared/.OCLP-AutoPatcher-Log-$(/bin/date +"%Y_%m_%d_%I_%M_%p").txt"
}

function _reboot() {
    /sbin/reboot
}

function _main() {
    _createAlias "$mainAppPath" "$shimAppPath"
    _startPatching "$executablePath"
    _reboot
}


# MARK: Main
# ---------------------------

_main