# Uninstalling OpenCore

To remove OpenCore is actually quite simply:

1. Remove OpenCore either from the USB or internal drive

* You'll need to mount the drive's EFI partition, and delete the `EFI/OC` and `System` folders
  * Note **do not** delete the entire EFI folder, this will likely break any existing Windows and Linux installations
  * [See here for an example on how to mount](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html)

2. [Reset NVRAM](https://support.apple.com/HT204063)

Know that if you are on Big Sur when you remove the EFI folder, your Mac will no longer boot and show the prohibited symbol. Be ready to install an older version of macOS before you uninstall OpenCore.
