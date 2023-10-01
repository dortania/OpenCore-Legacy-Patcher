![](../images/sonoma.png)

*Well here we are again, it's always such a pleasure~* 

Apple has yet again dropped a bunch of models, continuing their journey on discontinuing Intel Macs. With the release of OpenCore Legacy Patcher v1.0.0, early support for macOS Sonoma has been implemented.

## Newly dropped hardware


* MacBook10,1:       MacBook (Retina, 12-inch, 2017)
* MacBookPro14,1:    MacBook Pro (13-inch, 2017, Two Thunderbolt 3 ports)
* MacBookPro14,2:    MacBook Pro (13-inch, 2017, Four Thunderbolt 3 Ports) 
* MacBookPro14,3:    MacBook Pro (15-inch, 2017)
* iMac18,1:          iMac (21.5-inch, 2017)
* iMac18,2:          iMac (Retina 4K, 21.5-inch, 2017)
* iMac18,3:          iMac (Retina 5K, 27-inch, 2017)

## Current status

OpenCore Legacy Patcher 1.0.0 will provide most functionality in Sonoma, however some challenges remain.

* [Widgets freezing on 3802 systems](#widgets-freezing-on-3802-systems)
* [T1 Security chip](t1-security-chip)
* [USB 1.1 (OHCI/UHCI) Support](#usb-11-ohciuhci-support)


### Widgets freezing on 3802 systems

Opening the widget board on 3802 based systems can freeze the system.

::: details Graphics cards belonging under 3802 include: (click to expand)

__Intel Ivy Bridge__

```sh
Applicable Models:
- MacBookAir5,x
- MacBookPro9,x
- MacBookPro10,x
- iMac13,x
- Macmini6,x
```
__Intel Haswell__

```sh
Applicable Models:
- MacBookAir6,x
- MacBookPro11,x
- iMac14,x
- iMac15,1 (internal, headless iGPU)
- Macmini7,1
```

__NVIDIA Kepler__
```sh
Applicable Models:
- MacBookPro9,1
- MacBookPro10,1
- MacBookPro11,3
- iMac13,x
- iMac14,x
```
::: 

### T1 Security chip

Sonoma has removed support for T1 chips found in most 2016 and 2017 Macs. Therefore on these systems, the following will not function:

* Enable or disable FileVault
* Open the Password Settings window
* Add fingerprints (if upgrading, existing fingerprints will be deleted)
* Add cards to Apple Pay

::: warning ATTENTION: Additionally, due to Sonoma no longer caring about T1, erasing the entire drive will remove the T1 firmware and it won't be reinstalled.
:::



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
:::
