# macOS Monterey Support

With OpenCore Legacy Patcher v0.1.7 and newer, we've implemented beta macOS Monterey support for users. Please note that Apple has dropped a lot of hardware with this release as well as broken many of our previous patch sets. This page will be used to inform users regarding current issues and will be updated as new patch sets are developed and added to our patcher.

Current models with full, unhindered support in OpenCore Legacy Patcher are the following:

* iMac13,x and newer
  * iMac10,1-12,x included if Wireless Card and Bluetooth upgraded as well as Metal GPU
* Macmini7,1 and newer
* MacBook8,1 and newer
* MacBookAir6,x and newer
* MacBookPro11,x and newer
* MacPro3,1 and newer
  * Requires Wireless Card and Bluetooth upgrade for 3,1-5,1 as well as Metal GPU

## Current Hardware Drawbacks:

Below is a list of hardware that currently has issues with Monterey:

* [Acceleration Support Dropped](#acceleration-support-dropped)
  * [Metal GPUs](#metal-gpus)
  * [Non-Metal GPUs](#non-metal-gpus)
* [Bluetooth Support Dropped](#bluetooth-support-dropped)
* [Wireless Support Dropped](#wireless-support-dropped)

## Acceleration Support Dropped

### Metal GPUs

* Intel HD4000 iGPUs lost support

By default these machines require root volume patches to gain graphics acceleration in Monterey. OpenCore Legacy Patcher supports readding support however SIP and FileVault can no longer be enabled due to root patching:

* iMac13,x and older
* Macmini6,x and older
* MacBookAir5,x and older
* MacBookPro10,x and older

Note: Currently HD 4000 support in Monterey is not perfect, following are broken:

::: details HD 4000 Issues

* Photo Booth app crashing
* Safari sites crash if request camera access
* Full Screen recoding crashing with Screenshot app
* AirPlay to Mac crashes
* Full Screen apps crashes
  * Disable "Hide menubar in Full Screen" to avoid crash

:::

### Non-Metal GPUs

* Non-Metal GPUs no longer have working acceleration patches:
  * Intel Ironlake and Sandy Bridge iGPUs
  * Nvidia Tesla and Fermi GPUs
  * AMD TeraScale 1 and 2 GPUs

The following machines cannot gain graphics acceleration at all in Monterey, only basic framebuffer and brightness control (iMac8,1/9,1 and MacBook5,2 excluded):

* iMac12,x and older
* Macmini5,x and older
* MacBook7,1 and older
* MacBookAir4,x and older
* MacBookPro8,x and older

Note: iMac10,1 through iMac12,x can be upgraded with Metal GPUs, [see here for more info](https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/)

## Bluetooth Support Dropped 

* BRCM2046 and BRCM2070 Bluetooth Chipsets lost support

The following models lost Bluetooth support in macOS Monterey due to their legacy Bluetooth chipset:

* iMac12,x and older
* Macmini5,1 and older
* MacBook7,1 and older
* MacBookAir4,1 and older
* MacBookPro8,1 and older
* MacPro5,1 and older

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

Note: Native BRCM20702 and BRCM20703 are still fully support by OpenCore Legacy Patcher

## Wireless Support Dropped

* Broadcom BCM94328, BCM94322 and Atheros Wireless Chipsets lost support

The following models lost Bluetooth support in macOS Monterey due to their legacy Wireless chipset:

* iMac12,x and older
* Macmini3,1 and older
* MacBook5,x and older
* MacBookAir2,1 and older
* MacBookPro7,1 and older
* MacPro5,1 and older

Note: BCM943224, BCM94331, BCM94360 and BCM943602 are still fully support by OpenCore Legacy Patcher