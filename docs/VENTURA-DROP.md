![](../images/ventura.png)

With the release of OpenCore Legacy Patcher v0.5.0 and newer, early support for macOS Ventura has been implemented for most Metal-capable Macs. This page will be used to inform users regarding current issues and will be updated as new patch sets are developed and added to our patcher.

## Newly dropped hardware

Ventura's release dropped a large amount of Intel hardware, thus requiring the usage of OpenCore Legacy Patcher on the following models (in addition to previously removed models):

* iMac16,1 (21.5-inch, Late 2015)
* iMac16,2 (21.5-inch 4K, Late 2015)
* iMac17,1 (27-inch 5K, Late 2015)
* MacBook9,1 (12-inch, Early 2016)
* MacBookAir7,1 (11-inch, Early 2015)
* MacBookAir7,2 (13-inch, Early 2015)
* MacBookPro11,4 (15-inch, Mid 2015, iGPU)
* MacBookPro11,5 (15-inch, Mid 2015, dGPU)
* MacBookPro12,1 (13-inch, Early 2015)
* MacBookPro13,1 (13-inch, Late 2016)
* MacBookPro13,2 (13-inch, Late 2016)
* MacBookPro13,3 (15-inch, Late 2016)
* Macmini7,1 (Late 2014)
* MacPro6,1 (Late 2013)


## Current status

Overall, macOS Ventura is useable on most Metal-capable machines (ie. 2012 and newer). The graphics patches implemented have near feature parity to macOS Monterey, with patches still being under heavy development. See [Legacy Metal Graphics Support and macOS Ventura #1008](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008) issue for more information.

<img width="625" alt="" src="../images/OCLP-051-Initial-Support.png">

For older hardware, see below sections:

* [Currently Unsupported/Broken Hardware in Ventura](#currently-unsupportedbroken-hardware-in-ventura)
  * [AMD Polaris, Vega and Navi support on pre-2019 Mac Pros and pre-2012 iMacs](#amd-polaris-vega-and-navi-support-on-pre-2019-mac-pros-and-pre-2012-imacs)
  * [Non-Metal Graphics Acceleration](#non-metal-graphics-acceleration)
  * [Legacy Wireless Support](#legacy-wireless-support)
  * [USB 1.1 (OHCI/UHCI) Support](#usb-11-ohciuhci-support)
  * [Ethernet issue with Early 2008 Mac Pro](#ethernet-issue-with-early-2008-mac-pro)

The team is doing their best to investigate and fix the aforementioned issues, however no estimated time can be provided.

## Currently Unsupported/Broken Hardware in Ventura

### AMD Polaris, Vega and Navi support on pre-2019 Mac Pros and pre-2012 iMacs

For users with 2008 to 2013 Mac Pros (MacPro3,1-6,1) and 2009 to 2011 iMacs (iMac9,1-12,2), keep in mind macOS Ventura now requires [AVX2.0 support in the CPU](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#Advanced_Vector_Extensions_2) for native graphics acceleration. Thus while your GPU may be natively supported, you cannot run Ventura officially with these GPUs.

* CPUs supporting AVX2.0 are Haswell or newer, which no pre-2019 Mac Pros can be upgraded with.

Currently at this time, OpenCore Legacy Patcher only supports patching the AMD Polaris Graphics stack to no longer require AVX2.0. However due to lack of hardware on-hand, we cannot support AMD Vega or Navi on Ventura.

* If you have spare Vega or Navi GPUs you'd like to donate, feel free to reach out: khronokernel@icloud.com

Additionally, the native stack will crash over and over on macOS Ventura as it fails to load the AVX2.0-based binaries. Thus to patch Ventura, you will need to boot in Safe Mode and run OCLP's Root Volume Patcher

* To enter Safe Mode, hold Shift+Enter when selecting Ventura in OCLP's Boot Picker

Following GPUs are applicable:

| GPU Architecture | Model Families | Supported |
| :--- | :--- | :--- |
| AMD Polaris | RX 4xx/5xx (10/20 series) | <span style="color:#30BCD5"> Supported with patching </span> |
| AMD Vega    | Vega 56/64/VII (10/20 series) | <span style="color:red"> Unsupported </span> |
| AMD Navi    | RX 5xxx/6xxx (10/20 series) | ^^ |


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

::: warning Systems shipped with non-Metal Graphics Cards

* iMac7,1 - iMac12,x
* MacBook4,1 - MacBook7,1
* MacBookAir2,1 - MacBookAir4,x
* MacBookPro4,1 - MacBookPro8,x
* Macmini3,1 - Macmini5,x
* MacPro3,1 - MacPro5,1
* Xserve2,1 - Xserve3,1

:::


### Legacy Wireless Support

For systems that required Root Patches in macOS Monterey to achieve Wireless support, unfortunately macOS Ventura has broken the patch set. Currently the following Wifi cards are unsupported:

* Atheros: All models
* Broadcom: BCM94328 and BCM94322

The following machines shipped stock with these cards:

::: warning Systems shipped with applicable cards

* iMac12,x and older
* Macmini3,1 and older
* MacBook5,x and older
* MacBookAir2,1 and older
* MacBookPro7,1 and older
  * MacBookPro6,x is exempt
* MacPro5,1 and older

:::

Currently BCM943224, BCM94331, BCM94360 and BCM943602 are still fully supported by OpenCore Legacy Patcher. Consider upgrading to these cards if possible.


### USB 1.1 (OHCI/UHCI) Support

For Penryn systems and pre-2013 Mac Pros, USB 1.1 support was outright removed in macOS Ventura. While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth


::: warning The following systems rely on USB 1.1

* iMac10,x and older
* Macmini3,1 and older
* MacBook7,1 and older
* MacBookAir3,1 and older
* MacBookPro7,1 and older
  * MacBookPro6,x is exempt
* MacPro5,1 and older

:::

### Ethernet issue with Early 2008 Mac Pro

MacPro3,1 suffers from Ethernet driver dying after returning from sleep, current workaround is to use a USB Ethernet adapter or disable sleep.
