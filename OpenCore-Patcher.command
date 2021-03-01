#!/usr/bin/env python3

from __future__ import print_function

import subprocess

from Resources import build, ModelArray, Constants, utilities

PATCHER_VERSION = "0.0.11"


class OpenCoreLegacyPatcher():
    def __init__(self):
        self.constants = Constants.Constants()
        self.custom_model: str = None
        self.current_model: str = None
        opencore_model: str = subprocess.run("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if not opencore_model.startswith("nvram: Error getting variable"):
            opencore_model = [line.strip().split(":oem-product	", 1)[1] for line in opencore_model.split("\n") if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
            self.current_model = opencore_model
        else:
            self.current_model = subprocess.run("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.current_model = [line.strip().split(": ", 1)[1] for line in self.current_model.stdout.decode().split("\n") if line.strip().startswith("Model Identifier")][0]

    def build_opencore(self):
        build.BuildOpenCore(self.custom_model or self.current_model, self.constants).build_opencore()

    def install_opencore(self):
        build.BuildOpenCore(self.custom_model or self.current_model, self.constants).copy_efi()

    def change_model(self):
        utilities.cls()
        utilities.header(["Select Different Model"])
        print("""
Tip: Run the following command on the target machine to find the model identifier:

system_profiler SPHardwareDataType | grep 'Model Identifier'
    """)
        self.custom_model = input("Please enter the model identifier of the target machine: ").strip()

    def credits(self):
        utilities.TUIOnlyPrint(["Credits"], "Press [Enter] to go back.\n",
                               ["""Many thanks to the following:

  - Acidanthera:\tOpenCore, kexts and other tools
  - Khronokernel:\tWriting and maintaining this patcher
  - DhinakG:\t\tWriting and maintaining this patcher
  - Syncretic:\t\tAAAMouSSE and telemetrap
  - Slice:\t\tVoodooHDA"""]).start()

    def main_menu(self):
        response = None
        while not (response and response == -1):
            title = [
                f"OpenCore Legacy Patcher v{self.constants.patcher_version}",
                f"Selected Model: {self.custom_model or self.current_model}"
            ]

            if (self.custom_model or self.current_model) not in ModelArray.SupportedSMBIOS:
                in_between = [
                    'Your model is not supported by this patcher!',
                    '',
                    'If you plan to create the USB for another machine, please select the "Change Model" option in the menu.'
                ]
            elif not self.custom_model and self.current_model in ("MacPro3,1", "iMac7,1") and \
                    "SSE4.1" not in subprocess.run("sysctl machdep.cpu.features".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode():
                in_between = [
                    'Your model requires a CPU upgrade to a CPU supporting SSE4.1+ to be supported by this patcher!',
                    '',
                    f'If you plan to create the USB for another {self.current_model} with SSE4.1+, please select the "Change Model" option in the menu.'
                ]
            elif self.custom_model in ("MacPro3,1", "iMac7,1"):
                in_between = ["This model is supported",
                              "However please ensure the CPU has been upgraded to support SSE4.1+"
                              ]
            else:
                in_between = ["This model is supported"]

            menu = utilities.TUIMenu(title, "Please select an option: ", in_between=in_between, auto_number=True, top_level=True)

            options = ([["Build OpenCore", self.build_opencore]] if ((self.custom_model or self.current_model) in ModelArray.SupportedSMBIOS) else []) + [
                ["Install OpenCore to USB/internal drive", self.install_opencore],
                ["Change Model", self.change_model],
                ["Credits", self.credits]
            ]

            for option in options:
                menu.add_menu_option(option[0], function=option[1])

            response = menu.start()

        print("Bye")


OpenCoreLegacyPatcher().main_menu()
