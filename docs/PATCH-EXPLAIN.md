# Explaining the patches in OpenCore Legacy Patcher

In our patcher, there are numerous patches used to ensure a stable system. Here we're going to go over what patches are used and why we recommend or even require them.

## OpenCore Settings

### ACPI -> Patch

* EHCx and XHC1 Patches
  * Reason: Required for proper USB operation
  * Logic: Avoids USB maps of newer models attaching and breaking USB port functionality
  * Models: All models require

### Booter -> Quirks

* ForceBooterSignature
  * Reason: Required to ensure Hibernation support
  * Logic: Tricks boot.efi into thinking OpenCore is Apple's firmware
  * Models: All models require

### DeviceProperties -> Add

* `PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)`
  * Reason: Required to ensure Wifi works with full, native support
  * Logic: Tricks AirPortBrcmNIC.kext into thinking our device is a BCM94360 (`14e4,43ba`)
  * Models: [Machines with BCM943224 and BCM94331 chipsets](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/79ab028b0a039e97a528e0b99c876d95d9c2d41d/Resources/ModelArray.py#L199-L225)
* `PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)`
  * Reason: Required to ensure Brightness Control works on upgraded iMacs
  * Logic: Sets AppleBackLight properties
  * Models: iMac11,x and iMac12,x with upgraded Nvidia Metal GPUs
* `PciRoot(0x0)/Pci(0x2,0x0)`
  * Reason: Disables internal GPU to fix sleep issues on upgrades iMacs
  * Logic: Tricks macOS into thinking iGPU is a generic PCI device
  * Models: iMac12,x with upgraded Metal GPUs

### Kernel -> Patch

* SMC Patch
  * Reason: Required to avoid SMC Firmware updates
  * Logic: Patches out `smc-version` in AppleSMC.kext, requires SMC-Spoof.kext for full functionality
  * Models: All models require
* IOHIDFamily Patch
  * Reason: Required for HID peripheral support in macOS on older hardware
  * Logic: Tricks IOHIDFamily into thinking it's always booting recovery
  * Models: [2010 and older](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/79ab028b0a039e97a528e0b99c876d95d9c2d41d/Resources/ModelArray.py#L310-L332)

### Kernel -> Quirks

* ThridPartyDrives
  * Reason: Required to avoid Hibernation wake issues on 3rd party drives
  * Logic: Patches AppleAHCIPort.kext into support
  * Models: All models with standard SATA ports
* PanicNoKextDump
  * Reason: Avoids kext dump on kernel panics, easier kernel debugging
  * Logic: Patches Kernel to not dump dump unnecessary info
  * Models: Only set when Verbose Boot is enabled by the user

### Misc -> Security

* SecureBootModel
  * Reason: Required to ensure seamless OS updates with Big Sur
  * Logic: Sets iMacPro1,1's Secure Enclave Identifier (j137)
  * Models: All models require

### NVRAM -> Add

* `-v debug=0x100`
  * Reason: Used to see debug info of macOS's kernel and kexts, and avoids reboots on panic
  * Logic: Adds args to NVRAM
  * Models: Only set when Verbose Boot is enabled by the user
* `-liludbgall`
  * Reason: Enables Lilu and plugin debug logging
  * Logic: Adds args to NVRAM
  * Models: Only set when Kext DEBUG is enabled by the user
* `msgbuf=1048576`
  * Reason: Sets message buffer size to 1MB, ensures boot logs are retained
  * Logic: Adds args to NVRAM
  * Models: Only set when Kext DEBUG is enabled by the user
* `agdpmod=pikera`
  * Reason: Fixes GPU switching on MacBookPro9,x
  * Logic: Adds args to NVRAM
  * Models: MacBookPro9,x
* `shikigva=80 unfairgva=1`
* `shikigva=128 unfairgva=1 -wegtree`
  * Reason: Fixes DRM support on models with upgraded AMD Metal GPUs
  * Logic: Adds args to NVRAM
  * Models: Models with upgraded AMD Metal GPUs
### UEFI -> ProtocolOverrides

* GopPassThrough
  * Reason: Used for proper output on machines with UGA firmware but GOP GPU
  * Logic: Provide GOP protocol instances on top of UGA protocol instances 
  * Models: MacPro3,1

## Injected Kext

### Acidanthera

* Lilu
  * Reason: Patching engine for other kexts
  * Models: All models require
* WhateverGreen
  * Reason: Patches GPU Frameworks and kext to ensure proper support
  * Models: All models require
* CPUFriend
  * Reason: Patches IOx86PlatformPlugin to restore previous CPU profiles
  * Models: 2012 and newer models
* AirportBrcmFixup
  * Reason: Patches IO80211 and co to fix networking support for unsupported cards
  * Models: BCM943224 and BCM94331
* RestrictEvents
  * Reason: Disables memory errors on MacPro7,1
  * Models: Mac Pros and Xserves

### Audio

* VoodooHDA
  * Reason: Attempts to add audio support for pre-2012 hardware
  * Models: 2011 and older
### Ethernet

* nForceEthernet
* MarvelYukonEthernet
* CatalinaBCM5701Ethernet

### Maps

* USBMap
  * Reason: Inject old USB map profiles to fix USB
  * Models: All models require

### SSE

* AAMouSSE
  * Reason: Translates SSE4.2 instructions to compatible code for SSE4,1 CPUs, required for AMD Metal drives
  * Models: MacPro3,1
* telemetrap
  * Reason: Ensures temelemtry.plugin doesn't run, required for SSE4,1 CPUs
  * Models: Penryn CPUs

### Wifi

* IO80211HighSierra
  * Reason: Re-inject Atheros wifi drivers from High Sierra
  * Models: Atheros cards
* IO80211Mojave
  * Reason: Re-inject Broadcom wifi drivers from Mojave
  * Models: BCm94322

### Misc

* AppleBackLightFixup
  * Reason: Patch AppleBacklight for iMacs with Nvidia Metal GPU upgrades
  * Models: iMac11,x, iMac12,x with upgraded Nvidia Metal GPUs
* AppleIntelPIIXATA
  * Reason: Fix IDE support on MacPro3,1
  * Models: MacPro3,1
* AppleIntelMCEDisabler
  * Reason: Fix dual socket support in Catalina and newer
  * Models: Mac Pros and Xserves
* NightShiftEnabler
  * Reason: Enables NightShift support on unsupported models
  * Models: 2011 and older, MacBookPro9,x included
* SMC-Spoof
  * Reason: Spoofs SMC version to 9.9999
  * Models: All models require




