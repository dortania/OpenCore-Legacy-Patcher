![](../images/macos-monterey.png)

With OpenCore Legacy Patcher v0.1.7 and newer, we've implemented beta macOS Monterey support for users. Please note that Apple has dropped a lot of hardware with this release as well as broken many of our previous patch sets. This page will be used to inform users regarding current issues and will be updated as new patch sets are developed and added to our patcher.

## Newly dropped hardware

With Monterey, Apple continues their their somewhat ruthless march of dropping Intel hardware. This release saw the removal, and thus addition into OpenCore Legacy Patcher, of the following models:

* iMac14,4
* iMac15,1
* MacBook8,1
* MacBookAir6,1
* MacBookAir6,2
* MacBookPro11,1
* MacBookPro11,2
* MacBookPro11,3

::: details Model names

* iMac (21.5-inch, Mid 2014)
* iMac (Retina 5K, 27-inch, Late 2014)
* MacBook (Retina, 12-inch, Early 2015)
* MacBook Air (11-inch, Mid 2013)
* MacBook Air (13-inch, Mid 2013)
* MacBook Air (11-inch, Early 2014)
* MacBook Air (13-inch, Early 2014)
* MacBook Pro (Retina, 13-inch, Late 2013)
* MacBook Pro (Retina, 15-inch, Late 2013)
* MacBook Pro (Retina, 13-inch, Mid 2014)
* MacBook Pro (Retina, 15-inch, Mid 2014)

:::

All of these models now have support in OpenCore Legacy Patcher.

## Current Monterey Issues

### MacBookPro11,3 booting issue without Kepler acceleration

Due to the display being routed through the NVIDIA Kepler card and macOS being rendered on the Intel iGPU, users have been experiencing issues booting without post-install patches applied ([see here for more info](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/522).) Currently the only workaround is to install the patches in safe mode, by holding down `Shift+Enter` when you select macOS in the OCLP boot picker.

## Previously Broken Hardware

::: details iMac15,1 5K Display Output Issue (Resolved in 0.3.2 and newer)

* Documentation:
  * [5K iMac and UEFI: Fixing the dreaded output limitation](https://khronokernel.github.io/macos/2021/12/08/5K-UEFI.html)
* Associated Github Issue:
  * [5k Output issues on iMac15,1 (27" 5k iMac - 2014) #359](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/359)

:::

::: details macOS 12.0 Beta 4 issue on 2012 to early 2013 machines (Resolved in 0.2.5 and newer)

Currently in macOS 12.0 Beta 4, many Ivy Bridge Macs have experienced Bluetooth issues relating to their BCM20702 chipset. Currently the exact issue is unknown however is assumed to be a bug on Apple's end. Recommend downgrading to macOS 12.0 Beta 3 till resolved:

* [12.0 Beta 3 (21A5284e) InstallAssistant (Direct)](http://swcdn.apple.com/content/downloads/02/08/071-63739-A_G5RYVW5JHT/dfz5gp3s0jm9vl7m30oewq141zkpv8edr8/InstallAssistant.pkg)
* [12.0 Beta 3 (21A5284e) InstallAssistant (archive.org)](https://archive.org/details/12.0-21a5284e-beta-3)

A temporary fix is to restart the BlueTool and bluetoothd process with each boot, note it may not work for all users:

```sh
sudo killall -9 BlueTool bluetoothd
```

:::

::: details Wireless Support Dropped (Resolved in 0.2.5 and newer)

* Broadcom BCM94328, BCM94322 and Atheros Wireless Chipsets lost support

The following models lost Wifi support in macOS Monterey due to their legacy Wireless chipset:

* iMac12,x and older
* Macmini3,1 and older
* MacBook5,x and older
* MacBookAir2,1 and older
* MacBookPro7,1 and older
  * MacBookPro6,x is exempt
* MacPro5,1 and older

Note: BCM943224, BCM94331, BCM94360 and BCM943602 are still fully supported by OpenCore Legacy Patcher

:::

::: details Bluetooth Support Dropped (Resolved in 0.2.5 and newer)

* BRCM2046 and BRCM2070 Bluetooth Chipsets lost support

The following models lost Bluetooth support in macOS Monterey due to their legacy Bluetooth chipset:

* iMac12,x and older
* Macmini5,1 and older
* MacBook7,1 and older
* MacBookAir4,1 and older
* MacBookPro8,1 and older
* MacPro5,1 and older

Note: Native BRCM20702 and BRCM20703 are still fully supported by OpenCore Legacy Patcher

::: details Dropped Firmwares

Here are the firmwares macOS Monterey Dropped (previously located within IOBluetoothUSBDFU.kext):

* 2046_820F.dfu
* 2046_8210.dfu
* 2046_8213.dfu
* 2046_8215.dfu
* 2046_8216.dfu
* 2046_8217.dfu
* 2070_821A.dfu
* 2070_821B.dfu
* 2070_8218.dfu
* 20702_821D.dfu
* 20702_821F.dfu
* 20702_828A.dfu
* 20702_828B.dfu
* 20702_828C.dfu
* 20702_8281.dfu
* 20702_8286.dfu

:::

::: details Ivy Bridge iGPU Acceleration (Resolved in 0.1.7 and newer)

* Intel HD4000 iGPUs lost support

By default these machines require root volume patches to gain graphics acceleration in Monterey. OpenCore Legacy Patcher supports readding support however SIP can no longer be enabled due to root patching:

* Macmini6,x
* MacBookAir5,x
* MacBookPro9,x
* MacBookPro10,x

:::

::: details NVIDIA Kepler dGPU Acceleration (Resolved in 0.2.5 and newer)

* NVIDIA Kepler dGPUs lost support

By default these machines require root volume patches to gain graphics acceleration in Monterey. OpenCore Legacy Patcher supports readding support however SIP can no longer be enabled due to root patching:

* MacBookPro9,1
* MacBookPro10,1
* MacBookPro11,3
* iMac13,x
* iMac14,x

:::

::: details Non-Metal Acceleration (Resolved in 0.2.5 and newer)

* Non-Metal GPUs no longer have working acceleration patches:
  * Intel Ironlake and Sandy Bridge iGPUs
  * NVIDIA Tesla and Fermi GPUs
  * AMD TeraScale 1 and 2 GPUs

The following machines cannot gain graphics acceleration at all in Monterey, only basic framebuffer and brightness control (iMac8,1/9,1 and MacBook5,2 excluded):

* iMac12,x and older
* Macmini5,x and older
* MacBook7,1 and older
* MacBookAir4,x and older
* MacBookPro8,x and older

Note: iMac10,1 through iMac12,x can be upgraded with Metal GPUs, [see here for more info](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/)

:::
