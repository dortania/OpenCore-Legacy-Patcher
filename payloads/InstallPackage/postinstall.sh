#!/bin/sh
app_path="/Library/Application Support/Dortania/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher"
args="--patch_sys_vol"
"$app_path" "$args" > "/Users/Shared/.OCLP-AutoPatcher-Log-$(date +"%Y_%m_%d_%I_%M_%p").txt"
log show --last boot > "/Users/Shared/.System-Log-$(date +"%Y_%m_%d_%I_%M_%p").txt"
dmesg > "/Users/Shared/.Kernel-Log-$(date +"%Y_%m_%d_%I_%M_%p").txt"
ps aux > "/Users/Shared/.Process-List-$(date +"%Y_%m_%d_%I_%M_%p").txt"
ls -l "/System/Volumes/Update/mnt1/System/Library/KernelCollections" > "/Users/Shared/.Kernel-Collections-$(date +"%Y_%m_%d_%I_%M_%p").txt"
kmutil showloaded > "/Users/Shared/.Loaded-Kexts-$(date +"%Y_%m_%d_%I_%M_%p").txt"
kmutil inspect -B "/System/Volumes/Update/mnt1/System/Library/KernelCollections/BootKernelExtensions.kc" > "/Users/Shared/.BootKernelExtensions-$(date +"%Y_%m_%d_%I_%M_%p").txt"
kmutil inspect -S "/System/Volumes/Update/mnt1/System/Library/KernelCollections/SystemKernelExtensions.kc" > "/Users/Shared/.SystemKernelExtensions-$(date +"%Y_%m_%d_%I_%M_%p").txt"
reboot