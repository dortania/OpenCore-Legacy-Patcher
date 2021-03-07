#!/usr/bin/env python3

from __future__ import print_function

import subprocess, sys, time

from Resources import build, ModelArray, Constants, utilities


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
            print(f"{self.constants.custom_model} is not a valid SMBIOS Identifier!")
            print_models = input("Print list of valid options? (y/n)")
            if print_models in {"y", "Y", "yes", "Yes"}:
                print("\n".join(ModelArray.SupportedSMBIOS))
                input("Press any key to continue...")

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
        elif change_oc_menu in {"n", "N", "no", "No"}:
            self.constants.opencore_debug = False
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

    def patcher_settings(self):
        response = None
        while not (response and response == -1):
            title = [
                "Adjust Patcher Settings"
            ]
            menu = utilities.TUIMenu(title, "Please select an option: ", auto_number=True, top_level=True)
            options = [
                # TODO: Enable setting OS target when more OSes become supported by the patcher
                #[f"Change OS version:\t\tCurrently macOS {self.constants.os_support}", self.change_os],
                [f"Enable Verbose Mode:\tCurrently {self.constants.verbose_debug}", self.change_verbose],
                # TODO: Enable setting OC DEBUG when path handling for DEBUg files is resolved
                #[f"Enable OpenCore DEBUG:\tCurrently {self.constants.opencore_debug}", self.change_oc],
                [f"Enable Kext DEBUG:\t\tCurrently {self.constants.kext_debug}", self.change_kext]
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])
        
            response = menu.start()


            input("Press any key to continue...")

    def credits(self):
        utilities.TUIOnlyPrint(["Credits"], "Press [Enter] to go back.\n",
                               ["""Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - Khronokernel:\tWriting and maintaining this patcher
  - DhinakG:\t\tWriting and maintaining this patcher
  - Syncretic:\t\tAAAMouSSE and telemetrap
  - Slice:\t\tVoodooHDA
  - cdf:\t\tNightShiftEnabler"""]).start()

    def main_menu(self):
        response = None
        while not (response and response == -1):
            title = [
                f"OpenCore Legacy Patcher v{self.constants.patcher_version}",
                f"Selected Model: {self.constants.custom_model or self.current_model}"
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

            options = ([["Build OpenCore", self.build_opencore]] if ((self.constants.custom_model or self.current_model) in ModelArray.SupportedSMBIOS) else []) + [
                ["Install OpenCore to USB/internal drive", self.install_opencore],
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
