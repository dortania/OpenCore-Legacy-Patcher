# Hardware issues

#### General

* [No Brightness Control](#no-brightness-control)
* [Cannot connect Wi-Fi on Monterey with legacy cards](#cannot-connect-wi-fi-on-monterey-with-legacy-cards)
* [No Graphics Acceleration](#no-graphics-acceleration)
* [No DisplayPort Output on Mac Pros with NVIDIA Kepler](#no-displayport-output-on-mac-pros-with-nvidia-kepler)
* [Secondary CPU not visible on MacPro3,1/Xserve2,1](#secondary-cpu-not-visible-on-macpro3-1-xserve2-1)
* [No acceleration after a Metal GPU swap on Mac Pro](#no-acceleration-after-a-metal-gpu-swap-on-mac-pro)
* [Keyboard, Mouse and Trackpad not working in installer or after update](#keyboard-mouse-and-trackpad-not-working-in-installer-or-after-update)
* [No T1 functionality after installing Sonoma or newer](#no-t1-functionality-after-installing-sonoma-or-newer)

#### Non-Metal

* [Keyboard Backlight broken](#keyboard-backlight-broken)
* [Wake from sleep heavily distorted on AMD/ATI from macOS 11.3 to Monterey](#wake-from-sleep-heavily-distorted-on-ati-amd-terascale-1-from-macos-11-3-to-monterey)
* [Unable to switch GPUs on 2011 15" and 17" MacBook Pros](#unable-to-switch-gpus-on-2011-15-and-17-macbook-pros)
* [Erratic Colours on ATI TeraScale 2 GPUs (HD5000/HD6000)](#erratic-colours-on-ati-terascale-2-gpus-hd5000-hd6000)
* [Cannot Login on 2011 15" and 17" MacBook Pros](#cannot-login-on-2011-15-and-17-macbook-pros)
* [Black Boxes on HD3000 iGPUs](#black-boxes-on-hd3000-igpus)
* [Cannot Pair Bluetooth Devices](#cannot-pair-bluetooth-devices)

For those unfamiliar with what is considered a non-Metal GPU, see the chart in [FAQ](https://dortania.github.io/OpenCore-Legacy-Patcher/FAQ.html#what-is-metal-and-non-metal)

## No Brightness Control

With OCLP v0.0.22, we've added support for brightness control on many models. However, some users may have noticed that their brightness keys do not work.

As a work-around, we recommend users try out the below app:

* [Brightness Slider](https://actproductions.net/free-apps/brightness-slider/)

## Cannot connect Wi-Fi on Monterey with legacy cards

With OCLP v0.2.5, we've added support for legacy Wi-Fi on Monterey. However, some users may have noticed that they can't connect to wireless networks.

To work-around this, we recommend that users manually connect using the "Other" option in the Wi-Fi menu bar or manually adding the network in the "Network" preference pane.

## No Graphics Acceleration

In macOS, GPU drivers are often dropped from the OS with each major release of it. If you're using OCLP v0.4.4 or newer, you should have been prompted to install Root Volume patches after the first boot from installation of macOS. If you need to do this manually, you can do so within the patcher app. Once rebooted, acceleration will be re-enabled as well as brightness control for laptops. 

See [Applying Post Install Volume Patches](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#applying-post-install-volume-patches) for more information. 

If you swapped a GPU from stock to a Metal GPU in a Mac Pro after installing OS, see [No acceleration after a Metal GPU swap on Mac Pro](#no-acceleration-after-a-metal-gpu-swap-on-mac-pro) for instructions.

Check the list below to see what GPUs require patching in which OS versions.

:::details GPUs requiring patching in different macOS versions

AMD Navi (RX 5000 - 6000 series) GPUs are non-functional in Mac Pro 2008 to 2012 using Ventura and newer due to lack of AVX2 support.

**Sequoia**

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

**Sonoma**

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

**Ventura**

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


## No DisplayPort Output on Mac Pros with NVIDIA Kepler

If you're having trouble with DisplayPort output on Mac Pros, try enabling Minimal Spoofing in Settings -> SMBIOS Settings and rebuild/install OpenCore. This will trick macOS drivers into thinking you have a newer MacPro7,1 and resolve the issue.


<div align="left">
             <img src="./images/OCLP-GUI-SMBIOS-Minimal.png" alt="GUI SMBIOS minimal" width="800" />
</div>        


## Intermediate issues with USB 1.1 and Bluetooth on MacPro3,1 - MacPro5,1

For those experiencing issues with USB 1.1 devices (such as mice, keyboards and bluetooth chipsets), macOS Big Sur and newer have weakened OS-side reliability for the UHCI controller in older Mac Pros.

* UHCI is a USB 1.1 controller that is hooked together with the USB 2.0 ports in your system. Whenever a USB 1.1 device is detected, the UHCI controller is given ownership of the device at a hardware/firmware level.
  * EHCI is the USB 2.0 controller in older Mac Pros

Because of this, we recommend placing a USB 2.0/3.0 hub between your devices and the port on the Mac Pro. UHCI and EHCI cannot both be used at once, so using a USB hub will always force the EHCI controller on.

* Alternatively, you can try cold-starting the hardware and see if macOS recognizes the UHCI controller properly.


## Secondary CPU not visible on MacPro3,1/Xserve2,1

Starting with macOS Sequoia, OCLP has to disable the secondary CPU in these systems to avoid a panic. This also means by default, only single CPU will be usable even on older versions. To re-enable both CPUs on older versions, do the following: 

1. Open Settings -> `Build` tab.
2. Untick `MacPro3,1/Xserve2,1 Workaround`.
3. Rebuild OpenCore.
4. Reboot.

**Dual CPUs cannot be enabled in any circumstance if Sequoia or newer is installed, even in multiboot scenarios. Doing so will make Sequoia unbootable.**

[More information here](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1136#:~:text=we%20cannot%20verify.-,MacPro3%2C1%20Dual%20Socket%20Support,-Currently%20on%20macOS)

## No acceleration after a Metal GPU swap on Mac Pro

If you finished installing macOS with the original card installed (to see bootpicker for example) and swapped your GPU to a Metal supported one, you may notice that you're missing acceleration. 

To fix this, open OCLP and revert root patches to get your Metal-supported GPU work again. In macOS Ventura and newer, repatching is needed for most configurations after reversion. Reason why this happens is automatic root patching during USB install and the autopatcher assuming you will be using the original graphics card and therefore doing non-Metal patching. **Metal and non-Metal GPUs cannot be used at the same time** as Non-Metal patching completely bypasses Metal and requires removing some parts such as drivers for other cards, which causes Metal cards to not accelerate after swapping. 

Alternatively, you can remove "AutoPkg-Assets.pkg" from /Library/Packages on the USB drive before proceeding with the installation. This package includes the assets for root patching and the system won't be autopatched if they aren't present. To see the folder, enable hidden files with `Command` + `Shift` + `.`

## Keyboard, Mouse and Trackpad not working in installer or after update

Starting from macOS Ventura, USB 1.1 drivers are no longer provided in the operating system. For Macs using legacy USB 1.1 controllers, OpenCore Legacy Patcher can only restore support once it has performed root volume patches which restore the drivers. Thus when installing macOS or after an update, you need to hook up a USB hub between your Mac and keyboard/mouse, forcing USB 2.0 mode in order to install the root patches.

* For MacBook users, you'll need to find an external keyboard/mouse in addition to the USB hub

Applicable models include:

| Family      | Year                 | Model                         | Notes                                            |
| :---------- | :--------------------| :---------------------------- | :----------------------------------------------- |
| MacBook     | Mid 2010 and older   | MacBook5,1 - MacBook7,1       |                                                  |
| MacBook Air | Late 2010 and older  | MacBookAir2,1 - MacBookAir3,x |                                                  |
| MacBook Pro | Mid 2010 and older   | MacBookPro4,1 - MacBookPro7,x | Excludes Mid 2010 15" and 17" (MacBookPro6,x)    |
| iMac        | Late 2009 and older  | iMac7,1 - iMac10,x            | Excludes Core i5/7 27" late 2009 iMac (iMac11,1) |
| Mac mini    | Mid 2011 and older   | Macmini3,1 - Macmini5,x       |                                                  |
| Mac Pro     | Mid 2010 and older   | MacPro3,1 - MacPro5,1         |                                                  |


<div align="left">
             <img src="./images/usb11-chart.png" alt="USB1.1 chart" width="800" />
</div>

::: warning Note

In macOS Sonoma, this seems to have been further weakened and some hubs may not be functional. If you encounter this issue, try another hub.

:::

### Alternative method for Software Update

Alternative way for updates is making sure to enable "Remote Login" in General -> Sharing before updating, which will enable SSH. That means you can take control using Terminal in another system and run Post Install Volume Patching. 

**This only applies to updates via Software Update and is not applicable when booting to installer via USB drive.**

Use the following commands:

1. `ssh username@lan-ip-address` - Connects via SSH, change username and IP address to the system's
2. `/Applications/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher --patch_sys_vol` - Installs root patches via CLI
3. `sudo reboot`.

More information can be found here:

* [Legacy UHCI/OHCI support in Ventura #1021](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021)


## No T1 functionality after installing Sonoma or newer

If you notice your Touchbar etc not working, this means loss of T1 functionality. 

Wiping the entire disk using Disk Utility with Sonoma or newer causes the T1 firmware to be removed, which due to removed support, the macOS Sonoma+ installer will not restore. If the firmware is missing from EFI, T1 will not work regardless whether OCLP reinstates the driver during root patching. To restore T1 functionality, Ventura or older has to be reinstalled. This can be done in another volume or external disk as well, as long as the OS is booted once. After this you can wipe the old OS or unplug the external disk.


To prevent this from happening in the future, with T1 systems only wipe the volume containing the operating system.

<div align="left">
             <img src="./images/wipe-volume.png" alt="WipeVolume" width="800" />
</div>




## Keyboard Backlight broken

Due to forcing `hidd` into spinning up with the fallback mode enabled, this can break the OS's recognition of backlight keyboards. Thankfully the drivers themselves still do operate so applications such as [LabTick](https://www.macupdate.com/app/mac/22151/lab-tick) are able to set the brightness manually.

::: details For Big Sur (click to expand)

Due to the Metal Backend, the enhanced color output of these apps seems to heavily break overall UI usage. To work around this, [users reported](https://forums.macrumors.com/threads/macos-11-big-sur-on-unsupported-macs-thread.2242172/post-29870324) forcing the color output of their monitor from Billions to Millions of colors helped greatly. Apps easily allowing this customization are [SwitchResX](https://www.madrau.com), [ResXreme](https://macdownload.informer.com/resxtreme/) and [EasyRes](http://easyresapp.com).

:::

## Wake from sleep heavily distorted on ATI/AMD TeraScale 1 from macOS 11.3 to Monterey

**Fixed for macOS Ventura starting from 0.6.6. Big Sur and Monterey will continue to exhibit the issue.**

This issue affects TeraScale 1 GPUs (ie. ATI/AMD Radeon HD2000-4000). Only known solution is to downgrade to macOS 11.2.3 or older. Additionally, logging out and logging back in can resolve the issue without requiring a reboot.

In the event Apple removes 11.2.3 from their catalogue, we've provided a mirror below:

* [Install macOS 11.2.3 20D91](https://archive.org/details/install-mac-os-11.2.3-20-d-91)

## Unable to switch GPUs on 2011 15" and 17" MacBook Pros

Currently, with OpenCore Legacy Patcher, GPU switching between the iGPU and dGPU is broken. The simplest way to set a specific GPU is to disable the dGPU when you wish to remain on the more power efficient iGPU.

The best way to achieve this is to boot to Recovery (or Single User Mode if the dGPU refuses to function at all) and run the following command:

```sh
nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%01%00%00%00
```

This will disable the dGPU and allow the iGPU to function in Big Sur. Note that external display outputs are directly routed to the dGPU and therefore can no longer be used. Solutions such as [DisplayLink Adapters](https://www.displaylink.com/products/usb-adapters) can work around this limitation, however, note that you'll need to use older drivers (5.2.6):

* [DisplayLink USB Graphics Software for macOS - For Mojave and Catalina - 5.2.6](https://www.synaptics.com/products/displaylink-graphics/downloads/macos-5.2.6)

Note: This driver only provides partial support in macOS, full graphics acceleration is not currently available on displays driven by DisplayLink.


## Erratic Colours on ATI TeraScale 2 GPUs (HD5000/HD6000)

Resolved with OpenCore Legacy Patcher v0.4.2

::: details Legacy Fix (prior to 0.4.2)

Due to an odd bug with ATI's TeraScale 2 GPUs, many users will experience erratic/strobing colours once finished installing accelerated patches and rebooting into macOS. The issue stems from an incorrect assumption in the GPU drivers where it will enforce the Billion Colour space on your display. To fix, simply force your Display into a lower color depth such as Million Colours.

Applications that can set color depth are:

* [SwitchResX](https://www.madrau.com)
* [ResXtreme](https://macdownload.informer.com/resxtreme/)

:::

## Cannot Login on 2011 15" and 17" MacBook Pros

By default, OpenCore Legacy Patcher will assume MacBookPro8,2/3 have a faulty dGPU and disable acceleration. This is the safest option for most users as enabling dGPU acceleration on faulty Macs will result in failed booting.

However, if your machine does not have the dGPU disabled via NVRAM, you'll experience a login loop. To work around this is quite simple:

1. Boot macOS in Single User Mode
    * Press Cmd+S in OpenCore's menu when you turn the Mac on
2. When the command line prompt appears, enter the dGPU disabler argument (at the bottom)
3. Reboot and patched macOS should work normally
4. If you still want to use the dGPU, run OpenCore Legacy Patcher and enable TS2 Acceleration from settings. Go to `Patcher Settings -> Developer Settings -> Set TeraScale 2 Accel`, then root patch again.
5. Either Reset NVRAM or set `gpu-power-prefs` to zeros to re-enable the dGPU

```sh
# Forces GMUX to use iGPU only (ie. disable dGPU)
nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%01%00%00%00
# To reset, simply write zeros or NVRAM Reset your Mac
nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%00%00%00%00
```

## Black Boxes on HD3000 iGPUs

A somewhat strange issue on Intel HD3000-based Macs, on 3rd party displays sometimes UI elements may become black and unreadable. To resolve, select either the generic `Display` or `Display P3` Color Profiles in Display Settings.

* Mainly applicable for HDMI Displays, DVI and DisplayPort are generally unaffected.
* If you're inside Setup Assistant, press `Cmd` + `Option` + `Control` + `T` to launch Terminal. From there, run `open /System/Applications/System\ Preferences.app`
* Issue has spread to more Macs with macOS Ventura, including MacBook Airs and MacBook Pros

| Default Color Profile | Display/Display P3 Profile |
| :---                  | :---                       |
| ![](./images/HD3000-Default-Colors.png) | ![](./images/HD3000-Display-Colors.png) |

## Cannot Pair Bluetooth Devices

In macOS Ventura, hover states may not function correctly which results in the "Connect" button not appearing in System Settings. To resolve:

1. Enable Keyboard Navigation in System Settings -> Keyboard
2. Tab + space over Bluetooth devices in System Settings -> Bluetooth
3. Pair button should appear


For more information, see [ASentientBot's post](https://forums.macrumors.com/threads/macos-13-ventura-on-unsupported-macs-thread.2346881/page-116?post=31858759#post-31858759).







