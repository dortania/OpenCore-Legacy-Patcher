![](../images/sonoma.png)

*"Well here we are again, it's always such a pleasure"* 
Apple has yet again dropped a bunch of models, continuing their journey on discontinuing Intel Macs.

With the release of OpenCore Legacy Patcher v1.0.0, early support for macOS Sonoma has been implemented.

## Newly dropped hardware


* MacBook10,1:       MacBook (Retina, 12-inch, 2017)
* MacBookPro14,1:    MacBook Pro (13-inch, 2017, Two Thunderbolt 3 ports)
* MacBookPro14,2:    MacBook Pro (13-inch, 2017, Four Thunderbolt 3 Ports) 
* MacBookPro14,3:    MacBook Pro (15-inch, 2017)
* iMac18,1:          iMac (21.5-inch, 2017)
* iMac18,2:          iMac (Retina 4K, 21.5-inch, 2017)
* iMac18,3:          iMac (Retina 5K, 27-inch, 2017)

## Current status

OpenCore Legacy Patcher 1.0.0 will provide most functionality in Sonoma, however some issues remain.

One of these issues is Widgets on 3802 based systems freezing the system.
Graphics cards belonging under 3802 include:

**Intel Ivy Bridge**

# Applicable Models:
MacBookAir5,x
MacBookPro9,x
MacBookPro10,x
iMac13,x
Macmini6,x

**Intel Haswell**

# Applicable Models:
MacBookAir6,x
MacBookPro11,x
iMac14,x
iMac15,1 (internal, headless iGPU)
Macmini7,1

**NVIDIA Kepler**

# Applicable Models:
MacBookPro9,1
MacBookPro10,1
MacBookPro11,3
iMac13,x
iMac14,x

## Currently Unsupported/Broken Hardware in Sonoma

### T1 Security chip

Systems with T1 Security Chips will also face some significant challenges, specifically that Apple dropped communication support with the T1 chip through the KernelRelayHost stack. Previously kexts such as AppleSSE, AppleCredentialManager and AppleKeyStore used KernelRelayHost to speak with the T1 stub off the USB controller, however in Sonoma Apple dropped linkage to KernelRelayHost.kext. Downgrading these kexts do partially resolve communication, however ApplePay and Touch ID stacks are still unable to communicate correctly with the hardware.

No known solution to resolve supporting, a significant amount of time will be required to understand how both the T1 stack works, as well as where the core issue lies for support.

### USB 1.1 (OHCI/UHCI) Support

For Penryn systems and pre-2013 Mac Pros, USB 1.1 support was outright removed in macOS Ventura and naturally this continues in Sonoma. 
While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth

With OpenCore Legacy Patcher v0.6.0+, basic support has been implemented via Root Volume patching. However due to this, users will need to use a USB hub for installation and post-OS updates when patches are cleaned:

![](../images/usb11-chart.png)

::: warning The following systems rely on USB 1.1

* iMac10,x and older
* Macmini3,1 and older
* MacBook7,1 and older
* MacBookAir3,1 and older
* MacBookPro7,1 and older
  * MacBookPro6,x is exempt
* MacPro5,1 and older

:::

::: details Legacy Wireless Support (Resolved in v0.6.0 and newer)


### Legacy Wireless Support

For systems that required Root Patches in macOS Monterey to achieve Wireless support, unfortunately macOS Ventura has broken the patch set. Currently the following Wifi cards are unsupported:

* Atheros: All models
* Broadcom: BCM94328 and BCM94322

The following machines shipped stock with these cards:

* iMac12,x and older
* Macmini3,1 and older
* MacBook5,x and older
* MacBookAir2,1 and older
* MacBookPro7,1 and older
  * MacBookPro6,x is exempt
* MacPro5,1 and older


Currently BCM943224, BCM94331, BCM94360 and BCM943602 are still fully supported by OpenCore Legacy Patcher. Consider upgrading to these cards if possible.

:::


::: details Non-Metal Graphics Acceleration (Resolved in v0.6.0 and newer)


### Non-Metal Graphics Acceleration

Regarding non-Metal, the team is hard at work to get non-Metal working, however this is our greatest challenge since Big Sur.

Apple has made significant changes to the graphics stack in order to facilitate fancy effects, and in particularly, Stage Manager. We will update you as we work on development, however, now is not the best time to ask about ETAs.

The following GPUs are applicable:

* NVIDIA:
  * Tesla (8000 - 300 series)
* AMD:
  * TeraScale (2000 - 6000 series)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)


The following machines shipped stock with an unsupported GPU:

* iMac7,1 - iMac12,x
* MacBook5,1 - MacBook7,1
* MacBookAir2,1 - MacBookAir4,x
* MacBookPro4,1 - MacBookPro8,x
* Macmini3,1 - Macmini5,x
* MacPro3,1 - MacPro5,1
* Xserve2,1 - Xserve3,1


:::
