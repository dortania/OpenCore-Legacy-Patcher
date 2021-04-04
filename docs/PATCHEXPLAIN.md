# Explaining the patches in OpenCore Legacy Patcher

In our patcher, there are numerous patches used to ensure a stable system. Here we're going to go over what patches are used and why we recommend or even require them.

* [OpenCore Settings](#opencore-settings)
* [Injected Kexts](#injected-kexts)
* [On-Disk Patches](#on-disk-patches)

## OpenCore Settings

Below is a run down of the main logic OpenCore Legacy Patcher uses to gain native support in macOS. Note OpenCore's configuration is documented within [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) as well as an online version provided by us:

* [OpenCorePkg Online Docs](https://dortania.github.io/docs/latest/Configuration.html)

::: details Configuration Explanation

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
  * Models: Machines with BCM943224 and BCM94331 chipsets
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
  * Models: MacPro3,1, MacBook4,1 iMac7,1-8,1
  
:::

## Injected Kext

Below is an explanation of what Kexts OpenCore Legacy Patcher will inject into memory on boot-up.

::: details Injected Kext Explanation

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

### Ethernet

* nForceEthernet
  * Reason: Inject old Nvidia Ethernet kext to resolve networking in Catalina and newer
  * Models: 2010 and older Nvidia Ethernet require
* MarvelYukonEthernet
  * Reason: Inject old Marvel Ethernet kext to resolve networking in Catalina and newer
  * Models: 2008 and older Marvel Ethernet require
* CatalinaBCM5701Ethernet
  * Reason: Inject old Broadcom Ethernet kext to resolve networking in Big Sur
  * Logic: Patch out conflicting symbols to not colide existing BCM5701Ethernet
  * Models: 2011 and older Broadcom Ethernet require

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
  * Logic: Patch out conflicting symbols to not colide existing IO80211Family
  * Models: Atheros cards
* IO80211Mojave
  * Reason: Re-inject Broadcom wifi drivers from Mojave
  * Logic: Patch out conflicting symbols to not colide existing IO80211Family
  * Models: BCM94322

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
:::


## On-Disk Patches

Unfortunately certain on-disk patches are required to achieve full functionality. Below is a breakdown of patches supported

Note, GPU Acceleration Patches are not public yet, the below section is simply documentation for easier research with new aids.

::: details Audio Patches

### Extensions

* AppleHDA
  * Reason: Re-add High Sierra's AppleHDA to achieve audio support
  * Models: 2011 and older Macs (excluding MacPro4,1+)

:::

::: details Acceleration Patches

### Extensions

#### General Patches

* IOSurface.kext
  * Reason: Fixes immediate logout on login
  * Logic: Downgrade to Catalina IOSurface
  * Note: For AMD and Intel, additional `addMemoryRegion/removeMemoryRegion` patch added changing the first conditional jump to non conditional jump
    * At Offset `0xdb52` and `0xdbc6`, replace following bytes with `0xeb`

#### Dropped Acceleration Binaries

* Nvidia Binaries
  * GeForceGA.bundle
  * GeForceTesla.kext
  * GeForceTeslaGLDriver.bundle
  * GeForceTeslaVADriver.bundle
  * NVDANV50HalTesla.kext
  * NVDAResmanTesla.kext

* AMD/ATI Binaries
  * AMD2400Controller.kext
  * AMD2600Controller.kext
  * AMD3800Controller.kext
  * AMD4600Controller.kext
  * AMD4800Controller.kext
  * AMD5000Controller.kext
  * AMD6000Controller.kext
  * AMDFramebuffer.kext
  * AMDLegacyFramebuffer.kext
  * AMDLegacySupport.kext
  * AMDRadeonVADriver.bundle
  * AMDRadeonVADriver2.bundle
  * AMDRadeonX3000.kext
  * AMDRadeonX3000GLDriver.bundle
  * AMDShared.bundle
  * AMDSupport.kext
  * ATIRadeonX2000.kext
  * ATIRadeonX2000GA.plugin
  * ATIRadeonX2000GLDriver.bundle
  * ATIRadeonX2000VADriver.bundle

* Intel 5th Gen Binaries
  * AppleIntelFramebufferAzul.kext
  * AppleIntelFramebufferCapri.kext
  * AppleIntelHDGraphics.kext
  * AppleIntelHDGraphicsFB.kext
  * AppleIntelHDGraphicsGA.plugin
  * AppleIntelHDGraphicsGLDriver.bundle
  * AppleIntelHDGraphicsVADriver.bundle

* Intel 6th Gen Binaries
  * AppleIntelHD3000Graphics.kext
  * AppleIntelHD3000GraphicsGA.plugin
  * AppleIntelHD3000GraphicsGLDriver.bundle
  * AppleIntelHD3000GraphicsVADriver.bundle
  * AppleIntelSNBGraphicsFB.kext
  * AppleIntelSNBVA.bundle

### Frameworks

* CoreDisplay.framework
  * Logic: Copied from Mojave, heavy modifications/shims
* IOSurface.framework
* OpenGL.framework
  * Logic: Copied from Mojave

### PrivateFrameworks

* GPUSupport.framework
  * Logic: Copied from Mojave
* SkyLight.framework
  * Logic: Copied from Mojave, heavy modifications/shims

### LaunchDaemons

* HiddHack.plist
  * Reason: Fixes unresponsive input when patching Skylight
  * Logic: Forces `hidd` to register events, as Skylight handles them by default in Big Sur

:::
