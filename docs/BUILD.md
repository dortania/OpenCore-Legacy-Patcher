# Building and installing OpenCore

Now that we have a macOS installer, let's now build our OpenCore configuration!

If you haven't downloaded OpenCore Patcher yet, do so now:

* [OpenCore Legacy Patcher Releases](https://github.com/dortania/Opencore-Legacy-Patcher/releases)

Next, run the `OpenCore-Patcher.app`

Here we'll select Build and Install OpenCore and start building:


<div align="left">
             <img src="./images/OCLP-GUI-Main-Menu.png" alt="OCLP GUI Main Menu" width="700" />
</div>

::: warning
OpenCore configurations are hardware specific.
If you're building OpenCore for a different model than you're currently running, it is absolutely necessary to select the proper model from Settings.
:::


| Start Building | Finished Building |
| :--- | :--- |
| <img src="./images/OCLP-GUI-Build-Start.png" alt="Build start" width="600" /> | <img src="./images/OCLP-GUI-Build-Finished.png" alt="Build finished" width="600" /> |


Once it finishes building, you'll want to select the Install OpenCore button:

* If you created a macOS USB manually and don't see it listed, make sure it's either formatted as GUID/GPT or has a FAT32 partition for OpenCore to reside on.


| Select Drive | Select Partition |
| :--- | :--- |
| <img src="./images/OCLP-GUI-EFI-Select-Disk.png" alt="Select disk" width="600" /> | <img src="./images/OCLP-GUI-EFI-Select-Partition.png" alt="Select partition" width="600" /> |



# Once finished, head to [Booting OpenCore and macOS](./BOOT.md)
