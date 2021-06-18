#!/usr/bin/env python3
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

import platform
import subprocess
import sys

from Resources import (Build, CliMenu, Constants, ModelArray, SysPatch,
                       Utilities, device_probe)


class OpenCoreLegacyPatcher:
    def __init__(self):
        print("Loading...")
        self.constants = Constants.Constants()
        self.constants.computer = device_probe.Computer.probe()
        self.computer = self.constants.computer
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])
        self.set_defaults(self.computer.real_model, True)

        custom_cpu_model_value = Utilities.get_nvram("revcpuname", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if custom_cpu_model_value is not None:
            # TODO: Fix to not use two separate variables
            self.constants.custom_cpu_model = 1
            self.constants.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

        if "-v" in (Utilities.get_nvram("boot-args") or ""):
            self.constants.verbose_debug = True

        # Check if running in RecoveryOS
        self.constants.recovery_status = Utilities.check_recovery()

    def set_defaults(self, model, host_is_target):
        # Defaults
        self.constants.sip_status = True
        self.constants.secure_status = False  # Default false for Monterey
        self.constants.disable_amfi = False

        if model in ModelArray.LegacyGPU:
            if (
                host_is_target
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
                self.constants.disable_amfi = False
            else:
                self.constants.sip_status = False  # Unsigned kexts
                self.constants.secure_status = False  # Root volume modified
                self.constants.disable_amfi = True  # Unsigned binaries
        if model in ModelArray.ModernGPU:
            if host_is_target and model in ["iMac13,1", "iMac13,3"] and self.computer.dgpu:
                # Some models have a supported dGPU, others don't
                self.constants.sip_status = True
                # self.constants.secure_status = True  # Monterey
                #self.constants.disable_amfi = False  # Signed bundles, Don't need to explicitly set currently
            else:
                self.constants.sip_status = False  # Unsigned kexts
                self.constants.secure_status = False  # Modified root volume
                #self.constants.disable_amfi = False  # Signed bundles, Don't need to explicitly set currently

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
                [f"Enable Verbose Mode:\t\tCurrently {self.constants.verbose_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_verbose],
                [f"Enable OpenCore DEBUG:\t\tCurrently {self.constants.opencore_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_oc],
                [f"Enable Kext DEBUG:\t\t\tCurrently {self.constants.kext_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_kext],
                [f"Set ShowPicker Mode:\t\tCurrently {self.constants.showpicker}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_showpicker],
                [f"Set Vault Mode:\t\t\tCurrently {self.constants.vault}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_vault],
                [f"Allow FireWire Boot:\t\tCurrently {self.constants.firewire_boot}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_firewire],
                [f"Allow NVMe Boot:\t\t\tCurrently {self.constants.nvme_boot}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_nvme],
                [
                    f"Enable TeraScale 2 Acceleration:\tCurrently {self.constants.terascale_2_patch}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).enable_terascale,
                ],
                [f"Disable AMFI:\t\t\tCurrently {self.constants.disable_amfi}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_amfi],
                [
                    f"Set SIP and SecureBootModel:\tSIP: {self.constants.sip_status} SBM: {self.constants.secure_status}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_sip,
                ],
                [
                    f"Allow OpenCore on native Models:\tCurrently {self.constants.allow_oc_everywhere}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).allow_native_models,
                ],
                ["Advanced Patch Settings, for developers only", self.advanced_patcher_settings],
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
                [f"Assume Metal GPU Always:\t\tCurrently {self.constants.imac_vendor}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_metal],
                [f"Set SMBIOS Mode:\t\t\tCurrently {self.constants.serial_settings}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).change_serial],
                [f"DRM Preferences:\t\t\tCurrently {self.constants.drm_support}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).drm_setting],
                [f"Set Generic Bootstrap:\t\tCurrently {self.constants.boot_efi}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).bootstrap_setting],
                [
                    f"Disable CPU Friend:\t\t\tCurrently {self.constants.disallow_cpufriend}",
                    CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).disable_cpufriend,
                ],
                [f"Override SMBIOS Spoof:\t\tCurrently {self.constants.override_smbios}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_smbios],
                [f"Set Custom name {self.constants.custom_cpu_model_value}", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).custom_cpu],
                ["Set SeedUtil Status", CliMenu.MenuOptions(self.constants.custom_model or self.computer.real_model, self.constants).set_seedutil],
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

- Graphics Acceleration for non-Metal GPUs
  - Nvidia: Tesla - Fermi (8000-500 series)
  - Intel: Ironlake - Sandy Bridge
  - AMD: TeraScale 1 and 2 (2000-6000 series)
- Audio support for iMac7,1 and iMac8,1

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates or have FileVault
enabled.

Supported Options:

1. Patch System Volume
2. Unpatch System Volume (Experimental)
B. Exit
        """
        monterey = """Patches Root volume to fix misc issues such as:

- Graphics Acceleration
  - Intel: Ivy Bridge (4000 series iGPUs)
- Basic Framebuffer and brightness Control (No acceleration)
  - Nvidia: Tesla - Fermi (8000-500 series)
  - Intel: Ironlake - Sandy Bridge
  - AMD: TeraScale 1 and 2 (2000-6000 series)
- Audio support for iMac7,1 and iMac8,1

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates or have FileVault
enabled.

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
                    'If you plan to create the USB for another machine, please select the "Change Model" option in the menu.',
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
