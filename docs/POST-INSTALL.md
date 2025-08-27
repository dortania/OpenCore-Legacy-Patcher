# Post-Installation

* [Booting without USB drive](#booting-without-usb-drive)
* [Booting seamlessly without Boot Picker](#booting-seamlessly-without-boot-picker)
* [SIP settings](#sip-settings)
* [Applying Post Install Volume Patches](#applying-post-install-volume-patches)

## Booting without USB drive

Once you've installed macOS through OpenCore, you can boot up and go through the regular install process. To boot without the USB drive plugged in is quite simple:

* Download OpenCore Legacy Patcher
* Change Patcher settings as you'd like
* Build OpenCore again
* Install OpenCore to internal drive
* Reboot holding Option, and select the internal EFI

And voila! No more USB drive required.

If you're having issues with undetected internal disk, refer to [Internal disk missing when building OpenCore](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOT-APP.html#internal-disk-missing-when-building-opencore) for troubleshooting.

## Booting seamlessly without Boot Picker

To do this, run the OpenCore Patcher and head to Patcher Settings, then uncheck "Show OpenCore Bootpicker" on the Build tab:


<div align="left">
             <img src="./images/OCLP-GUI-Settings-ShowPicker.png" alt="GUI Settings ShowPicker" width="600" />
</div>


Once you've toggled it off, build your OpenCore EFI once again and install to your desired drive. Now to show the OpenCore selector, you can simply hold down the "ESC" key while clicking on EFI boot, and then you can release the "ESC" key when you see the cursor arrow at the top left.

## SIP settings

SIP, or System Integrity Protection, needs to be lowered on systems where root patching is required to patch data on disk. This will vary between OS versions and the model in question. 

OCLP by default will determine the proper SIP options for the OS version and Mac model, in most cases the user has no need to touch these settings.

:::warning

If you're unsure whether you should change the SIP settings, leave them as-is. Systems where you have already ran the Post Install Root Patching cannot enable SIP without potentially breaking the current install.

:::

| SIP Enabled | SIP Lowered (OCLP default) | SIP Disabled |
| :--- | :--- | :--- |
| ![](./images/OCLP-GUI-Settings-SIP-Enabled.png) | ![](./images/OCLP-GUI-Settings-SIP-Root-Patch.png) | ![](./images/OCLP-GUI-Settings-SIP-Disabled.png) |


The guide in the dropdown below explains how the SIP settings work in OCLP, where lowered SIP is needed and where full SIP could be enabled.

::: details Configuring SIP manually (click to expand)

SIP settings can be accessed from the Security tab shown in the images. To change SIP settings, make the changes here, return in main menu and rebuild OpenCore using the first option.

In the cases where SIP can be enabled, manually enabling it is needed. 

Easiest way to check whether you can fully enable SIP is the "Post Install Root Patch" section, if that section tells your system doesn't need patches (or you don't install the patches e.g. in case you don't need WiFi on a Mac Pro with upgraded GPU running Monterey) then it is safe to assume full SIP can be enabled.

**Ventura and newer**

All unsupported systems require lowered SIP.

**Monterey**

Majority of unsupported systems from 2013 onward can enable full SIP.

Pre-2012 systems, also known as "non-Metal", as well as NVIDIA Kepler and Intel HD 4000 GPUs require lowered SIP. Mac Pros also require lowered SIP for stock WiFi cards and stock GPUs (due to root patching) but if you do not need WiFi (or you plan to upgrade it) and you're running on an upgraded GPU, there is no need for root patching and as such SIP can be fully enabled.

**Big Sur**

All Metal capable systems from 2012 onward (incl. NVIDIA Kepler and Intel HD 4000) as well as Mac Pros with upgraded GPU can run with full SIP enabled. 
Non-Metal systems still require lowered SIP.

:::

## Applying Post Install Volume Patches

Post Install Volume Patches, sometimes also called root patches, are patches that have to be installed to disk for some older Macs to gain back functionality.

These patches include things such as:

- Graphics drivers
- WiFi drivers
- Bluetooth drivers
- Touchbar / T1 drivers
- Built-in camera (iSight) drivers
- USB 1.1 drivers
- Other patches for compatibility with older drivers

OCLP will automatically root patch your system if the USB install media was created within OCLP and the proper model was selected before installer creation. If you did not use OCLP to create the USB drive or autopatching failed, you will need to download OCLP manually and install root patches, since the application will be missing if autopatching wasn't successful.

**Root patches will be wiped by macOS updates and have to be reinstalled after each update.** OCLP will prompt to install these patches after macOS updates or whenever patches are not detected on the system. The USB installer method can also be used to install future updates, utilizing the autopatching process and avoiding the manual patching which is required when updating through System Settings.

In the Post-Install Menu, you can see whether applicable patches have been installed, including the date and version the system was root patched with.

::: warning Important

In some cases OCLP may require packages to be obtained from the internet, such as KDK or MetallibSupportPkg if they do not already exist on the system. In these cases OCLP may only install the WiFi driver on first patch run to ensure you can connect to the internet, which means no graphics acceleration 
after reboot. 

Root patching has to be ran again manually to install the rest of the required patches after internet connection is established to obtain the required packages. You can also utilize Ethernet, which should ensure that all patches will be installed at once.

[Check the affected systems and GPUs from below.](#packages-requiring-networking)

:::

:::warning

If you need to use Migration Assistant to bring over data to your new macOS install, [refer to the guide to do so here.](https://dortania.github.io/OpenCore-Legacy-Patcher/TIMEMACHINE.html)

:::

| Automatic install prompt | Status | Listing Patches | Patching Finished |
| :--- | :--- | :--- | :--- |
| ![](./images/OCLP-GUI-root-patch-update.png) | ![](./images/OCLP-GUI-Root-Patch-Status.png) | ![](./images/OCLP-GUI-Root-Patch.png) | ![](./images/OCLP-GUI-Root-Patch-Finished.png) |

You can install and revert Root Patching manually from the app. 

### Packages requiring networking

**MetallibSupportPkg**

Required for Ivy Bridge, Haswell and NVIDIA Kepler based systems (3802) running Sequoia or newer. You can download it manually from the following link: 

* [MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg/releases)

**Make sure the build matches exactly the OS version you're using.**

::: details Full GPU model list requiring MetallibSupportPkg (click to expand)

* NVIDIA
    * Kepler (GTX 600 - 700 series)
* Intel
   * Ivy Bridge (HD 4000 series)
   * Haswell (Iris/HD 4000-5000 series)
 
:::
 
**KDK / Kernel Debug Kit**

Macs with AMD Legacy GCN GPUs (ie. Metal) running Ventura or newer require Apple's Kernel Debug Kit to start root patching. You can manually download the KDK from the following link:

* [KDKSupportPkg](https://github.com/dortania/KdkSupportPkg/releases)

Grab the Kernel Debug Kit whose version is closest to the OS you installed and install it to the machine.

:::details Macs and GPUs requiring KDK (click to expand)

GPUs:
* Radeon HD 7000 series
* Radeon R9 series
* FirePro D300/D500/D700

Mac models with GCN GPUs:
* iMac 2014 - 2015 (iMac15,1 - 17,1)
* Mac Pro 2013 (MacPro6,1)
* MacBook Pro 2015 15", dGPU version (MacBookPro11,5)

Upgraded Macs:
* Mac Pro 2008 - 2012 (MacPro3,1 - 5,1) if upgraded with AMD GCN GPU.
* iMac 2009 - 2011 (iMac10,1 - 12,1) if upgraded with AMD GCN GPU.

:::

### Other information

Below entries represent GPUs no longer natively supported, ie. requiring root volume patching with OpenCore Legacy Patcher:

:::details GPUs requiring patching in different macOS versions

AMD Navi (RX 5000 - 6000 series) GPUs are non-functional in Mac Pro 2008 to 2012 using Ventura and newer due to lack of AVX2 support.

**Ventura/Sonoma/Sequoia**

* NVIDIA:
  * Tesla (8000 - 300 series)
  * Kepler (600 - 800 series)
* AMD:
  * TeraScale (2000 - 6000 series)
  * GCN 1-3 (7000 - R9 series)
  * Polaris (RX 4xx/5xx series, if CPU lacks AVX2)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)
  * Ivy Bridge (4000 series)
  * Haswell (4400, 4600, 5000 series)
  * Broadwell (6000 series)
  * Skylake (500 series)

**Monterey**

* NVIDIA:
  * Tesla (8000 - 300 series)
  * Kepler (600 - 800 series)
* AMD:
  * TeraScale (2000 - 6000 series)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)
  * Ivy Bridge (4000 series)


**Big Sur**

* NVIDIA:
  * Tesla (8000 - 300 series)
* AMD:
  * TeraScale (2000 - 6000 series)
* Intel:
  * Iron Lake
  * Sandy Bridge (2000 - 3000 series)

:::

:::details Wireless Cards requiring patching in macOS Monterey

* Broadcom:
  * BCM94328
  * BCM94322
* Atheros

:::
