# OpenCore Legacy Patcher changelog

## 0.0.16
- Move Serial selection to Patcher Settings
- Add new SMBIOS patching options:
  - Minimal:  Only update board ID and BIOSVersion, keep original serials
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
- Inital developer preview