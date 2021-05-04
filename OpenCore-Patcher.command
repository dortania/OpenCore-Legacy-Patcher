#!/usr/bin/env python3
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

import binascii
import plistlib
import subprocess
import sys
import time
import platform

from Resources import Build, ModelArray, Constants, SysPatch, Utilities, CliMenu


class OpenCoreLegacyPatcher():
    def __init__(self):
        self.constants = Constants.Constants()
        self.current_model: str = None
        opencore_model: str = subprocess.run("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if not opencore_model.startswith("nvram: Error getting variable"):
            opencore_model = [line.strip().split(":oem-product	", 1)[1] for line in opencore_model.split("\n") if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
            self.current_model = opencore_model
        else:
            self.current_model = plistlib.loads(subprocess.run("system_profiler -detailLevel mini -xml SPHardwareDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.strip())[0]["_items"][0]["machine_model"]
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])
        if self.current_model in ModelArray.NoAPFSsupport:
            self.constants.serial_settings = "Moderate"
        if self.current_model in ModelArray.LegacyGPU:
            try:
                dgpu_devices = plistlib.loads(subprocess.run("ioreg -r -n GFX0 -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                dgpu_vendor = self.hexswap(binascii.hexlify(dgpu_devices[0]["vendor-id"]).decode()[:4])
                dgpu_device = self.hexswap(binascii.hexlify(dgpu_devices[0]["device-id"]).decode()[:4])
            except ValueError:
                dgpu_vendor = ""
                dgpu_device = ""

            if (dgpu_vendor == self.constants.pci_amd_ati and dgpu_device in ModelArray.AMDMXMGPUs) or (dgpu_vendor == self.constants.pci_nvidia and dgpu_device in ModelArray.NVIDIAMXMGPUs):
                self.constants.sip_status = True
                self.constants.secure_status = True
            else:
                self.constants.sip_status = False
                self.constants.secure_status = False

        # Logic for when user runs custom OpenCore build and do not expose it
        # Note: This logic currently only applies for iMacPro1,1 users, see below threads on the culprits:
        # - https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/post-17425857
        # - https://forums.macrumors.com/threads/opencore-on-the-mac-pro.2207814/
        # PLEASE FOR THE LOVE OF GOD JUST SET ExposeSensitiveData CORRECTLY!!!
        if self.current_model == "iMacPro1,1":
            serial: str = subprocess.run("system_profiler SPHardwareDataType | grep Serial".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
            serial = [line.strip().split("Number (system): ", 1)[1] for line in serial.split("\n") if line.strip().startswith("Serial")][0]
            true_model = subprocess.run([str(self.constants.macserial_path), "--info", str(serial)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            true_model = [i.partition(" - ")[2] for i in true_model.stdout.decode().split("\n") if "Model: " in i][0]
            print(f"True Model: {true_model}")
            if not true_model.startswith("Unknown"):
                self.current_model = true_model

        custom_cpu_model_value: str = subprocess.run("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:revcpuname".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()

        if not custom_cpu_model_value.startswith("nvram: Error getting variable"):
            custom_cpu_model_value = [line.strip().split(":revcpuname	", 1)[1] for line in custom_cpu_model_value.split("\n") if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
            if custom_cpu_model_value.split("%00")[0] != "":
                self.constants.custom_cpu_model = 1
                self.constants.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

    def hexswap(self, input_hex: str):
        hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
        hex_rev = hex_pairs[::-1]
        hex_str = "".join(["".join(x) for x in hex_rev])
        return hex_str.upper()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).copy_efi()

    def change_model(self):
        Utilities.cls()
        Utilities.header(["Select Different Model"])
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

    def patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = [
                "Adjust Patcher Settings"
            ]
            menu = Utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                # TODO: Enable setting OS target when more OSes become supported by the patcher
                #[f"Change OS version:\t\t\tCurrently macOS {self.constants.os_support}", self.change_os],
                [f"Enable Verbose Mode:\t\tCurrently {self.constants.verbose_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_verbose],
                [f"Enable OpenCore DEBUG:\t\tCurrently {self.constants.opencore_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_oc],
                [f"Enable Kext DEBUG:\t\t\tCurrently {self.constants.kext_debug}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_kext],
                [f"Assume Metal GPU Always:\t\tCurrently {self.constants.imac_vendor}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_metal],
                [f"Assume Upgraded Wifi Always:\tCurrently {self.constants.wifi_build}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_wifi],
                [f"Set ShowPicker Mode:\t\tCurrently {self.constants.showpicker}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_showpicker],
                [f"Set Vault Mode:\t\t\tCurrently {self.constants.vault}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_vault],
                [f"Set SIP and SecureBootModel:\tSIP: {self.constants.sip_status} SBM: {self.constants.secure_status}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_sip],
                [f"Set SMBIOS Mode:\t\t\tCurrently {self.constants.serial_settings}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).change_serial],
                [f"DRM Preferences:\t\t\tCurrently {self.constants.drm_support}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).drm_setting],
                [f"Set Generic Bootstrap:\t\t{self.constants.boot_efi}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).bootstrap_setting],
                [f"Set Acceleration Patches:\t\t{self.constants.legacy_acceleration_patch}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).accel_setting],
                [f"Assume Legacy GPU:\t\t\t{self.constants.assume_legacy}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).force_accel_setting],
                [f"Allow OpenCore on native Models:\t{self.constants.allow_oc_everywhere}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).allow_native_models],
                [f"Download more RAM:\t\t\t{self.constants.download_ram}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).download_more_ram_dot_com],
                [f"Set Custom name {self.constants.custom_cpu_model_value}", CliMenu.MenuOptions(self.constants.custom_model or self.current_model, self.constants).custom_cpu],
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

    def credits(self):
        Utilities.TUIOnlyPrint(["Credits"], "Press [Enter] to go back.\n",
                               ["""Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - Khronokernel:\tWriting and maintaining this patcher
  - DhinakG:\t\tWriting and maintaining this patcher
  - ASentientBot:\tLegacy Acceleration Patches
  - Ausdauersportler:\tLinking fixes for SNBGraphicsFB and AMDX3000
  - Syncretic:\t\tAAAMouSSE and telemetrap
  - cdf:\t\tNightShiftEnabler"""]).start()

    def PatchVolume(self):
        Utilities.cls()
        Utilities.header(["Patching System Volume"])
        print("""Patches Root volume to fix misc issues such as:

- Graphics Acceleration for non-Metal GPUs
  - Nvidia: Tesla - Fermi (8000-500 series)
  - Intel: Ironlake - Sandy Bridge
  - AMD: TeraScale 1 (2000-4000 series)

WARNING: Root Volume Patching is still in active development, please
have all important user data backed up. Note when the system volume
is patched, you can no longer have Delta updates or have FileVault
enabled.

Supported Options:

1. Patch System Volume
2. Unpatch System Volume (Experimental)
B. Exit
        """)
        change_menu = input("Patch System Volume?: ")
        if change_menu == "1":
            SysPatch.PatchSysVolume(self.constants.custom_model or self.current_model, self.constants).start_patch()
        elif change_menu == "2":
            SysPatch.PatchSysVolume(self.constants.custom_model or self.current_model, self.constants).start_unpatch()
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

            if (self.constants.custom_model or self.current_model) not in ModelArray.SupportedSMBIOS and self.constants.allow_oc_everywhere is False:
                in_between = [
                    'Your model is not supported by this patcher for running unsupported OSes!',
                    '',
                    'If you plan to create the USB for another machine, please select the "Change Model" option in the menu.'
                ]
            elif not self.constants.custom_model and self.current_model == "iMac7,1" and \
                    "SSE4.1" not in subprocess.run("sysctl machdep.cpu.features".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode():
                in_between = [
                    'Your model requires a CPU upgrade to a CPU supporting SSE4.1+ to be supported by this patcher!',
                    '',
                    f'If you plan to create the USB for another {self.current_model} with SSE4.1+, please select the "Change Model" option in the menu.'
                ]
            elif self.constants.custom_model == "iMac7,1":
                in_between = ["This model is supported",
                              "However please ensure the CPU has been upgraded to support SSE4.1+"
                              ]
            else:
                in_between = ["This model is supported"]

            menu = Utilities.TUIMenu(title, "Please select an option: ", in_between=in_between, auto_number=True, top_level=True)

            options = (
                [["Build OpenCore", self.build_opencore]] if ((self.constants.custom_model or self.current_model) in ModelArray.SupportedSMBIOS) or self.constants.allow_oc_everywhere is True else []) + [
                ["Install OpenCore to USB/internal drive", self.install_opencore],
                ["Post-Install Volume Patch", self.PatchVolume],
                ["Change Model", self.change_model],
                ["Patcher Settings", self.patcher_settings],
                ["Credits", self.credits]
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        if getattr(sys, "frozen", False):
            subprocess.run("""osascript -e 'tell application "Terminal" to close first window' & exit""", shell=True)


OpenCoreLegacyPatcher().main_menu()
