# Download and build macOS Installers

This doc is centered around downloading and writing the macOS installer to a USB. If you're already familiar with how to do this, you can skip.

* Note: 16GB+ USB will be required for the installer

## Creating the installer

With OpenCore Legacy Patcher, our new GUI includes a download menu for macOS installers. So to start off, you'll want to grab our app:

* [OpenCore Legacy Patcher Release Apps](https://github.com/dortania/OpenCore-Legacy-Patcher/releases)

For this guide, we'll be using the standard OpenCore-Patcher (GUI).

Once downloaded, open the app and you should be greeted with this menu:

![OCLP GUI Main Menu](../images/OCLP-GUI-Main-Menu.png)

First we'll want to select the "Create macOS Installer" button. This will present you with 2 options:

![](../images/OCLP-GUI-Create-Installer-Menu.png)

For this example, we'll assume you'll need an installer. Selecting this option will download Apple's Installer Catalogs and build a list for you to choose:

| Downloading | Listed Installers | Unsupported Installer |
| :--- | :--- | :--- |
| ![OCLP GUI Installer Download Catalog](../images/OCLP-GUI-Installer-Download-Catalog.png) | ![OCLP GUI Installer Download Listed Products](../images/OCLP-GUI-Installer-Download-Listed-Products.png) | ![](../images/OCLP-GUI-Installer-Download-Unsupported.png)

Since the patcher officially supports Big Sur and newer for patching, only those entires will be shown. For ourselves, we'll select macOS 12 as that's the latest public release at the time of writing. This will download and install the macOS installer to your applications folder.

* Note that some machines (namely 2012 and older) may not be currently supported on macOS Ventura. If you see this prompt, you'll need to use an older version of macOS.

| Downloading the Installer | Requesting to install | Finished Installing |
| :--- | :--- | :--- |
| ![OCLP GUI Installer Download Progress](../images/OCLP-GUI-Installer-Download-Progress.png) | ![OCLP GUI Installer Needs Installing](../images/OCLP-GUI-Installer-Needs-Installing.png) | ![OCLP GUI Installer Download Finished](../images/OCLP-GUI-Installer-Download-Finished.png) |

Once finished, you can proceed to write the installer onto a USB drive.

* Note: The entire USB drive will be formatted

| Select Downloaded Installer | Select disk to format |
| :--- | :--- |
| ![](../images/OCLP-GUI-Installer-Select-Local-Installer.png) | ![](../images/OCLP-GUI-Installer-Format-USB.png) |

Now the patcher will start the installer flashing!

| Flashing | Success Prompt | Finished Flashing |
| :--- | :--- |
| ![](../images/OCLP-GUI-Installer-Flashing-Process.png) | ![](../images/OCLP-GUI-Installer-Sucess-Prompt.png) | ![](../images/OCLP-GUI-Installer-Finished-Script.png) |

# Once finished, head to [Building and installing OpenCore](./BUILD.md)
