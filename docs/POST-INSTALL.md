# Post-Installation

* [Booting without USB drive](#booting-without-usb-drive)
* [Booting seamlessly without Verbose or OpenCore Picker](#booting-seamlessly-without-verbose-or-opencore-picker)
* [Applying Post Install Volume Patches](#applying-post-install-volume-patches)

## Booting without USB drive

Once you've installed macOS through OpenCore, you can boot up and go through the regular install process. To boot without the USB drive plugged in is quite simple:

* Download OpenCore Legacy Patcher
* Change Patcher settings as you'd like
* Build OpenCore again
* Install OpenCore to internal drive
* Reboot holding Option, and select the internal EFI

And voila! No more USB drive required

## Booting seamlessly without Verbose or OpenCore Picker

To do this, run the OpenCore Patcher and head to Patcher Settings:

| GUI Settings | TUI Settings
| :--- | :--- |
|![](../images/OCLP-GUI-Settings-ShowPicker.png) | ![](../images/OCLP-TUI-Settings.png) |

Here you can change different patcher settings, however the main interest is:

* Show Boot Picker (GUI)
* Set ShowPicker Mode (TUI)

Once you've toggled them both off, build your OpenCore EFI once again and install to your desired drive. Now to show the OpenCore selector, you can simply hold down the "ESC" key while clicking on EFI boot, then you can release the "ESC" key when you see the cursor arrow at the top left.

## Enabling SIP

For many users, SIP will be enabled by default on build. For Intel HD 4000 users, you may have noticed that SIP is partially disabled. This is to ensure full compatibility with macOS Monterey and allow seamless booting between it and older OSes. However for users who do not plan to boot Monterey, you can re-enable under Patcher Settings.

Note: Machines with non-Metal GPUs cannot enable SIP in Big Sur either due to patched root volume

| SIP Enabled | SIP Lowered (Root Patching) | SIP Disabled |
| :--- | :--- | :--- |
| ![](../images/OCLP-GUI-Settings-SIP-Enabled.png) | ![](../images/OCLP-GUI-Settings-SIP-Root-Patch.png) | ![](../images/OCLP-GUI-Settings-SIP-Disabled.png) |

:::warning 

If you're unsure whether you should enable SIP, leave as-is. Systems where you have already ran the Post Install Root Patching cannot enable SIP without potentially breaking the current install. 

:::

## Applying Post Install Volume Patches

Post Install Volume Patches, sometimes also called root patches, are patches that have to be installed on disk for some older Macs to gain back functionality.

OCLP v0.4.4 and higher include an autopatcher, which will automatically root patch your system but **only if the USB install media was created within OCLP.**

::: details Note for Mac Pros when swapping a GPU from non-metal to Metal

If you finished installing Monterey with the original card installed (to see bootpicker for example) and swapped your GPU to a Metal supported one, you may notice that you're missing acceleration. To fix this, open OCLP and revert root patches to get your Metal-supported GPU work again.

Alternatively, you can remove "AutoPkg-Assets.pkg" from /Library/Packages on the USB drive before proceeding with the installation. To see the folder, enable hidden files with `Command` + `Shift` + `.` 
:::


Users with OCLP v0.4.4 or higher will also be prompted to install these patches after macOS updates or whenever patches are not detected on the system. We recommend rebuilding OpenCore with the latest version of OCLP to take advantage of these new features.



In OCLP v0.4.5 a new indicator was added to help users to see if, when and on what version the system was root patched. Note that the "Available patches" section above this does not track the status and will always show the patches that are available, whether they're installed or not.

| Automatic install prompt in 0.4.4+ | Last patched status in 0.4.5+ |
| :--- | :--- |
| ![](../images/OCLP-GUI-root-patch-update.png) | ![](../images/OCLP-GUI-Root-Patch-Status.png)  |





### Running Post Install patches manually

If you're using OCLP v0.4.3 or earlier, or need to run the patcher manually, you can do so with the app. There is no harm in trying to run the Patcher, as without compatible hardware nothing will be done. You can see below on whether your hardware needs root volume patching. 

| Listing Patches | Patching Finished |
| :--- | :--- |
| ![](../images/OCLP-GUI-Root-Patch.png) | ![](../images/OCLP-GUI-Root-Patch-Finished.png) |


:::warning

With OpenCore Legacy Patcher versions prior to v0.4.4, Root Patching requires a network connection by default to grab associated resources. If your system is having difficulties with wifi or ethernet, you can grab the newest release :

* [OpenCore Legacy Patcher releases](https://github.com/dortania/OpenCore-Legacy-Patcher/releases/latest)

:::

:::details Unsupported GPUs in macOS Big Sur

* NVIDIA:
  * Tesla (8000 - 300 series)
* AMD:
  * TeraScale (2000 - 6000 series)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)

:::

:::details Unsupported GPUs in macOS Monterey

* NVIDIA:
  * Tesla (8000 - 300 series)
  * Kepler (600 - 800 series)
* AMD:
  * TeraScale (2000 - 6000 series)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)
  * Ivy Bridge (4000 series)

:::

:::details Unsupported Wireless Cards in macOS Monterey

* Broadcom:
  * BCM94328
  * BCM94322
* Atheros

:::
