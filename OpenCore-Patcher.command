#!/usr/bin/env python3

from __future__ import print_function

import subprocess, sys, time, platform

from Resources import build, ModelArray, Constants, SysPatch, utilities


class OpenCoreLegacyPatcher():
    def __init__(self):
        self.constants = Constants.Constants()
        self.current_model: str = None
        opencore_model: str = subprocess.run("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if not opencore_model.startswith("nvram: Error getting variable"):
            opencore_model = [line.strip().split(":oem-product	", 1)[1] for line in opencore_model.split("\n") if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
            self.current_model = opencore_model
        else:
            self.current_model = subprocess.run("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.current_model = [line.strip().split(": ", 1)[1] for line in self.current_model.stdout.decode().split("\n") if line.strip().startswith("Model Identifier")][0]
        self.constants.detected_os, _, _ = platform.mac_ver()
        self.constants.detected_os = float('.'.join(self.constants.detected_os.split('.')[:2]))
        if self.current_model in ModelArray.NoAPFSsupport:
            self.constants.serial_settings = "Moderate"

    def build_opencore(self):
        build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).build_opencore()

    def install_opencore(self):
        build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).copy_efi()

    def change_model(self):
        utilities.cls()
        utilities.header(["Select Different Model"])
        print("""
Tip: Run the following command on the target machine to find the model identifier:

system_profiler SPHardwareDataType | grep 'Model Identifier'
    """)
        self.constants.custom_model = input("Please enter the model identifier of the target machine: ").strip()
        if self.constants.custom_model not in ModelArray.SupportedSMBIOS:
            print(f"""
        {self.constants.custom_model} is not a valid SMBIOS Identifier for macOS {self.constants.os_support}!
            """)
            print_models = input(f"Print list of valid options for macOS {self.constants.os_support}? (y/n)")
            if print_models in {"y", "Y", "yes", "Yes"}:
                print("\n".join(ModelArray.SupportedSMBIOS))
                input("Press any key to continue...")
        if self.constants.custom_model in ModelArray.NoAPFSsupport:
            self.constants.serial_settings = "Moderate"

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
        verbose_menu = input("Enable Verbose mode(y/n): ")
        if verbose_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.verbose_debug = True
        elif verbose_menu in {"n", "N", "no", "No"}:
            self.constants.verbose_debug = False
        else:
            print("Invalid option")

    def change_oc(self):
        utilities.cls()
        utilities.header(["Set OpenCore DEBUG mode"])
        change_oc_menu = input("Enable OpenCore DEBUG mode(y/n): ")
        if change_oc_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        elif change_oc_menu in {"n", "N", "no", "No"}:
            self.constants.opencore_debug = False
            self.constants.opencore_build = "RELEASE"
        else:
            print("Invalid option")
    def change_kext(self):
        utilities.cls()
        utilities.header(["Set Kext DEBUG mode"])
        change_kext_menu = input("Enable Kext DEBUG mode(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.kext_debug = True
        elif change_kext_menu in {"n", "N", "no", "No"}:
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
        change_kext_menu = input("Set GPU Patch type(ie. 1): ")
        if change_kext_menu == "1":
            self.constants.metal_build = False
            self.constants.imac_vendor = "None"
        elif change_kext_menu == "2":
            self.constants.metal_build = True
            self.constants.imac_vendor = "Nvidia"
        elif change_kext_menu == "3":
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
        change_kext_menu = input("Enable Upgraded Wifi build algorithm?(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.wifi_build = True
        elif change_kext_menu in {"n", "N", "no", "No"}:
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
        change_serial_menu = input("Set SMBIOS Mode(ie. 1): ")
        if change_serial_menu == "1":
            self.constants.serial_settings = "Minimal"
        elif change_serial_menu == "2":
            self.constants.serial_settings = "Moderate"
        elif change_serial_menu == "3":
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
        change_kext_menu = input("Show OpenCore Picker by default(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.showpicker = True
        elif change_kext_menu in {"n", "N", "no", "No"}:
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
        change_kext_menu = input("Enable Vault(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.vault = True
        elif change_kext_menu in {"n", "N", "no", "No"}:
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
        change_kext_menu = input("Set SIP and SecureBootModel(ie. 1): ")
        if change_kext_menu == "1":
            self.constants.sip_status = True
            self.constants.secure_status = True
        elif change_kext_menu == "2":
            self.constants.sip_status = False
            self.constants.secure_status = True
        elif change_kext_menu == "3":
            self.constants.sip_status = True
            self.constants.secure_status = False
        elif change_kext_menu == "4":
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
        change_kext_menu = input("Assume iMac Nvidia patches(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            self.constants.imac_nvidia_build = True
        elif change_kext_menu in {"n", "N", "no", "No"}:
            self.constants.imac_nvidia_build = False
        else:
            print("Invalid option")

    def patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = [
                "Adjust Patcher Settings"
            ]
            menu = utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                # TODO: Enable setting OS target when more OSes become supported by the patcher
                #[f"Change OS version:\t\t\tCurrently macOS {self.constants.os_support}", self.change_os],
                [f"Enable Verbose Mode:\t\tCurrently {self.constants.verbose_debug}", self.change_verbose],
                [f"Enable OpenCore DEBUG:\t\tCurrently {self.constants.opencore_debug}", self.change_oc],
                [f"Enable Kext DEBUG:\t\t\tCurrently {self.constants.kext_debug}", self.change_kext],
                [f"Force iMac Metal Patch:\t\tCurrently {self.constants.imac_vendor}", self.change_metal],
                [f"Assume Upgraded Wifi Always:\tCurrently {self.constants.wifi_build}", self.change_wifi],
                [f"Set ShowPicker Mode:\t\tCurrently {self.constants.showpicker}", self.change_showpicker],
                [f"Set Vault Mode:\t\t\tCurrently {self.constants.vault}", self.change_vault],
                [f"Set SIP and SecureBootModel:\tSIP: {self.constants.sip_status} SBM: {self.constants.secure_status}", self.change_sip],
                [f"Set SMBIOS Mode:\t\t\tCurrently {self.constants.serial_settings}", self.change_serial],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def credits(self):
        utilities.TUIOnlyPrint(["Credits"], "Press [Enter] to go back.\n",
                               ["""Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - Khronokernel:\tWriting and maintaining this patcher
  - DhinakG:\t\tWriting and maintaining this patcher
  - Syncretic:\t\tAAAMouSSE and telemetrap
  - Slice:\t\tVoodooHDA
  - cdf:\t\tNightShiftEnabler"""]).start()

    def PatchVolume(self):
        utilities.cls()
        utilities.header(["Patching System Volume"])
        print("""Patches Root volume to fix misc issues such as:

- Audio
- Ethernet

Note: When the system volume is patched, you can no longer have Delta
updates or have FileVault enabled. Please think carefully if this is
desired.
        """)
        change_kext_menu = input("Patch System Volume?(y/n): ")
        if change_kext_menu in {"y", "Y", "yes", "Yes"}:
            SysPatch.PatchSysVolume(self.constants.custom_model or self.current_model, self.constants).start_patch()
        else:
            print("Returning to main menu")


    def main_menu(self):
        response = None
        ModelArray.SupportedSMBIOS = ModelArray.SupportedSMBIOS11
        while not (response and response == -1):
            title = [
                f"OpenCore Legacy Patcher v{self.constants.patcher_version}",
                f"Selected Model: {self.constants.custom_model or self.current_model}",
                f"Target OS: macOS {self.constants.os_support}",
            ]

            if (self.constants.custom_model or self.current_model) not in ModelArray.SupportedSMBIOS:
                in_between = [
                    'Your model is not supported by this patcher!',
                    '',
                    'If you plan to create the USB for another machine, please select the "Change Model" option in the menu.'
                ]
            elif not self.constants.custom_model and self.current_model in ("MacPro3,1", "iMac7,1") and \
                    "SSE4.1" not in subprocess.run("sysctl machdep.cpu.features".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode():
                in_between = [
                    'Your model requires a CPU upgrade to a CPU supporting SSE4.1+ to be supported by this patcher!',
                    '',
                    f'If you plan to create the USB for another {self.current_model} with SSE4.1+, please select the "Change Model" option in the menu.'
                ]
            elif self.constants.custom_model in ("MacPro3,1", "iMac7,1"):
                in_between = ["This model is supported",
                              "However please ensure the CPU has been upgraded to support SSE4.1+"
                              ]
            else:
                in_between = ["This model is supported"]

            menu = utilities.TUIMenu(title, "Please select an option: ", in_between=in_between, auto_number=True, top_level=True)

            options = (
                [["Build OpenCore", self.build_opencore]] if ((self.constants.custom_model or self.current_model) in ModelArray.SupportedSMBIOS) else []) + [
                ["Install OpenCore to USB/internal drive", self.install_opencore],
                ["Change Model", self.change_model],
                ["Patcher Settings", self.patcher_settings],
                #["Patch Volume", self.PatchVolume],
                ["Credits", self.credits]
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        if getattr(sys, "frozen", False):
            subprocess.run("""osascript -e 'tell application "Terminal" to close first window' & exit""", shell=True)


OpenCoreLegacyPatcher().main_menu()
