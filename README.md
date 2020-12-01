# OpenCore Legacy Patcher

A python script for building and booting OpenCore on legacy Macs, see [Supported SMBIOS](#supported-smbios) on whether your model is supported.

Current TO-DO's with this patcher:

* [ ] Create macOS Installer
* [ ] Legacy GPU Patches
  * ie. 2011 and older
* [ ] Legacy Audio Patches
  * ie. 2011 and older

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
  * Blank USB drives formatted as GUID Partition Table are also supported

1. [Download the release](https://github.com/dortania/Opencore-Legacy-Patcher/releases)
2. Run the `OpenCore-Patcher.command` file
3. Once opened, select option 1 and build your EFI
  * if poatching for a different patching, selectect option 3 first
4. Once finished, run option 2 a the main menu and install onto your desired drive

Once you're done making your OpenCore installer, you can simply reboot holding the Option key. In the picker, you should see a new EFI Boot Option. Boot it and from there you'll be in the OpenCore picker.