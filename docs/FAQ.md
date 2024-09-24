# FAQ

* [Why are the settings not "saving"?](#why-are-the-settings-not-saving)
* [Can I use OTA updates?](#can-i-use-ota-updates)
* [Can I update to macOS betas?](#can-i-update-to-macos-betas)
* [Can I use automatic updates?](#can-i-use-automatic-updates)
* [Why is my system slow?](#why-is-my-system-slow)
* [Crashing in random places](#crashing-in-random-places)
* [Why can't I connect to iPhone Mirroring?](#iphone-mirroring)
* [Why is Apple Intelligence not working?](#apple-intelligence)


## Why are the settings not "saving"?

OpenCore Legacy Patcher is a config build tool and as such the user interface always reverts to safe defaults, the user interface therefore **does not** reflect the status of settings. 

Settings are saved to a config.plist file inside your EFI partition when building OpenCore. You will always have to build OpenCore again after settings change.

## Can I use OTA updates?

You can. However it is extremely recommended to use USB drive for major OS upgrades (such as 13 -> 14) to avoid larger issues from potentially occurring.

General updates are usually fine, though it is always a good idea to wait few days to see whether patches break and have to be fixed.

## Can I update to macOS betas?

If you are feeling brave and don't mind having to possibly recover your system. However, be advised that no help will be given in situations where a beta was installed.

## Can I use automatic updates?

It is extremely recommended to disable automatic updates (even downloading) when using OCLP, as Apple has recently changed the way automatic updates work.

For a related "System version mismatch" error while root patching, refer to [this troubleshooting section](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html#system-version-mismatch-error-when-root-patching.

## Why is my system slow?

This can mean many things. Firstly, newer operating systems are harder to run and can appear more slow.

However, if your system is being **really** slow and you have no transparency in Dock and menubar, this typically indicates that root patches are not installed and as such there is no acceleration. Make sure to install root patches to get proper drivers and functionality. Refer to [Applying post install volume patches](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#applying-post-install-volume-patches) and the [Troubleshooting](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html) section for more information.

Patches can also break if automatic updates are enabled and an update modifies the system volume, refer to [Can I use automatic updates?](#can-i-use-automatic-updates) for more information.

## Crashing in random places

There are two rather common things that can cause weird crashing. First is a process called "mediaanalysisd" on 3802-based systems* and secondly FeatureUnlock. You can try disabling these settings in OCLP to try and gain higher stability.

Be advised that by disabling FeatureUnlock, you will lose some macOS functionality. The features enabled by FeatureUnlock are listed [here](https://github.com/acidanthera/FeatureUnlock).

*3802 systems include:
* NVIDIA
    * Kepler (600-800 series GPUs)
* Intel
    * Ivy Bridge (3rd generation, HD 4000 series GPUs)
    * Haswell (4th generation, HD/Iris 4000-5000 series GPUs)

These GPUs are typically met in systems from 2012-2015.



## Unsupported features

### iPhone Mirroring

iPhone Mirroring requires a T2 chip, which means it will not be available on OCLP patched systems.

### Apple Intelligence

Apple Intelligence requires Neural Engine, which is only found in Apple Silicon chips.

