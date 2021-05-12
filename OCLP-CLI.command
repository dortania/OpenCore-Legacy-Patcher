#!/usr/bin/env python3
# Copyright (C) 2020-2021 Mykola Grymalyuk

from __future__ import print_function

import subprocess
import sys
import platform
import argparse
from pathlib import Path

from Resources import Build, ModelArray, PCIIDArray, Constants, SysPatch, DeviceProbe


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
        if self.current_model in ModelArray.LegacyGPU:
            dgpu_vendor,dgpu_device,dgpu_acpi = DeviceProbe.pci_probe().gpu_probe("GFX0")
            if dgpu_vendor:
                if (dgpu_vendor == self.constants.pci_amd_ati and (dgpu_device in PCIIDArray.amd_ids().polaris_ids or dgpu_device in PCIIDArray.amd_ids().vega_ids or dgpu_device in PCIIDArray.amd_ids().navi_ids or dgpu_device in PCIIDArray.amd_ids().legacy_gcn_ids)) or (dgpu_vendor == self.constants.pci_nvidia and dgpu_device in PCIIDArray.nvidia_ids().kepler_ids):
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


        parser = argparse.ArgumentParser()

        # Generic building args
        parser.add_argument('--build', help='Build OpenCore', action='store_true', required=False)
        parser.add_argument('--verbose', help='Enable verbose boot', action='store_true', required=False)
        parser.add_argument('--debug_oc', help='Enable OpenCore DEBUG', action='store_true', required=False)
        parser.add_argument('--debug_kext', help='Enable kext DEBUG', action='store_true', required=False)
        parser.add_argument('--skip_wifi', help='Skip wifi patches', action='store_true', required=False)
        parser.add_argument('--hide_picker', help='Hide OpenCore picker', action='store_true', required=False)
        parser.add_argument('--disable_sip', help='Disable SIP', action='store_true', required=False)
        parser.add_argument('--disable_smb', help='Disable SecureBootModel', action='store_true', required=False)
        parser.add_argument('--vault', help='Enable OpenCore Vaulting', action='store_true', required=False)
        parser.add_argument('--support_all', help='Allow OpenCore on natively supported Models', action='store_true', required=False)
        parser.add_argument('--force_legacy', help='Allow acceleration on Mac Pros and Xserves', action='store_true', required=False)

        # Building args requiring value values
        parser.add_argument('--model', action='store', help='Set custom model', required=False)
        parser.add_argument('--metal_gpu', action='store', help='Set Metal GPU Vendor', required=False)
        parser.add_argument('--smbios_spoof', action='store', help='Set SMBIOS patching mode', required=False)

        # SysPatch args
        parser.add_argument('--patch_sys_vol', help='Patches root volume', action='store_true', required=False)
        parser.add_argument('--unpatch_sys_vol', help='Unpatches root volume, EXPERIMENTAL', action='store_true', required=False)

        args = parser.parse_args()

        self.constants.gui_mode = True
        self.constants.current_path = Path.cwd()

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            print("- Rerouting payloads location")
            self.constants.payload_path = sys._MEIPASS / Path("payloads")
        else:
            print("- Using default payloads location")

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
        if args.metal_gpu:
            if args.metal_gpu == "Nvidia":
                print("- Set Metal GPU patches to Nvidia")
                self.constants.metal_build = True
                self.constants.imac_vendor = "Nvidia"
            elif args.metal_gpu == "AMD":
                print("- Set Metal GPU patches to AMD")
                self.constants.metal_build = True
                self.constants.imac_vendor = "AMD"
            else:
                print(f"- Unknown GPU arg passed: {args.metal_gpu}")
                self.constants.metal_build = False
                self.constants.imac_vendor = "None"
        if args.smbios_spoof:
            if args.smbios_spoof == "Minimal":
                self.constants.serial_settings = "Minimal"
            elif args.smbios_spoof == "Moderate":
                self.constants.serial_settings = "Moderate"
            elif args.smbios_spoof == "Advanced":
                self.constants.serial_settings = "Advanced"
            else:
                print(f"- Unknown SMBIOS arg passed: {args.smbios_spoof}")

        if args.support_all:
            print("- Building for natively supported model")
            self.constants.allow_oc_everywhere = True
            self.constants.serial_settings = "None"

        if args.force_legacy:
            print("- Allowing legacy acceleration patches on newer models")
            self.constants.assume_legacy = True

        if args.build:
            if args.model:
                print(f"- Using custom model: {args.model}")
                self.constants.custom_model = args.model
                self.build_opencore()
            else:
                print(f"- Using detected model: {self.current_model}")
                self.build_opencore()
        if args.patch_sys_vol:
            print("- Set System Volume patching")
            self.patch_vol()
        elif args.unpatch_sys_vol:
            print("- Set System Volume unpatching")
            self.unpatch_vol()

    def hexswap(self, input_hex: str):
        hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
        hex_rev = hex_pairs[::-1]
        hex_str = "".join(["".join(x) for x in hex_rev])
        return hex_str.upper()

    def patch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.current_model, self.constants).start_patch()

    def unpatch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.current_model, self.constants).start_unpatch()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.current_model, self.constants).copy_efi()

OpenCoreLegacyPatcher()

# Example arg for OCLP command line
# ./OCLP-CLI --build --verbose --debug_oc --debug_kext --model iMac11,2