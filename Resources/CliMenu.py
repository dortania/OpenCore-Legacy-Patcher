# Handle misc CLI menu options
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
from __future__ import print_function
import subprocess

from Resources import ModelArray, Constants, Utilities


class MenuOptions:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions

    def change_os(self):
        Utilities.cls()
        Utilities.header(["Select Patcher's Target OS"])
        print(f"""
Minimum Target:\t{self.constants.min_os_support}
Maximum Target:\t{self.constants.max_os_support}
Current target:\t{self.constants.os_support}
        """)
        temp_os_support = float(input("Please enter OS target: "))
        if (self.constants.max_os_support < temp_os_support) or (temp_os_support < self.constants.min_os_support):
            print("Unsupported entry")
        else:
            self.constants.os_support = temp_os_support
        if temp_os_support == 11.0:
            ModelArray.SupportedSMBIOS = ModelArray.SupportedSMBIOS11
        elif temp_os_support == 12.0:
            ModelArray.SupportedSMBIOS = ModelArray.SupportedSMBIOS12

    def change_verbose(self):
        Utilities.cls()
        Utilities.header(["Set Verbose mode"])
        change_menu = input("Enable Verbose mode(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.verbose_debug = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.verbose_debug = False
        else:
            print("Invalid option")

    def change_oc(self):
        Utilities.cls()
        Utilities.header(["Set OpenCore DEBUG mode"])
        change_menu = input("Enable OpenCore DEBUG mode(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.opencore_debug = False
            self.constants.opencore_build = "RELEASE"
        else:
            print("Invalid option")

    def change_kext(self):
        Utilities.cls()
        Utilities.header(["Set Kext DEBUG mode"])
        change_menu = input("Enable Kext DEBUG mode(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.kext_debug = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.kext_debug = False
        else:
            print("Invalid option")

    def change_metal(self):
        Utilities.cls()
        Utilities.header(["Assume Metal GPU Always in iMac"])
        print("""This is for iMacs that have upgraded Metal GPUs, otherwise
Patcher assumes based on stock configuration (ie. iMac10,x-12,x)

Valid Options:

1. None(stock GPU)
2. Nvidia GPU
3. AMD GPU

Note: Patcher will detect whether hardware has been upgraded regardless, this
option is for those patching on a different machine or OCLP cannot detect.
        """)
        change_menu = input("Set GPU Patch type(ie. 1): ")
        if change_menu == "1":
            self.constants.metal_build = False
            self.constants.imac_vendor = "None"
        elif change_menu == "2":
            self.constants.metal_build = True
            self.constants.imac_vendor = "Nvidia"
        elif change_menu == "3":
            self.constants.metal_build = True
            self.constants.imac_vendor = "AMD"
        else:
            print("Invalid option")

    def change_wifi(self):
        Utilities.cls()
        Utilities.header(["Assume Upgraded Wifi Always"])
        print("""This is for Macs with upgraded wifi cards(ie. BCM94360/2)

Note: Patcher will detect whether hardware has been upgraded regardless, this
option is for those patching on a different machine or cannot detect.
        """)
        change_menu = input("Enable Upgraded Wifi build algorithm?(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.wifi_build = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.wifi_build = False
        else:
            print("Invalid option")

    def change_serial(self):
        Utilities.cls()
        Utilities.header(["Set SMBIOS Mode"])
        print("""This section is for setting how OpenCore generates the SMBIOS
Recommended for adanced users who want control how serials are handled

Valid options:

1. Minimal:\tUse original serials and minimally update SMBIOS
2. Moderate:\tReplace entire SMBIOS but keep original serials
3. Advanced:\tReplace entire SMBIOS and generate new serials

Note: For new users we recommend leaving as default(1. Minimal)
        """)
        change_menu = input("Set SMBIOS Mode(ie. 1): ")
        if change_menu == "1":
            self.constants.serial_settings = "Minimal"
        elif change_menu == "2":
            self.constants.serial_settings = "Moderate"
        elif change_menu == "3":
            self.constants.serial_settings = "Advanced"
        else:
            print("Invalid option")

    def change_showpicker(self):
        Utilities.cls()
        Utilities.header(["Set OpenCore Picker mode"])
        print("""By default, OpenCore will show its boot picker each time on boot up,
however this can be disabled by default and be shown on command by repeatedly
pressing the "Esc" key
        """)
        change_menu = input("Show OpenCore Picker by default(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.showpicker = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.showpicker = False
        else:
            print("Invalid option")

    def change_vault(self):
        Utilities.cls()
        Utilities.header(["Set OpenCore Vaulting"])
        print("""By default, this patcher will sign all your files and ensure none of the
contents can be tampered with. However for more advanced users, you may
want to be able to freely edit the config.plist and files.

Note: For security reasons, OpenShell will be disabled when Vault is set.

        """)
        change_menu = input("Enable Vault(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.vault = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.vault = False
        else:
            print("Invalid option")

    def change_sip(self):
        Utilities.cls()
        Utilities.header(["Set SIP and SecureBootModel"])
        print("""SIP and SecureBootModel are used to ensure proper OTA functionality,
however to patch the root volume both of these must be disabled.
Only disable is absolutely necessary. SIP value = 0xFEF

Valid options:

1. Enable Both
2. Disable SIP only
3. Disable SecureBootModel Only
4. Disable Both

        """)
        change_menu = input("Set SIP and SecureBootModel(ie. 1): ")
        if change_menu == "1":
            self.constants.sip_status = True
            self.constants.secure_status = True
        elif change_menu == "2":
            self.constants.sip_status = False
            self.constants.secure_status = True
        elif change_menu == "3":
            self.constants.sip_status = True
            self.constants.secure_status = False
        elif change_menu == "4":
            self.constants.sip_status = False
            self.constants.secure_status = False
        else:
            print("Invalid option")

    def set_amfi(self):
        Utilities.cls()
        Utilities.header(["Disable AMFI"])
        print("""Required for Root Patching non-Metal GPUs
in macOS Big Sur. Without this, will receive kernel panic once
Patcher finishes installing legacy acceleration patches.
        """)
        change_menu = input("Disable AMFI(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.disable_amfi = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.disable_amfi = False
        else:
            print("Invalid option")

    def change_imac_nvidia(self):
        Utilities.cls()
        Utilities.header(["Assume Metal GPU Always"])
        print("""Specifically for iMac10,x-12,x with Metal Nvidia GPU upgrades
By default the patcher will try to detect what hardware is
running, however this will enforce iMac Nvidia Build Patches.
        """)
        change_menu = input("Assume iMac Nvidia patches(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.imac_nvidia_build = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.imac_nvidia_build = False
        else:
            print("Invalid option")

    def bootstrap_setting(self):
        Utilities.cls()
        Utilities.header(["Set Bootstrap method"])
        print("""Sets OpenCore's bootstrap method, currently the patcher supports the
following options.

Valid options:

1. System/Library/CoreServices/boot.efi (default)
2. EFI/BOOT/BOOTx64.efi
3. Exit

Note: S*/L*/C*/boot.efi method is only installed to the EFI partition only
and not to macOS itself.

Recommended to set to BOOTx64.efi in situations where your Mac cannot
see the EFI Boot entry in the boot picker.

        """)
        change_menu = input("Set Bootstrap method: ")
        if change_menu == "1":
            self.constants.boot_efi = False
        elif change_menu == "2":
            self.constants.boot_efi = True
        else:
            print("Invalid option")


    def drm_setting(self):
        Utilities.cls()
        Utilities.header(["Set DRM preferences"])
        print("""Sets OpenCore's DRM preferences for iMac13,x and iMac14,x.
In Big Sur, some DRM based content may be broken by
default in AppleTV, Photobooth, etc.

To resolve, you can opt to disable Intel QuickSync support in
favor of Nvidia's Software rendering. This can aid in DRM however
greatly hampers Video rendering performance in Final Cut Pro and
other programs relying on such features.

Recommend only disabling if absolutely required.
        """)
        change_menu = input("Enable Nvidia's Software DRM rendering(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.drm_support = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.drm_support = False
        else:
            print("Invalid option")

    def force_accel_setting(self):
        Utilities.cls()
        Utilities.header(["Assume Legacy GPU"])
        print("""Allows any model to force install Legacy Acceleration
patches. Only required for Mac Pro and Xserve users.

DO NOT RUN IF METAL GPU IS INSTALLED
        """)
        change_menu = input("Enable Beta Acceleration Patches(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.assume_legacy = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.assume_legacy = False
        else:
            print("Invalid option")

    def allow_native_models(self):
        Utilities.cls()
        Utilities.header(["Allow OpenCore on native Models"])
        print("""Allows natively supported Macs to use OpenCore. Recommended
for users with 3rd Party NVMe SSDs to achieve improved overall
power usage.

        """)
        change_menu = input("Allow OpenCore on all Models(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.allow_oc_everywhere = False
            self.constants.serial_settings = "Minimal"
        else:
            print("Invalid option")

    def custom_cpu(self):
        Utilities.cls()
        Utilities.header(["Set custom CPU Model Name"])
        print("""Change reported CPU Model name in About This Mac
Custom names will report as follows:

1: Original Name: 2.5 Ghz Dual-Core Intel Core i5
2. CPU name:      Intel(R) Core(TM) i5-3210M CPU @ 2.50Ghz
3. Custom Name:   2.5Ghz Cotton Candy (example)
        """)
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
        else:
            print("Invalid option")

    def custom_color_thing(self):
        Utilities.cls()
        Utilities.header(["Set custom CPU Model Name"])
        print("""Change reported CPU Model name in About This Mac
Custom names will report as follows:

1: Custom Color
2. Reset
        """)
        change_menu = input("Set custom CPU Name(1,2,3): ")
        if change_menu == "1":
            print("")
            #temp_tk_root = tk.Tk()
            #temp_tk_root.wm_withdraw()
            #self.constants.custom_color = colorchooser.askcolor(title="Choose color")
            #temp_tk_root.destroy()
        elif change_menu == "2":
            self.constants.custom_color = ""
        else:
            print("Invalid option")

    def download_more_ram_dot_com(self):
        Utilities.cls()
        Utilities.header(["Download more RAM"])
        print("""Downloads more RAM to your Mac!
Currently only offers 1.5TB bundles
        """)
        change_menu = input("Download more RAM?(y/n): ")
        if change_menu == "y":
            self.constants.download_ram = True
        elif change_menu == "n":
            self.constants.download_ram = False
        else:
            print("Invalid option")

    def disable_cpufriend(self):
        Utilities.cls()
        Utilities.header(["Disable CPU Friend?"])
        print("""Only recommended for advanced users
Disabling CPUFriend forces macOS into using a different
Mac's power profile for CPUs and GPUs, which can harm the
hardware
        """)
        change_menu = input("Disable CPU Friend?(y/n): ")
        if change_menu == "y":
            self.constants.disallow_cpufriend = True
        elif change_menu == "n":
            self.constants.disallow_cpufriend = False
        else:
            print("Invalid option")

    def set_seedutil(self):
        Utilities.cls()
        Utilities.header(["Set SeedUtil Status"])
        print("""Used for setting OS Update Preferences

Valid options:
1. Public Release Seed (Default)
2. Public Beta Seed
3. Developer Beta Seed
4. Check SeedUtil's current status
        """)

        change_menu = input("Set update status(Press [ENTER] to exit): ")
        if change_menu == "1":
            subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "unenroll"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
        elif change_menu == "2":
            subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "unenroll"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "enroll", "PublicSeed"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
        elif change_menu == "3":
            subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "unenroll"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "enroll", "DeveloperSeed"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
        elif change_menu == "4":
            result = subprocess.run(["sudo", "/System/Library/PrivateFrameworks/Seeding.framework/Versions/A/Resources/seedutil", "current"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            result = [i.partition(":")[2] for i in result.stdout.decode().split("\n") if "Currently enrolled in" in i][0]
            print(f"SeedUtil Current Status: {result}")
            input("\nPress [ENTER] to continue")
            self.set_seedutil()
        else:
            print("Returning to main menu")

    def set_smbios(self):
        Utilities.cls()
        Utilities.header(["Override SMBIOS Spoof"])
        print("""Change model OpenCore spoofs Mac too

Valid options:
1. Default set by OpenCore (Default)
2. User Override
3. Disable all spoofing (unsupported configuration)
        """)

        change_menu = input("Set SMBIOS status: ")
        if change_menu == "1":
            print("Setting SMBIOS spoof to default mode")
            self.constants.override_smbios = "Default"
        elif change_menu == "2":
            custom_smbios = input("Set new SMBIOS mode: ")
            try:
                test = self.constants.board_id[custom_smbios]
                self.constants.override_smbios = custom_smbios
            except KeyError:
                print("Unsupported SMBIOS, defaulting to Default setting")
                self.constants.override_smbios = "Default"
        elif change_menu == "3":
            print("Disabling SMBIOS spoof")
            self.constants.override_smbios = self.model
        else:
            print("Returning to main menu")

    def allow_firewire(self):
        Utilities.cls()
        Utilities.header(["Allow FireWire Boot Support"])
        print("""
In macOS Catalina and newer, Apple restricted
usage of FireWire devices to boot macOS for
security concerns relating to DMA access.

If you are comfortable lowering the security,
you can re-enable FireWire support for Catalina
and newer.

Note: MacBook5,x-7,1 don't support FireWire boot
        """)

        change_menu = input("Enable FireWire Boot support?(y/n): ")
        if change_menu == "y":
            self.constants.firewire_boot = True
        elif change_menu == "n":
            self.constants.firewire_boot = False
        else:
            print("Invalid option")

    def allow_nvme(self):
        Utilities.cls()
        Utilities.header(["Allow NVMe UEFI Support"])
        print("""
For machines not natively supporting NVMe,
this option allows you to see and boot NVMe
drive in OpenCore's picker

Not required if your machine natively supports NVMe

Note: You must have OpenCore on a bootable volume
first, ie. USB or SATA drive. Once loaded,
OpenCore will enable NVMe support in it's picker
        """)

        change_menu = input("Enable NVMe Boot support?(y/n): ")
        if change_menu == "y":
            self.constants.nvme_boot = True
        elif change_menu == "n":
            self.constants.nvme_boot = False
        else:
            print("Invalid option")