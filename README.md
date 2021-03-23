# OpenCore Legacy Patcher

<img src="images/OC-Patcher.png" width="256">

A python program for building and booting [OpenCore](https://github.com/acidanthera/OpenCorePkg) on legacy Macs, see [Supported SMBIOS](https://dortania.github.io/OpenCore-Legacy-Patcher/MODELS.html) on whether your model is supported.

Supported features:

* System Integrity Protection, FileVault 2, .im4m Secure Boot and Vaulting
* Native OTA OS DELTA updates on all Macs
* Recovery OS, Safe Mode and Single-user Mode booting
* Zero firmware patching required (ie. APFS ROM patching)
* GPU Switching on MacBook Pro models (2012 and newer)

Note: Only clean-installs and upgrades are supported, installs already patched with [Patched-Sur](https://github.com/BenSova/Patched-Sur) or [bigmac](https://github.com/StarPlayrX/bigmac) cannot be used due to broken file integrity with APFS snapshots and SIP.

* You can however reinstall macOS with this patcher and retain your original data

Note 2: Currently OpenCore Legacy Patcher only supports macOS 11, Big Sur installs. For older OSes, please use [dosdude1's patchers](http://dosdude1.com)

## How to use

See the online guide on how:

* [OpenCore Legacy Patcher Guide](https://dortania.github.io/OpenCore-Legacy-Patcher/)

## Patcher Warnings

Since this patcher tricks macOS into thinking you're running a newer Mac, certain functionality may be broken:

* Boot Camp Assistant.app
  * We recommend running the assistant on a natively supported OS, running via the patcher may result in unforeseen issues
* Legacy Windows Booting
  * Currently OpenCore cannot boot MBR-based installs, so Ivy Bridge and older Machines may not be able to see Windows in OpenCore's Boot Picker
  * [Add MBR loading tool to OpenCore #912](https://github.com/acidanthera/bugtracker/issues/912)
* Boot Buddy support
  * Due to how OpenCore overwrites NVRAM, the usage of Boot Buddy and such tools are **highly** in-advised

## Support

To get aid with the patcher, we recommend joining the [Unsupported Mac Discord Server](https://discord.gg/XbbWAsE) and heading over to our `#opencore-patcher` channel. We're actively there and is the quickest way to receive help. For bigger issues such as patcher crashing on build and such, we recommend opening an issue right here on GitHub:

* [OpenCore Legacy Patcher's Issue's tab](https://github.com/dortania/OpenCore-Legacy-Patcher/issues)

Regarding how to debug OpenCore Patcher, we recommend seeing the below:

* [How to debug with OpenCore](https://dortania.github.io/OpenCore-Legacy-Patcher/DEBUG.html)
