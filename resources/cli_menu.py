# Handle misc CLI menu options
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk
import sys

from resources import constants, install, utilities, defaults, sys_patch, installer, tui_helpers, global_settings
from data import cpu_data, smbios_data, model_array, os_data, mirror_data


class MenuOptions:
    def __init__(self, model, versions):
        self.model = model
        self.constants: constants.Constants() = versions

    def change_verbose(self):
        utilities.cls()
        utilities.header(["Set Verbose mode"])
        change_menu = input("Enable Verbose mode(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.verbose_debug = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.verbose_debug = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_verbose()

    def change_oc(self):
        utilities.cls()
        utilities.header(["Set OpenCore DEBUG mode"])
        change_menu = input("Enable OpenCore DEBUG mode(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.opencore_debug = False
            self.constants.opencore_build = "RELEASE"
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_oc()

    def change_kext(self):
        utilities.cls()
        utilities.header(["Set Kext DEBUG mode"])
        change_menu = input("Enable Kext DEBUG mode(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.kext_debug = True
            self.constants.kext_variant = "DEBUG"
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.kext_debug = False
            self.constants.kext_variant = "RELEASE"
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_kext()

    def change_metal(self):
        utilities.cls()
        utilities.header(["Assume Metal GPU Always in iMac"])
        print(
            """This is for iMacs that have upgraded Metal GPUs, otherwise
Patcher assumes based on stock configuration (ie. iMac10,x-12,x)

Valid Options:

1. None (stock GPU)
2. Nvidia Kepler
3. AMD Polaris
4. AMD Legacy GCN
Q. Return to previous menu

Note: Patcher will detect whether hardware has been upgraded regardless, this
option is for those patching on a different machine or OCLP cannot detect.
        """
        )
        change_menu = input("Set GPU Patch type(ie. 1): ")
        if change_menu == "1":
            self.constants.metal_build = False
            self.constants.imac_vendor = "None"
            self.constants.imac_model = ""
        elif change_menu == "2":
            self.constants.metal_build = True
            self.constants.imac_vendor = "Nvidia"
            self.constants.imac_model = "Kepler"
        elif change_menu == "3":
            self.constants.metal_build = True
            self.constants.imac_vendor = "AMD"
            self.constants.imac_model = "Polaris"
        elif change_menu == "4":
            self.constants.metal_build = True
            self.constants.imac_vendor = "AMD"
            self.constants.imac_model = "Legacy GCN"
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_metal()

    def change_serial(self):
        utilities.cls()
        utilities.header(["Set SMBIOS Spoof Level"])
        print(
            """This section is for setting how OpenCore generates the SMBIOS
Recommended for advanced users who want control how serials are handled

Valid options:

0. None:\tUse stock SMBIOS (VMM Masking)
1. Minimal:\tUse original serials and minimally update SMBIOS
2. Moderate:\tReplace entire SMBIOS but keep original serials
3. Advanced:\tReplace entire SMBIOS and generate new serials
Q. Return to previous menu

        """
        )
        change_menu = input("Set SMBIOS Spoof Level(ie. 1): ")
        if change_menu == "0":
            self.constants.serial_settings = "None"
        elif change_menu == "1":
            self.constants.serial_settings = "Minimal"
        elif change_menu == "2":
            self.constants.serial_settings = "Moderate"
        elif change_menu == "3":
            self.constants.serial_settings = "Advanced"
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_serial()

    def change_showpicker(self):
        utilities.cls()
        utilities.header(["Set OpenCore Picker mode"])
        print(
            """By default, OpenCore will show its boot picker each time on boot up,
however this can be disabled by default and be shown on command by repeatedly
pressing the "Esc" key
        """
        )
        change_menu = input("Show OpenCore Picker by default(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.showpicker = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.showpicker = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_showpicker()

    def change_vault(self):
        utilities.cls()
        utilities.header(["Set OpenCore Vaulting"])
        print(
            """By default, this patcher will sign all your files and ensure none of the
contents can be tampered with. However for more advanced users, you may
want to be able to freely edit the config.plist and files.

Note: For security reasons, OpenShell will be disabled when Vault is set.

        """
        )
        change_menu = input("Enable Vault(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.vault = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.vault = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_vault()

    def change_sip(self):
        utilities.cls()
        utilities.header(["Set System Integrity protection"])
        print(
            f"""SIP is used to ensure proper secuirty measures are set,
however to patch the root volume this must be lowered partially.
Only disable is absolutely necessary. SIP value = 0x802

Valid options:

1. Enable SIP
2. Lower SIP partially (allow root volume patching)
3. Set Custom SIP value {self.constants.custom_sip_value}
Q. Return to previous menu

        """
        )
        change_menu = input("Set SIP: ")
        if change_menu == "1":
            self.constants.sip_status = True
        elif change_menu == "2":
            self.constants.sip_status = False
        elif change_menu == "3":
            self.set_custom_sip_value()
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_sip()

    def change_sbm(self):
        utilities.cls()
        utilities.header(["Set SecureBootModel"])
        print(
            """SecureBootModel is used to ensure best firmware security,
however to patch the root volume this must be disabled.
Only recommended to enable for users with T2 SMBIOS spoofs.

Valid options:

1. Enable SecureBootModel
2. Disable SecureBootModel
Q. Return to previous menu

        """
        )
        change_menu = input("Set SecureBootModel: ")
        if change_menu == "1":
            self.constants.secure_status = True
        elif change_menu == "2":
            self.constants.secure_status = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.change_sbm()

    def set_amfi(self):
        utilities.cls()
        utilities.header(["Set AMFI"])
        print(
            """Required for Root Patching non-Metal GPUs
in macOS Big Sur. Without this, will receive kernel panic once
Patcher finishes installing legacy acceleration patches.
        """
        )
        change_menu = input("Disable AMFI(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.amfi_status = False
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.amfi_status = True
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_amfi()

    def bootstrap_setting(self):
        utilities.cls()
        utilities.header(["Set Bootstrap method"])
        print(
            """Sets OpenCore's bootstrap method, currently the patcher supports the
following options.

Valid options:

1. System/Library/CoreServices/boot.efi (default)
2. EFI/BOOT/BOOTx64.efi
Q. Return to previous menu

Note: S*/L*/C*/boot.efi method is only installed to the EFI partition only
and not to macOS itself.

Recommended to set to BOOTx64.efi in situations where your Mac cannot
see the EFI Boot entry in the boot picker.

        """
        )
        change_menu = input("Set Bootstrap method: ")
        if change_menu == "1":
            self.constants.boot_efi = False
        elif change_menu == "2":
            self.constants.boot_efi = True
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.bootstrap_setting()

    def drm_setting(self):
        utilities.cls()
        utilities.header(["Set DRM preferences"])
        print(
            """Sets OpenCore's DRM preferences for iMac13,x and iMac14,x.
In Big Sur, some DRM based content may be broken by
default in AppleTV, Photobooth, etc.

To resolve, you can opt to disable Intel QuickSync support in
favor of Nvidia's Software rendering. This can aid in DRM however
greatly hampers Video rendering performance in Final Cut Pro and
other programs relying on such features.

Recommend only disabling if absolutely required.
        """
        )
        change_menu = input("Enable Nvidia's Software DRM rendering(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.drm_support = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.drm_support = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.drm_setting()

    def allow_native_models(self):
        utilities.cls()
        utilities.header(["Allow OpenCore on native Models"])
        print(
            """Allows natively supported Macs to use OpenCore. Recommended
for users with 3rd Party NVMe SSDs to achieve improved overall
power usage.

        """
        )
        change_menu = input("Allow OpenCore on all Models(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.allow_oc_everywhere = False
            self.constants.serial_settings = "Minimal"
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_native_models()

    def custom_cpu(self):
        utilities.cls()
        utilities.header(["Set custom CPU Model Name"])
        print(
            """Change reported CPU Model name in About This Mac
Custom names will report as follows:

1: Original Name: 2.5 Ghz Dual-Core Intel Core i5
2. CPU name:      Intel(R) Core(TM) i5-3210M CPU @ 2.50Ghz
3. Custom Name:   2.5Ghz Cotton Candy (example)
Q. Return to previous menu
        """
        )
        if self.constants.custom_cpu_model_value == "":
            if self.constants.custom_cpu_model == 0:
                print("Currently using original name")
            else:
                print("Currently using CPU name")
        else:
            print(f"Custom CPU name currently: {self.constants.custom_cpu_model_value}")
        change_menu = input("Set custom CPU Name(1,2,3): ")
        if change_menu == "1":
            self.constants.custom_cpu_model = 2
            self.constants.custom_cpu_model_value = ""
        elif change_menu == "2":
            self.constants.custom_cpu_model = 0
            self.constants.custom_cpu_model_value = ""
        elif change_menu == "3":
            self.constants.custom_cpu_model = 1
            self.constants.custom_cpu_model_value = input("Enter new CPU Name: ")
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.custom_cpu()

    def disable_cpufriend(self):
        utilities.cls()
        utilities.header(["Disable CPU Friend?"])
        print(
            """Only recommended for advanced users
Disabling CPUFriend forces macOS into using a different
Mac's power profile for CPUs and GPUs, which can harm the
hardware
        """
        )
        change_menu = input("Disable CPU Friend?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disallow_cpufriend = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disallow_cpufriend = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.disable_cpufriend()

    def set_smbios(self):
        utilities.cls()
        utilities.header(["Set SMBIOS Spoof Model"])
        print(
            """Change model OpenCore spoofs Mac too

Valid options:
1. Default set by OpenCore (Default)
2. User Override
3. Disable all spoofing (unsupported configuration)
Q. Return to previous menu
        """
        )

        change_menu = input("Set SMBIOS Spoof Model: ")
        if change_menu == "1":
            print("Setting SMBIOS spoof to default mode")
            self.constants.override_smbios = "Default"
        elif change_menu == "2":
            custom_smbios = input("Set new SMBIOS mode: ")
            try:
                if smbios_data.smbios_dictionary[custom_smbios]["Board ID"] != None:
                    self.constants.override_smbios = custom_smbios
                else:
                    print("Non-Intel SMBIOS, reverting to Default setting")
                    self.constants.override_smbios = "Default"
            except KeyError:
                print("Unsupported SMBIOS, reverting to Default setting")
                self.constants.override_smbios = "Default"
        elif change_menu == "3":
            print("Disabling SMBIOS spoof")
            self.constants.override_smbios = self.model
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_smbios()

    def allow_firewire(self):
        utilities.cls()
        utilities.header(["Allow FireWire Boot Support"])
        print(
            """
In macOS Catalina and newer, Apple restricted
usage of FireWire devices to boot macOS for
security concerns relating to DMA access.

If you are comfortable lowering the security,
you can re-enable FireWire support for Catalina
and newer.

Note: MacBook5,x-7,1 don't support FireWire boot
        """
        )

        change_menu = input("Enable FireWire Boot support?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.firewire_boot = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.firewire_boot = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_firewire()

    def allow_nvme(self):
        utilities.cls()
        utilities.header(["Allow NVMe UEFI Support"])
        print(
            """
For machines not natively supporting NVMe,
this option allows you to see and boot NVMe
drive in OpenCore's picker

Not required if your machine natively supports NVMe

Note: You must have OpenCore on a bootable volume
first, ie. USB or SATA drive. Once loaded,
OpenCore will enable NVMe support in it's picker
        """
        )

        change_menu = input("Enable NVMe Boot support?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.nvme_boot = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.nvme_boot = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_nvme()

    def allow_nvme_pwr_mgmt(self):
        utilities.cls()
        utilities.header(["Allow NVMe Power Management Adjustments"])
        print(
            """
For machines with upgraded NVMe drives, this
option allows for better power management support
within macOS.

Note that some NVMe drives don't support macOS's
power management settings, and can result in boot
issues. Disable this option if you experience
IONVMeFamily kernel panics. Mainly applicable for
Skylake and newer Macs.
        """
        )

        change_menu = input("Enable NVMe Power Management?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.allow_nvme_fixing = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.allow_nvme_fixing = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_nvme()

    def allow_xhci(self):
        utilities.cls()
        utilities.header(["Allow NVMe UEFI Support"])
        print(
            """
For machines not natively supporting XHCI/USB 3.o,
this option allows you to see and boot XHCI
drive in OpenCore's picker

Not required if your machine natively supports USB 3.0

Note: You must have OpenCore on a bootable volume
first, ie. USB 2.0 or SATA drive. Once loaded,
OpenCore will enable XHCI support in it's picker
        """
        )

        change_menu = input("Enable XHCI Boot support?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.xhci_boot = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.xhci_boot = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_xhci()

    def allow_wowl(self):
        utilities.cls()
        utilities.header(["Allow Wake on WLAN"])
        print(
            """
Due to an unfortunate bug in macOS Big Sur+, Wake on WLAN is
disabled by default for BCM943224, BCM94331 and BCM94360/2 chipsets.

This is due to Wake on WLAN creating network instability and in other cases
halving network speeds. This issue is not replicable across machines however
be prepared if enabling.
        """
        )

        change_menu = input("Allow Wake on WLAN?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.enable_wake_on_wlan = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.enable_wake_on_wlan = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.allow_wowl()


    def disable_tb(self):
        utilities.cls()
        utilities.header(["Disable Thunderbolt on 2013-14 MacBook Pros"])
        print(
            """
Some 2013-14 MacBook Pro's have issues with the built-in thunderbolt,
resulting in kernel panics and random shutdowns.

To alliviate, you can disable the thunderbolt controller on MacBookPro11,x
machines with this option.

Note: This option only works on MacBookPro11,x, file an issue if you know of
other devices that benefit from this fix.
        """
        )

        change_menu = input("Disable Thunderbolt?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disable_tb = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disable_tb = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.disable_tb()

    def terascale_2_accel(self):
        utilities.cls()
        utilities.header(["Set TeraScale 2 Acceleration"])
        print(
            """
By default this patcher will install TeraScale 2 acceleration, however
for some laptops this may be undesired due to how degraded their dGPU
is.

Disabling TeraScale 2 acceleration will instead install basic framebuffer
support allowing for basic brightness control and let the HD3000 iGPU
handle acceleration tasks.
        """
        )

        change_menu = input("Allow TeraScale 2 Acceleration?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            global_settings.global_settings().write_property("MacBookPro_TeraScale_2_Accel", True)
            self.constants.allow_ts2_accel = True
        elif change_menu in {"n", "N", "no", "No"}:
            global_settings.global_settings().write_property("MacBookPro_TeraScale_2_Accel", False)
            self.constants.allow_ts2_accel = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.terascale_2_accel()

    def dump_hardware(self):
        utilities.cls()
        utilities.header(["Dumping detected hardware"])
        print("")
        print(self.constants.computer)
        input("\nPress [ENTER] to exit: ")

    def applealc_support(self):
        utilities.cls()
        utilities.header(["Set AppleALC usage"])
        print(
            """
By default this patcher will install audio patches in-memory via
AppleALC. However for systems that cannot achieve boot screen support,
this option will allow you to install the legacy AppleHDA patch via
root patching.

If AppleALC is detected, the Patcher will not install AppleHDA.
        """
        )

        change_menu = input("Set AppleALC usage?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.set_alc_usage = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.set_alc_usage = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.applealc_support()

    def dGPU_switch_support(self):
        utilities.cls()
        utilities.header(["Set Windows GMUX support"])
        print(
            """
With OCLP, we're able to restore iGPU functionality on iGPU+dGPU
MacBook Pros. However for some this may not be desires, ie. eGPUs
for Windows may prefer to only work with the dGPU and eGPU active.
        """
        )

        change_menu = input("Set Windows GMUX support?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.dGPU_switch = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.dGPU_switch = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.dGPU_switch_support()

    def set_3rd_party_drices(self):
        utilities.cls()
        utilities.header(["Set enhanced 3rd Party SSD Support"])
        print(
            """
On SATA-based Macs, Apple restricts enhanced OS support to native
drives. Namely hibernation and TRIM.

This option allows you to disable enhanced support in situations where
TRIM is not ideal.
        """
        )

        change_menu = input("Set enhanced 3rd Party SSD Support?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.allow_3rd_party_drives = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.allow_3rd_party_drives = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_3rd_party_drices()

    def set_software_demux(self):
        utilities.cls()
        utilities.header(["Set Software Demux"])
        print(
            """
For MacBookPro8,2/3 users, it's very common for the dGPU to fail and
thus require the user to disable them via the 'gpu-power-prefs'
nvram argument.

However this solution still allows the dGPU to pull power (6-7w). Enabling
this option will simulate a demuxed enviroment allowing the dGPU to pull nearly
no power and have the iGPU handle all tasks including brightness control.

Note: this option requires dGPU to be disabled via NVRAM:
https://dortania.github.io/OpenCore-Legacy-Patcher/ACCEL.html#unable-to-switch-gpus-on-2011-15-and-17-macbook-pros
        """
        )

        change_menu = input("Set Software Demux?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.software_demux = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.software_demux = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_software_demux()

    def set_battery_throttle(self):
        utilities.cls()
        utilities.header(["Disable Firmware Throttling"])
        print(
            """
By default on Nehalem and newer Macs, the firmware will throttle if
the battery or Display is either dead or missing. The firmware will set
'BD PROCHOT' to notify the OS the machine needs to run in an extreme
low power mode.

Enabling this option will patch 'MSR_POWER_CTL' to be unset allowing
proper CPU behaviour as if hardware is present. Note that this can cause
instability in situations where the CPU is being taxed and pulls more
power than the laptop's PSU can supply.

Note: Only supported on Nehalem and newer Macs (2010+)
        """
        )

        change_menu = input("Disable Firmware Throttling?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disable_msr_power_ctl = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disable_msr_power_ctl = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_battery_throttle()

    def set_xcpm(self):
        utilities.cls()
        utilities.header(["Disable XCPM"])
        print(
            """
By default on Ivy Bridge EP and newer Macs, the system will throttle if
the battery or Display is either dead or missing. Apple's XCPM will set
'BD PROCHOT' to avoid damage to the system.

Enabling this option will disable Apple's XNU CPU Power Management (XCPM)
and fall back onto the older ACPI_SMC_PlatformPlugin.kext.

Note: Only supported on Ivy Bridge EP and newer Macs (2013+)
        """
        )

        change_menu = input("Disable XCPM?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disable_xcpm = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disable_xcpm = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_xcpm()

    def set_surplus(self):
        utilities.cls()
        utilities.header(["Override SurPlus MaxKernel"])
        print(
            """
By default OCLP will only allow SurPlus to be used on Big Sur and Monterey.
This is for safety reasons in the event newer OSes may break compatibility
and result in boot loops.

Enabling this option will allow SurPlus to have no MaxKernel set, and
therefore allow it to run on anything newer than 11.2.3. However if you
do toggle this setting, ensure you have a known-good OS to return to in
the event there's issues.
        """
        )

        change_menu = input("Force SurPlus on all newer OSes?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.force_surplus = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.force_surplus = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_surplus()

    def set_hibernation_workaround(self):
        utilities.cls()
        utilities.header(["Set Hibernation Workaround"])
        print(
            """
For users with Hibernation issues, you can flip this option to disable certain
OpenCore settings that may affect the stability of Hibernation. Namely
OpenCore's ConnectDrivers option.

Flipping this setting will disable automatic loading of additional drives in
OpenCore's boot menu other than what was booted.

Note: This option should only be flipped under the following circumstances:
      - You are experincing wake failures from hibernation
      - You are only using 1 disk in your system for booting (ie. no RAID)
      - OpenCore is installed on the same disk as the OS
      - Your system has an Intel iGPU and Nvidia dGPU
      - You have no need to boot external media through OpenCore
        """
        )

        change_menu = input("Disable ConnectDrivers?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disable_connectdrivers = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disable_connectdrivers = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_hibernation_workaround()

    def set_custom_sip_value(self):
        utilities.cls()
        utilities.header(["Set Custom SIP Value"])
        print(
            """
By default OCLP will use the SIP value of 0x00 as the enabled and
0xA03 for machines that require root patching. For users who wish
to flip additional bits in SIP may use this option.

To disable SIP outright, set it to 0xFEF
            """
        )
        change_menu = input("Set Custom SIP Value (0xFEF): ")
        try:
            # Verify whether input is a valid hex value
            int(change_menu, 16)
            # Convert to binary hex
            self.constants.custom_sip_value = change_menu
        except ValueError:
            print("Invalid input, returning to previous menu")
            self.set_custom_sip_value()

    def set_fu_settings(self):
        utilities.cls()
        utilities.header(["Set FeatureUnlock Settings"])
        print(
            """
By default OCLP will add a kext called FeatureUnlock to enable
features locked out from older models. Including:

- AirPlay to Mac
- SideCar
- Night Shift

However for systems experiencing memory instability, disabling this
kext can help.

Supported Options:

1. Enable FeatureUnlock and all patches
2. Enable FeatureUnlock and disable AirPlay to Mac and SideCar
3. Disable FeatureUnlock
            """
        )
        change_menu = input("Set FeatreUnlock (ie. 1): ")
        if change_menu == "1":
            self.constants.fu_status = True
            self.constants.fu_arguments = None
        elif change_menu == "2":
            self.constants.fu_status = True
            self.constants.fu_arguments = " -disable_sidecar_mac"
        elif change_menu == "3":
            self.constants.fu_status = False
            self.constants.fu_arguments = None
        else:
            print("Invalid input, returning to previous menu")
            self.set_fu_settings()

    def set_allow_native_spoofs(self):
        utilities.cls()
        utilities.header(["Allow Native Spoofs"])
        print(
            """
By default OCLP will not touch the SMBIOS of native models
to ensure a "stock-like" environment. However for systems that
cannot update their firmware, this option will allow OCLP to
spoof the SMBIOS.

By default VMM is used to spoof the SMBIOS. Minimal and higher are
available however not officially supported.
            """
        )
        change_menu = input("Allow Native Spoofs?(y/n/q): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.allow_native_spoofs = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.allow_native_spoofs = False
        elif change_menu in {"q", "Q", "Quit", "quit"}:
            print("Returning to previous menu")
        else:
            self.set_allow_native_spoofs()

    def set_nvram_write(self):
        utilities.cls()
        utilities.header(["Set NVRAM Write"])
        print(
            """
By default, OpenCore will write NVRAM variables to flash. This is
recommended for majority of systems however for extremely degraded
or fragile systems, you may wish to disable this.

Supported Options:

1. Enable NVRAM Write
2. Disable NVRAM Write
            """
        )
        change_menu = input("Set NVRAM Write (ie. 1): ")
        if change_menu == "1":
            self.constants.nvram_write = True
        elif change_menu == "2":
            self.constants.nvram_write = False
        else:
            print("Invalid input, returning to previous menu")
            self.set_nvram_write()

    def set_cc_support(self):
        utilities.cls()
        utilities.header(["Set Content Caching Support"])
        print(
            """
On systems spoofing via VMM, Content Caching is disabled by
default by Apple. This option allows you to mask VMM from
AssetCache.
            """
        )
        change_menu = input("Set Content Caching Support (y/n/q): ")
        if change_menu in ["y", "Y", "yes", "Yes"]:
            self.constants.set_content_caching = True
        elif change_menu in ["n", "N", "no", "No"]:
            self.constants.set_content_caching = False
        elif change_menu in ["q", "Q", "Quit", "quit"]:
            print("Returning to previous menu")
        else:
            self.set_cc_support()

    def credits(self):
        tui_helpers.TUIOnlyPrint(
            ["Credits"],
            "Press [Enter] to go back.\n",
            [
                """Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - DhinakG:\t\tWriting and maintaining this patcher
  - Khronokernel:\tWriting and maintaining this patcher
  - ASentientBot:\tLegacy Acceleration Patches
  - Ausdauersportler:\tLinking fixes for SNBGraphicsFB and AMDX3000
  - Syncretic:\t\tAAAMouSSE, telemetrap, and SurPlus
  - cdf:\t\tNightShiftEnabler and Innie
  - parrotgeek1:\tVMM Patch Set

Source Code:
https://github.com/dortania/OpenCore-Legacy-Patcher
  """
            ],
        ).start()

    def change_model(self):
        utilities.cls()
        utilities.header(["Select Different Model"])
        print(
            """
Tip: Run the following command on the target machine to find the model identifier:

system_profiler SPHardwareDataType | grep 'Model Identifier'
    """
        )
        self.constants.custom_model = input("Please enter the model identifier of the target machine: ").strip()
        if self.constants.custom_model not in model_array.SupportedSMBIOS:
            print(
                f"""
{self.constants.custom_model} is not a valid SMBIOS Identifier for macOS {self.constants.os_support}!
"""
            )
            print_models = input(f"Print list of valid options for macOS {self.constants.os_support}? (y/n)")
            if print_models.lower() in {"y", "yes"}:
                print("\n".join(model_array.SupportedSMBIOS))
                input("\nPress [ENTER] to continue")
        else:
            defaults.generate_defaults.probe(self.constants.custom_model, False, self.constants)

    def PatchVolume(self):
        utilities.cls()
        utilities.header(["Patching System Volume"])

        no_patch = False
        no_unpatch = False
        if self.constants.detected_os == os_data.os_data.monterey:
            print(MenuOptions.monterey)
        elif self.constants.detected_os == os_data.os_data.big_sur:
            print(MenuOptions.big_sur)
        else:
            print(MenuOptions.default)
            no_patch = True
            no_unpatch = True
        change_menu = input("Patch System Volume?: ")
        if no_patch is not True and change_menu == "1":
            sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, None).start_patch()
        elif no_unpatch is not True and change_menu == "2":
            sys_patch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants, None).start_unpatch()
        else:
            print("Returning to main menu")

    def advanced_patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Advanced Patcher Settings, for developers ONLY"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set Metal GPU Status:\t\tCurrently {self.constants.imac_vendor}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_metal],
                [f"Set DRM Preferences:\t\tCurrently {self.constants.drm_support}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).drm_setting],
                [f"Set Generic Bootstrap:\t\tCurrently {self.constants.boot_efi}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).bootstrap_setting],
                [
                    f"Disable CPU Friend:\t\t\tCurrently {self.constants.disallow_cpufriend}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).disable_cpufriend,
                ],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Patcher Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                ["Debug Settings", self.patcher_setting_debug],
                ["Security Settings", self.patcher_settings_security],
                ["SMBIOS Settings", self.patcher_settings_smbios],
                ["Boot Volume Settings", self.patcher_settings_boot],
                ["Miscellaneous Settings", self.patcher_settings_misc],
                ["Dump detected hardware", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).dump_hardware],
                [
                    f"Allow OpenCore on native Models:\tCurrently {self.constants.allow_oc_everywhere}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_native_models,
                ],
                ["Advanced Settings, for developers only", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).advanced_patcher_settings],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_setting_debug(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Debug Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Enable Verbose Mode:\tCurrently {self.constants.verbose_debug}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_verbose],
                [f"Enable OpenCore DEBUG:\tCurrently {self.constants.opencore_debug}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_oc],
                [f"Enable Kext DEBUG:\t\tCurrently {self.constants.kext_debug}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_kext],
            ] + (
                [[f"Set SurPlus Settings:\tCurrently {self.constants.force_surplus}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_surplus]]
                if (smbios_data.smbios_dictionary[self.constants.custom_model or self.constants.computer.real_model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge)
                else []
            )

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_security(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Security Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                # [
                #     f"Set Apple Mobile File Integrity (AMFI):\tCurrently {self.constants.amfi_status}",
                #     MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_amfi,
                # ],
                [
                    f"Set System Integrity Protection (SIP):\tCurrently {self.constants.custom_sip_value or self.constants.sip_status}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_sip,
                ],
                [
                    f"Set Secure Boot Model (SBM):\t\tCurrently {self.constants.secure_status}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_sbm,
                ],
                [f"Set Vault Mode:\t\t\t\tCurrently {self.constants.vault}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_vault],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_smbios(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust SMBIOS Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set SMBIOS Spoof Level:\tCurrently {self.constants.serial_settings}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_serial],
                [f"Set SMBIOS Spoof Model:\tCurrently {self.constants.override_smbios}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_smbios],
                [f"Allow Native Spoofs:\tCurrently {self.constants.allow_native_spoofs}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_allow_native_spoofs],
                [f"Set Custom name {self.constants.custom_cpu_model_value}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).custom_cpu],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_boot(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Bootable Volume Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set FireWire Boot:\t\tCurrently {self.constants.firewire_boot}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_firewire],
                [f"Set XHCI Boot:\t\tCurrently {self.constants.xhci_boot}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_xhci],
                [f"Set NVMe Boot:\t\tCurrently {self.constants.nvme_boot}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_nvme],
                [f"Set NVMe Power Management:\tCurrently {self.constants.allow_nvme_fixing}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_nvme_pwr_mgmt],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_misc(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Miscellaneous Settings"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set ShowPicker Mode:\tCurrently {self.constants.showpicker}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_showpicker],
                [f"Set Wake on WLAN:\t\tCurrently {self.constants.enable_wake_on_wlan}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).allow_wowl],
                [
                    f"Set TeraScale 2 Accel:\tCurrently {self.constants.allow_ts2_accel}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).terascale_2_accel,
                ],
                [
                    f"Disable Thunderbolt:\tCurrently {self.constants.disable_tb}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).disable_tb,
                ],
                [f"Set AppleALC Usage:\t\tCurrently {self.constants.set_alc_usage}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).applealc_support],
                [
                    f"Set Windows GMUX support:\tCurrently {self.constants.dGPU_switch}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).dGPU_switch_support,
                ],
                [f"Set Hibernation Workaround:\tCurrently {self.constants.disable_connectdrivers}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_hibernation_workaround],
                [f"Disable Battery Throttling:\tCurrently {self.constants.disable_msr_power_ctl}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_battery_throttle],
                [f"Disable XCPM:\t\tCurrently {self.constants.disable_xcpm}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_xcpm],
                [f"Set Software Demux:\tCurrently {self.constants.software_demux}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_software_demux],
                [f"Set 3rd Party SSD Support:\tCurrently {self.constants.allow_3rd_party_drives}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_3rd_party_drices],
                [f"Set FeatureUnlock: \tCurrently {self.constants.fu_status}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_fu_settings],
                [f"Set NVRAM Write:\t\tCurrently {self.constants.nvram_write}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_nvram_write],
                [f"Set Content Caching:\tCurrently {self.constants.set_content_caching}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).set_cc_support],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def advanced_patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Advanced Patcher Settings, for developers ONLY"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set Metal GPU Status:\t\tCurrently {self.constants.imac_vendor}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).change_metal],
                [f"Set DRM Preferences:\t\tCurrently {self.constants.drm_support}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).drm_setting],
                [f"Set Generic Bootstrap:\t\tCurrently {self.constants.boot_efi}", MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).bootstrap_setting],
                [
                    f"Disable CPU Friend:\t\t\tCurrently {self.constants.disallow_cpufriend}",
                    MenuOptions(self.constants.custom_model or self.constants.computer.real_model, self.constants).disable_cpufriend,
                ],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def download_macOS(self):
        utilities.cls()
        utilities.header(["Create macOS installer"])
        print(
            """
This option allows you to download and flash a macOS installer
to your USB drive.

1. Download macOS Installer
2. Use Existing Installer
B. Exit
"""
        )
        change_menu = input("Select an option: ")
        if change_menu == "1":
            self.download_macOS_installer()
        elif change_menu == "2":
            self.find_local_installer()
        elif change_menu in ["B", "b"]:
            return
        else:
            self.download_macOS()

    def download_install_assistant(self, link):
        if installer.download_install_assistant(self.constants.payload_path, link):
            installer.install_macOS_installer(self.constants.payload_path)
            input("Press any key to continue...")
            # To avoid selecting the wrong installer by mistake, let user select the correct one
            self.find_local_installer()
        else:
            print("Failed to start download")
            input("Press any key to continue...")


    def download_macOS_installer(self):
        response = None
        while not (response and response == -1):
            options = []
            title = ["Select the macOS Installer you wish to download"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            available_installers = installer.list_downloadable_macOS_installers(self.constants.payload_path, "DeveloperSeed")
            if available_installers:
                # Add mirror of 11.2.3 for users who want it
                options.append([f"macOS {mirror_data.Install_macOS_Big_Sur_11_2_3['Version']} ({mirror_data.Install_macOS_Big_Sur_11_2_3['Build']} - {utilities.human_fmt(mirror_data.Install_macOS_Big_Sur_11_2_3['Size'])} - {mirror_data.Install_macOS_Big_Sur_11_2_3['Source']})", lambda: self.download_install_assistant(mirror_data.Install_macOS_Big_Sur_11_2_3['Link'])])
                for app in available_installers:
                    if available_installers[app]['Variant'] in ["DeveloperSeed", "PublicSeed"]:
                        variant = " Beta"
                    else:
                        variant = ""
                    options.append([f"macOS {available_installers[app]['Version']}{variant} ({available_installers[app]['Build']} - {utilities.human_fmt(available_installers[app]['Size'])} - {available_installers[app]['Source']})", lambda x=app: self.download_install_assistant(available_installers[x]['Link'])])
                for option in options:
                    menu.add_menu_option(option[0], function=option[1])
            response = menu.start()

    def find_local_installer(self):
        response = None
        while not (response and response == -1):
            options = []
            title = ["Select the macOS Installer you wish to use"]
            menu = tui_helpers.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            available_installers = installer.list_local_macOS_installers()
            if available_installers:
                for app in available_installers:
                    options.append([f"{available_installers[app]['Short Name']}: {available_installers[app]['Version']} ({available_installers[app]['Build']})", lambda x=app: self.list_disks(available_installers[x]['Path'])])
                for option in options:
                    menu.add_menu_option(option[0], function=option[1])
            response = menu.start()

    def list_disks(self, installer_path):
        disk = installer.select_disk_to_format()
        if disk != None:
            if installer.format_drive(disk) is True:
                # Only install if OC is found
                # Allows a user to create a macOS Installer without OCLP if desired
                if self.constants.opencore_release_folder.exists() and self.constants.walkthrough is True:
                    # ESP will always be the first partition when formatted by disk utility
                    install.tui_disk_installation.install_opencore(self, f"disk{disk}", "1")
                if installer.create_installer(installer_path, "OCLP-Installer") is True:
                    utilities.cls()
                    utilities.header(["Create macOS installer"])
                    print("Installer created successfully.")
                    input("Press enter to exit.")
                    if self.constants.walkthrough is True:
                        self.closing_message()
                else:
                    utilities.cls()
                    utilities.header(["Create macOS installer"])
                    print("Installer creation failed.")
                    input("Press enter to return to the previous.")
                    return
            else:
                if self.constants.walkthrough is True:
                    sys.exit()

    def closing_message(self):
        utilities.cls()
        utilities.header(["Create macOS installer"])
        print("Thank you for using OpenCore Legacy Patcher!")
        print("Reboot your machine and select EFI Boot to load OpenCore")
        print("")
        print("If you have any issues, remember to check the guide as well as\nour Discord server:")
        print("\n\tGuide: https://dortania.github.io/OpenCore-Legacy-Patcher/")
        print("\tDiscord: https://discord.gg/rqdPgH8xSN")
        input("\nPress enter to exit: ")
        sys.exit()

    big_sur = """Patches Root volume to fix misc issues such as:

- Non-Metal Graphics Acceleration
  - Intel: Ironlake - Sandy Bridge
  - Nvidia: Tesla - Fermi (8000-500 series)
  - AMD: TeraScale 1 and 2 (2000-6000 series)
- Audio support for iMac7,1 and iMac8,1

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates.

Supported Options:

1. Patch System Volume
2. Unpatch System Volume (Experimental)
B. Exit
        """
    monterey = """Patches Root volume to fix misc issues such as:

- Metal Graphics Acceleration
  - Intel: Ivy Bridge (4000 series iGPUs)
  - Nvidia: Kepler (600-700)
- Non-Metal Graphics Accelertation
  - Intel: Ironlake - Sandy Bridge
  - Nvidia: Tesla - Fermi (8000-500 series)
  - AMD: TeraScale 1 and 2 (2000-6000 series)
- Audio support for iMac7,1 and iMac8,1
- Wifi support for BCM94328, BCM94322 and Atheros cards

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates.

Supported Options:

1. Patch System Volume
2. Unpatch System Volume
B. Exit
        """
    mojave_catalina = """Patches Root volume to fix misc issues such as:

- Non-Metal Graphics Acceleration
  - Intel: Ironlake - Sandy Bridge
  - Nvidia: Tesla - Fermi (8000-500 series)
  - AMD: TeraScale 1 and 2 (2000-6000 series)
- Audio support for iMac7,1 and iMac8,1

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates.

Supported Options:

1. Patch System Volume
B. Exit
         """

    default = """
This OS has no root patches available to apply, please ensure you're patching a booted
install that requires root patches such as macOS Big Sur or Monterey

Supported Options:

B. Exit
        """
