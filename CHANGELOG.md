# OpenCore Legacy Patcher changelog

## 0.0.10
- Increment binaries
    - OpenCore 43f5339(0.6.6 release)
    - Lilu d107554(1.5.1 release)
    - WhateverGreen 9e53d8a(1.4.7 release)
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