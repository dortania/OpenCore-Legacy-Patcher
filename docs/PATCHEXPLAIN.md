# Explaining the patches in OpenCore Legacy Patcher

In our patcher, there are numerous patches used to ensure a stable system. Here, we're going to go over what patches are used and why we recommend or even require them.

* [OpenCore Settings](#opencore-settings)
* [Injected Kexts](#injected-kexts)
* [On-Disk Patches](#on-disk-patches)

## OpenCore Settings

Below is a rundown of the main logic that OpenCore Legacy Patcher uses to gain native support in macOS. Note that OpenCore's configuration is documented within [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) as well as on an online version provided by us:

* [OpenCorePkg Online Docs](https://dortania.github.io/docs/latest/Configuration.html)

::: details Configuration Explanation

### ACPI -> Add

* SSDT-CPBG
  * Reason: Resolves Kernel Panic on Arrandale Macs in early Big Sur builds
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
* `amfi=0x80`
  * Reason: Disables Apple Mobile File Integrity to allow for root patches
  * Logic: Adds args to NVRAM
  * Models: Any model that requires unsigned root patches

### UEFI -> ProtocolOverrides

* GopPassThrough
  * Reason: Used for proper output on machines with UGA firmware but GOP GPU
  * Logic: Provide GOP protocol instances on top of UGA protocol instances
  * Models: MacPro3,1, iMac7,1-8,1

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
* CryptexFixup
  * Reason: Installs non AVX2.0 Cryptex on non AVX2.0 CPUs
  * Models: All CPUs Ivy Bridge and older
* AutoPkgInstaller
  * Reason: Allows for automatic root patching
* NVMeFix
  * Reason: Fixes 3rd party NVMe support
* RSRHelper
  * Reason: Fixes Rapid Security Response Support on root patched installs
* 

### Ethernet

* nForceEthernet
  * Reason: Inject old NVIDIA Ethernet kext to resolve networking in Catalina and newer
  * Models: 2010 and older NVIDIA Ethernet require
* MarvelYukonEthernet
  * Reason: Inject old Marvel Ethernet kext to resolve networking in Catalina and newer
  * Models: 2008 and older Marvel Ethernet require
* CatalinaBCM5701Ethernet
  * Reason: Inject old Broadcom Ethernet kext to resolve networking in Big Sur
  * Logic: Patch out conflicting symbols to not collide existing BCM5701Ethernet
  * Models: 2011 and older Broadcom Ethernet require
* Intel82574L
  * Reason: Resolves Ethernet Support on MacPros 
  * Models: MacPro3,1 - 5,1
* CatalinaIntelI210Ethernet
  * Reason: Fixes Intel i210/i225 NIC support on pre-Ivy Macs
* AppleIntel8254XEthernet
  * Reason: Resolves Ethernet Support on MacPros 
  * Models: MacPro3,1 - 5,1

### Firewire 

* IOFireWireFamily
  * Reason: Allows for FireWire Boot Support
* IOFireWireSBP2
  * Reason: Allows for FireWire Boot Support
* IOFireWireSerialBusProtoColTransport
  * Reason: Allows for FireWire Boot Support

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

* IO80211ElCap
  * Reason: Re-inject WiFi drivers from El Capitan 
  * Models: BCM94328, BCM94322 and Atheros chipsets
* corecaptureElCap.kext
  * Reason: Re-inject WiFi drivers from El Capitan 
  * Models: BCM94328, BCM94322 and Atheros chipsets

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
* AppleRAIDCard
  * Adds AppleRaidCard Support for Xserves
* AMDGPUWakeHandler
  * Reason: Adds Software Based Demux for 2011 15/17 Macbook Pros
* AppleIntelCPUPowerManagement and AppleIntelCPUPowerManagementClient
  * Reason: Restores Ivy Bridge and older CPU Power Management
* AppleUSBTopCase
  * Reason: Restore USB Keyboard support on Mac OS Ventura
* AppleUSBMultitouch and AppleUSBTrackpad
  * Reason: Restore USB Trackpad support on Mac OS Ventura
* ASPP-Override
  * Reason: Forces ACPI_SMC_PlatformPlugin to outmatch X86PlatformPlugin and disable firmware throttling 
* BacklightInjector
  * Reason: Fixes Brightness in iMacs with upgraded GPUs
* BigSurSDXC
  * Reason: Restores SDXC Support in Pre Ivy-Bridge Macs
* Bluetooth-spoof
  * Reason: Spoofs legacy Bluetooth to work on Monterey and newer
* Innie
  * Reason: Makes all PCIe drives appear internal
  * Models: MacPro3,1 and newer & Xserve3,1 and newer 
* KDKlessWorkaround
  * Reason: Helps with Mac os updates on KDKless patched systems
* LegacyUSBVieoSupport
  * Reason: Fixes Legacy USB iSight support
* MonteAHCIPort
  * Reason: Fixes SSD support for stock SSD found in MacBookAir6,x
* NoAVXFSCompressionTypeZlib
  * Reason: Prevents AVXFSCompressionTypeZlib crash on pre AVX1.0 systems in 12.4+
* SimpleMSR 
  * Reason: Disables BD PROCHOT to prevent firmware throttling on Nehalem+ MacBooks
* LegacyKeyboardInjector
  * Reason: Fixes function keys on MacBook5,2


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
* Metal 
  * Reason: 3802 based GPU's broken by 13.3, requiring a Metal downgrade to 13.2.1

### PrivateFrameworks

* MTLCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a MTLCompiler downgrade to 13.2.1
* GPUCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a GPUCompiler downgrade to 13.2.1

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
* MTLCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a MTLCompiler downgrade to 13.2.1
* GPUCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a GPUCompiler downgrade to 13.2.1

### Frameworks

* OpenCL (libCLVMIGILPlugin.dylib)
  * Reason: Re-add Ivy Bridge hardware acceleration support
* WebKit (com.apple.WebProcess.sb)
  * Reason: Re-add Ivy Bridge Safari rendering support
* Metal 
  * Reason:  3802 based GPU's broken by 13.3, requiring a Metal downgrade to 13.2.1
:::

::: details Intel Haswell Graphics Acceleration Patches (13.0+)

### Extensions 

* AppleIntelFramebufferAzul.kext
* AppleIntelHD5000Graphics.kext
* AppleIntelHD5000GraphicsGLDriver.bundle
* AppleIntelHD5000GraphicsMTLDriver.bundle
* AppleIntelHD5000GraphicsVADriver.bundle 
* AppleIntelHSWVA.bundle
* AppleIntelGraphicsShared.bundle

### Frameworks 

* Metal 
  * Reason:  3802 based GPU's broken by 13.3, requiring a Metal downgrade to 13.2.1

### PrivateFrameworks

* MTLCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a MTLCompiler downgrade to 13.2.1
* GPUCompiler
  * Reason: 3802 based GPU's broken by 13.3, requiring a GPUCompiler downgrade to 13.2.1

:::

::: details Intel Broadwell Graphics Acceleration Patches (13.0+)

### Extensions 

* AppleIntelBDWGraphics.kext
* AppleIntelBDWGraphicsFramebuffer.kext
* AppleIntelBDWGraphicsGLDriver.bundle
* AppleIntelBDWGraphicsMTLDriver.bundle
* AppleIntelBDWGraphicsVADriver.bundle
* AppleIntelBDWGraphicsVAME.bundle
* AppleIntelGraphicsShared.bundle



:::

::: details Intel Skylake Graphics Acceleration Patches (13.0+)

### Extensions 

* AppleIntelSKLGraphics.kext
* AppleIntelSKLGraphicsFramebuffer.kext
* AppleIntelSKLGraphicsGLDriver.bundle
* AppleIntelSKLGraphicsMTLDriver.bundle
* AppleIntelSKLGraphicsVADriver.bundle
* AppleIntelSKLGraphicsVAME.bundle
* AppleIntelGraphicsShared.bundle


:::

::: details AMD Legacy Vega Graphics Acceleration Patches (13.0+)

### Extensions

* AMDRadeonX5000.kext
* AMDRadeonVADriver2.bundle
* AMDRadeonX5000GLDriver.bundle
* AMDRadeonX5000MTLDriver.bundle
* AMDRadeonX5000Shared.bundle
* AMDShared.bundle

:::

::: details AMD Legacy Polaris Graphics Acceleration Patches (13.0+)

### Extensions

* AMDRadeonX4000.kext
* AMDRadeonX4000HWServices.kext
* AMDRadeonVADriver2.bundle
* AMDRadeonX4000GLDriver.bundle
* AMDMTLBronzeDriver.bundle
* AMDShared.bundle

:::

::: details AMD Legacy GCN Graphics Acceleration Patches

### Extensions

* AMD7000Controller.kext
* AMD8000Controller.kext
* AMD9000Controller.kext
* AMD9500Controller.kext
* AMD10000Controller.kext
* AMDRadeonX4000.kext
* AMDRadeonX4000HWServices.kext
* AMDFramebuffer.kext
* AMDSupport.kext
* AMDRadeonVADriver.bundle
* AMDRadeonVADriver2.bundle
* AMDRadeonX4000GLDriver.bundle
* AMDMTLBronzeDriver.bundle
* AMDShared.bundle




::: details non-Metal Graphics Acceleration Patches (11.0+)

### General Patches

* IOSurface.kext
  * Reason: Fixes immediate logout on login
  * Logic: Downgrade to Catalina IOSurface
  * Note: For AMD and Intel, additional `addMemoryRegion/removeMemoryRegion` patch added changing the first conditional jump to non conditional jump
    * At Offset `0xdb52` and `0xdbc6`, replace following bytes with `0xeb`

### Dropped Acceleration Binaries

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

* NVIDIA Web Drivers Binaries 
  * GeForceWeb.kext
  * NVDAGF100HalWeb.kext
  * NVDAGK100HalWeb.kext
  * NVDAGM100HalWeb.kext
  * NVDAGP100HalWeb.kext
  * NVDAResmanWeb.kext
  * NVDAStartupWeb.kext
  * GeForceTeslaWeb.kext
  * NVDANV50HalTeslaWeb.kext
  * NVDAResmanTeslaWeb.kext
    * Reason: Allows for non-Metal Acceleration for NVIDIA Maxwell and Pascal GPUs

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
