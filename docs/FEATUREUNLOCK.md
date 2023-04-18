# Enabling blacklisted features

OpenCore Legacy Patcher makes use of **FeatureUnlock**, a powerful patching engine to enable features on Macs restricted from using them by Apple.
* This applies to natively-supported Macs as well.
* If your model is not listed in a specific section, that feature is not restricted from being enabled on your Mac. 
  * This does not mean your Mac hardware is capable of those features. See the Special notes of each section.

::: warning
FeatureUnlock can cause instability and performance issues in macOS. If random issues with the operating system arise while enabled, try disabling FeatureUnlock before asking for support.
:::

## Night Shift

Requirements:
* macOS 10.12.4 or later

Applicable for:
* [MacBook5,x - MacBook7,1](MODELS.md#macbook)
* [MacBookAir2,1 - MacBookAir4,x](MODELS.md#macbook-air)
* [MacBookPro4,1 - MacBookPro8,x](MODELS.md#macbook-pro)
* [Macmini3,1 - Macmini5,x](MODELS.md#mac-mini)
* [MacPro3,1 - MacPro5,1](MODELS.md#mac-pro)
* [iMac7,1 - iMac12,x](MODELS.md#imac)

::: details Special notes
Nothing to see here...
:::

## Sidecar 

Requirements: 
* macOS 10.15 or later
* iPadOS 13.0 or later
* WiFi N and Bluetooth 4.0 (for wireless usage)
* Apple ID, with 2FA enabled and signed into both devices

Applicable for:
* [MacBook8,1](MODELS.md#macbook)
* [MacBookAir5,x - MacBookAir7,x](MODELS.md#macbook-air)
* [MacBookPro9,x - MacBookPro12,x](MODELS.md#macbook-pro)
* [Macmini6,x - Macmini7,1](MODELS.md#mac-mini)
* [MacPro5,1 - MacPro6,1](MODELS.md#mac-pro)
* [iMac13,x - iMac16,x](MODELS.md#imac)

Additionally if the `-allow_sidecar_ipad` argument is present:
* iPad4,x - iPad5,x
* iPad6,11 - iPad6,12

::: details Special notes
* Most machines will reliably work
  * Mac Pros and iMacs with no iGPUs may have difficulties
  * All other unsupported models will not have the highest streaming quality due to no H.265 encoding support
:::

## AirPlay to Mac 
Requirements:
* macOS 12.0 or later


Applicable for:
* [MacBook8,1](MODELS.md#macbook)
* [MacBookAir5,x - MacBookAir7,x](MODELS.md#macbook-air)
* [MacBookPro9,x - MacBookPro14,x](MODELS.md#macbook-pro)
* [Macmini6,x - Macmini8,1](MODELS.md#mac-mini)
* [MacPro5,1 - MacPro6,1](MODELS.md#mac-pro)
* [iMac13,x - iMac18,x](MODELS.md#imac)

::: details Special notes
* May not work properly on non-Metal Macs when root patches are installed
:::

## Universal Control 
Requirements:
* macOS 12.3 or later
* iPadOS 15.4 or later (if applicable)
* WiFi N and Bluetooth 4.0
* Apple ID, with 2FA enabled and signed into all devices

Applicable for:
* [MacBookAir7,x](MODELS.md#macbook-air)
* [MacBookPro11,4 - MacBookPro12,x](MODELS.md#macbook-pro)
* [Macmini7,1](MODELS.md#mac-mini)
* [MacPro6,1](MODELS.md#mac-pro)
* [iMac16,x](MODELS.md#imac)

::: details Special notes
* All devices check for eligibility, giving blacklisted models a few quirks:
    * If their SMBIOS is unchanged:
        * Other devices will require this patch to connect to the blacklisted Mac
        * Due to this, Apple Silicon Macs, iPads, and unpatched Intel Macs will not work
    * The SMBIOS can be spoofed to an officially supported Mac
        * Can present other oddities in regards to SMBIOS-specific features and issues
        * Changes with each new macOS release as hardware is dropped
        * Allows Apple Silicon Macs, iPads, and unpatched Intel Macs to connect

| Device 1 | Device 2 | Solution |
| --- | --- | --- |
| Unsupported Mac | Unsupported Mac | No patch needed |
| ^^ | Supported Mac | ^^ |
| ^^ | Supported iPad | ^^ |
| ^^ | Blacklisted Mac | `-force_uc_unlock` boot argument |
| Supported Mac | Unsupported Mac | No patch needed |
| ^^ | Supported Mac | ^^ |
| ^^ | Supported iPad | ^^ |
| ^^ | Blacklisted Mac | OpenCore + `-force_uc_unlock` boot argument (Intel)<br>Spoofing (Apple Silicon) |
:::

## Continuity Camera
Requirements:
* macOS 13.0 or later
* iPhone XS/XR or later, with iOS 16.0 or later
* WiFi N and BLuetooth 4.0 (for wireless usage)
* Apple ID, with 2FA enabled and signed into both devices

Applicable for:
* All Macs unsupported in macOS Ventura

::: details Special notes
* Patch does not unlock unsupported iPhones/iPhone features:
    * iPhone XS/XR or later required to use Continuity Camera
    * iPhone 11 or later required for Center Stage
    * iPhone 11 or later (excluding iPhone SE) for Desk View
    * iPhone 12 or later for Studio Light
* Blacklist is not model based, instead is CPU based
:::
