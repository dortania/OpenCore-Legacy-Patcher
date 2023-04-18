![](../images/macos-ventura.png)

::: warning
macOS Ventura is supported by OpenCore Legacy Patcher **0.5.0 and later,** currently in early stages.  
Use the latest available version for the most stability.
:::

## Dropped Hardware

In addition to all unsupported Macs, the following models will now require OpenCore Legacy Patcher to run macOS Ventura:

| Model Name | Model Identifier |
| --- | --- |
| iMac (21.5-inch, Late 2015) | `iMac16,1` | 
| iMac (Retina 4K, 21.5-inch, Late 2015) | `iMac16,2` | 
| iMac (Retina 5K, 27-inch, Late 2015) | `iMac17,1` |
| MacBook (Retina, 12-inch, Early 2016) | `MacBook9,1` |
| MacBook Air (11-inch, Early 2015) | `MacBookAir7,1` | 
| MacBook Air (13-inch, Early 2015)<br>MacBook Air (13-inch, 2017) | `MacBookAir7,2` | 
| MacBook Pro (Retina, 15-inch, Mid 2015) | `MacBookPro11,4`<br>`MacBookPro11,5` | 
| MacBook Pro (Retina, 13-inch, Early 2015) | `MacBookPro12,1` | 
| MacBook Pro (13-inch, 2016, 2 Thunderbolt 3 ports) | `MacBookPro13,1` | 
| MacBook Pro (13-inch, 2016, 4 Thunderbolt 3 ports) | `MacBookPro13,2` | 
| MacBook Pro (15-inch, 2016) | `MacBookPro13,3` | 
| Mac mini (Late 2014) | `Macmini7,1` | 
| Mac Pro (Late 2013) | `MacPro6,1` |

## Current issues

### AMD Polaris, Vega and Navi support on pre-2019 Mac Pros and pre-2012 iMacs

For users with 2008 to 2013 Mac Pros (MacPro3,1-6,1) and 2009 to 2011 iMacs (iMac9,1-12,2), keep in mind that macOS Ventura now requires [AVX2.0 support in the CPU](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#Advanced_Vector_Extensions_2) for native graphics acceleration. Thus while your GPU may be natively supported, you cannot run Ventura officially with these GPUs.

* CPUs supporting AVX2.0 are Haswell or newer, which no pre-2019 Mac Pros can be upgraded with.

Currently at this time, OpenCore Legacy Patcher only supports patching the AMD Polaris and Vega Graphics stack to no longer require AVX2.0. We're recently received an AMD RX 6600 donation, so hopefully in the future the project can support AMD Navi with pre-Haswell Macs. However, no time estimates can be given.

Following GPUs are applicable:

| GPU Architecture | Model Families | Supported |
| :--- | :--- | :--- |
| AMD Polaris | RX 4xx/5xx (10/20 series) | <span style="color:#30BCD5"> Supported with patching </span> |
| AMD Vega    | Vega 56/64/VII (10/20 series) | ^^ |
| AMD Navi    | RX 5xxx/6xxx (10/20 series) | <span style="color:red"> Unsupported </span> |


### USB 1.1 (OHCI/UHCI) Support

For Penryn systems and pre-2013 Mac Pros, USB 1.1 support was outright removed in macOS Ventura. While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth

With OpenCore Legacy Patcher 0.6.0, basic support has been implemented via Root Volume patching. However due to this, users will need to use a USB hub for installation and post-OS updates when patches are cleaned:

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

### Ethernet issue with Early 2008 Mac Pro

MacPro3,1 suffers from the Ethernet driver dying after returning from sleep, current workaround is to use a USB Ethernet adapter or disable sleep.

## Resolved Issues

::: details Legacy Wireless Support (Resolved in 0.6.0 and later)


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


::: details Non-Metal Graphics Acceleration (Resolved in 0.6.0 and later)


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
* MacBook4,1 - MacBook7,1
* MacBookAir2,1 - MacBookAir4,x
* MacBookPro4,1 - MacBookPro8,x
* Macmini3,1 - Macmini5,x
* MacPro3,1 - MacPro5,1
* Xserve2,1 - Xserve3,1


:::