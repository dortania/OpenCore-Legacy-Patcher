from __future__ import print_function

import subprocess, sys, time, platform

from Resources import build, ModelArray, Constants, SysPatch, utilities

class MenuOptions:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions

    def change_os(self):
        utilities.cls()
        utilities.header(["Select Patcher's Target OS"])
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
        utilities.cls()
        utilities.header(["Set Verbose mode"])
        change_menu = input("Enable Verbose mode(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.verbose_debug = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.verbose_debug = False
        else:
            print("Invalid option")

    def change_oc(self):
        utilities.cls()
        utilities.header(["Set OpenCore DEBUG mode"])
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
        utilities.cls()
        utilities.header(["Set Kext DEBUG mode"])
        change_menu = input("Enable Kext DEBUG mode(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.kext_debug = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.kext_debug = False
        else:
            print("Invalid option")

    def change_metal(self):
        utilities.cls()
        utilities.header(["Assume Metal GPU Always in iMac"])
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
        utilities.cls()
        utilities.header(["Assume Upgraded Wifi Always"])
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
        utilities.cls()
        utilities.header(["Set SMBIOS Mode"])
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
        utilities.cls()
        utilities.header(["Set OpenCore Picker mode"])
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
        utilities.cls()
        utilities.header(["Set OpenCore Vaulting"])
        print("""By default, this patcher will sign all your files and ensure none of the
contents can be tampered with. However for more advanced users, you may
want to be able to freely edit the config.plist and files.

Note: For secuirty reasons, OpenShell will be disabled when Vault is set.

        """)
        change_menu = input("Enable Vault(y/n): ")
        if change_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.vault = True
        elif change_menu in {"n", "N", "no", "No"}:
            self.constants.vault = False
        else:
            print("Invalid option")

    def change_sip(self):
        utilities.cls()
        utilities.header(["Set SIP and SecureBootModel"])
        print("""SIP and SecureBootModel are used to ensure proper OTA functionality,
however to patch the root volume both of these must be disabled.
Only disable is absolutely necessary. SIP value = 0xFEF

Note: for minor changes, SIP can be adjusted in recovery like normal.
Additionally, when disabling SIP via the patcher amfi_get_out_of_my_way=1
will be added to boot-args.

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

    def change_imac_nvidia(self):
        utilities.cls()
        utilities.header(["Force iMac Nvidia Patches"])
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