# OpenCore Legacy Patcher

<img src="images/OC-Patcher.png" width="256">

A python program for building and booting [OpenCore](https://github.com/acidanthera/OpenCorePkg) on both legacy and modern Macs, see our in-depth [Guide](https://dortania.github.io/OpenCore-Legacy-Patcher/) for more information.

Supported features:

* System Integrity Protection, FileVault 2, .im4m Secure Boot and Vaulting
* WPA Wifi and Personal Hotspot support
* Native OTA OS DELTA updates on all Macs
* Recovery OS, Safe Mode and Single-user Mode booting
* Zero firmware patching required (ie. APFS ROM patching)
* GPU Switching on MacBook Pro models (2012 and newer)

Note: Only clean-installs and upgrades are supported, macOS Big Sur installs already patched with other patchers, such as [Patched Sur](https://github.com/BenSova/Patched-Sur) or [bigmac](https://github.com/StarPlayrX/bigmac), cannot be used due to broken file integrity with APFS snapshots and SIP.

* You can however reinstall macOS with this patcher and retain your original data

Note 2: Currently OpenCore Legacy Patcher officially supports patching to run macOS 11, Big Sur installs. For older OSes, OpenCore may function however support is currently not provided from Dortania.

* For Mojave and Catalina support, we recommend the use of [dosdude1's patchers](http://dosdude1.com)

## Support

To get aid with the patcher, we recommend joining the [OpenCore Patcher Paradise Discord Server](https://discord.gg/rqdPgH8xSN). We're actively there and is the quickest way to receive help. For bigger issues such as patcher crashing on build and such, we recommend opening an issue right here on GitHub(Please review [How to debug with OpenCore](https://dortania.github.io/OpenCore-Legacy-Patcher/DEBUG.html) before opening issues):

* [OpenCore Legacy Patcher's Issue's tab](https://github.com/dortania/OpenCore-Legacy-Patcher/issues)

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
* [ASentientBot](https://github.com/ASentientBot)
  * Legacy Acceleration Patch set and documentation
* [cdf](https://github.com/cdf)
  * Mac Pro on OpenCore Patch set and documentation
  * [Innie](https://github.com/cdf/Innie) and [NightShiftEnabler](https://github.com/cdf/NightShiftEnabler)
* [Syncretic](https://forums.macrumors.com/members/syncretic.1173816/)
  * [AAAMouSSE](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/) and [telemetrap](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707)
* [dosdude1](https://github.com/dosdude1) and [BarryKN](https://github.com/BarryKN)
  * Development of previous patchers, laying out much of what needs to be patched
* [mario_bros_tech](https://github.com/mariobrostech) and the rest of the Unsupported Mac Discord
  * Catalyst that started OpenCore Legacy Patcher
* MacRumors and Unsupported Mac Communities
  * Endless testing, reporting issues
* Apple
  * for macOS and many of the kexts, frameworks and other binaries we reimplemented into newer OSes