#!/bin/sh

# Create alias for OpenCore-Patcher.app
if [ ! -d "/Applications/OpenCore-Patcher.app" ]; then
    ln -s "/Library/Application Support/Dortania/OpenCore-Patcher.app" "/Applications/OpenCore-Patcher.app"
fi

# Start root patching
app_path="/Library/Application Support/Dortania/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher"
args="--patch_sys_vol"
"$app_path" "$args" &> "/Users/Shared/.OCLP-AutoPatcher-Log-$(date +"%Y_%m_%d_%I_%M_%p").txt"
log show --last boot > "/Users/Shared/.OCLP-System-Log-$(date +"%Y_%m_%d_%I_%M_%p").txt"
reboot