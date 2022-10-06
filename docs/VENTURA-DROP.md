![](../images/ventura.png)

With OpenCore Legacy Patcher 0.5.0, support for macOS Ventura has been implemented for most Metal supported Macs. This page informs users of the current status and will be updated as new patch sets are developed and added to our patcher.


## Newly dropped hardware

Ventura's release has dropped a huge amount of Intel hardware, requiring support for the following models to be added into OpenCore Legacy Patcher:

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
* MacPro6,1 (Late 2013)



## Current status

For the most part, Ventura is usable on all Metal supported Macs, having only a few minor known issues. Currently the only machine unable to boot is the Mac Pro Late 2013, having an issue with display initialization. More information [here](https://github.com/acidanthera/bugtracker/issues/2126).

Refer to [this GitHub issue](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/998#issuecomment-1222926337) to see up-to-date information about issues with Ventura.

### Currently broken hardware

BCM94328, BCM94322 and Atheros WiFi cards will not function under Ventura, as Ventura has broken legacy WiFi patches.

## Ivy Bridge and older CPU support (Pre-AVX 2.0)

OpenCore Legacy Patcher supports booting and updates on these machines, a way to implement automatic dyld cache swap was added. However, power management is currently not functional.

* Note: AVX 2.0 is required for Vega and Navi drivers, making these cards non-functional under Ventura when a Pre-AVX 2.0 CPU is used, which includes all classic Mac Pros. Therefore Polaris is the newest architecture functional with these machines.

## Non-Metal support

Currently not supported. Apple has changed the graphics stack significantly to support new features (such as Stage Manager) by adding a new layer called WindowManager, breaking all previous patches. 
Therefore an estimated time for non-Metal support cannot be provided, as this has created a much greater challenge. 

