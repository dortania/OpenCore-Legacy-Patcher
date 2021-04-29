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

![](../images/settings.png)

Here you can change different patcher settings, however the main interest is:

* Set ShowPicker Mode

Once you've toggled them both off, build your OpenCore EFI once again and install to your desired drive. Now to show the OpenCore selector, you can simply hold down the "ESC" key while clicking on EFI boot, then you can release the "ESC" key when you see the cursor arrow at the top left.

## Applying Post Install Volume Patches

**Note**: For users who need Post-Install Volume patches for legacy video acceleration support, you **must** disable the following settings in "Patcher Settings" when building and installing your new OpenCore:

* SIP: Disabled
* SecureBootModel: Disabled

Once set, rebuild OpenCore, install to drive and reboot. Then, Post-Install Volume patches will run just fine

To apply the Post-Install Volume patches on your [supported system](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) just use option #3 as shown below

![3-Post-Install-Volume-Patch](https://user-images.githubusercontent.com/71768134/116527398-e8fa8080-a8da-11eb-8e52-c482154403fa.png)

and go ahead to option #1 and let the OCLP patcher apply the needed legacy vidoe patches.

![1-Patch-System-Volume](https://user-images.githubusercontent.com/71768134/116527423-f0218e80-a8da-11eb-8ab7-aaa4b8cd9069.png)

Reboot your system and check out the now working graphics acceleration on your legacy system. This is still Beta software.
