# Background process

OpenCore Legacy Patcher utilizes a background process to:
- Check for mismatched configurations and warn the user (e.g. installed MacBookPro11,1 config on MacBookPro11,5)
- Monitor the status of installed Root Patches and OpenCore
- Ask you to install Root Patches in case they aren't detected (typically after an update)
- Check whether OpenCore is being booted from USB drive or internal drive
- Ask you to install OpenCore on the internal disk in case booted from USB
- React to upcoming updates requiring a new KDK to be downloaded, starting KDK download automatically

It is recommended to keep the background process enabled for smoothest functionality. e.g. to try and avoid failed patching when new KDK is not found.

If you decide to disable the background process, the KDK installation for each update has to be done manually. OCLP is also unable to detect Root Patches on boot, meaning manually opening the app and root patching is required.

::: warning  Note:

In some cases macOS may report background process being added by "Mykola Grymalyuk", this happens due to a macOS bug where sometimes the developer name who sent the app for notarization is shown instead of the application name.
Dortania cannot do anything about this.
:::
