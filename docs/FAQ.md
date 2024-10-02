# FAQ


* [Application requirements](#application-requirements)
* [How do I make sure I'm all up to date?](#how-do-i-make-sure-i-m-all-up-to-date)
* [Why are the settings "not saving"?](#why-are-the-settings-not-saving)
* [Can I use the same USB install media as a universal installer?](#can-i-use-the-same-usb-install-media-as-a-universal-installer)
* [Can I use OTA updates?](#can-i-use-ota-updates)
* [Can I update to macOS betas?](#can-i-update-to-macos-betas)
* [Can I use automatic updates?](#can-i-use-automatic-updates)
* [Why is my system slow?](#why-is-my-system-slow)
* [Crashing in random places](#crashing-in-random-places)
* [Why isn't iPhone Mirroring working?](#why-isn-t-iphone-mirroring-working)
* [Where is Apple Intelligence?](#where-is-apple-intelligence)



## Application requirements
The patcher application requires **OS X Yosemite 10.10** or later to run.
* **OS X El Capitan 10.11** or later is required to make installers for macOS Ventura and later.

The patcher is designed to target **macOS Big Sur 11.x to macOS Sequoia 15.x**.
* Other versions may work, albeit in a broken state. No support is provided for any version outside of the above.

## How do I make sure I'm all up to date?

Updating the OCLP installation is a three step process, first the application, second the bootloader and finally root patches.

Refer to [Updating OpenCore and patches](https://dortania.github.io/OpenCore-Legacy-Patcher/UPDATE.html) for how to update the application and patches.

## Why are the settings "not saving"?

OpenCore Legacy Patcher is a config build tool and as such the user interface always reverts to safe defaults, the user interface therefore **does not** reflect the status of settings. Settings are accounted for and saved by the OpenCore building process and you will always have to build OpenCore again after settings change. 

Settings are saved to a config.plist file inside your EFI partition.

In SIP settings, booted SIP is reported in text form e.g. "0x803" but the checkboxes **do not** reflect the applied settings. Refer to [SIP Settings](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#sip-settings) for more information.

## Can I use the same USB install media as a universal installer?

OpenCore configurations are device specific, due to different quirks needed for different systems. If you are building OpenCore for a different system that you're running, you will have to select the targeted model from Settings before building OpenCore on the USB media.

When building OpenCore on a different system, OCLP cannot be aware of all the hardware installed in the target, meaning safe defaults will be used. However, this may not be the most optimal experience especially with custom hardware. As such it's recommended to rebuild OpenCore **on device** to apply settings that are based on hardware detection, after the OS has been installed.

## Can I use OTA updates?

You can. However it is extremely recommended to use USB drive for major OS upgrades (such as 13 -> 14) to avoid larger issues from potentially occurring.

General updates are usually fine, though it is always a good idea to wait few days to see whether patches break and have to be fixed.

## Can I update to macOS betas?

If you are feeling brave and don't mind having to possibly recover your system. However, be advised that no help will be given in situations where a beta was installed.

## Can I use automatic updates?

It is extremely recommended to disable automatic updates (even downloading) when using OCLP, as Apple has recently changed the way automatic updates work. You can still manually initiate an update when you're ready to do so.

For a related "System version mismatch" error while root patching, refer to [System version mismatch error when root patching](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html#system-version-mismatch-error-when-root-patching) for troubleshooting.

## Why is my system slow?

This can mean many things. Firstly, newer operating systems are harder to run and can appear more slow.

However, if your system is being **really** slow and you have no transparency in Dock and menubar, this typically indicates that root patches are not installed and as such there is no acceleration. Make sure to install root patches to get proper drivers and functionality. Refer to [Applying post install volume patches](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#applying-post-install-volume-patches) and the [Troubleshooting](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html) section for more information.

Patches can also break if automatic updates are enabled and an update modifies the system volume, refer to [System version mismatch error when root patching](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html#system-version-mismatch-error-when-root-patching) for more information.

## Crashing in random places

There are two rather common things that can cause weird crashing. First is a process called "mediaanalysisd" on 3802-based systems* and secondly FeatureUnlock. You can try disabling these settings in OCLP to try and gain higher stability. As always, install a new OpenCore build after selecting the settings and restart.

Be advised that by disabling FeatureUnlock, you will lose some macOS functionality. The features enabled by FeatureUnlock are listed [here](https://github.com/acidanthera/FeatureUnlock).

| FeatureUnlock | mediaanalysisd |
| :--- | :--- |
| ![FeatureUnlock](./images/OCLP_FeatureUnlock_Setting.png) | ![mediaanalysisd](./images/OCLP_Disable_mediaanalysisd_Setting.png) |

*3802 systems include:
* NVIDIA
    * Kepler (600-800 series GPUs)
* Intel
    * Ivy Bridge (3rd generation, HD 4000 series GPUs)
    * Haswell (4th generation, HD/Iris 4000-5000 series GPUs)

These GPUs are typically met in systems from 2012-2015.


## Why isn't iPhone Mirroring working?

iPhone Mirroring requires a T2 chip, which means it will not be available on OCLP patched systems. The connection fails due to failure to establish T2 attestation.

## Where is Apple Intelligence?

Apple Intelligence requires Neural Engine, which is only found in Apple Silicon chips.

