# Download and build macOS Installers

This document is centered around downloading and writing the macOS installer to a USB drive. If you're already familiar with how to do this, you can skip this section.

* Note: A 32GB drive is recommended, later versions of Sonoma and Sequoia cannot fit installer and patches to a 16GB disk. 16GB drive may work for older versions.

## Creating the installer

With OpenCore Legacy Patcher, our new GUI includes a download menu for macOS installers. So to start off, you'll want to grab our app:

* [OpenCore Legacy Patcher Release Apps](https://github.com/dortania/OpenCore-Legacy-Patcher/releases)

Once downloaded, open the app and you should be greeted by the main menu. 

First, we'll want to select the "Create macOS Installer" button. This will present you with 2 options.

For this example, we'll assume you'll need an installer. Select the "Download macOS installer" to get you a list of installers

| Main menu | Installer creation menu |
| :--- | :--- |
| ![OCLP GUI Installer Download Progress](./images/OCLP-GUI-Main-Menu.png) | ![OCLP GUI Installer Download Finished](./images/OCLP-GUI-Create-Installer-Menu.png) |

Available installers will be listed as follows, click to download the version you want.
<div align="center">
             <img src="./images/OCLP-GUI-Installer-Download-Listed-Products.png" alt="ListedInstallers" width="400" />
</div>  

Once the download is finished, you can proceed to write the installer onto a USB drive.

* Note: The entire USB drive will be formatted

| Select Downloaded Installer | Select disk to format |
| :--- | :--- |
| ![](./images/OCLP-GUI-Installer-Select-Local-Installer.png) | ![](./images/OCLP-GUI-Installer-Format-USB.png) |

Now the patcher will start the installer flashing!

| Flashing | Success Prompt | Finished Flashing |
| :--- | :--- | :--- |
| ![](./images/OCLP-GUI-Installer-Flashing-Process.png) | ![](./images/OCLP-GUI-Installer-Sucess-Prompt.png) | ![](./images/OCLP-GUI-Installer-Finished-Script.png) |

# Once finished, head to [Building and installing OpenCore](./BUILD.md)
