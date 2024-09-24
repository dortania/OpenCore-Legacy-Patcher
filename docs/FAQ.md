# FAQ

* [Why are the settings not "saving"?](#why-are-the-settings-not-saving)
* [Can I use OTA updates?](#can-i-use-ota-updates)
* [Can I update to macOS betas?](#can-i-update-to-macos-betas)
* [Why can't I connect to iPhone Mirroring?](#why-cant-i-connect-to-iphone-mirroring)
* [Why is Apple Intelligence not working?](#why-is-apple-intelligence-not-working)


## Why are the settings not "saving"?

OpenCore Legacy Patcher is a config build tool and as such the user interface always reverts to safe defaults, the user interface therefore **does not** reflect the status of settings. 

Settings are saved to a config.plist file inside your EFI partition when building OpenCore. You will always have to build OpenCore again after settings change.

## Can I use OTA updates?

You can. However it is extremely recommended to use USB drive for major OS upgrades (such as 13 -> 14) to avoid larger issues from potentially occurring.

General updates are usually fine, though it is always a good idea to wait few days to see whether patches break and have to be fixed.

## Can I update to macOS betas?

If you are feeling brave and don't mind having to possibly recover your system. However, be advised that no help will be given in situations where a beta was installed.

## Why can't I connect to iPhone Mirroring?

iPhone Mirroring requires a T2 chip, which means it will not be available on OCLP patched systems.

## Why is Apple Intelligence not working?

Apple Intelligence requires Neural Engine, which is only found in Apple Silicon chips.
