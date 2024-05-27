#!/bin/zsh --no-rcs
# ------------------------------------------------------
# AutoPkg Assets Postinstall Script
# ------------------------------------------------------
# Create alias for app, start patching and reboot.
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

helperPath="Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
mainAppPath="Library/Application Support/Dortania/OpenCore-Patcher.app"
shimAppPath="Applications/OpenCore-Patcher.app"
executablePath="$mainAppPath/Contents/MacOS/OpenCore-Patcher"


# MARK: Functions
# ---------------------------

function _setSUIDBit() {
    local binaryPath=$1

    echo "Setting SUID bit on: $binaryPath"

    # Check if path is a directory
    if [[ -d $binaryPath ]]; then
        /bin/chmod -R +s $binaryPath
    else
        /bin/chmod +s $binaryPath
    fi
}

function _createAlias() {
    local mainPath=$1
    local aliasPath=$2

    # Check if alias path exists
    if [[ -e $aliasPath ]]; then
        # Check if alias path is a symbolic link
        if [[ -L $aliasPath ]]; then
            echo "Removing old symbolic link: $aliasPath"
            /bin/rm -f $aliasPath
        else
            echo "Removing old file: $aliasPath"
            /bin/rm -rf $aliasPath
        fi
    fi

    # Create symbolic link
    echo "Creating symbolic link: $aliasPath"
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
    _setSUIDBit "$pathToTargetVolume/$helperPath"
    _createAlias "$pathToTargetVolume/$mainAppPath" "$pathToTargetVolume/$shimAppPath"
    _startPatching "$pathToTargetVolume/$executablePath"
    _reboot
}


# MARK: Main
# ---------------------------

echo "Starting postinstall script..."
_main