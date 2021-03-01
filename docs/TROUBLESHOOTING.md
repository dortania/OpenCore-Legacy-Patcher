# Troubleshooting

Here are some common errors users may experience while using this patcher:

* [Stuck on `This version of Mac OS X is not supported on this platform`](#stuck-on-this-version-of-mac-os-x-is-not-supported-on-this-platform)
* [Cannot boot macOS without the USB](#cannot-boot-macos-without-the-usb)
* [Infinite Recovery OS Booting](#infinite-recovery-os-reboot)

## Stuck on `This version of Mac OS X is not supported on this platform`

This means macOS has detected a SMBIOS it does not support, to resolve this ensure you're booting OpenCore **before** the macOS installer in the boot picker. Reminder the option will be called `EFI Boot`

Once you've booted OpenCore at least once, your hardware should now auto boot it until either NVRAM reset or you remove the drive with OpenCore installed.

## Cannot boot macOS without the USB

At this time, the OpenCore Patcher won't install macOS onto the internal drive itself during installs. Instead, you'll need to either [manually transfer](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html) OpenCore to the internal drive's EFI or run this patcher's Option 2 again but select your internal drive.

Reminder that once this is done, you'll need to select OpenCore in the boot picker again for your hardware to remember this entry and auto boot from then on.

## Infinite Recovery OS Booting

With OpenCore Legacy Patcher, we rely on Apple Secure Boot to ensure OS updates work correctly and reliably with Big Sur. However this installs NVRAM variables that will confuse your Mac if not running with openCore. To resolve, simply uninstall OpenCore and [reset NVRAM](https://support.apple.com/en-mide/HT201255).