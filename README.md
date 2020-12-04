# OpenCore Legacy Patcher

<img src="OC-Patcher.png" width="256">

A python script for building and booting OpenCore on legacy Macs, see [Supported SMBIOS](#supported-smbios) on whether your model is supported.

See [here](https://github.com/dortania/Opencore-Legacy-Patcher/issues/1) for current TO-DOs on this patcher.

## Supported SMBIOS

Any hardware supporting SSE4.1 CPU and 64-Bit firmware work on this patcher. To check your hardware model, run the below command on the applicable machine:

```bash
system_profiler SPHardwareDataType | grep 'Model Identifier'
```

<details>
<summary>SMBIOS Support Table</summary>

```
MacBook5,1
MacBook5,2
MacBook6,1
MacBook7,1

MacBookAir2,1
MacBookAir3,1
MacBookAir3,2
MacBookAir4,1
MacBookAir4,2
MacBookAir5,1
MacBookAir5,2

MacBookPro3,1
MacBookPro4,1
MacBookPro5,1
MacBookPro5,2
MacBookPro5,3
MacBookPro5,4
MacBookPro5,5
MacBookPro6,1
MacBookPro6,2
MacBookPro7,1
MacBookPro8,1
MacBookPro8,2
MacBookPro8,3
MacBookPro9,1
MacBookPro9,2
MacBookPro10,1
MacBookPro10,2

Macmini3,1
Macmini4,1
Macmini5,1
Macmini5,2
Macmini5,3
Macmini6,1
Macmini6,2

iMac7,1
iMac8,1
iMac9,1
iMac10,1
iMac11,1
iMac11,2
iMac11,3
iMac12,1
iMac12,2
iMac13,1
iMac13,2
iMac14,1
iMac14,2
iMac14,3

MacPro3,1
MacPro4,1
MacPro5,1

Xserve3,1
```

</details>
<br>

## How to run

Prerequists:

* Supported Mac(see above)
* macOS Installer installed to USB
  * See here on how to download and create an installer: [Creating a macOS Installer](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/mac-install.html)
  * Blank USB drives formatted as GUID Partition Table are also supported

1. [Download the release](https://github.com/dortania/Opencore-Legacy-Patcher/releases)
2. Run the `OpenCore-Patcher.command` file
3. Once opened, select option 1 and build your EFI
  * if patching for a different patching, select option 3 first
4. Once finished, run option 2 a the main menu and install onto your desired drive

Once you're done making your OpenCore installer, you can simply reboot holding the Option key. In the picker, you should see a new EFI Boot Option. Boot it and from there you'll be in the OpenCore picker.

## How to uninstall OpenCore?

To remve OpenCore is actually quite simply:

1. Remove OpenCore either from the USB or internal drive
  * You'll need to mount the drive's EFI partition, and delete the EFI folder
  * [See here for example how to mount](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html)
2. Reset NVRAM
  * [Reset NVRAM or PRAM on your Mac](https://support.apple.com/HT204063)

## Troubleshooting

Here are some common errors users may experience while using this patcher:

* [Stuck on `This version of Mac OS X is not supported on this platform`](#stuck-on-this-version-of-mac-os-x-is-not-supported-on-this-platform)
* [Cannot boot macOS without the USB](#cannot-boot-macos-without-the-usb)

### Stuck on `This version of Mac OS X is not supported on this platform`

This means macOS has detected a SMBIOS it does not support, to resolve this ensure you're booting OpenCore **before** the macOS installer in the boot picker. Reminder the option will be called `EFI Boot`

Once you've booted OpenCore at least once, your hardware should now auto boot it until either NVRAM reset or you remove the drive with OpenCore installed.

### Cannot boot macOS without the USB

At this time, the OpenCore Patcher won't install macOS onto the internal drive itself during installs. Instead, you'll need to either [manually transfer](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html) OpenCore to the internal drive's EFI or run this patcher's Option 2 again but select your internal drive.

Reminder that once this is done, you'll need to select OpenCore in the boot picker again for your hardware to remenber this entry and auto boot from then on.

