#!/usr/bin/env python3
# Copyright (C) 2020-2021 Mykola Grymalyuk

from __future__ import print_function

import subprocess
import sys
import platform
import argparse
from pathlib import Path

from Resources import Build, ModelArray, Constants, SysPatch, device_probe, Utilities


class OpenCoreLegacyPatcher():
    def __init__(self):
        print("Loading...")
        self.constants = Constants.Constants()
        self.constants.computer = device_probe.Computer.probe()
        self.computer = self.constants.computer
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])

        custom_cpu_model_value = Utilities.get_nvram("revcpuname", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        if custom_cpu_model_value is not None:
            # TODO: Fix to not use two separate variables
            self.constants.custom_cpu_model = 1
            self.constants.custom_cpu_model_value = custom_cpu_model_value.split("%00")[0]

        if "-v" in (Utilities.get_nvram("boot-args") or ""):
            self.constants.verbose_debug = True

        # Check if running in RecoveryOS
        self.constants.recovery_status = Utilities.check_recovery()

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
        parser.add_argument('--firewire', help='Enable FireWire Booting', action='store_true', required=False)
        parser.add_argument('--nvme', help='Enable NVMe Booting', action='store_true', required=False)
        parser.add_argument('--disable_amfi', help='Disable AMFI', action='store_true', required=False)

        # Building args requiring value values
        parser.add_argument('--model', action='store', help='Set custom model', required=False)
        parser.add_argument('--metal_gpu', action='store', help='Set Metal GPU Vendor', required=False)
        parser.add_argument('--smbios_spoof', action='store', help='Set SMBIOS patching mode', required=False)

        # SysPatch args
        parser.add_argument('--patch_sys_vol', help='Patches root volume', action='store_true', required=False)
        parser.add_argument('--unpatch_sys_vol', help='Unpatches root volume, EXPERIMENTAL', action='store_true', required=False)
        parser.add_argument('--terascale_2', help='Enable TeraScale 2 Acceleration', action='store_true', required=False)

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
        if args.firewire:
            print("- Set FireWire Boot configuration")
            self.constants.firewire_boot = True
        if args.nvme:
            print("- Set NVMe Boot configuration")
            self.constants.nvme_boot = True
        if args.disable_amfi:
            print("- Set Disable AMFI configuration")
            self.constants.disable_amfi = True
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

        if args.build:
            if args.model:
                print(f"- Using custom model: {args.model}")
                self.constants.custom_model = args.model
                self.set_defaults(self.constants.custom_model, False)
                self.build_opencore()
            else:
                print(f"- Using detected model: {self.constants.computer.real_model}")
                self.build_opencore()
        if args.patch_sys_vol:
            if args.terascale_2:
                print("- Set TeraScale 2 Accel configuration")
                self.constants.terascale_2_patch = True
            print("- Set System Volume patching")
            self.patch_vol()
        elif args.unpatch_sys_vol:
            print("- Set System Volume unpatching")
            self.unpatch_vol()

    def set_defaults(self, model, host_is_target):
        # Defaults
        self.constants.sip_status = True
        self.constants.secure_status = False  # Default false for Monterey
        self.constants.disable_amfi = False

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
        if model == "MacBook8,1":
            # MacBook8,1 has an odd bug where it cannot install Monterey with Minimal spoofing
            self.constants.serial_settings == "Moderate"

    def patch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_patch()

    def unpatch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_unpatch()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).copy_efi()

OpenCoreLegacyPatcher()

# Example arg for OCLP command line
# ./OCLP-CLI --build --verbose --debug_oc --debug_kext --model iMac11,2