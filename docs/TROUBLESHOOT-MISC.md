# Booting, installer and other issues

**Booting**

* [Stuck on `This version of Mac OS X is not supported on this platform` or (🚫) Prohibited Symbol](#stuck-on-this-version-of-mac-os-x-is-not-supported-on-this-platform-or-🚫-prohibited-symbol)
* [Cannot boot macOS without the USB](#cannot-boot-macos-without-the-usb)
* [Infinite Recovery OS Booting](#infinite-recovery-os-booting)
* [Stuck on boot after root patching](#stuck-on-boot-after-root-patching)
* [Booting Recovery through OpenCore Legacy Patcher](#booting-recovery-through-opencore-legacy-patcher)
* [Black Screen on MacBookPro11,3 in macOS Monterey](#black-screen-on-macbookpro11-3-in-macos-monterey)

**Installer**

* [Stuck on hard disk selection with greyed out buttons in installer](#stuck-on-hard-disk-selection-with-greyed-out-buttons-in-installer)
* [Installer fails with "an error occurred preparing the software update"](#installer-fails-with-an-error-occurred-preparing-the-software-update)
* [Stuck on "Less than a minute remaining..."](#stuck-on-less-than-a-minute-remaining)
* [Stuck on "Your Mac needs a firmware update"](#stuck-on-your-mac-needs-a-firmware-update)

**Other**

* [Reboot when entering Hibernation (`Sleep Wake Failure`)](#reboot-when-entering-hibernation-sleep-wake-failure)
* [Volume Hash Mismatch Error in macOS Monterey](#volume-hash-mismatch-error-in-macos-monterey)
* [Cannot Disable SIP in recoveryOS](#cannot-disable-sip-in-recoveryos)


## Stuck on `This version of Mac OS X is not supported on this platform` or (🚫) Prohibited Symbol

This means macOS has detected an SMBIOS it does not support. To resolve this, ensure you're booting OpenCore **before** the macOS installer in the boot picker. Reminder that the option will be called `EFI Boot`.

Once you've booted OpenCore at least once, your hardware should now auto-boot it until either an NVRAM reset occurs, or you remove the drive with OpenCore installed.

However, if the 🚫 Symbol only appears after the boot process has already started (the bootscreen appears/verbose boot starts), it could mean that your USB drive has failed to pass macOS' integrity checks. To resolve this, create a new installer using a different USB drive (preferably of a different model.)

## Cannot boot macOS without the USB

By default, the OpenCore Patcher won't install OpenCore onto the internal drive itself during installs.

After installing macOS, OpenCore Legacy Patcher should automatically prompt you to install OpenCore onto the internal drive. However, if it doesn't show the prompt, you'll need to either [manually transfer](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html) OpenCore to the internal drive's EFI or Build and Install again and select your internal drive.

Reminder that once this is done, you'll need to select OpenCore in the boot picker again for your hardware to remember this entry and auto boot from then on.

## Infinite Recovery OS Booting

With OpenCore Legacy Patcher, we rely on Apple Secure Boot to ensure OS updates work correctly and reliably with Big Sur. However this installs NVRAM variables that will confuse your Mac if not running with OpenCore. To resolve this, simply uninstall OpenCore and [reset NVRAM](https://support.apple.com/en-mide/HT201255).

* Note: Machines with modified root volumes will also result in an infinite recovery loop until integrity is restored.

## Stuck on boot after root patching

**Applies to macOS Monterey and newer. Big Sur does not support snapshot reversion.**

Boot into recovery by pressing space when your disk is selected on the OCLP bootpicker (if you have it hidden, hold ESC while starting up)

* **Note:** If your disk name is something else than "Macintosh HD", make sure to change the path accordingly. You can figure out your disk name by typing `ls /Volumes`.

Go into terminal and first mount the disk by typing
```sh
mount -uw "/Volumes/Macintosh HD"
```
Then revert the snapshot
```sh
bless --mount "/Volumes/Macintosh HD" --bootefi --last-sealed-snapshot
```
Now we're going to clean the /Library/Extensions folder from offending kexts while keeping needed ones.

Run the following and **make sure to type it carefully**

::: warning
If you have **FileVault 2 enabled**, you will need to mount the Data volume first. This can be done in Disk Utility by locating your macOS volume name, selecting its Data volume, and selecting the Mount option in the toolbar.
:::

```sh
cd "/Volumes/Macintosh HD - Data/Library/Extensions" && ls | grep -v "HighPoint*\|SoftRAID*" | xargs rm -rf
```

Then restart and now your system should be restored to the unpatched snapshot and should be able to boot again.

## Booting Recovery through OpenCore Legacy Patcher

Booting into Recovery through the regular key combination (cmd+r) will result in a "no entry" screen, due to the checks detecting an unsupported Mac. 

To access Recovery, you will have to boot it through OpenCore using the bootpicker. By default, the patcher will try to hide extra boot options such as recovery from the user. To make them appear, press the `Spacebar` key while inside OpenCore's bootpicker to list all boot options and select recovery for the corresponding OS version.

## Black Screen on MacBookPro11,3 in macOS Monterey

Due to Apple dropping NVIDIA Kepler support in macOS Monterey, [MacBookPro11,3's GMUX has difficulties switching back to the iGPU to display macOS correctly.](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/522) To work-around this issue, boot the MacBookPro11,3 in Safe Mode and once macOS is installed, run OCLP's Post Install Root Patches to enable GPU Acceleration for the NVIDIA dGPU.

* Safe Mode can be started by holding `Shift` + `Enter` when selecting macOS Monterey in OCLP's Boot Menu.

## Stuck on hard disk selection with greyed out buttons in installer

Switch installer language to English. If the language selector doesn't show up, [reset NVRAM](https://support.apple.com/en-mide/102603) and boot into the installer again.

You can switch back to different language once macOS has installed.

## Installer fails with "an error occurred preparing the software update"

This issue can be faced in the second phase of the installer with black background and Apple logo, cause of this issue is unknown. To possibly resolve this issue, keep rebooting into 'macOS Installer' (the second phase) multiple times until it ultimately goes through.

## Stuck on "Less than a minute remaining..."

A common area for systems to get "stuck", namely for units that are missing the `AES` CPU instruction/older mobile hardware. During this stage, a lot of heavy cryptography is performed, which can make systems appear to be stuck. In reality they are working quite hard to finish up the installation.

Because this step can take a few hours or more depending on drive speeds, be patient at this stage and do not manually power off or reboot your machine as this will break the installation and require you to reinstall. If you think your system has stalled, press the Caps Lock key. If the light turns on, your system is busy and not actually frozen.

## Stuck on "Your Mac needs a firmware update"

Full error: "Your Mac needs a firmware update in order to install to this Volume. Please select a Mac OS Extended (Journaled) volume instead."

This error occurs when macOS determines that the current firmware does not have full APFS support. To resolve this, when installing OpenCore, head to "Patcher Settings" and enable "Moderate SMBIOS Patching" or higher. This will ensure that the firmware reported will show support for full APFS capabilities.


## Reboot when entering Hibernation (`Sleep Wake Failure`)

[Known issue on some models](https://github.com/dortania/Opencore-Legacy-Patcher/issues/72), a temporary fix is to disable Hibernation by executing the following command in the terminal:

```
sudo pmset -a hibernatemode 0
```

## Volume Hash Mismatch Error in macOS Monterey

A semi-common popup some users face is the "Volume Hash Mismatch" error:

<p align="left">
<img src="./images/Hash-Mismatch.png">
</p>

What this error signifies is that the OS detects that the boot volume's hash does not match what the OS is expecting, this error is generally cosmetic and can be ignored. However if your system starts to crash spontaneously shortly after, you'll want to reinstall macOS fresh without importing any data at first.

* Note that this bug affects native Macs as well and is not due to issues with unsupported Macs: [OSX Daily: “Volume Hash Mismatch” Error in MacOS Monterey](https://osxdaily.com/2021/11/10/volume-hash-mismatch-error-in-macos-monterey/)

Additionally, it can help to disable FeatureUnlock in Settings -> Misc Settings as this tool can be strenuous on systems with weaker memory stability.


## Cannot Disable SIP in recoveryOS

With OCLP, the patcher will always overwrite the current SIP value on boot to ensure that users don't brick an installation after an NVRAM reset. However, for users wanting to disable SIP entirely, this can be done easily.

Head into the GUI, go to Patcher Settings, and toggle the bits you need disabled from SIP:

| SIP Enabled | SIP Lowered (Root Patching) | SIP Disabled |
| :--- | :--- | :--- |
| ![](./images/OCLP-GUI-Settings-SIP-Enabled.png) | ![](./images/OCLP-GUI-Settings-SIP-Root-Patch.png) | ![](./images/OCLP-GUI-Settings-SIP-Disabled.png) |


