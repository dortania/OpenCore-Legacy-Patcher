#!/usr/bin/env python3
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

import subprocess
import sys
from pathlib import Path

from Resources import Build, CliMenu, Constants, ModelArray, SysPatch, Utilities, device_probe, os_probe, defaults, arguments
from Data import smbios_data, cpu_data

class OpenCoreLegacyPatcher:
    def __init__(self):
        print("- Loading...")
        self.constants = Constants.Constants()
        self.generate_base_data()
        if arguments.arguments().check_cli() is False:
            self.main_menu()
        
    def generate_base_data(self):
        self.constants.detected_os = os_probe.detect_kernel_major()
        self.constants.detected_os_minor = os_probe.detect_kernel_minor()
        self.constants.detected_os_build = os_probe.detect_kernel_build()
        self.constants.computer = device_probe.Computer.probe()
        self.constants.recovery_status = Utilities.check_recovery()
        self.computer = self.constants.computer
        defaults.generate_defaults.probe(self.computer.real_model, True, self.constants)
        if arguments.arguments().check_cli() is True:
            print("- Detected arguments, switching to CLI mode")
            self.constants.gui_mode = True # Assumes no user interaction is required
            self.constants.current_path = Path.cwd()
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                print("- Rerouting payloads location")
                self.constants.payload_path = sys._MEIPASS / Path("payloads")
            arguments.arguments().parse_arguments(self.constants)
        else:
            print("- No arguments present, loading TUI")

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).copy_efi()

    def patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Patcher Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                ["Debug Settings", self.patcher_setting_debug],
                ["Security Settings", self.patcher_settings_security],
                ["SMBIOS Settings", self.patcher_settings_smbios],
                ["Boot Volume Settings", self.patcher_settings_boot],
                ["Miscellaneous Settings", self.patcher_settings_misc],
                ["Dump detected hardware", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).dump_hardware],
                [
                    f"Allow Accel on Mojave/Catalina:\tCurrently {self.constants.moj_cat_accel}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_moj_cat_patch,
                ],
                [
                    f"Allow OpenCore on native Models:\tCurrently {self.constants.allow_oc_everywhere}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_native_models,
                ],
                ["Advanced Settings, for developers only", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).advanced_patcher_settings],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_setting_debug(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Debug Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Enable Verbose Mode:\tCurrently {self.constants.verbose_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_verbose],
                [f"Enable OpenCore DEBUG:\tCurrently {self.constants.opencore_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_oc],
                [f"Enable Kext DEBUG:\t\tCurrently {self.constants.kext_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_kext],
            ] + (
                [
                    [f"Set SurPlus Settings:\tCurrently {self.constants.force_surplus}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_surplus]
                ]
                if (smbios_data.smbios_dictionary[self.constants.custom_model or self.computer.real_model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge)
                else []
            )

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_security(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Security Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                # [
                #     f"Set Apple Mobile File Integrity (AMFI):\tCurrently {self.constants.amfi_status}",
                #     CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_amfi,
                # ],
                [
                    f"Set System Intrgity Protection (SIP):\tCurrently {self.constants.sip_status}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_sip,
                ],
                [
                    f"Set Secure Boot Model (SBM):\t\tCurrently {self.constants.secure_status}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_sbm,
                ],
                [f"Set Vault Mode:\t\t\t\tCurrently {self.constants.vault}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_vault],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_smbios(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust SMBIOS Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set SMBIOS Spoof Level:\tCurrently {self.constants.serial_settings}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_serial],
                [f"Set SMBIOS Spoof Model:\tCurrently {self.constants.override_smbios}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_smbios],
                [f"Set Custom name {self.constants.custom_cpu_model_value}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).custom_cpu],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_boot(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Bootable Volume Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set FireWire Boot:\tCurrently {self.constants.firewire_boot}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_firewire],
                [f"Set NVMe Boot:\tCurrently {self.constants.nvme_boot}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_nvme],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def patcher_settings_misc(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Miscellaneous Settings"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set ShowPicker Mode:\tCurrently {self.constants.showpicker}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_showpicker],
                [f"Set Wake on WLAN:\t\tCurrently {self.constants.enable_wake_on_wlan}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_wowl],
                [f"Set Ivy iMac iGPU:\t\tCurrently {self.constants.allow_ivy_igpu}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_ivy],
                [f"Set TeraScale 2 Accel:\tCurrently {self.constants.allow_ts2_accel}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).terascale_2_accel],
                [
                    f"Disable Thunderbolt:\tCurrently {self.constants.disable_tb}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).disable_tb,
                ],
                [f"Set AppleALC Usage:\t\tCurrently {self.constants.set_alc_usage}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).applealc_support],
                [f"Set Windows GMUX support:\tCurrently {self.constants.dGPU_switch}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).dGPU_switch_support],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def advanced_patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = ["Adjust Advanced Patcher Settings, for developers ONLY"]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                [f"Set Metal GPU Status:\t\tCurrently {self.constants.imac_vendor}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_metal],
                [f"Set DRM Preferences:\t\tCurrently {self.constants.drm_support}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).drm_setting],
                [f"Set Generic Bootstrap:\t\tCurrently {self.constants.boot_efi}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).bootstrap_setting],
                [
                    f"Disable CPU Friend:\t\t\tCurrently {self.constants.disallow_cpufriend}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).disable_cpufriend,
                ],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def main_menu(self):
        response = None
        while not (response and response == -1):
            title = [
                f"OpenCore Legacy Patcher v{self.constants.patcher_version}",
                f"Selected Model: {self.constants.custom_model or self.computer.real_model}",
            ]

            if (self.constants.custom_model or self.computer.real_model) not in ModelArray.SupportedSMBIOS and self.constants.allow_oc_everywhere is False:
                in_between = [
                    "Your model is not supported by this patcher for running unsupported OSes!",
                    "",
                    'If you plan to create the USB for another machine, please select the \n"Change Model" option in the menu.',
                    "",
                    'If you want to run OCLP on a native Mac, please toggle \n"Allow OpenCore on native Models" in settings',
                ]
            elif not self.constants.custom_model and self.computer.real_model == "iMac7,1" and "SSE4.1" not in self.computer.cpu.flags:
                in_between = [
                    "Your model requires a CPU upgrade to a CPU supporting SSE4.1+ to be supported by this patcher!",
                    "",
                    f'If you plan to create the USB for another {self.computer.real_model} with SSE4.1+, please select the "Change Model" option in the menu.',
                ]
            elif self.constants.custom_model == "iMac7,1":
                in_between = ["This model is supported", "However please ensure the CPU has been upgraded to support SSE4.1+"]
            else:
                in_between = ["This model is supported"]

            menu = Utilities.TUIMenu(title, "Please select an option: ", in_between=in_between, auto_number=True, top_level=True)

            options = (
                [["Build OpenCore", self.build_opencore]]
                if ((self.constants.custom_model or self.computer.real_model) in ModelArray.SupportedSMBIOS) or self.constants.allow_oc_everywhere is True
                else []
            ) + [
                ["Install OpenCore to USB/internal drive", self.install_opencore],
                ["Post-Install Volume Patch", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).PatchVolume],
                ["Change Model", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_model],
                ["Patcher Settings", self.patcher_settings],
                ["Credits", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).credits],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        if getattr(sys, "frozen", False) and self.constants.recovery_status is False:
            subprocess.run("""osascript -e 'tell application "Terminal" to close first window' & exit""", shell=True)


OpenCoreLegacyPatcher()
