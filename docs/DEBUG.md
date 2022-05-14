# How to debug with OpenCore

For those who've hit an odd bug and unsure if it's user error or patcher, we recommend asking on the [OpenCore Patcher Paradise Discord Server](https://discord.gg/rqdPgH8xSN) for help.

## Debugging yourself

The easiest way to debug yourself is via Patcher Settings. Here there are many different settings however the 3 main options that will help are:

* "Enable Verbose Mode"
* "Enable OpenCore DEBUG"
* "Enable Kext DEBUG"

When you've enabled these 3 options, rebuild OpenCore and install to your drive. This will provide much greater debug information as well as write logs to the EFI Partition.

## Obtaining OpenCore logs from disk

With "Enable OpenCore DEBUG" set, every boot there will be a .txt file generated in your disk. To grab these logs, [download and run MountEFI](https://github.com/corpnewt/MountEFI):

![](../images/mountefi.png)

Once you've mounted the EFI Partition of the drive you have macOS on, you should see some nice logs:

![](../images/logs-efi.png)

## Obtaining Kernel logs from macOS

With "Enable Kext DEBUG" set, every boot will now have much more detailed logs stored in the OS. To get these logs, simply run the below command:

```sh
sudo dmesg > ~/Desktop/DMESG.txt
```

From there, you'll have a log on your desktop.

## Filing an issue with us

::: warning
Currently issues have been disabled due to [current events](ISSUES-HOLD.md). You can continue to receive support in the [OpenCore Patcher Paradise Discord Server](https://discord.gg/rqdPgH8xSN), where there are active members of the community available.
:::

Now that you have proper logs, you can now [file issues with us](https://github.com/dortania/OpenCore-Legacy-Patcher/issues). Reminder we want the following info:

* Model patching for (ie. MacBookPro10,1)
* Target OS (ie. macOS 11.2.3)
* Host OS (ie. macOS 10.15.7)
* Upload of your OpenCore Build Folder
* Upload of your OpenCore log (if applicable)
* Upload of your Kernel log (if applicable)

Additionally, please search whether the issue has been reported before. This avoids having duplicate issues.
