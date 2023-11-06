# OpenCore Legacy Patcher changelog

## 1.3.0

## 1.2.0
- Resolve application not existing if user dismisses an update instead of installing
- Resolve lldb crashes on extracted binaries
  - Remove MH_DYLIB_IN_CACHE flag from binaries extracted with DSCE
- Add support for detecting T1 Security Chips in DFU mode
- Resolve macOS 14.2 coreauthd crashes on T1 Macs
- Resolve missing NFC firmware on T1 Macs
- Update non-Metal Binaries for macOS Sonoma:
  - Resolve Photos app crash
  - Resolve loginwindow crashes
  - Workaround tile window popup freezing apps by disabling the feature
  - Workaround monochrome desktop widgets rendering issues by enforcing full color (can be disabled in OCLP settings)
- Add new arguments:
  - `--cache_os`: Cache necessary patcher files for OS to be installed (ex. KDKs)
  - `--prepare_for_update`: Clean up patcher files for OS to be installed (ex. /Library/Extensions)
- Add new Launch Daemons for handling macOS updates:
  - `macos-update.plist`:
    - Resolves KDKless Macs failing to boot after updating from 14.0 to 14.x
    - Adds support for KDK caching for OS to be installed
    - Invoked when update is staged
    - `/Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.macos-update.plist`
  - `os-caching.plist`
    - Resolves unsupported/old KDKs from being used post-update
    - Invoked when update is downloading
    - `/Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.os-caching.plist`
- Load UI icons from local path
  - Resolves macOS downloader crash on slower machines
- Resolve iMac18,2 internal 4K display support
- Remove News Widget removal from Control Centre
  - News Widget no longer crashes on 3802-based GPUs
- Resolve i210 NIC support for macOS Sonoma
- Increment Binaries:
  - PatcherSupportPkg 1.4.5 - release
  - OpenCorePkg 0.9.6 - release

## 1.1.0
- Resolve rendering issues on Intel Broadwell iGPUs
- Update non-Metal Binaries for macOS Sonoma:
  - Resolve unresponsive Weather app
  - Resolve full screen menubar covering the app toolbar
  - Resolve unfocused password windows
- Resolve USB 1.1 kernel panics on macOS 14.1
- Resolve PCIe FaceTime camera support on macOS 14.1
- Resolve T1 Security Chip support on macOS 14
  - Applicable for MacBookPro13,2, MacBookPro13,3, MacBookPro14,2, MacBookPro14,3
- Add support for stand alone OpenCore Vaulting without Xcode Command Line Tools (Jazzzny)
- Re-allow NVMeFix for macOS 14
- Remove `-lilubetaall` argument for machines without AppleALC
- Increment Binaries:
  - PatcherSupportPkg 1.4.2 - release
  - AirportBrcmFixup 2.1.8 - release
  - BlueToolFixup 2.6.8 - release
  - RestrictEvents 1.1.3 - release
  - AMFIPass 1.4.0 - release

## 1.0.1
- Resolve rendering issues on Intel Ivy Bridge iGPUs
- Update non-Metal Binaries for macOS Sonoma:
  - Resolve unresponsive Catalyst buttons
  - Resolve window unfocusing issues
  - Resolve menu bar fonts not changing color automatically with Beta Menu Bar enabled
  - Improve Lock Screen clock transparency
- Prevent random WiFiAgent crashes
- Add error handling for corrupted patcher settings
- Remove CoreImage patch for 3802 GPUs on Ventura
- Avoid listing PCIe FaceTime camera patch on pre-Sonoma OSes
  - Only cosmetic in Root Patching UI, however it has been removed to avoid confusion

## 1.0.0
- Resolve BCM2046 and BCM2070 support on macOS 13.3 and newer
- Workaround 13.3+ Kernel Panic on AMD GCN GPUs playing DRM content
- Add new macOS Installer download menu (Jazzzny)
- Refresh download UI (Jazzzny)
- Add support for Universal 2 distribution (x86_64 and ARM64)
  - Drops Rosetta requirement on Apple Silicon Macs
  - Note building from source will require Python 3.11 or newer and up-to-date Python modules
- Update font handling code, fixing font issues on Yosemite and El Capitan
- Resolve incorrect RELEASE usage of OpenCore binaries when DEBUG enabled
- Add RenderBox.framework patch for 3802-based Intel GPUs on macOS 13.3 and newer
  - Works around Weather and Widget freezing
  - Applicable for Intel Ivy Bridge and Haswell iGPUs
- Add macOS Sonoma support to PatcherSupportPkg validation in CI
- Implement basic support for macOS Sonoma:
  - Supports same range of hardware as Ventura, in addition to:
    - iMac18,x
    - MacBook10,1
    - MacBookPro14,x
      - [T1 chip currently unsupported in Sonoma](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1103)
  - Resolved issues:
    - Graphics Acceleration support for 3802 and non-Metal GPUs
    - UI corruption on 31001 GPUs
    - Wireless Networking for BCM94360, 4360, 4350, 4331 and 43224
    - USB ethernet support for adapters based on ECM protocol (ex. Realtek)
    - dGPU support for MacBookPro14,3
    - S1X/S3X NVMe Drive Support
    - PCIe-based FaceTime Camera support
    - Bluetooth support by switching to dynamic VMM spoofing
- Increment Binaries:
  - OpenCorePkg 0.9.3 - release
  - Lilu 1.6.7 - release
  - WhateverGreen 1.6.6 - release
  - RestrictEvents 1.1.3 - (rolling - 4f233dd)
  - FeatureUnlock 1.1.5 - release
  - DebugEnhancer 1.0.8 - release
  - CPUFriend 1.2.7 - release
  - BlueToolFixup 2.6.8 - rolling (2305aaa)
  - CryptexFixup 1.0.2 - release
  - NVMeFix 1.1.1 - release
  - PatcherSupportPkg 1.3.2 - release
- Build Server Changes:
  - Upgrade Python backend to 3.11.5
  - Upgrade Python modules:
    - requests - 2.31.0
    - pyobjc - 9.2
    - wxpython - 4.2.1
    - pyinstaller - 5.13.2
    - packaging - 23.1

## 0.6.8
- Update non-Metal Binaries:
  - Improve experimental Menubar implementation stability
  - Implement reduce transparency Menubar
  - Resolve Color Profile support and Black Box rendering issues on HD 3000 Macs
    - Drops ColorSync downgrade configuration option
    - Resolves macOS 13.5 booting on HD 3000 Macs
- Resolve app not updating in `/Applications` after an update
  - Work-around users manually copying app to `/Applications` instead of allowing Root Volume Patcher to create a proper alias
- Add configuration for mediaanalysisd usage
  - For systems that are the primary iCloud Photo Library host, mediaanalysisd may be unstable on large amounts of unprocessed faces
  - Applicable to 3802-based GPUs (ie. Intel Ivy Bridge and Haswell iGPUs, Nvidia Kepler dGPUs)
- Remove MacBook4,1 references
  - Machine was never properly supported by OCLP
- Restore support for Aquantia Aqtion 10GBe Ethernet for Pre-VT-d systems on 12.3 and newer
  - i.e. MacPro5,1 with AQC107 expansion card running macOS Ventura/Monterey 12.6.x
  - Thanks [@jazzzny](https://github.com/jazzzny)
- Resolve AMD Vega support on pre-AVX2 Macs in macOS Ventura
  - Originally caused by regression from 0.6.2
- Disable non-Metal's Menubar 2 configuration
  - Can be manually re-enabled, however application will try to disable to prevent issues
- Remove AppleGVA downgrade on Intel Skylake iGPUs
- Implement AMFIPass system
  - Removes need for disabling Library Validation and AMFI outright on all applicable systems
- Backend Changes:
  - device_probe.py:
    - Add USB device parsing via `IOUSBDevice` class
    - Streamline Bluetooth device detection
    - Add Probing for Top Case hardware (Jazzzny)
      - Improves handling for altered hardware scenarios (i.e. MacBookPro4,1 with MacBookPro3,1 topcase)
  - utilities.py:
    - Fix indexing error on Device Paths (thx [@Ausdauersportler](https://github.com/Ausdauersportler))
- Increment Binaries:
- PatcherSupportPkg 1.2.2 - release

## 0.6.7
- Resolve partition buttons overlapping in Install OpenCore UI
  - ex. "EFI" and additional FAT32 partitions on a single drive
- Re-enable mediaanalysisd on Ventura
  - Allows for Live Text support on systems with 3802 GPUs
    - ie. Intel Ivy Bridge and Haswell, Nvidia Kepler
  - Previously disabled due to high instability in Photos with Face Scanning, now resolved
- Work-around crashing after patching with MenuBar2 implementation enabled
  - Setting must be re-enabled after patching
- Update non-Metal Binaries:
  - Resolve window placement defaulting past top of screen for some apps
    - ex. OpenCore-Patcher.app during root patching
  - Resolve indeterminate progress bars not rendering with wxWidgets in Monterey and later
    - ex. OpenCore-Patcher.app
- UI changes:
  - Add "Show Log File" button to menubar
- Avoid listing unsupported installer to download by default
  - ex. macOS 14 InstallAssistant.pkg
- Resolve crash when fetching remote macOS installers offline
- Avoid displaying root patches on unsupported macOS versions
  - ex. macOS 14
- Backend changes:
  - Call `setpgrp()` to prevent app from being killed if parent process is killed (ie. LaunchAgents)
  - Rework logging handler:
    - Implement formatted logging
      - Allowing easier debugging
    - Implement per-version, per-run file logging
      - ex. OpenCore-Patcher (0.6.7) (2021-12-31-12-34-56-666903).log
    - Keep only 10 latest log files
    - Reveal log file in Finder on main thread crash
    - Avoid writing username to log file
  - Resolve SharedSupport.dmg pathing error during macOS Installer Verification
    - Applicable to systems with 2 (or more) USB Installers with the same name plugged in
  - Resolve payloads path being mis-routed during CLI calls
  - Add UI when fetching root patches for host
  - Remove progress bar work-around for non-Metal in Monterey and later
    - Requires host to have been patched with PatcherSupportPkg 1.1.2 or newer
- Increment Binaries:
  - PatcherSupportPkg 1.1.2 - release

## 0.6.6
- Implement option to disable ColorSync downgrade on HD 3000 Macs
  - Allows for Display Profiles support on some units
    - Note: black box rendering issues will likely appear
  - Thanks [@jazzzny](https://github.com/Jazzzny)
- Rename payloads.dmg volume name to "OpenCore Patcher Resources (Base)"
  - Allows for better identification when mounted (ex. Disk Utility while app is running)
- Implement DMG-based PatcherSupportPkg system
  - Reduces both app size and root patching time
- Resolve incorrect remote KDK matching for macOS betas
  - ex. Beta 4 KDK being recommended for Beta 3 install
- Resolve low power mode on MacPro6,1
  - Credit to CaseyJ's [PCI Bus Enumeration Patch](https://github.com/AMD-OSX/AMD_Vanilla/pull/196)
- Resolve PCI eject menu appearing on unsupported hardware
- Resolve kernel panic on wake for AMD TeraScale 1 and Nvidia Tesla 8000 series GPUs
- Resolve loss of Ethernet after wake on MacPro3,1 in Ventura
- Resolve graphics corruption on wake for TeraScale 1
  - Patch currently limited to Ventura and newer
- Restore Function Keys on MacBook5,2 and MacBook4,1
  - Implementation by [@jazzzny](https://github.com/Jazzzny)
- Update non-Metal Binaries:
  - Resolves cryptexd and sshd crashes
  - Resolves screen recording regression
  - Resolves Photo Booth on macOS Monterey and later
    - May require tccplus for permissions
- Resolve Application alias not being created with AutoPatcher
- Backend changes:
  - Rename OCLP-Helper to OpenCore-Patcher
    - Allows for better identification when displaying prompts
  - Reimplement wxPython GUI into modularized system:
    - Allows for easier maintenance and future expansion
    - Changes include:
      - Reworked settings UI
      - Unified download UI with time remaining
      - Implement in-app update system
        - Guides users to update OpenCore and Root Patches once update's installed
      - Expand app update checks to include nightly users
        - ex. 0.6.6 nightly -> 0.6.6 release
      - Implement macOS installer verification after flashing
      - Implement proper UI call backs on long processes
        - ex. Root patching
      - Implement default selections for disks and installers
      - Set about and quit items
  - Utilize `py-applescript` for authorization prompts
    - Avoids displaying prompts with `osascript` in the title
    - Due to limitations, only used for installer creation and OpenCore installation
  - Resolve exception handler not logging to file
  - Display raised exceptions from main thread to users
- Increment Binaries:
  - PatcherSupportPkg 1.1.0 - release
  - OpenCorePkg 0.9.2 - release
  - Lilu 1.6.6 - rolling (d8f3782)
  - RestrictEvents 1.1.1 - release
  - FeatureUnlock 1.1.4 - release
  - BlueToolFixup 2.6.6 - release

## 0.6.5
- Update 3802 Patchset Binaries:
  - Resolves additional 3rd party app crashes on Metal with macOS 13.3+
  - ex: PowerPoint's "Presentation Mode"
- Update non-Metal Binaries:
  - Resolves Safari 16.4 frozen canvas rendering
  - ex: Google Docs
- Allow for coexistence of USB 3.0 controllers and USB 1.1 patches on macOS 13+
  - Restores USB 3.0 expansion card support on USB 1.1 machines such as MacPro5,1
- Resolve OpenCL rendering on Nvidia Web Drivers
  - thanks [@jazzzny](https://github.com/Jazzzny)
- Resolve UI unable to download macOS installers on unknown models
  - ex. M2 Macs and Hackintoshes
- Implement minimum OS check for installer creation
  - Prevents vague errors when creating Ventura installers on Yosemite
- Resolve WindowServer crashing with Rapid Security Response (RSR) installation
  - Primarily applicable for Haswell iGPUs on 13.3.1 (a)
- Update legacy Wireless binaries
  - Resolve wifi crashing on 13.4 with BCM94322, BCM943224 and Atheros chipsets
- Backend changes:
  - macos_installer_handler.py:
    - Expand OS support for IA parsing in SUCatalog
  - gui_main.py:
    - Fix spacing regression introduced with `.AppleSystemUIFont` implementation
- Increment Binaries:
  - PatcherSupportPkg 0.9.7 - release
- Build Server Changes:
  - Upgrade CI Host to macOS Monterey
  - Upgrade Xcode to 14.2
  - Switch from `altool` to `notarytool` for notarization

## 0.6.4
- Backend changes:
  - Implement new analytics_handler.py module
    - Adds support for anonymous analytics including host info (and crash reports in the future)
    - Can be disabled via GUI or `defaults write com.dortania.opencore-legacy-patcher DisableCrashAndAnalyticsReporting -bool true`
- Resolve Safari rendering error on Ivy Bridge in macOS 13.3+
- Increment Binaries:
  - RestrictEvents 1.1.1 - rolling (495f4d5)

## 0.6.3
- Update non-Metal Binaries:
  - Resolves Safari 16.4 rendering issue
  - Resolves left side menubar selections
  - Implements automatic menubar text color
  - New experimental Menubar implementation can be enabled via `defaults write -g Amy.MenuBar2Beta -bool true`
    - Note: If you experience issues with the new implementation, you can revert back to the old implementation by running `defaults delete -g Amy.MenuBar2Beta`
- Implement full IOUSBHostFamily downgrade for UHCI/OHCI
  - Resolves panics on certain iMac models
- Resolve unused KDKs not being properly cleaned up
- Implement MXM graphics handling for iMac9,1
  - Credit to [@Ausdauersportler](https://github.com/Ausdauersportler) for implementation
- Resolve CoreGraphics.framework crashing on Ivy Bridge CPUs in macOS 13.3+
  - Disables f16c sysctl reporting
- Resolve accidental CPU renaming with RestrictEvents
- Resolve backlight and internal display support for AMD Navi MXM GPUs
  - Credit to [@Ausdauersportler](https://github.com/Ausdauersportler) for bug fix
- Resolve 3rd Party Apps erroring on Metal with macOS 13.3
  - Applicable Software: Applications directly using Metal (ex. Blender, Parallels Desktop)
  - Applicable Hardware: 3802-based GPUs (ie. Intel Ivy Bridge and Haswell iGPUs, Nvidia Kepler dGPUs)
- Backend changes:
  - Use `.AppleSystemUIFont` for wxPython text rendering (thanks [@jazzzny](https://github.com/Jazzzny))
  - Add extra error handling for network errors:
    - Handles `RemoteDisconnected('Remote end closed connection without response')` exceptions
  - Move root volume patch set generation to dedicated sys_patch_generate.py module
  - Refactored integrity_verification.py:
    - Implemented Object-Oriented design
    - Reduced disk I/O and main thread monopolization
- Increment Binaries:
  - PatcherSupportPkg 0.9.3 - release
  - OpenCorePkg 0.9.1 - release
  - AirPortBrcmFixup 2.1.7 - release
  - RestrictEvents 1.1.0 - release
  - BrcmPatchRAM 2.6.5 - release

## 0.6.2
- Work around Black Box rendering issues on certain Display Color Profiles
  - Limited to Ventura currently due to limitations with other color profiles
  - Applicable for HD3000-based machines (ex. MacBookAir4,x, MacBookPro8,x, Macmini5,x)
- Ensure `Moraea_BlurBeta` is set on non-Metal systems
- Implement proper Root Unpatching verification in GUI
  - Removes arbitrary patch requirements used against unpatching (ex. network connection)
- Implement Kernel Debug Kit installation during OS installs
  - Avoids network requirement for first time installs
  - Paired along side AutoPkgInstaller
- Implement Kernel Debug Kit backup system
  - Allows for easy restoration of KDKs if OS updates corrupted installed KDKs
- Update Wireless binaries
  - Fixed WiFi preferences crash with legacy wifi patches
- Update non-Metal Binaries
  - Improved menubar blur saturation
  - Fixed System Settings hover effects, including Bluetooth connect button
  - Add Books hacks (reimplement cover image generation, disable broken page curl animation)
  - Fixed unresponsive buttons
- Implement Hardware Encoding support for AMD GCN 1-3, Polaris and Vega GPUs
  - Applicable for pre-Haswell Macs on macOS Ventura
  - Resolves DRM playback issues on Netflix, Disney+, etc.
    - Note: GCN 1-3 DRM is functional, however hardware video encoding is still experimental
      - AppleTV+ may be unstable due to this
- Implement support for AMD Navi and Lexa MXM GPUs in 2009-2011 iMacs
  - Primarily applicable for MXM 3.0 variants of AMD WX3200 (0x6981) and AMD RX5500XT (0x7340)
  - Credit to [Ausdauersportler](https://github.com/Ausdauersportler) for implementation
- Implement Continuity Camera Unlocking for pre-Kaby Lake CPUs
  - Applicable for all legacy Macs in macOS Ventura
- Resolve boot support for 3802-based GPUs with macOS 13.3
  - Applicable for following GPUs:
    - Intel Ivy Bridge and Haswell iGPUs
    - Nvidia Kepler dGPUs
  - Note: patchset now requires AMFI to be disabled, patchset still in active development to remove this requirement
- Backend Changes:
  - Refactored kdk_handler.py
    - Prioritizes KdkSupportPkg repository for downloads
      - Skips calls to Apple's now defunct Developer Portal API
    - Support local loose matching when no network connection is available
    - Implement pkg receipt verification to validate integrity of KDKs
  - Implemented logging framework usage for more reliable logging
    - Logs are stored under `~/Library/Logs/OpenCore-Patcher.log`
    - Subsequent runs are appended to the log, allowing for easy debugging
  - Implemented new network_handler.py module
    - Allows for more reliable network calls and downloads
    - Better supports network timeouts and disconnects
    - Dramatically less noise in console during downloads
  - Implemented new macOS Installer handler
  - Removed unused modules:
    - sys_patch_downloader.py
    - run.py
    - TUI modules
- Build Server Changes:
  - Upgrade Python backend to 3.10.9
  - Upgrade Python modules:
    - requests - 2.28.2
    - pyobjc - 9.0.1
    - wxpython - 4.2.0
    - pyinstaller - 5.7.0
    - packaging - 23.0
- Increment Binaries:
  - PatcherSupportPkg 0.8.7 - release
  - AutoPkgInstaller 1.0.2 - release
  - FeatureUnlock 1.1.4 - rolling (0e8d87f)
  - Lilu 1.6.4 - release
  - WhateverGreen 1.6.4 - release
  - NVMeFix 1.1.0 - release
  - Innie 1.3.1 - release
  - OpenCorePkg 0.9.0 - release

## 0.6.1
- Avoid usage of KDKlessWorkaround on hardware not requiring it
  - Resolves AMD Graphics Regression from 0.5.3
- Increment Binaries:
  - KDKlessWorkaround 1.0.0 - rolling (8e41f39)

## 0.6.0
- Resolve external NVMe reporting regression from 0.5.2
- Implement Legacy Wireless support for Ventura
  - Applicable for BCM94328, BCM94322 and Atheros chipsets
- Implement Wifi-only patches when no internet connection available but required (ie. KDKs)
  - Allows users to install Legacy Wireless patches, then connect to the internet to install remaining patches
- Resolve `/Library/Extensions` not being cleaned on KDK-less root patches
- Add AMD Vega Graphics support for pre-AVX2.0 systems on Ventura
  - ex. AMD Vega 56 and 64, AMD Radeon VII
  - Note: As with Polaris, Vega GPUs cannot be mixed with AMD GCN 1-3 patches
    - Patcher will prioritize the AMD GCN 1-3 (assumption that GCN is primary GPU, ex. MacPro6,1)
- Implement proper `APPLE SSD TS0128F/256F` detection
  - Allows all Macs to utilize patch if required
  - Avoids usage of patch when host lacks affected drive (ex. MacBookAir6,x with upgraded SSD)
- Prompt with auto patcher when booted OpenCore is out of date to root patcher
  - ex. Booted OCLP is 0.5.2, root patcher is 0.5.3
- Disable native AMD Graphics on pre-Haswell Macs in Ventura
  - Allows for easy root patching, dropping reliance on Safe Mode to boot
  - Primarily applicable for iMacs and Mac Pros with AMD Polaris and Vega GPUs
- Implement mini validation during GUI build
- Add early UHCI/OHCI support (USB1.1)
  - Implemented via Root Volume patching, ie. no installer support at this time
    - Support should be seen as experimental, especially for laptops
  - Applicable for Penryn Macs and Cheese Grater Mac Pros (MacPro3,1 - MacPro5,1)
  - See associated issue for current limitations: [Legacy UHCI/OHCI support in Ventura](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)
    - USB 3.0 controllers cannot be used along side USB 1.1 patches, OCLP will prioritize USB 3.0 support
- Add early non-Metal Graphics Acceleration support for macOS Ventura
  - Applicable for following GPU architectures:
    - Intel Ironlake and Sandy Bridge
    - Nvidia Tesla, Maxwell and Pascal
    - AMD TeraScale 1 and 2
  - Notes:
    - Bluetooth Pairing is currently semi-functional, see here for work around: [Tab+Space work-around](https://forums.macrumors.com/threads/macos-13-ventura-on-unsupported-macs-thread.2346881/post-31858759)
    - AMFI currently needs to be outright disabled in Ventura
- Overall non-Metal improvements:
  - Improved fake rim
  - Fixed full screen animation
  - Fixed split screen
  - Improved menubar blur
- Add Nvidia Kepler GOP Driver injection
  - Primarily for GPUs lacking GOPs and can't have a newer VBIOS flashed
- Resolve Rapid Security Response support for Haswell+ Macs requiring KDKs
  - Implemented via:
    - Userspace: [RSRRepair](https://github.com/flagersgit/RSRRepair) at `/etc/rc.server` (2b1c9e3)
    - Kernelspace: [RSRHelper.kext](https://github.com/khronokernel/RSRHelper) (cbe1be9)
- Add APFS Trim Configuration
  - Settings -> Misc Settings -> APFS Trim
- Increment Binaries:
  - OpenCorePkg 0.8.8 - release
  - PatcherSupportPkg 0.8.2 - release
  - KDKlessWorkaround 1.0.0 - rolling (4924276)
  - FeatureUnlock 1.1.2 - release
  - CPUFriend 1.2.6 - release
  - Lilu 1.6.3 - release

## 0.5.3
- Integrate FixPCIeLinkrate.efi v0.1.0
  - Fixes link rate for PCIe 3.0 devices on MacPro3,1
- Resolve AppleIntelCPUPowerManagement Panic in Safe Mode
  - Applicable for pre-Haswell Macs on Ventura
- Revert AppleALC 1.7.6 update back to 1.6.3
  - Resolves audio issues on certain Intel HDEF devices
  - Regression currently being investigated within AppleALC
- Remove `Force Web Drivers` option
  - Avoids accidental use of non-Metal Web Drivers on Kepler GPUs
- Resolve silent auto patcher crash when new OCLP version is available
- Implement [`py_sip_xnu`](https://github.com/khronokernel/py_sip_xnu) module
- Resolve Content Caching Patch Regression
- Resolve KDK Versioning Fallback crashing when primary KDK site is down
- Resolve AirPlay to Mac support on Ventura with VMM
- Resolve WindowServer crashing on KDK-less with macOS 13.2 and Rapid Security Response updates
- Resolve Host Versioning when RSR is installed
- Resolve iMac7,1-8,1 and MacBookPro4,1 boot support in Ventura
- Increment Binaries:
  - OpenCorePkg 0.8.7 - release
  - FeatureUnlock 1.1.2 - rolling (94e29ce)
  - WhateverGreen 1.6.2 - release

## 0.5.2
- Ventura Specific Updates:
  - Resolve AMD Polaris external display output support
    - AMD Polaris and legacy GCN cannot be mixed in the same system
      - Legacy GCN support will be prioritized when both are present
      - AMD Polaris GPU can still be used headless for rendering with legacy GCN (ex. [macOS: Prefer External GPU option](https://support.apple.com/en-ca/HT208544))
  - Disables unsupported `mediaanalysisd` on Metal 1 GPUs
    - Alleviates kernel panic when on prolonged idle
  - Automatically remove unsupported News Widgets on Ivy Bridge and Haswell iGPUs
    - Alleviates Notification Centre Crashing
  - Implement downloading from Kernel Debug Kit Backup Repository
    - Alleviates issues with Apple blocking KDK downloads from OCLP (Ref: [Issue #1016](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1016))
- Work-around MacPro6,1 and Lilu race condition
  - Ensure Model and Board ID are set correctly before Lilu loads
- Publish Application Version in UI header
  - Allows for easier identification of version when reporting issues
- Drop usage of `HW_BID` rerouting in boot.efi
  - Patch out PlatformSupport.plist instead, allows for less maintenance overall
- Add support for AMD GOP injection (AMDGOP.efi)
  - For MXM iMacs and Mac Pros with GPU VBIOS lacking GOP support (ie. no UEFI output even after OC loads)
- Hide OpenCore Boot Picker when waking from hibernation
- Increment Binaries:
  - AirPortBrcmFixup 2.1.6 - release
  - AppleALC 1.7.6 - release
  - CryptexFixup 1.0.1 - release
  - DebugEnhancer 1.0.7 - release
  - FeatureUnlock 1.1.0 - release
  - OpenCorePkg 0.8.7 - rolling (fcb4e33)
  - RestrictEvents 1.0.9 - release
  - WhateverGreen 1.6.1 - release

## 0.5.1
- Add support for `APPLE SSD TS0128F/256F` SSDs in macOS Ventura
  - ie. stock SSD found in MacBookAir6,x
- Lax KDK N-1 logic to allow 1 minor version difference
  - ex. Allow 13.0 KDK on 13.1
- Clean out `/Library/Extensions` on KDK-less root patches
  - Ensures old, incompatible kexts are not linked against
  - Old kexts are relocated to `/Library/Relocated Extensions`
- Add OpenCore Picker timeout selection
- Partially resolve MacPro6,1 support
  - Allows for install and usage of 2013 Mac Pros on Ventura
  - Currently CPU Power Management is not supported

## 0.5.0
- Ventura Specific Updates:
  - Switch boot.efi model patch to iMac18,1
  - Resolve pre-Force Touch Trackpad support in Ventura
  - Add Ventura-dropped Models:
    - MacPro6,1
    - Macmini7,1
    - iMac16,x, iMac17,1
    - MacBook9,1
    - MacBookAir7,x
    - MacBookPro11,4/5, MacBookPro12,1, MacBookPro13,x
  - Add Ventura Software Catalog parsing
  - Add Kernel Debug Kit checks to Ventura root patching
  - Add USB map injection for dropped models
  - Resolve Ethernet support on MacPro3,1-5,1
  - Fix VMM patch set
  - Allow dyld shared cache swapping on pre-Haswell
  - Fix MouSSE/SSE4,2 emulation in macOS 13.0 Beta 3 (22A5295h)
  - Graphics Acceleration for legacy Metal GPUs
    - Intel: Ivy Bridge, Haswell, Broadwell and Skylake
    - Nvidia: Kepler
    - AMD: GCN 1 through 3
    - AMD: Polaris (on pre-AVX2.0 systems)
      - Boot in safe mode to avoid stock driver loading
  - Raise SIP requirement to 0x803 for root patching
  - Add Ventura Boot Picker icons
  - Implement KDK-less root patching for Metal Intel and Nvidia GPUs
    - AMD GCN will still require a KDK installed for patching
  - Resolve OpenCL support for legacy Metal GPUs
  - Implement Automatic Rosetta Cryptex installation on OS installs and updates
    - Drops need for manual OS.dmg swapping on pre-Haswell
  - Implement automatic Kernel Debug Kit downloader for systems requiring Boot/SysKC rebuilding
    - ex. AMD GCN
    - Relies on N-1 system for when matching KDK is not present
  - Delete unused KDKs in `/Library/Developer/KDKs` during root patching
  - Resolve Power Management support for Ivy Bridge and older
  - Drop AMFI requirement for Nvidia Kepler and AMD GCN 1-3
  - Resolve numerous AMD GCN 1-3 issues (ex. Photos.app, Screen Saver, etc.)
  - Resolve dGPU support for MacBookPro13,3
- Add work-around to Catalyst Buttons not responding on non-Metal in macOS Monterey
- Re-export OpenCanopy icons to better support Haswell and newer Macs
- Increment Binaries:
  - OpenCorePkg 0.8.5 release
  - Lilu 1.6.2 - release
  - FeatureUnlock 1.0.9 release
  - PatcherSupportPkg 0.7.1 - release
  - BrcmPatchRAM 2.6.4 - release
  - AutoPkgInstaller 1.0.1 - release
  - CryptexFixup 1.0.1 - rolling (cf3a1e4)

## 0.4.12

## 0.4.11
- Enable AppleMCEReporterDisabler whenever spoofing affected SMBIOS
  - ie. iMacPro1,1, MacPro6,1 and MacPro7,1
- Verify host's disk space before downloading macOS Installers
- Remove duplicate OS builds in macOS downloader
  - Avoids Apple's odd bug of publishing 2 different 12.5.1 products
- Implement deeper macOS installer parsing
  - Provides better version detection than Apple provides in .app
- Ensure WhateverGreen is always installed on Mac Pro configurations
- Resolve Safari 16 rendering in macOS 12.6
- Increment Binaries:
  - PatcherSupportPkg 0.5.4 - release
- Add missing OpenCL resources for Nvidia GPUs

## 0.4.10
- Resolve Nvidia Kepler support in macOS 12.5 Beta 3 and newer
- Increment Binaries:
  - PatcherSupportPkg 0.5.2 - release

## 0.4.9
- Split Kepler userspace and kernel space patches
  - Only installs kernel space patches on 12.5 and newer
  - Avoids lock out of user, however breaks graphics acceleration
  - Install 12.4 or older for full graphics acceleration on Kepler
  - Reference: [macOS 12.5: Nvidia Kepler and WindowServer crashing #1004](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1004)

## 0.4.8
- Ensure Apple Silicon-specific installers are not listed
  - ie. M2 specific build (21F2092)
- Avoid adding OpenCore icon in boot picker if Windows bootloader on same partition
- Add error-handling to corrupt/non-standard NVRAM variables
- Add warning prompt when using 'Allow native models'
  - Attempt to avoid misuse of option
- Work-around `Failed to extract AssetData` during installer creation
  - Apple bug, resolved by using CoW into a different directory than `/Applications`
- Avoid listing beta installers in downloader
- Warn about downloading macOS Ventura installers, unsupported by current patcher
- Fix AppleGVA regression introduced in 0.4.6
  - Applicable for Ivy Bridge-only systems

## 0.4.7
- Fix crashing on defaults parsing

## 0.4.6
- Fix Bluetooth support in 12.4 Release
  - Applicable for BCM2046 and BCM2070 chipsets
  - Fix backported to 0.4.5 release
- GUI Enhancements:
  - Greatly improve GUI load times (300-800% on average)
  - Resolve failing to find new updates
  - Implement Modal Sheets for longer windows
    - Avoids UI elements getting under the dock
  - Add return to disk when selecting partitions
  - Add "Search for disks again" option during OpenCore Install
  - Prevent Idle Sleep while running long processes (ie. downloading, flashing)
  - Start OpenCore build automatically when entering Build menu
  - Standardize Application Identifier for defaults
- Resolve failing to find binaries with `--patch_sys_vol` argument
- Downgrade AppleFSCompressionTypeZlib to 12.3.1 on pre-Sandy Bridge Macs
  - Resolves ZLib decompression kernel panics on 12.4 and newer
- Resolve AppleGVACore crashing on MacBookPro11,3 in Monterey 12.4+
- Add Nvidia Web Driver support for Maxwell and Pascal
  - Currently running in OpenGL mode, [non-Metal issues](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108) applicable
- Enable Beta Blur settings on non-Metal by default
  - For slower hardware, disabling may slightly improve performance
- Deprecate TUI support
  - Users may still manually run from source for future builds
  - Binaries will no longer be provided on future release

## 0.4.5
- Fix AutoPatcher.pkg download on releases
  - Fix backported to 0.4.4 release binaries
- Add Macmini8,1 FeatureUnlock support
  - Drops CPU check, supports all machines
- Refactor Root Patching System
  - Adds preflight checks validating patch set data and presence
  - Adds dynamic Sandy Bridge Board ID patching
    - Allows for unrestricted SMBIOS usage with `AppleIntelSNBGraphicsFB`
  - Adds OpenCL downgrade for TeraScale 2
    - Resolves VNC support (credit IronApple#2711)
  - Fix SecureBootModel detection
- Add `OpenCore-Legacy-Patcher.plist` for applied patch info
  - Located under `/System/Library/CoreServices`
  - Lists patch sets applied including files installed and removed
- Add `preinstall` script to AutoPatcher
  - Removes old patcher files before installing new
- Add Serial Number Spoofing
  - For recycled machines where MDM was mistakenly left on
- Add sys_patch file validation during CI
- GUI Enhancements:
  - Add GUI Prompt for booting mismatched OpenCore configs
    - ex. Booting MacBookPro8,1 config on MacBookPro11,1
  - Add Checksum verification to InstallAssistant.pkg download
  - Fix showing latest 12.4 remote installers
  - Add local Root Patcher version info when previously patched
    - Helps notify users they already patched, or should be repatched with a newer version
- Add error handling to non-standard/malformed OpenCore Boot Path
- Non-Metal Enhancements:
  - Add work-around to double clock bug introduced in macOS 12.4
  - Resolve non-functioning Dismiss buttons bug introduced in macOS 12.4
  - Refresh Status Bar when item length changes
  - Add smoother transition for auto appearance
- Increment Binaries:
  - PatcherSupportPkg 0.4.1 - release

## 0.4.4
- Lower SIP requirement for Root Patching
  - Sets to 0x802 (previously 0xA03)
  - Drops `CSR_ALLOW_UNTRUSTED_KEXTS` and `CSR_ALLOW_UNAPPROVED_KEXTS`
- Remember TeraScale 2 Setting on MacBookPro8,2/3
  - Avoids requiring toggling after first time
- Resolve Electron Crashing with SIP lowered on 12.3
  - Adds `ipc_control_port_options=0` boot argument
  - Unknown whether this is a "bug" or intentional from Apple, affects native Macs with SIP disabled
- Resolved non-Metal issues:
  - Catalyst crashing after 1200 seconds on non-Metal
  - Automatic Light/Dark mode (credit @moosethegoose2213)
  - Rim improvements
  - Trackpad swipe between pages
  - Cycle between windows
  - Improve Display Preference pane Image
  - Defaults prefix change (`ASB_` -> `MORAEA_`, reopen non-Metal Settings to apply)
- Increment Binaries:
  - PatcherSupportPkg 0.3.9 - release
  - OpenCorePkg 0.8.0 - release
  - FeatureUnlock 1.0.8 - release
  - CPUFriend 1.2.5 - release
  - WhateverGreen 1.5.8 - release
  - AutoPkgInstaller 1.0.0 - release
  - BlueToolFixup 2.6.2 - adjusted
- Speed up loading available remote macOS Installers from Apple
  - Skips writing catalogs to disk, loads into memory directly
- Implement Automatic Patch Detection/Installation
  - Requires GUI for usage
  - Installations:
    - During macOS Installer creating in-app, AutoPkg-Assets.pkg is installed to macOS installer
    - After running the installer with AutoPkgInstaller.kext, Root Patcher will install patches
    - Must boot macOS Installer, does not support in-OS usage
  - Post OS Updates:
    - After OS updates, Patcher will detect whether system requires root patches and prompt you
    - Implemented via Launch Agent in `/Library/LaunchAgents`
    - OpenCore-Patcher.app will be copied to `/Library/Application Support/Dortania` for storage
  - Notify users when OpenCore is booted from external disk not matching macOS (ie. USB installer)
    - Disable notification via `defaults write com.dortania.opencore-legacy-patcher AutoPatch_Notify_Mismatched_Disks -bool FALSE`
- GUI Enhancements:
  - Add Reboot Prompt after Root Patching
  - Add Disk Installation Prompt after OpenCore Config Building
  - Streamline GUI relaunch for Root Patch/Unpatch (remembering previous state during patching)
  - Grey out return buttons while performing sensitive tasks
  - Add `Currently Booted SIP` info to SIP Settings
  - Add Disk Highlighting during Build/Install for previously installed disks
  - Only list newest installers by default (reload to show older binaries)
- Remove manual root unpatching
  - Removed due to reliability issues
  - `bless` based reversion still supported in Big Sur+
- Remove Unofficial Mojave/Catalina Root Patching
  - For TeraScale 2-based acceleration on older OSes, use v0.4.3
- Simplify Binary options
  - Removes Online Patcher Variants
  - Offline variants are now new defaults, no longer retain `Offline` suffix
- Resolve legacy Bluetooth Support on 12.4 Beta 3
  - Disables USB Address erroring on some pre-Bluetooth 4.0 chipsets
  - ex. `ERROR -- Third Party Dongle has the same address as the internal module`

## 0.4.3
- Increment Binaries:
  - PatcherSupportPkg 0.3.4 - release
  - OpenCorePkg 0.7.8 - release
  - Lilu 1.6.0 - release
  - WhateverGreen 1.5.7 - release
  - FeatureUnlock 1.0.7 - rolling (6a87f65)
- Resolve many non-Metal issues:
  - Control Centre Sliders
  - Shift/missing icons
  - Hardware Cursor
    - Note cursor images will be static (ie. beach ball)
  - Quicklook dismiss/expand
  - Keyboard Backlight
    - Drops reliance on LabTick
- Add Ethernet Controller detection to build
- Resolve i210/i225 NIC support on pre-Ivy Macs
- Resolve AirPlay to Mac support on Skylake+ Macs in 12.3 Beta 2+
- Resolve SDXC support in Monterey for Pre-Ivy Bridge Macs
- Rename Battery Throttling option to Firmware Throttling
  - Expands support to desktops (ie. iMacs without Displays)
- Add XCPM disabling
  - Forces `ACPI_SMC_PlatformPlugin` to outmatch `X86PlatformPlugin`

## 0.4.2
- Resolve app crashing on some 3rd party SAS/SATA controllers
- Add Beta identifier to macOS Installer menu
- Resolve showing unsupported installers in Creation menu
- Resolve Macmini4,1 HDEF pathing
- Increment Binaries:
  - FeatureUnlock 1.0.6 - rolling (d296645)
  - PatcherSupportPkg 0.3.1
- Resolve SIP and SecureBootModel not disabling by default on some non-Metal Mac Pros
- Add Content Caching support configurability
- Limit SurPlus patchset to 20.4.0 - 21.1.0
  - No longer required for macOS 12.1 and newer
- Add Universal Control support for Monterey native Macs
  - Applicable for Haswell/Broadwell
  - Requires macOS 12.3 or newer
- Fix Power Management Support in macOS 12.3 Beta 1
  - Applicable for Sandy Bridge and older
  - Enforces ACPI_SMC_PlatformPlugin matching
- Add NVMe Enhanced Power Management configuration
  - Disables NVMe adjustments on Skylake and newer Macs by default
- Resolve Catalyst Scrolling on non-Metal GPUs
- Add new TUI icon to differentiate between GUI
- Resolve Color Strobing on AMD TeraScale 2 GPUs
  - Drops reliance on ResXtreme and SwitchResX

## 0.4.1
- Add XHCI Boot Support to pre-UEFI 2.0 Macs
  - Applicable to pre-Ivy Macs with upgraded USB 3.0 controllers, allows USB 3.0 boot
  - Credit to Jazzzny for testing, [DearthnVader for original research](https://forums.macrumors.com/threads/bootable-xhci-pci-e-for-the-3-1-experimental.2217479/)
  - Drivers stripped from MacPro6,1 firmware
- Resolve OCLP-Helper dyld crash

## 0.4.0
- Resolves Install USB Creation using incorrect installer
- Resolves `installer` failing to extract InstallAssistant in older OSes
- Resolves certain Samsung NVMe drives appearing as external on Mac Pros
- Add FeatureUnlock configurability
- Add NVRAM WriteFlash configurability for degraded/fragile systems
- Add `ThirdPartyDrives` quirk configurability
- Resolve Skylight dylib injection issue
- Increment Binaries:
  - OpenCore 0.7.7 - release
  - RestrictEvents 1.0.6 - release
  - FeatureUnlock 1.0.6 - rolling (1d0bc7b)
  - WhateverGreen 1.5.6 - release
  - Lilu 1.5.9 - release
  - gfxutil 1.8.2b - release
  - PatcherSupportPkg 0.2.9 - release
- Re-add Content Caching support for VMM-spoofed systems
- Add wxPython Based GUI
  - Supersedes Obj-C Based GUI
  - Both standard and offline builds provided
- Allow optional spoofing on native Models
  - Recommended for systems that cannot update their firmware natively (ie. dead internal drive)
- Add Dropbox fix for non-Metal on Monterey
- Add App Update checks to GUI
  - If new version available, app will prompt on launch.
  - Configurable in Developer Settings
- Resolved OS crashing on slow Macs with FeatureUnlock
- Disable Windows GMUX support by default
  - Resolves brightness control issues on MacBookPro11,3 in Windows
  - Configurable in Developer Settings
- Add Commit Data to Info.plist

## 0.3.3
- Disable Asset Caching support with spoofless approach
  - Switch to Minimal or higher if required

## 0.3.2
- Implement spoofless support (ie. no SMBIOS patching)
  - Requires macOS 11.3 or newer, for 11.2.3 and older use Minimal or higher spoofing
  - See additional notes before updating: [VMM usage notes](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/543#issuecomment-953441283)
- Adjust SIP setting to better reflect current SIP usage
- Resolve Monterey Bluetooth issues on user-upgraded BCM94331 BT4.0 modules
- Fix iGPU-only iMac14,x display output when using Minimal/Moderate spoof
- Increment Binaries:
  - OpenCore 0.7.6 - release
  - Lilu 1.5.8 - release
  - BrcmPatchRAM 2.6.1 - release
  - WhateverGreen 1.5.5 - release
  - PatcherSupportPkg 0.2.8 - release
  - FeatureUnlock 1.0.5 - rolling (9cf1e81)
- Fix AirPlay to Mac on macOS 12.1
- Add macOS InstallAssistant downloader to TUI
- Resolve rare memory corruption due to FeatureUnlock
- Raise SurPlus MaxKernel to 21.99.99
- Fix Content Caching with spoofless usage
- Allow disabling of ConnectDrivers
  - Aid with Hibernation on MacBookPro9,1/MacBookPro10,1
- Add legacy iSight patch
  - Applicable for MacBook4,1/5,2
  - Affected Device IDs: 0x8300, 0x8501, 0x8503
  - Credit to parrotgeek1 for LegacyUSBVideoSupport
- Fix Wifi Password prompt in Monterey on legacy wifi
  - Applicable for Atheros, BCM94328, BCM94322
- Fix OpenCL Acceleration on Ivy Bridge and Kepler
- Add Apple RAID Card support
- Add Legacy GCN build support off model for MXM iMacs
- Resolve 5k Display Output support on 5k iMacs and iMac Pro
- Resolve NVMe Patching on 2016-2017 MacBook Pros
- Enable Windows VMX support for Haswell and Broadwell MacBooks

## 0.3.1
- Increment Binaries:
  - OpenCorePkg 0.7.4 release
  - RestrictEvents 1.0.5 release
  - WhateverGreen 1.5.4 release
- Allow for setting custom SIP values via TUI
- Drop `CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE` requirement for root patching
  - Lowers default SIP Disabled value to 0xA03
- Update Legacy GMUX patchset to latest Sierra security Update
  - [Source](https://github.com/HackintoshHD/mbp5x-instant-gpu-switching)
- Fix non-Metal acceleration crashing on 12.0.1
  - Yes Apple adding a notch broke our accel patches
- Fix non-Metal Control Center crashing on 12.0 Beta 10+
- Increment Binaries:
  - PatcherSupportPkg 0.1.12

## 0.3.0
- Fix Nvidia Tesla Acceleration in Monterey Beta 7+
  - Add missing NVDAStartup
- Allow configuring GMUX usage for Windows
   - Applicable for iGPU+dGPU MacBook Pros
- Allow usage of legacy AppleHDA
   - Only use for machines that cannot achieve audio support normally
   - Main usage for Macs without boot screen output
- Revert iMacPro1,1 SMBIOS usage on Mac Pros and Xserves
  - Resolves display output issues on Legacy GCN
- Limit SIP bits flipped when disabled
  - 0xFEF -> 0xE03
      - `CSR_ALLOW_UNTRUSTED_KEXTS`
      - `CSR_ALLOW_UNRESTRICTED_FS`
      - `CSR_ALLOW_UNAPPROVED_KEXTS`
      - `CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE`
      - `CSR_ALLOW_UNAUTHENTICATED_ROOT`
- Fix Kepler DisplayPort output
  - Apply `agdpmod=vit9696` patch
- Add Syncretic's SurPlus 11.3+ Race Condition Patch
  - [Source](https://github.com/reenigneorcim/SurPlus)
- Downgrade Nvidia Kepler Bundles to 11.0 Beta 3
  - Resolves crashing at high loads, credit to [Jackluke](https://github.com/jacklukem) for discovery
- Add Legacy GMUX patchsets
  - Applicable for dual GPU MacBookPro5,x and demuxed MacBookPro8,x
- Increment Binaries:
  - PatcherSupportPkg 0.1.7 release
  - RestrictEvents  1.0.5 rolling (2430ed0)
- Limit MacBookPro6,2 G State
  - Works around crashing when switching GPUs
- Fix OTA updates on T2 SMBIOS
- Allow iMac13,x iGPU usage always
  - Due to both Kepler and Ivy needing root patching, no benefit to disable the iGPU
- Refactor Hardware Model building
- Resolve dGPU output on MacBookPro10,1
- Add Panel ID `9cd6` for iMac11,3
  - Resolves Brightness control
- Add AppleGVA patch set for HD3000 machines
  - Mainly applicable for iMac12,x and iGPU-only MacBooks
- Add EFICheckDisabler
  - Based off stripped RestrictEvents.kext
- Add SimpleMSR to disable missing battery throttling on Nehalem+ MacBooks
- Implement software demux patch set for 2011 15/17" MacBook Pros
  - Alternative to hardware demux
  - Adds [AMDGPUWakeHandler](https://github.com/blackgate/AMDGPUWakeHandler)
- Add Legacy GCN support for iMac11,x and iMac12,x with upgraded GPUs
  - Note: iMac12,x with legacy GCN will fail to wake
- Fix Beta 10 Bluetooth
  - Works around new Broadcom/CSR vendor checks in `bluetoothd`

## 0.2.5

- Implement Latebloom configuration via command line tool
- Implement Root Volume backups in addition to APFS snapshot reversions
  - Backups applicable to machines with sealed APFS snapshots
- Allow Root Patching on Mojave and Catalina
  - Currently experimental
- Allow disabling of faulty Thunderbolt controllers on 2013-2014 MacBook Pros
  - Currently limited to MacBookPro11,x
- Set iMacPro1,1 SMBIOS for Mac Pro and Xserve models
  - Allows for wider array of OS support (High Sierra+)
- Use plist override for BCM943224 and BCM94331 support in Big Sur+
  - Allows for older OS support through OpenCore
- Increment Binaries:
  - OpenCore 0.7.2 release
  - Lilu 1.5.5 release
  - AppleALC 1.6.3 release
  - WhateverGreen 1.5.2 release
  - FeatureUnlock 1.0.3 release
  - PatcherSupportPkg 0.1.2 release
- Allow iGPU/dGPU switching in Windows
  - Applicable to MacBook Pros with Intel iGPU and Nvidia/AMD dGPU
- Clean up Patcher Settings
- Allow disabling of TeraScale 2 Acceleration during root volume patch
  - Use for MacBookPro8,x with heavily degraded dGPUs
- Add non-Metal Monterey Acceleration
  - Currently supports:
    - Intel Ironlake and Sandy Bridge
    - Nvidia Tesla
    - AMD TeraScale 1 and 2
- Allow Trackpad gestures on MacBook4,1 and MacBook5,2
  - System Preferences will not report settings however
- Allow Root Volume Patched Systems to use FileVault 2
  - Requires macOS 11.3 (20E232) or newer
  - Unsupported on APFS ROM Patched Macs, revert to stock firmware to resolve
- Add offline TUI build
  - Allows for root patching without network connection
- Add Legacy Wireless support for Monterey
  - Applicable for BCM94328, BCM94322 and Atheros chipsets
- Add Legacy Bluetooth support for Monterey
  - Applicable for BRCM2046 and BRCM2070 chipsets
- Disable Library Validation allowing for AMFI usage
  - Remove reliance on amfi_get_out_of_my_way=1
- Add Kepler Acceleration Patches for Monterey Beta 7 and newer
- Add FirmwareFeature upgrading to all Models
  - Fixes Monterey Beta 7 installation issues
- Add iMac7,1 USB map

## 0.2.4

- Fix BlessOverride typo
- Fix Wake on WLAN typo
- Fix Catalyst App crashing in macOS 11.5 (ie. Messages.app)
- Increment Binaries
  - PatcherSupportPkg 0.0.15 release
- Implement Latebloom.kext support (v0.19)
  - Work around macOS 11.3+ race condition on pre-Sandy Bridge Macs
- Disable USB Map injection when unneeded

## 0.2.3

- Fix more IORegistry issues
- Implement OpenCore GUI
- Ensure symlinks are preserved
- Enable TeraScale 2 patches by default on all models
- Fix NightShift support for macOS Monterey
- Add UniversalControl support
  - Currently not enabled by Apple in macOS Monterey Beta 2/iOS 15 Beta 2
- Add optional Wake in WLAN setting
  - Note: enabling may create network instability
- Increment Binaries
  - OpenCore 0.7.1 release (07-05-2021)
  - FeatureUnlock 1.0.3 rolling (07-07-2021)
    - Previously known as SidecarFixup
  - Lilu 1.5.4 release (07-05-2021)
  - AppleALC 1.6.2 release
  - WhateverGreen 1.6.2 release
  - PatcherSupportPkg 0.0.13 release
- Fix Intel HD4000 DRM Support in macOS Monterey (thanks EduCovas!)
- Support optionally re-enabling iGPU in iMac14,x with dGPUs
- Fix Windows scanning in OpenCore menu when Windows and macOS are stored on the same ESP

## 0.2.2

- Fix IORegistry issue
- Fix Root Patch Failure on Nvidia Tesla GPUs

## 0.2.1

- Fix NVMe Crash on build

## 0.2.0

- Refactor device probe logic
- Implement PatcherSupportPkg v0.0.10
  - Reduces binary sizes depending on OS
  - Deprecates Apple-Binaries-OCLP
- Fix full screen and Airplay to Mac support for Intel HD4000 iGPUs in Monterey
- Automatically set `CMIO_Unit_Input_ASC.DoNotUseOpenCL` on TeraScale 2 GPUs
- Fix Country Code detection on Wireless Cards
- Add Windows detection and prompt during installation
- Fix Google Fonts rendering for Intel HD4000 iGPUs in Monterey
- Increment Binaries
  - Lilu 1.5.4 rolling (f69a972 - 06-20-2021)
  - RestrictEvents 1.0.3 rolling (3773ce2 - 06-20-2021)
  - SidecarFixup 1.0.2 rolling (2c29166 - 06-21-2021)
  - PatcherSupportPkg 0.0.18
- Allow AirPlay to Mac support on Skylake - Coffee Lake Macs

## 0.1.9

- Fix incorrect AMFI and SIP detection

## 0.1.8

- Fix Kernel Panic in Big Sur and Monterey
- Increment binaries:
  - Lilu (1.5.4 rolling - 06-15-2021)

## 0.1.7

- Add FireWire Boot Support for Catalina and newer
- Add NVMe firmware support for older models (ie. MacPro3,1)
  - OpenCore must be stored on a bootable volume (ie. USB or SATA)
- Fix Thunderbolt Ethernet support on MacBookAir4,x
- Fix XHCI hangs on pre-2012 Machines
  - XHCI boot support dropped due to instability
- Add beta macOS Monterey Support
  - Fix iMac13,x sleep support
  - Add support for following models:
    - iMac14,4
    - iMac15,1
    - MacBook8,1
    - MacBookAir6,1
    - MacBookAir6,2
    - MacBookPro11,1
    - MacBookPro11,2
    - MacBookPro11,3
- Increment binaries:
  - OpenCore (0.7.0 release - 06-07-2021)
  - AirportBrcmFixup (2.1.3 rolling - 06-08-2021)
  - AppleALC (1.6.2 rolling - 06-08-2021)
  - CPUFriend (1.2.4 rolling - 06-08-2021)
  - Lilu (1.5.4 rolling - 06-11-2021)
  - NVMeFix (1.0.9 rolling - 06-12-2021)
  - WhateverGreen (1.5.1 rolling - 06-08-2021)
  - RestrictEvents (1.0.3 rolling - 06-11-2021)
  - Apple Binaries (0.0.18 release - 06-12-2021)
  - MouSSE (0.95 release - 06-08-2021)
  - SidecarFixup (1.0.2 rolling - 06-11-2021)
- Fix SSE4,2 Emulation
- Fix Sidecar and CPU renaming support in macOS Monterey
- Add AirPlay support to older Models
- Add Intel HD4000 Acceleration
  - Big thanks to Jackluke, EduCovas, DhinakG, MykolaG!
- Add DebugEnhancer for better macOS Monterey logs
  - DebugEnhancer (1.0.3 rolling - 06-08-2021)
- Add TeraScale 2 Graphics Acceleration to Big Sur
  - User configurable, those prone to seizures are recommended to avoid or have another setup the machine due to initial colour strobing before forcing Million Colours on the display with SwitchResX or ResXtreme

## 0.1.6

- Add XHCI UEFI Driver for 3rd Party USB 3.0 Controllers
  - Allows for Boot Support from OpenCore' Picker
- Fix UEFI output on MacPro3,1 with PC GPUs
- Increment binaries:
  - OpenCore 4e0ff2d (0.7.0 rolling - 05-23-2021)
  - Apple Binaries 59a52a3 (0.0.8 release - 05-24-2021)
- Allow legacy macOS Booting
- Fix Photos app distortion on legacy GPUs
- Fix device tree renaming on Mac Pros and Xserves
- Ensure no Acceleration Patches applied when no compatible GPU found
- Allow custom SMBIOS overriding
- Fix incorrectly setting CPU override for non-Minimal SMBIOS spoofs
- Support Minimal SMBIOS spoofing on El Capitan era Macs
- Fix GPU Switching on MacBookPro6,x

## 0.1.5

- Fix crashing when Wireless module not present
- Add iMac10,1 default dGPU pathing
- Add agdpmod=vit9696 to all Nvidia Metal iMacs
  - Fixes external display support on Nvidia iMac12,x
- Remove reliance on AppleBacklightFixup
- Support space in path when downloading Root Patches
- Enable PanicNoKextDump by default
- Expand AppleGraphicsPowerManagement and AppleGraphicsDeviceControl Override support
- Fix MacBookPro8,2/3 Brightness Control
  - dGPU must be disabled via NVRAM or deMUXed
- Increment binaries:
  - Apple Binaries 478f6a6 (0.0.7 release - 05-16-2021)
- Add SeedUtil option to Advanced Patcher Settings

## 0.1.4

- Fix Device Path formatting on 2012+ iMacs

## 0.1.3

- Fix internal PCIe devices reporting as external
  - Opt for `built-in` when device path is detectable
  - Innie 0ccd95e (1.3.0 release - 01-16-2021)
- Fix MacBookPro5,4 audio support
- Increment binaries
  - AppleALC 58b57ee (1.6.1 rolling - 05-07-2021)
  - Apple Binaries 74bd80f (0.0.6 release - 05-09-2021)
- Support custom CPU names in About This Mac
- Fix NightShift accidentally disabling on Minimal SMBIOS configs
- Fix iMac9,1 audio support
- Heavily expand Graphics ID list
- Fix iMac7,1 and iMac8,1 audio support
- Work-around Bluetooth Kernel Panic on Apple's Bluetooth 2.0 Controllers (USB 05AC:8206)
  - Affects iMac7,1 and MacPro3,1
- Fix iMac external display support
- Fix NVMe properties not applying when OpenCore is installed

## 0.1.2

- Fix IDE support on 2008 era MacBooks, iMacs and Xserves
- Fix reduced output speeds on BCM94360 series Wifi cards
- Fix accidentally disabling non-existent iGPU in iMac11,2
- Remove USB ACPI Patching requirement for Minimal SMBIOS setups
- Probe hardware for Backlight pathing on iMac10,1, iMac11,x and iMac12,x with Metal GPUs
- Add Windows UEFI Audio support to Sandy and Ivy Bridge Macs
- Add 3rd Party NVMe Power Management Patches
  - NVMeFix fafc52d (1.0.7 release - 05-03-2021)
- Strip unused ACPI and Kernel entries during build
- Allow native Macs to use OpenCore
  - Better 3rd party NVMe support
  - Better Wireless networking support
- Fix MacBook6,1 audio support
- Increment binaries
  - OpenCore 65cc81b (0.6.9 release - 05-03-2021)
  - Lilu c77722d (1.5.3 release - 05-03-2021)
  - AppleALC 84850d0 (1.6.0 rolling - 04-30-2021)
  - RestrictEvents 9e2bb0f (1.0.1 release - 05-03-2021)
- Allow CPUFriend on all El-Capitan Era Macs
- Fix UEFI 2.0 Application support on upgraded Nvidia GPUs
- Add experimental Sidecar support
  - Requires Mac with Metal Intel iGPU and the iPad to be directly plugged in, wireless highly unstable
  - SidecarFixup efdf11c (1.0.0 release - 05-02-2021)

## 0.1.1

- Fix iMac11,3 GFX0 pathing
- Add MouSSE support to iMac10,1 with Metal AMD GPU
- Fix iMac11,1 and iMac11,3 Nvidia boot issues after PRAM reset
- Fix DRM support on Nvidia-only configurations
  - Support optional setting between DRM and QuickSync support on iMacs13,x and iMac14,x
- Add public beta support for Legacy GPU Acceleration (v0.0.4)
  - Note ATI/AMD TeraScale 2 unsupported (HD 5/6000)
- Add better kmutil crash handling
- Fix build crashing when no wifi card is present
- Allow Legacy Acceleration Patches on Mac Pros and Xserves
- Fix USB kernel panics on iMac7,1
- Fix AppleALC support in Mojave
- Fix TeraScale 1 GPU detection
- Enable Graphics Acceleration on legacy GPUs by default
- Fix incorrectly disabling SIP/SMB on Metal GPUs
- Fix error output when rebuilding kernel cache fails
- Fix Acceleration Linking for Intel Ironlake iGPUs

## 0.1.0

- Fix crash on iMacs with Metal GPUs

## 0.0.23

- Fix MacBookPro4,1 15" and 17" audio support
- Fix iMac7,1 24" and iMac9,1 24" audio support
- Fix Macmini4,1 audio support
- Increment binaries
  - AppleALC 1a3e5cb (1.6.0 rolling - 04-14-2021)
- Enhance Wifi model detection
- Hide OpenShell.efi by default
- Add Brightness Control patches for legacy Nvidia, AMD and Intel GPUs
  - Models with brightness control issues in Catalina partially supported
- Add user configurable Bootstrap setting
- Enhance GPU Detection logic
- Increment AppleBackLightFixup v1.0.1
  - Add panel type F10T9cde
- Enhance HDMI audio support on Mac Pros and Xserves
- Strip unused kext entries during build
- Add gfxutil support for better DeviceProperty path detection
- Add basic CLI support
- Disable SIP and SecureBootModel by default on legacy GPUs

## 0.0.22

- Add ExFat support for models missing driver
  - Aids BootCamp support for EFI based installs on 2010 and older Macs
- Fix CPU Boosting on 2011 and older Macs
- Add basic support for Xserve2,1
- Add AppleALC support(99b3662 - 1.6.0 rolling - 04-09-2021), remove AppleHDA patching requirement
- Add BCM94322 and BCM94321 chipset support

## 0.0.21

- Fix botched images in OpenCanopy
- Add support for 3rd party OpenCore usage detection during building
  - Mainly for users transitioning from Ausdauersportler's OpenCore configuration

## 0.0.20

- Fix CPU Calculation on early MCP79 chipsets (ie. iMac9,1, MacBook5,x)
- Increment binaries
  - OpenCore c528597 (0.6.8 release - 2021-04-05)
  - Lilu 3ef7ca1 (1.5.2 release - 2021-04-05)
  - WhateverGreen afcd687 (1.4.9 release - 2021-04-05)
- Move Apple binaries to dedicated repo and allow custom repos
  - Reduces App size 1/5th compared to 0.0.19
- Fix OpenCanopy support on iMac7,1 and 8,1
- Set iGPU-less iMacs to iMacPro1,1
  - Additionally fixes Bluetooth on older iMacs with BRCM2046 modules
- Add MacBook4,1 support
- Create dedicated RestrictEvents build for MacBookPro9,1
- Fix Mac Pro and Xserve output issues

## 0.0.19

- Add SMC-Spoof.kext to avoid triggering `smcupdater`
- Add Root Volume patching for older machines
  - AppleHDA Patch for 2011 and older (Excluding MacPro4,1+)
- Fix CPU Speed reporting
- Increment binaries
  - OpenCore 9cd61bb (0.6.8 rolling - 2021-03-27)
- Add Mavericks and newer .app support
- Refactor USB map building, fixes USB 3.0 displaying as USB 2.0
- Fix black screen on MacBookPro9,1
- Update RestrictEvents with custom build (1.0.1)
  - Blocks `/usr/libexec/displaypolicyd` on MacBookPro9,1 to ensure smooth GPU switching
- Add custom SD Card icon
- Add automatic codesiging and notarization
- Fix crashing when CD is present
- Add custom SSD icon
- Fix Broadcom Ethernet on older 2009-2011 Macs

## 0.0.18

- Disable Vault by default due to breaking installations
- Move BOOTx64.efi to System/Library/CoreServices/ to support GPT BootCamp installs
- Disable verbose by default, still configurable by end-user
- Remove `AppleInternal`(0x10) from SIP value
- Add Mac Pro DRM patches for Metal GPUs
- Force `Moderate` SMBIOS replacement for models without native APFS support
- Re-enable legacy BCM94322 networking patches
- Add custom drive icons for external drives

## 0.0.17

- Fix build detection breaking on older OS

## 0.0.16

- Move Serial selection to Patcher Settings
- Add new SMBIOS patching options:
  - Minimal: Only update board ID and BIOSVersion, keep original serials
  - Moderate: Update entire SMBIOS, keep original serials
  - Advanced: Update entire SMBIOS, generate new serials
- Fix crash on MacBookPro4,1
- Fix External Display Support on MacBookPro10,1
- Inject Patcher version into NVRAM for easier debugging
- Add user-configurable ShowPicker
- Add user-configurable Vaulting, enabled by default
- Add user-configurable SIP and SecureBootModel
- Fix USB Maps not working on "Minimal" SMBIOS
- Fix GPU vendor user-configuration
- Fix custom EFI Boot icon in Mac Boot Picker
- Enable UserInterfaceTheme to ensure DefaultBackgroundColor is respected
- Enable `amfi_get_out_of_my_way=1` when SIP is disabled

## 0.0.15

- Add user-configurable OpenCore DEBUG builds
- Add user-configurable Wifi and GPU patches
- Fix ThirdPartyDrives model detection
- Add HW_BID injection to fix boot.efi error

## 0.0.14

- Enable ThirdPartyDrives to aid with hibernation on 3rd party SATA drives
- Increment OpenCore 7bb41aa (0.6.8 rolling, 2021-03-06)
- Add ForceBooterSignature to resolve hibernation issues
- Add NightShiftEnabler (1.1.0 release e1639f9)
- Add user-configurable verbose and debug settings
- Add GopPassThrough quirk for UGA-based systems

## 0.0.13

- Add CPUFriend support to resolve X86PlatformPlugin clashes
  - (1.2.3 c388a62 release)
- Fix crash with MacBookAir5,x
- Fix hibernation support
- Remove Wireless patches for BCM4328/4321(14e4:4328) due to boot issues

## 0.0.12

- Convert OpenCore-Patcher binary to OpenCore-Patcher.app
- Add Backlight patches for modded Nvidia GPUs in iMac10,x-12,x
- Fix sleep for iMac12,x with upgraded GPUs

## 0.0.11

- Re-add OpenCore GUI
- Rewrite in py3
- Add OpenCore-Patcher binary for releases avoiding local python requirement
- Increment binaries
  - OpenCore cbd2fa3 (0.6.7 release)
  - WhateverGreen 2e19d1b (1.4.8 release)
- Rework SMBIOS allowing both original and custom serials(Should resolve all iMessage issues)
- Support upgraded GPU detection in iMac10,x-12,x
- Add Wifi card upgrade detection

## 0.0.10

- Increment binaries
  - OpenCore 43f5339 (0.6.6 release)
  - Lilu d107554 (1.5.1 release)
  - WhateverGreen 9e53d8a (1.4.7 release)
- Add IDE support to MacPro3,1
- Set SecureBootModel to iMac Pro(should aid in booting older OSes with OpenCore)
- Update MacBookPro SMBIOS

## 0.0.9

- Resolve firmware install issues bricking Macs

## 0.0.8

- Fix USB Map
- Add HiDPI patch

## 0.0.7

- Add MacPro3,1 to HID patch
- Fix missing SSDT-CPBG patch
- Fix BlacklistAppleUpdate
- Add RestrictEvents kext

## 0.0.6

- Fix macserial crashing

## 0.0.5

- Enable hibernation support
- Work around USB Map failing
- Add checks whether booting with OpenCore
- Fix MouSSE injection

## 0.0.4

- Add basic audio support for legacy chipsets
- Add patch for dual GPU machines

## 0.0.3

- Fix Wireless patch logic

## 0.0.2

- Expand IOHIDFamily Patch to all Nvidia chipsets
- Fix Airdrop 1.0 support
- Add El Capitan era wireless cards

## 0.0.1

- Initial developer preview
