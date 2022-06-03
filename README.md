<div align="center">
             <img src="images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
             <h1>OpenCore Legacy Patcher</h1>
</div>

A Python-based project revolving around [Acidanthera's OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [Lilu](https://github.com/acidanthera/Lilu) for both running and unlocking features in macOS on supported and unsupported Macs.

Our project's main goal is to breath new life to Macs no longer supported by Apple, allowing for the installation and usage of macOS Big Sur and newer on machines as old as 2007.

----------

![GitHub all releases](https://img.shields.io/github/downloads/dortania/OpenCore-Legacy-Patcher/total?color=white&style=plastic) ![GitHub top language](https://img.shields.io/github/languages/top/dortania/OpenCore-Legacy-Patcher?color=4B8BBE&style=plastic) ![Discord](https://img.shields.io/discord/417165963327176704?color=7289da&label=discord&style=plastic)

----------

Noteworthy features of OpenCore Legacy Patcher:

* Support for macOS Big Sur and Monterey
* Native Over the Air(OTA) System Updates
* Supports Penryn and newer Macs
* Full support for WPA Wifi and Personal Hotspot on BCM943224 and newer chipsets
* System Integrity Protection, FileVault 2, .im4m Secure Boot and Vaulting
* Recovery OS, Safe Mode and Single-user Mode booting on non-native OSes
* Unlocks features such as Sidecar and AirPlay to Mac even on native Macs
* Enable enhanced SATA and NVMe power management on non-stock hardware
* Zero firmware patching required (ie. APFS ROM patching)
* Graphics acceleration for both Metal and non-Metal GPUs

----------

Note: Only clean-installs and upgrades are supported, macOS Big Sur installs already patched with other patchers, such as [Patched Sur](https://github.com/BenSova/Patched-Sur) or [bigmac](https://github.com/StarPlayrX/bigmac), cannot be used due to broken file integrity with APFS snapshots and SIP.

* You can however reinstall macOS with this patcher and retain your original data

Note 2: Currently OpenCore Legacy Patcher officially supports patching to run macOS Big Sur and Monterey installs. For older OSes, OpenCore may function however support is currently not provided from Dortania.

* For macOS Mojave and Catalina support, we recommend the use of [dosdude1's patchers](http://dosdude1.com)

## Getting Started

To start using the project, please see our in-depth guide:

* [OpenCore Legacy Patcher Guide](https://dortania.github.io/OpenCore-Legacy-Patcher/)

## Support

To get aid with the patcher, we recommend joining the [OpenCore Patcher Paradise Discord Server](https://discord.gg/rqdPgH8xSN). We're actively there and is the quickest way to receive help.

  * Please review our docs on [how to debug with OpenCore](https://dortania.github.io/OpenCore-Legacy-Patcher/DEBUG.html) to gather important information to help others with troubleshooting.

## Running from source

To run the project from source, see here: [Build and run from source](./SOURCE.md)

## Credits

* [Acidanthera](https://github.com/Acidanthera)
  * OpenCorePkg as well as many of the core kexts and tools
* [DhinakG](https://github.com/DhinakG)
  * Main co-author
* [Khronokernel](https://github.com/Khronokernel)
  * Main co-author
* [Ausdauersportler](https://github.com/Ausdauersportler)
  * iMacs Metal GPUs Upgrade Patch set and documentation
  * Great amounts of help debugging and code suggestions
* [vit9696](https://github.com/vit9696)
  * Endless amount of help troubleshooting, determining fixes and writing patches
* [ASentientBot](https://github.com/ASentientBot), [EduCovas](https://github.com/educovas) and [ASentientHedgehog](https://github.com/moosethegoose2213)
  * Legacy Acceleration Patch set and documentation, [Moraea Organization](https://github.com/moraea)
* [cdf](https://github.com/cdf)
  * Mac Pro on OpenCore Patch set and documentation
  * [Innie](https://github.com/cdf/Innie) and [NightShiftEnabler](https://github.com/cdf/NightShiftEnabler)
* [Syncretic](https://forums.macrumors.com/members/syncretic.1173816/)
  * [AAAMouSSE](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/), [telemetrap](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707) and [SurPlus](https://github.com/reenigneorcim/SurPlus)
* [dosdude1](https://github.com/dosdude1)
  * Main author of [original GUI](https://github.com/dortania/OCLP-GUI)
  * Development of previous patchers, laying out much of what needs to be patched
* [parrotgeek1](https://github.com/parrotgeek1)
  * [VMM Patch Set](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/4a8f61a01da72b38a4b2250386cc4b497a31a839/payloads/Config/config.plist#L1222-L1281)
* [BarryKN](https://github.com/BarryKN)
  * Development of previous patchers, laying out much of what needs to be patched
* [mario_bros_tech](https://github.com/mariobrostech) and the rest of the Unsupported Mac Discord
  * Catalyst that started OpenCore Legacy Patcher
* [arter97](https://github.com/arter97/)
  * [SimpleMSR](https://github.com/arter97/SimpleMSR/) to disable firmware throttling in Nehalem+ MacBooks without batteries
* [Mr.Macintosh](https://mrmacintosh.com)
  * Endless hours helping architect and troubleshoot many portions of the project
* [flagers](https://github.com/flagersgit)
  * Aid with Nvidia Web Driver research and development
* MacRumors and Unsupported Mac Communities
  * Endless testing, reporting issues
* Apple
  * for macOS and many of the kexts, frameworks and other binaries we reimplemented into newer OSes
