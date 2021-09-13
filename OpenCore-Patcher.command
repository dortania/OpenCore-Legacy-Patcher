#!/usr/bin/env python3
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

import platform
import subprocess
import sys

from Resources import Build, CliMenu, Constants, ModelArray, SysPatch, Utilities, device_probe


class OpenCoreLegacyPatcher:
    def __init__(self):
        print("Loading...")
        self.constants = Constants.Constants()
        self.constants.computer = device_probe.Computer.probe()
        self.computer = self.constants.computer
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])
        self.constants.detected_os_minor = int(platform.uname().release.partition(".")[2].partition(".")[0])
        self.set_defaults(self.computer.real_model, True)

    def set_defaults(self, model, host_is_target):
        # Defaults
        self.constants.sip_status = True
        self.constants.secure_status = False  # Default false for Monterey
        self.constants.amfi_status = True

        if model in ModelArray.LegacyGPU:
            if (
                host_is_target
                and self.computer.dgpu
                and self.computer.dgpu.arch
                in [
                    device_probe.AMD.Archs.Legacy_GCN,
                    device_probe.AMD.Archs.Polaris,
                    device_probe.AMD.Archs.Vega,
                    device_probe.AMD.Archs.Navi,
                    device_probe.NVIDIA.Archs.Kepler,
                ]
            ):
                # Building on device and we have a native, supported GPU
                self.constants.sip_status = True
                # self.constants.secure_status = True  # Monterey
                self.constants.amfi_status = True
            else:
                self.constants.sip_status = False  #    Unsigned kexts
                self.constants.secure_status = False  # Root volume modified
                self.constants.amfi_status = False  #   Unsigned binaries
                self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
        if model in ModelArray.ModernGPU:
            if host_is_target and model in ["iMac13,1", "iMac13,3"] and self.computer.dgpu:
                # Some models have a supported dGPU, others don't
                self.constants.sip_status = True
                # self.constants.secure_status = True  # Monterey
                # self.constants.amfi_status = True  #  Signed bundles, Don't need to explicitly set currently
            else:
                self.constants.sip_status = False  #    Unsigned kexts
                self.constants.secure_status = False  # Modified root volume
                self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
                # self.constants.amfi_status = True  #  Signed bundles, Don't need to explicitly set currently
        if model == "MacBook8,1":
            # MacBook8,1 has an odd bug where it cannot install Monterey with Minimal spoofing
            self.constants.serial_settings = "Moderate"

        custom_cpu_model_value = Utilities.get_nvram("revcpuname", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if custom_cpu_model_value is not None:
            # TODO: Fix to not use two separate variables
            self.constants.custom_cpu_model = 1
            self.constants.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

        if "-v" in (Utilities.get_nvram("boot-args") or ""):
            self.constants.verbose_debug = True

        if Utilities.amfi_status() is False:
            self.constants.amfi_status = False

        self.constants.latebloom_delay, self.constants.latebloom_range, self.constants.latebloom_debug = Utilities.latebloom_detection(model)

        # Check if running in RecoveryOS
        self.constants.recovery_status = Utilities.check_recovery()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).copy_efi()

    def change_model(self):
        Utilities.cls()
        Utilities.header(["Select Different Model"])
        print(
            """
Tip: Run the following command on the target machine to find the model identifier:

system_profiler SPHardwareDataType | grep 'Model Identifier'
    """
        )
        self.constants.custom_model = input("Please enter the model identifier of the target machine: ").strip()
        if self.constants.custom_model not in ModelArray.SupportedSMBIOS:
            print(
                f"""
{self.constants.custom_model} is not a valid SMBIOS Identifier for macOS {self.constants.os_support}!
"""
            )
            print_models = input(f"Print list of valid options for macOS {self.constants.os_support}? (y/n)")
            if print_models.lower() in {"y", "yes"}:
                print("\n".join(ModelArray.SupportedSMBIOS))
                input("\nPress [ENTER] to continue")
        else:
            self.set_defaults(self.constants.custom_model, False)

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
                ["Advanced Settings, for developers only", self.advanced_patcher_settings],
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
                    [
                        f"Set Latebloom args:\t\tDelay {self.constants.latebloom_delay}, Range {self.constants.latebloom_range}, Debug {self.constants.latebloom_debug}",
                        CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).latebloom_settings,
                    ]
                ]
                if ((self.constants.custom_model or self.computer.real_model) in ModelArray.PCIRaceCondition)
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
                [
                    f"Set Apple Mobile File Integrity (AMFI):\tCurrently {self.constants.amfi_status}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_amfi,
                ],
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
                    f"Disable Thunderbolt:\tCurrently {self.constants.disable_thunderbolt}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).disable_thunderbolt,
                ],
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

    def credits(self):
        Utilities.TUIOnlyPrint(
            ["Credits"],
            "Press [Enter] to go back.\n",
            [
                """Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - Khronokernel:\tWriting and maintaining this patcher
  - DhinakG:\t\tWriting and maintaining this patcher
  - ASentientBot:\tLegacy Acceleration Patches
  - Ausdauersportler:\tLinking fixes for SNBGraphicsFB and AMDX3000
  - Syncretic:\t\tAAAMouSSE and telemetrap
  - cdf:\t\tNightShiftEnabler and Innie"""
            ],
        ).start()

    def PatchVolume(self):
        Utilities.cls()
        Utilities.header(["Patching System Volume"])
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
- Non-Metal Graphics Accelertation
  - Intel: Ironlake - Sandy Bridge
  - Nvidia: Tesla - Fermi (8000-500 series)
  - AMD: TeraScale 1 (2000-4000 series)
- Basic Framebuffer and brightness Control (No acceleration)
  - AMD: TeraScale 2 (5000-6000 series)
- Audio support for iMac7,1 and iMac8,1

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates.

Supported Options:

1. Patch System Volume
2. Unpatch System Volume (Experimental)
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
2. Unpatch System Volume (Experimental)
B. Exit
         """

        default = """
This OS has no root patches available to apply, please ensure you're patching a booted
install that requires root patches such as macOS Big Sur or Monterey

Supported Options:

B. Exit
        """
        no_patch = False
        if self.constants.detected_os == self.constants.monterey:
            print(monterey)
        elif self.constants.detected_os == self.constants.big_sur:
            print(big_sur)
        elif self.constants.detected_os in [self.constants.mojave, self.constants.catalina] and self.constants.moj_cat_accel == True:
            print(mojave_catalina)
        else:
            print(default)
            no_patch = True
        change_menu = input("Patch System Volume?: ")
        if no_patch is not True and change_menu == "1":
            SysPatch.PatchSysVolume(self.constants.custom_model or self.computer.real_model, self.constants).start_patch()
        elif no_patch is not True and change_menu == "2":
            SysPatch.PatchSysVolume(self.constants.custom_model or self.computer.real_model, self.constants).start_unpatch()
        else:
            print("Returning to main menu")

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
                ["Post-Install Volume Patch", self.PatchVolume],
                ["Change Model", self.change_model],
                ["Patcher Settings", self.patcher_settings],
                ["Credits", self.credits],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        if getattr(sys, "frozen", False) and self.constants.recovery_status is False:
            subprocess.run("""osascript -e 'tell application "Terminal" to close first window' & exit""", shell=True)


OpenCoreLegacyPatcher().main_menu()
