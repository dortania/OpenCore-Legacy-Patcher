# OpenCore Legacy Patcher changelog

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
  - Automatic Light/Darkmode (credit @moosethegoose2213)
  - Rim improvements
  - Trackpad swipe between pages
  - Cycle between windows
  - Improve Display Prefpane Image
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
  - Removed due to reliablity issues
  - `bless` based reversion still supported in Big Sur+
- Remove Unoffical Mojave/Catalina Root Patching
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
    - Note cursor images will be static (ie. beachball)
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
  - Superceeds Obj-C Based GUI
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
- Update Legacy GMUX patchset to latest Sierra Secuirty Update
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
- Add Kepler Accleration Patches for Monterey Beta 7 and newer
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
- Allow AirPlay to Mac support on Skylake - Coffeelake Macs

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
- Fix blackscreen on MacBookPro9,1
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
