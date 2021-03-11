# Building and installing OpenCore

Now that we have a macOS installer, lets now build our OpenCore configuration!

First Download the latest release: 

* [OpenCore Legacy Patcher Releases](https://github.com/dortania/Opencore-Legacy-Patcher/releases)

Next, run the `OpenCore-Patcher.app`:

![](../images/first-run.png)

From here you have a couple important options:

* Build OpenCore
* Install OpenCore to USB/internal drive
* Change Model
* Patcher Settings 

If you're patching for a different machine than you're running, please select "Change Model" and enter the updated SMBIOS. For more advanced users, you may also tweak the patcher's build settings via "Patcher Settings"

Now lets enter "Build OpenCore":

![](../images/build-efi.png)

The process should be quite quick to build, once finished you'll be plopped back to the main menu.

Next lets run `Install OpenCore to USB/internal drive`:

| Select Drive | Select EFI/FAT32 Partition |
| :--- | :--- |
| ![](../images/disk-start.png) | ![](../images/disk-efi.png) |

  * If you have issues, please ensure you install OpenCore onto a FAT32 partition to ensure your Mac is able to boot it. You will need to format your drive as GUID/GPT in Disk Utility
  

# Once finished, head to [Booting OpenCore and macOS](./BOOT.md)