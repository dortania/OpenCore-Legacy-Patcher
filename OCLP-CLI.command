#!/usr/bin/env python3
# Copyright (C) 2020-2021 Mykola Grymalyuk

from __future__ import print_function

import subprocess
import sys
import platform
import argparse
from pathlib import Path

from Resources import Build, ModelArray, Constants, SysPatch, device_probe, Utilities, ModelExample


class OpenCoreLegacyPatcher:
    def __init__(self):
        print("Loading...")
        Utilities.disable_cls()
        self.constants = Constants.Constants()
        self.constants.computer = device_probe.Computer.probe()
        self.computer = self.constants.computer
        self.constants.detected_os = int(platform.uname().release.partition(".")[0])
        self.constants.detected_os_minor = int(platform.uname().release.partition(".")[2].partition(".")[0])
        detected_os_build: str = subprocess.run("sw_vers -buildVersion".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        self.constants.detected_os_build = detected_os_build

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
        parser.add_argument("--build", help="Build OpenCore", action="store_true", required=False)
        parser.add_argument("--verbose", help="Enable verbose boot", action="store_true", required=False)
        parser.add_argument("--debug_oc", help="Enable OpenCore DEBUG", action="store_true", required=False)
        parser.add_argument("--debug_kext", help="Enable kext DEBUG", action="store_true", required=False)
        parser.add_argument("--hide_picker", help="Hide OpenCore picker", action="store_true", required=False)
        parser.add_argument("--disable_sip", help="Disable SIP", action="store_true", required=False)
        parser.add_argument("--disable_smb", help="Disable SecureBootModel", action="store_true", required=False)
        parser.add_argument("--vault", help="Enable OpenCore Vaulting", action="store_true", required=False)
        parser.add_argument("--support_all", help="Allow OpenCore on natively supported Models", action="store_true", required=False)
        parser.add_argument("--firewire", help="Enable FireWire Booting", action="store_true", required=False)
        parser.add_argument("--nvme", help="Enable NVMe Booting", action="store_true", required=False)
        parser.add_argument("--wlan", help="Enable Wake on WLAN support", action="store_true", required=False)
        # parser.add_argument("--disable_amfi", help="Disable AMFI", action="store_true", required=False)
        parser.add_argument("--moderate_smbios", help="Moderate SMBIOS Patching", action="store_true", required=False)
        parser.add_argument("--moj_cat_accel", help="Allow Root Patching on Mojave and Catalina", action="store_true", required=False)
        parser.add_argument("--disable_thunderbolt", help="Disable Thunderbolt on 2013-2014 MacBook Pros", action="store_true", required=False)

        # Building args requiring value values (ie. --model iMac12,2)
        parser.add_argument("--model", action="store", help="Set custom model", required=False)
        parser.add_argument("--disk", action="store", help="Specifies disk to install to", required=False)
        parser.add_argument("--smbios_spoof", action="store", help="Set SMBIOS patching mode", required=False)
        parser.add_argument("--lb_delay", action="store", help="Set Latebloom delay in ms", required=False)
        parser.add_argument("--lb_range", action="store", help="Set Latebloom range in ms", required=False)
        parser.add_argument("--lb_debug", action="store", help="Set Latebloom debug", required=False)

        # SysPatch args
        parser.add_argument("--patch_sys_vol", help="Patches root volume", action="store_true", required=False)
        parser.add_argument("--unpatch_sys_vol", help="Unpatches root volume, EXPERIMENTAL", action="store_true", required=False)
        # parser.add_argument("--patch_disk", action="store", help="Specifies disk to root patch", required=False)

        parser.add_argument("--validate", help="Validate", action="store_true", required=False)

        args = parser.parse_args()

        self.constants.gui_mode = True
        self.constants.current_path = Path.cwd()

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            print("- Rerouting payloads location")
            self.constants.payload_path = sys._MEIPASS / Path("payloads")
        else:
            print("- Using default payloads location")

        if args.disk:
            print(f"- Install Disk set: {args.disk}")
            self.constants.disk = args.disk
        if args.validate:
            self.validate()
        # if args.patch_disk:
        #    print(f"- Patch Disk set: {args.patch_disk}")
        #    self.constants.patch_disk = args.patch_disk
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
        # if args.disable_amfi:
        #     print("- Set Disable AMFI configuration")
        #     self.constants.amfi_status = False
        if args.wlan:
            print("- Set Wake on WLAN configuration")
            self.constants.enable_wake_on_wlan = True
        if args.disable_thunderbolt:
            print("- Set Disable Thunderbolt configuration")
            self.constants.disable_thunderbolt = True
        if args.moderate_smbios:
            print("- Set Moderate SMBIOS Patching configuration")
            self.constants.serial_settings = "Moderate"
        if args.smbios_spoof:
            if args.smbios_spoof == "Minimal":
                self.constants.serial_settings = "Minimal"
            elif args.smbios_spoof == "Moderate":
                self.constants.serial_settings = "Moderate"
            elif args.smbios_spoof == "Advanced":
                self.constants.serial_settings = "Advanced"
            else:
                print(f"- Unknown SMBIOS arg passed: {args.smbios_spoof}")

        if args.lb_delay:
            try:
                self.constants.latebloom_delay = int(args.lb_delay)
                print(f"- Set LateBloom delay: {args.lb_delay}")
            except ValueError:
                print(f"- Invalid LateBloom delay: {args.lb_delay}")

        if args.lb_range:
            try:
                self.constants.latebloom_range = int(args.lb_range)
                print(f"- Set LateBloom range: {args.lb_range}")
            except ValueError:
                print(f"- Invalid LateBloom range: {args.lb_range}")

        if args.lb_debug:
            try:
                self.constants.latebloom_debug = int(args.lb_debug)
                if self.constants.latebloom_debug in [0, 1]:
                    print(f"- Set LateBloom debug: {args.lb_debug}")
                else:
                    print(f"- Invalid LateBloom debug: {args.lb_debug}")
            except ValueError:
                print(f"- Invalid LateBloom range: {args.lb_debug}")

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
            elif self.computer.real_model not in ModelArray.SupportedSMBIOS and self.constants.allow_oc_everywhere is False:
                print(
                    """Your model is not supported by this patcher for running unsupported OSes!"

If you plan to create the USB for another machine, please select the "Change Model" option in the menu."""
                )
                sys.exit(1)
            else:
                print(f"- Using detected model: {self.constants.computer.real_model}")
                self.set_defaults(self.constants.custom_model, True)
                self.build_opencore()
        if args.patch_sys_vol:
            if args.moj_cat_accel:
                print("- Set Mojave/Catalina root patch configuration")
                self.constants.moj_cat_accel = True
            print("- Set System Volume patching")
            self.patch_vol()
        elif args.unpatch_sys_vol:
            print("- Set System Volume unpatching")
            self.unpatch_vol()

    def set_defaults(self, model, host_is_target):
        if host_is_target:
            if Utilities.check_metal_support(device_probe, self.computer) is False:
                self.constants.disable_cs_lv = True
            if self.computer.dgpu and self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                self.constants.sip_status = False
                self.constants.amfi_status = True
                self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
        elif model in ModelArray.LegacyGPU:
            self.constants.disable_cs_lv = True
        if model in ModelArray.LegacyGPU:
            if host_is_target and Utilities.check_metal_support(device_probe, self.computer) is True:
                # Building on device and we have a native, supported GPU
                if self.computer.dgpu and self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                    self.constants.sip_status = False
                    # self.constants.secure_status = True  # Monterey
                    self.constants.amfi_status = True
                    self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
                else:
                    self.constants.sip_status = True
                    # self.constants.secure_status = True  # Monterey
                    self.constants.amfi_status = True
            else:
                self.constants.sip_status = False  #    Unsigned kexts
                self.constants.secure_status = False  # Root volume modified
                self.constants.amfi_status = False  #   Unsigned binaries
                self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
        if model in ModelArray.ModernGPU:
            self.constants.sip_status = False  #    Unsigned kexts
            self.constants.secure_status = False  # Modified root volume
            self.constants.allow_fv_root = True  #  Allow FileVault on broken seal
            # self.constants.amfi_status = True  #  Signed bundles, Don't need to explicitly set currently
        if model == "MacBook8,1":
            # MacBook8,1 has an odd bug where it cannot install Monterey with Minimal spoofing
            self.constants.serial_settings == "Moderate"

        if self.constants.latebloom_delay == 0:
            self.constants.latebloom_delay, self.constants.latebloom_range, self.constants.latebloom_debug = Utilities.latebloom_detection(model)

        if Utilities.get_nvram("gpu-power-prefs", "FA4CE28D-B62F-4C99-9CC3-6815686E30F9", decode=True):
            self.constants.allow_ts2_accel = False

    def patch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_patch()

    def unpatch_vol(self):
        SysPatch.PatchSysVolume(self.constants.custom_model or self.constants.computer.real_model, self.constants).start_unpatch()

    def build_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).build_opencore()

    def install_opencore(self):
        Build.BuildOpenCore(self.constants.custom_model or self.constants.computer.real_model, self.constants).copy_efi()

    def validate(self):
        # Runs through ocvalidate to check for errors

        valid_dumps = [
            ModelExample.MacBookPro.MacBookPro92_Stock,
            # ModelExample.MacBookPro.MacBookPro171_Stock,
            # ModelExample.Macmini.Macmini91_Stock,
            ModelExample.iMac.iMac81_Stock,
            ModelExample.iMac.iMac112_Stock,
            ModelExample.iMac.iMac122_Upgraded,
            ModelExample.MacPro.MacPro31_Stock,
            ModelExample.MacPro.MacPro31_Upgrade,
            ModelExample.MacPro.MacPro31_Modern_AMD,
            ModelExample.MacPro.MacPro31_Modern_Kepler,
            ModelExample.MacPro.MacPro41_Upgrade,
            ModelExample.MacPro.MacPro41_Modern_AMD,
            ModelExample.MacPro.MacPro41_51__Flashed_Modern_AMD,
        ]
        self.constants.validate = True

        for model in ModelArray.SupportedSMBIOS:
            print(f"Validating predefined model: {model}")
            self.constants.custom_model = model
            self.build_opencore()
            result = subprocess.run([self.constants.ocvalidate_path, f"{self.constants.opencore_release_folder}/EFI/OC/config.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("Error on build!")
                print(result.stdout.decode())
                raise Exception(f"Validation failed for predefined model: {model}")
            else:
                print(f"Validation succeeded for predefined model: {model}")

        for model in valid_dumps:
            self.constants.computer = model
            self.computer = self.constants.computer
            self.constants.custom_model = ""
            print(f"Validating dumped model: {self.computer.real_model}")
            self.build_opencore()
            result = subprocess.run([self.constants.ocvalidate_path, f"{self.constants.opencore_release_folder}/EFI/OC/config.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("Error on build!")
                print(result.stdout.decode())
                raise Exception(f"Validation failed for predefined model: {self.computer.real_model}")
            else:
                print(f"Validation succeeded for predefined model: {self.computer.real_model}")


OpenCoreLegacyPatcher()

# Example arg for OCLP command line
# ./OCLP-CLI --build --verbose --debug_oc --debug_kext --model iMac11,2
