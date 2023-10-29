# Uninstalling OpenCore

## Uninstalling the bootloader

1. Remove OpenCore either from the USB or internal drive

  * You'll need to mount the drive's EFI partition, and delete the `EFI/OC` and `System` folders
    * Note: **Do not** delete the entire EFI folder, this will likely break any existing Windows and Linux installations.
    * [See here for an example on how to mount](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html)
    * For 5K iMac users, you will also need to delete `boot.efi` on the root of the EFI partition.

2. [Reset NVRAM](https://support.apple.com/HT204063)

:::warning

Note that after you remove OpenCore, your Mac will no longer boot and show the "prohibited" symbol. Be ready to install an natively-supported version of macOS before you uninstall OpenCore.

* This does not apply to native Macs just using OpenCore to achieve features like AirPlay to Mac and Sidecar, but it is still recommended to reinstall macOS after removing OpenCore, if using SMBIOS spoofing to enable Univeral Control.
:::

## Uninstalling the application

If you want to remove the application without reinstalling the OS, navigate to `/Library/Application Support/` and delete the Dortania folder.
