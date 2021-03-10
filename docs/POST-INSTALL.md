# Post-Installation

* [Booting without USB drive](#booting-without-usb-drive)
* [Booting seamlessly without Verbose or OpenCore Picker](#booting-seamlessly-without-verbose-or-opencore-picker)

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

Here you can change different patcher settings, however the main 2 of interest are:

* Enable Verbose Mode
* Set ShowPicker Mode

Once you've toggled them both off, build your OpenCore EFI once again and install to your desired drive. Now to show OpenCore picker, you can simply press "Esc" key repeatedly.