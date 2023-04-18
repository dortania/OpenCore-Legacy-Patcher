![](../images/macos-bigsur.png)

::: warning
macOS Big Sur is supported by OpenCore Legacy Patcher **0.0.1 and later.**  
Use the latest available version for the most stability.
:::

## Dropped Hardware

In addition to all unsupported Macs, the following models will now require OpenCore Legacy Patcher to run macOS Big Sur:

| Model Name | Model Identifier |
| --- | --- |
| iMac (21.5-inch, Late 2012) | `iMac13,1` |
| iMac (27-inch, Late 2012) | `iMac13,2` |
| iMac (21.5-inch, Early 2013) | `iMac13,3` |
| MacBook Air (11-inch, Mid 2012) | `MacBookAir6,1` |
| MacBook Air (13-inch, Mid 2012) | `MacBookAir6,2` |
| MacBook Air (11-inch, Mid 2013) | `MacBookAir6,1` |
| MacBook Air (13-inch, Mid 2013) | `MacBookAir6,2` |
| MacBook Pro (15-inch, Mid 2012) | `MacBookPro9,1` |
| MacBook Pro (13-inch, Mid 2012) | `MacBookPro9,2` |
| MacBook Pro (Retina, 15-inch, Mid 2012) | `MacBookPro10,1` |
| MacBook Pro (Retina, 13-inch, Late 2012) | `MacBookPro10,2` |
| MacBook Pro (Retina, 15-inch, Early 2013) | `MacBookPro10,1` |
| MacBook Pro (Retina, 13-inch, Early 2013) | `MacBookPro10,2` |
| Mac mini (Late 2012) | `Macmini6,1` |

## Current Issues

### Root unpatching resulting in failure

When running Big Sur with root patches installed, macOS will delete the original system snapshot after 2-3 days. This presents no issue under normal use, however users will be required to reinstall macOS in order to remove root patches.

## Resolved Issues

::: details TeraScale 2 Acceleration Issues (Resolved in 0.4.2 and later)

AMD TeraScale 2 GPUs can be subject to **severe** graphical anomolies, such as

* Windows flashing violently
* Heavy artifacting when waking from sleep
* Apps not rendering properly

Changes have been slowly introduced over multiple versions to try and allieviate the issues.

::: warning For photosensitive epileptics
People who are prone to epilepsy should exercise **extreme** caution when using TeraScale 2 GPUs on Big Sur, or wait until the proper fixes have been found.
::: 

::: details Stock bluetooth panics on iMac7,1 and MacPro3,1 (Resolved in 0.1.3 and later)

Due to the connection of the stock Bluetooth card in the imac7,1 and MacPro3,1, it can cause kernel panics when loading `com.apple.driver.CSRHIDTransitionDriver` in the macOS installer or macOS itself.

Workaround is to remove the stock Bluetooth card in these models, however be aware that Bluetooth will not function until it is replaced.

:::

::: details Non-Metal Acceleration (Resolved in 0.1.1 and later)

* Non-Metal GPUs do not have working acceleration patches:
  * Intel Ironlake and Sandy Bridge iGPUs
  * NVIDIA Tesla and Fermi GPUs
  * AMD TeraScale 1 and 2 GPUs

The following machines cannot gain graphics acceleration at all in Big Sur:

* iMac12,x and older
* Macmini5,x and older
* MacBook7,1 and older
* MacBookAir4,x and older
* MacBookPro8,x and older

Note: iMac10,1 through iMac12,x can be upgraded with Metal GPUs, [see here for more info](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/)

:::

::: details Incorrect firmware updates bricking Macs (Resolved in 0.0.9 and later)

As a result of the spoofing done by OpenCore, some users began to report issues with macOS updates installing firmware for different Mac models and rendering them unable to be used. We strongly recommend holding off on any macOS updates until this issue is resolved.

* Some users have reported that you can remove the RTC battery to fix the issue. If the firmware update is installed, **this is not the case,** and a firmware flasher will be required to fix the issue.

Signs that this has occurred:

* System's display is black and/or completely off
* Fans spin to 100% when pressing the power button
* A chime can't be heard
* Various hardware may not work (such as charger, USB ports, etc)

:::