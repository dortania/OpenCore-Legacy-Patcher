# FAQ


* [Application requirements](#application-requirements)
* [How do I make sure I'm all up to date?](#how-do-i-make-sure-i-m-all-up-to-date)
* [Why are the settings "not saving"?](#why-are-the-settings-not-saving)
* [Can I use the same USB install media as a universal installer?](#can-i-use-the-same-usb-install-media-as-a-universal-installer)
* [Can I use OTA updates?](#can-i-use-ota-updates)
* [Can I use automatic updates?](#can-i-use-automatic-updates)
* [Why are macOS updates so large?](#why-are-macos-updates-so-large)
* [Can I update to macOS betas?](#can-i-update-to-macos-betas)
* [Can I downgrade macOS while keeping data?](#can-i-downgrade-macos-while-keeping-data)
* [Why is my system slow?](#why-is-my-system-slow)
* [Applications crashing with "illegal instruction"](#applications-crashing-with-illegal-instruction)
* [What is Metal and non-Metal?](#what-is-metal-and-non-metal)
* [What are FeatureUnlock and mediaanalysisd?](#what-are-featureunlock-and-mediaanalysisd)
* [Why isn't iPhone Mirroring working?](#why-isn-t-iphone-mirroring-working)
* [Where is Apple Intelligence?](#where-is-apple-intelligence)



## Application requirements
The patcher application requires **OS X Yosemite 10.10** or later to run.
* **El Capitan 10.11** or later is required to make installers for macOS Ventura
* **High Sierra 10.13** or later is required to make installers for macOS Sonoma and newer.

The patcher is designed to target **macOS Big Sur 11.x to macOS Sequoia 15.x**.
* Other versions may work, albeit in a broken state. No support is provided for any version outside of the above.

## How do I make sure I'm all up to date?

Updating the OCLP installation is a three step process, first the application, second the bootloader and finally root patches.

Refer to [Updating OpenCore and patches](https://dortania.github.io/OpenCore-Legacy-Patcher/UPDATE.html) for how to update the application and patches.

## Why are the settings "not saving"?

Starting with OpenCore Legacy Patcher 2.1.0, the status of settings in the GUI will now be saved under ```/Users/Shared/.com.dortania.opencore-legacy-patcher.plist```. The application will utilize this file to keep track of and retain settings for relaunches and application updates, no longer requiring a reconfiguring each time. The user interface will reset if any model other than "Host Model" is selected, as building for a different model will require different settings.

In case of issues, delete the file and restart the application to revert the GUI to default settings, then rebuild OpenCore with newly configured settings.

::: warning

Only settings made within OCLP are accounted for, modifications made directly into the ```config.plist``` file in the EFI partition outside of OCLP **will continue to reset**. Additionally, modifying ```config.plist``` manually may lead to a state where settings showed in the GUI are not in sync compared to settings in use, due to the application not knowing whether the file has been manually modified. 

:::

::: details Explainer for older versions (click to expand)

OpenCore Legacy Patcher is a config build tool and as such the user interface always reverts to safe defaults, the user interface therefore **does not** reflect the status of settings. Settings are accounted for and saved by the OpenCore building process and you will always have to build OpenCore again after settings change. 

Settings are saved to a config.plist file inside your EFI partition.

In SIP settings, booted SIP is reported in text form e.g. "0x803" but the checkboxes **do not** reflect the applied settings. Refer to [SIP Settings](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#sip-settings) for more information.

:::

## Can I use the same USB install media as a universal installer?

OpenCore configurations are device specific, due to different quirks needed for different systems. If you are building OpenCore for a different system that you're running, you will have to select the targeted model from Settings before building OpenCore on the USB media.

When building OpenCore on a different system, OCLP cannot be aware of all the hardware installed in the target, meaning safe defaults will be used. However, this may not be the most optimal experience especially with custom hardware. As such it's recommended to rebuild OpenCore **on device** to apply settings that are based on hardware detection, after the OS has been installed.

## Can I use OTA updates?

You can. However it is extremely recommended to use USB drive for major OS upgrades (such as 13 -> 14) to avoid larger issues from potentially occurring.

General updates are usually fine, though it is always a good idea to wait few days to see whether patches break and have to be fixed.

## Can I use automatic updates?

It is extremely recommended to disable automatic updates (even downloading) when using OCLP, as Apple has recently changed the way automatic updates work. Updates are now getting staged during the download process and are already modifying the system volume, which can lead to broken system out of nowhere since the operating system gets into a liminal state between two versions. You can still manually initiate an update when you're ready to do so. 

For a related "System version mismatch" error while root patching and more information, refer to [System version mismatch error when root patching](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html#system-version-mismatch-error-when-root-patching) for troubleshooting.

### Disabling updates

**macOS Ventura and newer:**

System Settings -> General -> Software Update -> (i) button next to Automatic Updates -> Disable "Download new updates when available".

**macOS Big Sur and Monterey:**

System Preferences -> Software Update -> Advanced -> Disable "Download new updates when available".

## Why are macOS updates so large?

macOS by default uses a sealed system volume that is unwritable. When the seal is broken, macOS thinks the volume is broken and downloads a full copy of macOS for every update to "repair" it to a known state. In order for root patching to work, this seal has to be broken since root patching by design requires on-disk file manipulation. This is also why root patches have to be reinstalled after each update.

## Can I update to macOS betas?

If you are feeling brave and don't mind having to possibly recover your system. However, be advised that no help will be given in situations where a beta was installed.


## Can I downgrade macOS while keeping data?

macOS doesn't allow direct downgrades, as such you will have to wipe the disk in order to revert. Backup your data beforehand either via Time Machine, ASR or some other solution.

## Why is my system slow?

This can mean many things. Firstly, newer operating systems are harder to run and can appear more slow. 

Additionally if your macOS installation is recent, Spotlight starts creating a full disk index which can cause high CPU load, high temps and general slowness. It's recommended to keep the system running for few hours, once Spotlight has indexed the load will ease. A way to check whether it's caused by Spotlight is to open Activity Monitor, choosing "All Processes" from the "View" menu item, then sorting by the CPU value to see if a process called ```mds_stores``` is using a lot of CPU resources.

However, if your system is being **really** slow and you have no transparency in Dock and menubar, this typically indicates that root patches are not installed and as such there is no acceleration. Make sure to install root patches to get proper drivers and functionality. Refer to [Applying post install volume patches](https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html#applying-post-install-volume-patches) and the [Troubleshooting](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html) section for more information.

Patches can also break if automatic updates are enabled and an update modifies the system volume, refer to [System version mismatch error when root patching](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOTING.html#system-version-mismatch-error-when-root-patching) for more information.

## Applications crashing with "illegal instruction"

If the crash log includes a string saying "illegal instruction", this typically means the application requires AVX or AVX2 CPU instructions. 

Since macOS Ventura, AVX2 is required from all Macs supported by it. While OCLP is able to patch macOS to boot without it, many applications are beginning to utilize AVX and AVX2 as well in newer versions because all supported Macs are expected to have them. This creates an issue for older systems where some applications cannot be ran on CPUs lacking such instructions. Some older Macs may need older versions of applications and cannot update to newer versions. AVX was introduced in Sandy Bridge CPU generation and AVX2 in Haswell generation.

In essence, this means that some models are now aging rapidly and newer OS won't always provide support for newer applications because of hardware requirements. If an application still supports macOS versions older than Ventura, it may have a chance of running on an older OS version on the old system, since some Macs running them natively don't support AVX2 and the app takes a different path.

Earliest Mac models supporting AVX instruction:

- Macmini5,x (2011)
- iMac12,x (2011)
- MacBookPro8,x (2011)
- MacBookAir4,x (2011)
- MacBook8,x (2015)
- MacPro6,1 (2013)

Earliest Mac models supporting AVX2 instruction:

- Macmini7,x (2014)
- iMac14,x (2013)
- MacBookPro11,x (2013)
- MacBookAir6,x (2013)
- MacBook8,x (2015)
- MacPro7,1 (2019)


## What is Metal and Non-Metal?

Metal is Apple's proprietary graphics API which fully superseded OpenGL rendering of the operating system starting from macOS Mojave. When the word "Non-Metal" is used, it describes GPUs that are not Metal supported and require using OpenGL instead.

GPUs that support Metal are as follows:

* Intel HD 4000 series (Ivy Bridge/3rd gen) and newer
* AMD HD 7000 series and newer (GCN 1)
* NVIDIA GTX 600 and 700 series (Kepler)

Everything older than mentioned are Non-Metal and therefore only support OpenGL. A great rule of thumb is that Macs older than 2012 are non-Metal, with the exception of systems with upgradable GPUs. Non-Metal also includes NVIDIA Maxwell (GTX 900 series) and Pascal (GTX 1000 series) when used with patched Web Drivers on newer than macOS High Sierra.

Refer to [Supported models](https://dortania.github.io/OpenCore-Legacy-Patcher/MODELS.html) and [Working Around Non-Metal Issues](https://dortania.github.io/OpenCore-Legacy-Patcher/ACCEL.html) pages for more information.

Due to deprecation of OpenGL, many newer applications may require Metal rendering and as such will fail to run on systems with Non-Metal GPUs.


## What are FeatureUnlock and mediaanalysisd?

**Important:** These features have the potential to cause instability in many places and as such a decision has been made to disable them by default (mediaanalysisd only on 3802-based* systems) starting from OpenCore Legacy Patcher version 2.1.0.  If you want to enable these features at the risk of additional instability, you can do so in the OCLP settings and rebuilding OpenCore.

FeatureUnlock is an extension to enable some macOS features, including:
- Sidecar
- Universal Control
- AirPlay to Mac
- Continuity Camera
- NightShift (non-Metal)

Further information, requirements and the models affected for FeatureUnlock features can be found [here](https://github.com/acidanthera/FeatureUnlock). 

Medianalysisd is utilized for
- Face detection in Photos
- Live Text

| FeatureUnlock | mediaanalysisd |
| :--- | :--- |
| ![FeatureUnlock](./images/OCLP_FeatureUnlock_Setting.png) | ![mediaanalysisd](./images/OCLP_Disable_mediaanalysisd_Setting.png) |


::: details *3802 systems list (click to expand)

* NVIDIA
    * Kepler (600-800 series GPUs)
* Intel
    * Ivy Bridge (3rd generation, HD 4000 series GPUs)
    * Haswell (4th generation, HD/Iris 4000-5000 series GPUs)

These GPUs are typically met in systems from 2012-2015.

:::

## Why isn't iPhone Mirroring working?

iPhone Mirroring requires a T2 chip, which means it will not be available on OCLP patched systems. The connection fails due to failure to establish T2 attestation.

## Where is Apple Intelligence?

Apple Intelligence requires Neural Engine, which is only found in Apple Silicon chips.

