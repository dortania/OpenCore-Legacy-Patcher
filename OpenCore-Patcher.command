#!/usr/bin/env python3
# Copyright (C) 2020-2021 Mykola Grymalyuk

from __future__ import print_function

import subprocess
import sys
import time
import platform
import argparse
from pathlib import Path

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
            self.current_model = subprocess.run("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.current_model = [line.strip().split(": ", 1)[1] for line in self.current_model.stdout.decode().split("\n") if line.strip().startswith("Model Identifier")][0]
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])
        if self.current_model in ModelArray.NoAPFSsupport:
            self.constants.serial_settings = "Moderate"

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

        parser = argparse.ArgumentParser()

        # Generic args
        parser.add_argument('--build', help='Build OpenCore', action='store_true', required=False)
        parser.add_argument('--verbose', help='Enable verbose boot', action='store_true', required=False)
        parser.add_argument('--debug_oc', help='Enable OpenCore DEBUG', action='store_true', required=False)
        parser.add_argument('--debug_kext', help='Enable kext DEBUG', action='store_true', required=False)
        parser.add_argument('--skip_wifi', help='Skip wifi patches', action='store_true', required=False)
        parser.add_argument('--hide_picker', help='Hide OpenCore picker', action='store_true', required=False)
        parser.add_argument('--disable_sip', help='Disable SIP', action='store_true', required=False)
        parser.add_argument('--disable_smb', help='Disable SecureBootModel', action='store_true', required=False)
        parser.add_argument('--vault', help='Enable OpenCore Vaulting', action='store_true', required=False)

        # Args requiring value values
        parser.add_argument('--model', action='store', help='Set custom model', required=False)
        parser.add_argument('--gpu', action='store', help='Set Metal GPU Vendor', required=False)
        parser.add_argument('--smbios', action='store', help='Set SMBIOS patching mode', required=False)

        args = parser.parse_args()

        self.constants.gui_mode = True
        self.constants.current_path = Path.cwd()

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            print("- Rerouting payloads location")
            self.constants.payload_path = sys._MEIPASS / Path("payloads")
        else:
            print("- Using defaul payloads location")

        if args.verbose:
            print("- Set verbose configuration")
            self.constants.verbose_debug = True
        if args.debug_oc:
            print("- Set OpenCore DEBUG configuration")
            self.constants.opencore_debug = True
            self.constants.opencore_build = "DEBUG"
        if args.debug_kext:
            print("- Set kext DEBUG configuration")
            self.constants.kext_debug = True
        if args.skip_wifi:
            print("- Set wifi skip configuration")
            self.constants.wifi_build = True
        if args.hide_picker:
            print("- Set HidePicker configuration")
            self.constants.showpicker = False
        if args.disable_sip:
            print("- Set Disable SIP configuration")
            self.constants.sip_status = False
        if args.disable_smb:
            print("- Set Disable SecureBootModel configuration")
            self.constants.secure_status = False
        if args.vault:
            print("- Set Vault configuration")
            self.constants.vault = True

        if args.build:

            if args.model:
                print(f"- Using custom model: {args.model}")
                self.constants.custom_model = args.model
                self.build_opencore()
            else:
                print(f"- Using detected model: {self.current_model}")
                self.build_opencore()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).copy_efi()

OpenCoreLegacyPatcher()







