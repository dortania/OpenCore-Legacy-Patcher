# Explaining the patches in OpenCore Legacy Patcher

In our patcher, there are numerous patches used to ensure a stable system. Here we're going to go over what patches are used and why we recommend or even require them.

* [OpenCore Settings](#opencore-settings)
* [Injected Kexts](#injected-kexts)
* [On-Disk Patches](#on-disk-patches)

## OpenCore Settings

Below is a run down of the main logic OpenCore Legacy Patcher uses to gain native support in macOS. Note OpenCore's configuration is documented within [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) as well as an online version provided by us:

* [OpenCorePkg Online Docs](https://dortania.github.io/docs/latest/Configuration.html)

::: details Configuration Explanation

### ACPI -> Add

* SSDT-CPBG
  * Reason: Resolves Kernel Panic on Arrendale Macs in early Big Sur builds
  * Logic: Disable dummy CPBG device in ACPI
  * Models: MacBookPro6,x and iMac11,x
* SSDT-PCI
  * Reason: Patch Windows Audio support for Sandy and Ivy Bridge
  * Logic: Removes PCI0's 32-bit Allocation Limitation
  * Models: All Sandy and Ivy Bridge Macs, excluding MacPro6,1
* SSDT-DGPU
  * Reason: Allows for software based deMUX disabling dGPUs in 2011 MacBook Pros
  * Logic: Sends power down request to dGPU via ACPI
  * Models: MacBookPro8,2 and MacBookPro8,3 with dead dGPUs
 
### ACPI -> Patch

* `EHCx` and `XHC1` Patches
  * Reason: Required for proper USB operation
  * Logic: Avoids USB maps of newer models attaching and breaking USB port functionality
  * Models: All models require when spoofing with Moderate or Advanced SMBIOS
* `BUF0` to `BUF1` Patch
  * Reason: To be paired with SSDT-PCI
* `_INI` to `XINI` Patch
  * Reason: To be paired with SSDT-DGPU
  
### Booter -> Patch

* Reroute `HW_BID` to `OC_BID`
  * Reason: Allows macOS installers to be used on unsupported models
  * Logic: Reroutes Board ID macOS checks to custom variable
  * Models: All systems using VMM spoofing 

### Booter -> Quirks

* ForceBooterSignature
  * Reason: Required to ensure Hibernation support
  * Logic: Tricks boot.efi into thinking OpenCore is Apple's firmware
  * Models: All models require

### DeviceProperties -> Add

* `PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)`
* `PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)`
  * Reason: Required to ensure Brightness Control works on upgraded iMacs
  * Logic: Sets AppleBackLight properties
  * Models: iMac11,x and iMac12,x with upgraded NVIDIA Metal GPUs
* `PciRoot(0x0)/Pci(0x2,0x0)`
  * Reason: Disables internal GPU to fix sleep issues on upgraded iMacs
  * Logic: Tricks macOS into thinking iGPU is a generic PCI device
  * Models: iMac12,x with upgraded Metal GPUs

### Kernel -> Patch

* SMC Patch
  * Reason: Required to avoid SMC Firmware updates
  * Logic: Patches out `smc-version` in AppleSMC.kext, requires SMC-Spoof.kext for full functionality
  * Models: All models require when spoofing SMBIOS
* IOHIDFamily Patch
  * Reason: Required for HID peripheral support in macOS on older hardware
  * Logic: Tricks IOHIDFamily into thinking it's always booting recovery
  * Models: Penryn CPUs (Core2 series)
* Force FileVault on Broken Seal Patch
  * Reason: Allow FileVault on root patched Macs
  * Logic: Forces APFS.kext to always return true on FileVault support
  * Models: Any model needing root patches
* Disable Library Validation Enforcement Patch
  * Reason: non-Metal Root Volume Patches do not pass library validation tests
  * Logic: Forces Library Validation function to always return not required
  * Models: Non-Metal GPUs
* SurPlus Patch
  * Reason: macOS 11.3-12.0.1 require systems to have RDRAND support in the CPU for stable boot
  * Logic: Forces RDRAND code to return predetermined value
  * Models: All pre-Ivy Bridge Macs
* Reroute `kern.hv_vmm_present` Patch
  * Reason: Allows macOS to be installed and updated on unsupported hardware
  * Logic: Forces userspace to see system as Virtual Machine
  * Models: Any model using VMM spoofing


### Kernel -> Quirks

* ThirdPartyDrives
  * Reason: Required to avoid Hibernation wake issues on 3rd party drives
  * Logic: Patches AppleAHCIPort.kext into support
  * Models: All models with standard SATA ports
* PanicNoKextDump
  * Reason: Avoids kext dump on kernel panics, easier kernel debugging
  * Logic: Patches Kernel to not dump dump unnecessary info
  * Models: Only set when Verbose Boot is enabled by the user

### Misc -> Security

* SecureBootModel
  * Reason: Required to allow native OS updates on T2 model spoofs
  * Logic: Sets T2's Secure Enclave Identifier
  * Models: All models required that spoof T2 model with minimal or higher

### NVRAM -> Add

* `-v keepsyms=1 debug=0x100`
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
* `-revasset`
  * Reason: Enables Content Caching when using VMM spoofing
  * Logic: Adds args to NVRAM
  * Models: Any model using VMM spoofing

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
  * Models: All models require when spoofing or have non-stock GPU
* CPUFriend
  * Reason: Patches IOx86PlatformPlugin to restore previous CPU profiles
  * Models: All models using minimal or higher spoofing
* AirportBrcmFixup
  * Reason: Patches IO80211 and co to fix networking support for unsupported cards, and fix bugs on native ones as well (ie. random degraded network performance)
  * Models: BCM943224, BCM94331, BCM94360 and BCM943602
* BlueToolFixup
  * Reason: Patches BlueTool to enable bluetooth functionality on Monterey
  * Models: All models with pre-BCM94360 wireless cards or 3rd-party chipsets
* Bluetooth-Spoof
  * Reason: Injects extra data into certain bluetooth chipsets for recognition by the system 
  * Models: Models with the BCM2070 or BCM2046 chipsets
* FeatureUnlock (Night Shift)
  * Reason: Patches CoreBrightness.framework to enable Night Shift on unsupported models
  * Models: 2011 or older
* FeatureUnlock (Sidecar/AirPlay)
  * Reason: Patches SidecarCore.framework and AirPlaySupport.framework to enable Sidecar and AirPlay to Mac on unsupported models
  * Models: All models with Metal capable GPUs
* RestrictEvents
  * Reason: Disables memory errors on MacPro7,1
  * Models: Mac Pros and Xserves

### Ethernet

* nForceEthernet
  * Reason: Inject old NVIDIA Ethernet kext to resolve networking in Catalina and newer
  * Models: 2010 and older NVIDIA Ethernet require
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
  * Models: All models require when spoofing moderate or higher, as well as pre-2012 models

### SSE

* AAMouSSE
  * Reason: Translates SSE4.2 instructions to compatible code for SSE4,1 CPUs, required for AMD Metal drives
  * Models: MacPro3,1
* telemetrap
  * Reason: Ensures telemetry.plugin doesn't run, required for SSE4,1 CPUs
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
  * Reason: Patch AppleBacklight for iMacs with NVIDIA Metal GPU upgrades
  * Models: iMac11,x, iMac12,x with upgraded NVIDIA Metal GPUs
* AppleIntelPIIXATA
  * Reason: Fix IDE support on MacPro3,1
  * Models: MacPro3,1
* AppleIntelMCEDisabler
  * Reason: Fix dual socket support in Catalina and newer
  * Models: Mac Pros and Xserves
* SMC-Spoof
  * Reason: Spoofs SMC version to 9.9999
  * Models: All models require when spoofing minimal or higher
:::

## On-Disk Patches

Unfortunately certain on-disk patches are required to achieve full functionality. Below is a breakdown of patches supported

::: details Audio Patches (11.0+)

### Extensions

* AppleHDA
  * Reason: Re-add El Capitan's AppleHDA to achieve audio support
  * Models: iMac7,1 and iMac8,1

:::

::: details Legacy Wireless Patches (12.0+)

Applicable for BCM94328, BCM94322 and Atheros Wifi cards

### CoreServices

* WiFiAgent.app

### /usr/libexec

* airportd

:::

::: details NVIDIA Kepler Graphics Acceleration Patches (12.0+)

### Extensions

* GeForce.kext
* GeForceAIRPlugin.bundle
* GeForceGLDriver.bundle
* GeForceMTLDriver.bundle
* GeForceVADriver.bundle
* NVDAGF100Hal.kext
* NVDAGK100Hal.kext
* NVDAResman.kext
* NVDAStartup.kext

### Frameworks

* OpenCL (libCLVMNVPTXPlugin.dylib, NVPTX.dylib)
  * Reason: Re-add Kepler hardware acceleration support

:::


::: details Intel Ivy Bridge Graphics Acceleration Patches (12.0+)

### Extensions

* AppleIntelIVBVA.bundle
* AppleIntelFramebufferCapri.kext
* AppleIntelGraphicsShared.bundle
* AppleIntelHD4000Graphics.kext
* AppleIntelHD4000GraphicsGLDriver.bundle
* AppleIntelHD4000GraphicsMTLDriver.bundle
* AppleIntelHD4000GraphicsVADriver.bundle

### PrivateFrameworks

* AppleGVA/AppleGVACore
  * Reason: Enable DRM support

### Frameworks

* OpenCL (libCLVMIGILPlugin.dylib)
  * Reason: Re-add Ivy Bridge hardware acceleration support
* WebKit (com.apple.WebProcess.sb)
  * Reason: Re-add Ivy Bridge Safari rendering support
:::

::: details non-Metal Graphics Acceleration Patches (11.0+)

### Extensions

#### General Patches

* IOSurface.kext
  * Reason: Fixes immediate logout on login
  * Logic: Downgrade to Catalina IOSurface
  * Note: For AMD and Intel, additional `addMemoryRegion/removeMemoryRegion` patch added changing the first conditional jump to non conditional jump
    * At Offset `0xdb52` and `0xdbc6`, replace following bytes with `0xeb`

#### Dropped Acceleration Binaries

* NVIDIA Binaries
  * GeForceGA.bundle
  * GeForceTesla.kext
    * Skip IOFree Panic - Mojave+
      * At Offset `0x5CF9A` replace following bytes with `0xEB`
    * Avoids `addMemoryRegion/removeMemoryRegion` calls
      * At Offset `0x5527` and `0x77993`, replace following bytes with `0x909090909090`
  * GeForceTeslaGLDriver.bundle
  * GeForceTeslaVADriver.bundle
  * NVDANV50HalTesla.kext
  * NVDAResmanTesla.kext
    * 0x1ea59a - 0x1ea5b3: nop
    * Replace VSLGestalt to IOLockLock or any other known symbol of the same length.

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
    * Board ID Patch
      * Replace original Board ID with updated model
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

:::
