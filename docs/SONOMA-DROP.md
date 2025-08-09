# macOS Sonoma

![](./images/sonoma.png)

*Well here we are again, it's always such a pleasure~*

Apple has yet again dropped a bunch of models, continuing their journey on discontinuing Intel Macs. With the release of OpenCore Legacy Patcher 1.0.0, early support for macOS Sonoma has been implemented.

## Newly dropped hardware

* MacBook10,1:       MacBook (Retina, 12-inch, 2017)
* MacBookPro14,1:    MacBook Pro (13-inch, 2017, Two Thunderbolt 3 ports)
* MacBookPro14,2:    MacBook Pro (13-inch, 2017, Four Thunderbolt 3 Ports)
* MacBookPro14,3:    MacBook Pro (15-inch, 2017)
* iMac18,1:          iMac (21.5-inch, 2017)
* iMac18,2:          iMac (Retina 4K, 21.5-inch, 2017)
* iMac18,3:          iMac (Retina 5K, 27-inch, 2017)

## Current status

OpenCore Legacy Patcher 1.0.0 will support Sonoma for all models normally supported by the Patcher, however some challenges remain. You can find information about them below.

## Issues

* [Bluetooth](#bluetooth)
* [T1 Security chip](#t1-security-chip)
* [USB 1.1 (OHCI/UHCI) Support](#usb-1-1-ohci-uhci-support)
* [Graphics support and issues](#graphics-support-and-issues)


### Bluetooth

Sometimes Bluetooth may not work after boot on pre-2012 models. Running NVRAM reset can alleviate it.

Dual boots may also bring the issue back even after the reset.

### T1 Security chip

::: details Support for the T1 Security chip (Resolved in 1.1.0 and newer)

Sonoma has removed support for T1 chips found in most 2016 and 2017 Macs. Therefore on these systems, the following will not function:

* Enable or disable FileVault
* Open the Password Settings window
* Add fingerprints (if upgrading, existing fingerprints will be deleted)
* Add cards to Apple Pay

[More information here](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1103)

:::

::: warning
Note that erasing the entire drive will remove the T1 firmware and it won't be reinstalled.
:::

### USB 1.1 (OHCI/UHCI) Support

For Penryn systems, pre-2013 Mac Pros and Xserve, USB 1.1 support was outright removed in macOS Ventura and naturally this continues in Sonoma.
While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth

Refer to [the troubleshooting page](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOT-HARDWARE.html#keyboard-mouse-and-trackpad-not-working-in-installer-or-after-update) on how to workaround this issue.

### Graphics support and issues
This build includes both Legacy Metal and non-Metal patches for macOS Sonoma. Refer to the following links for more information about Legacy Metal and non-Metal support and their respective issues.

* [Legacy Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008)
* [Non-Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)

