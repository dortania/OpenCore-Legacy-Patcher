# Commands for building the EFI and SMBIOS
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
from __future__ import print_function

import binascii
import plistlib
import shutil
import subprocess
import uuid
import zipfile
import os
import sys
import platform
from pathlib import Path
from datetime import date

from Resources import Constants, ModelArray, Utilities


def human_fmt(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, "EB")


def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise


class BuildOpenCore:
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.constants: Constants.Constants = versions

    def hexswap(self, input_hex: str):
        hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
        hex_rev = hex_pairs[::-1]
        hex_str = "".join(["".join(x) for x in hex_rev])
        return hex_str.upper()

    def check_pciid(self, print_status):
        try:
            self.constants.igpu_devices = plistlib.loads(subprocess.run("ioreg -r -n IGPU -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            self.constants.igpu_vendor = self.hexswap(binascii.hexlify(self.constants.igpu_devices[0]["vendor-id"]).decode()[:4])
            self.constants.igpu_device = self.hexswap(binascii.hexlify(self.constants.igpu_devices[0]["device-id"]).decode()[:4])
            if print_status is True:
                print(f"- Detected iGPU: {self.constants.igpu_vendor}:{self.constants.igpu_device}")
        except ValueError:
            if print_status is True:
                print("- No iGPU detected")
            self.constants.igpu_devices = ""

        try:
            self.constants.dgpu_devices = plistlib.loads(subprocess.run("ioreg -r -n GFX0 -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            self.constants.dgpu_vendor = self.hexswap(binascii.hexlify(self.constants.dgpu_devices[0]["vendor-id"]).decode()[:4])
            self.constants.dgpu_device = self.hexswap(binascii.hexlify(self.constants.dgpu_devices[0]["device-id"]).decode()[:4])
            if print_status is True:
                print(f"- Detected dGPU: {self.constants.dgpu_vendor}:{self.constants.dgpu_device}")
        except ValueError:
            if print_status is True:
                print("- No dGPU detected")
            self.constants.dgpu_devices = ""

    def build_efi(self):
        Utilities.cls()
        print(f"Building Configuration for model: {self.model}")
        if not Path(self.constants.build_path).exists():
            Path(self.constants.build_path).mkdir()
            print("Created build folder")
        else:
            print("Build folder already present, skipping")

        if Path(self.constants.opencore_zip_copied).exists():
            print("Deleting old copy of OpenCore zip")
            Path(self.constants.opencore_zip_copied).unlink()
        if Path(self.constants.opencore_release_folder).exists():
            print("Deleting old copy of OpenCore folder")
            shutil.rmtree(self.constants.opencore_release_folder, onerror=rmtree_handler)

        print()
        print(f"- Adding OpenCore v{self.constants.opencore_version} {self.constants.opencore_build}")
        shutil.copy(self.constants.opencore_zip_source, self.constants.build_path)
        zipfile.ZipFile(self.constants.opencore_zip_copied).extractall(self.constants.build_path)

        print("- Adding config.plist for OpenCore")
        # Setup config.plist for editing
        shutil.copy(self.constants.plist_template, self.constants.oc_folder)
        self.config = plistlib.load(Path(self.constants.plist_path).open("rb"))

        # Set revision in config
        self.config["#Revision"]["Build-Version"] = f"{self.constants.patcher_version} - {date.today()}"
        self.config["#Revision"]["OpenCore-Version"] = f"{self.constants.opencore_version} - {self.constants.opencore_build} - {self.constants.opencore_commit}"
        self.config["#Revision"]["Original-Model"] = self.model
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Version"] = f"{self.constants.patcher_version}"

        for name, version, path, check in [
            # Essential kexts
            ("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path, lambda: True),
            ("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path, lambda: True),
            ("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path, lambda: self.model in ModelArray.MacPro71),
            ("RestrictEvents.kext", self.constants.restrictevents_mbp_version, self.constants.restrictevents_mbp_path, lambda: self.model == "MacBookPro9,1"),
            ("NightShiftEnabler.kext", self.constants.nightshift_version, self.constants.nightshift_path, lambda: self.model not in ModelArray.NightShiftExclude),
            ("SMC-Spoof.kext", self.constants.smcspoof_version, self.constants.smcspoof_path, lambda: True),
            # CPU patches
            ("AppleMCEReporterDisabler.kext", self.constants.mce_version, self.constants.mce_path, lambda: self.model in ModelArray.DualSocket),
            ("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path, lambda: self.model in ModelArray.SSEEmulator),
            ("telemetrap.kext", self.constants.telemetrap_version, self.constants.telemetrap_path, lambda: self.model in ModelArray.MissingSSE42),
            ("CPUFriend.kext", self.constants.cpufriend_version, self.constants.cpufriend_path, lambda: self.model not in ModelArray.NoAPFSsupport),
            # Ethernet patches
            ("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path, lambda: self.model in ModelArray.EthernetNvidia),
            ("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path, lambda: self.model in ModelArray.EthernetMarvell),
            ("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path, lambda: self.model in ModelArray.EthernetBroadcom),
            # Legacy audio
            ("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path, lambda: self.model in ModelArray.LegacyAudio or self.model in ModelArray.MacPro71),
            # IDE patch
            ("AppleIntelPIIXATA.kext", self.constants.piixata_version, self.constants.piixata_path, lambda: self.model in ModelArray.IDEPatch),
        ]:
            self.enable_kext(name, version, path, check)

        def wifi_fake_id(self):
            default_path = True
            self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
            self.get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True
            if not self.constants.custom_model:
                arpt_path: str = subprocess.run([self.constants.gfxutil_path] + f"-v".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
                try:
                    arpt_path = [line.strip().split("= ", 1)[1] for line in arpt_path.split("\n") if f"{wifi_vendor}:{wifi_device}".lower() in line.strip()][0]
                    print(f"- Found ARPT device at {arpt_path}")
                    default_path = False
                except IndexError:
                    print("- Failed to find Device path")
                    default_path = True
            if default_path is True:
                if self.model in ModelArray.nvidiaHDEF:
                    # Nvidia chipsets all have the same path to ARPT
                    arpt_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
                elif self.model in ("iMac7,1", "iMac8,1", "MacPro3,1", "MacBookPro4,1"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)"
                elif self.model in ("iMac13,1", "iMac13,2"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)"
                elif self.model in ("MacPro4,1", "MacPro5,1"):
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)"
                else:
                    # Assumes we have a laptop with Intel chipset
                    # iMac11,x-12,x also apply
                    arpt_path = "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"
                print(f"- Using known DevicePath {arpt_path}")
            print("- Applying fake ID for WiFi")
            self.config["DeviceProperties"]["Add"][arpt_path] = {"device-id": binascii.unhexlify("ba430000"), "compatible": "pci14e4,43ba"}

        # WiFi patches
        # TODO: -a is not supported in Lion and older, need to add proper fix
        if self.constants.detected_os > self.constants.lion:
            try:
                wifi_devices = plistlib.loads(subprocess.run("ioreg -r -n ARPT -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            except ValueError:
                # Work-around Mac Pros where Wifi card may not be named ARPT (ie. installed in dedicated PCIe card slot)
                wifi_devices = plistlib.loads(subprocess.run("ioreg -c IOPCIDevice -r -d2 -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            vendor_atheros = binascii.unhexlify("E4140000")
            vendor_broadcom = binascii.unhexlify("8C160000")
            wifi_devices = [i for i in wifi_devices if i["vendor-id"] == vendor_atheros or i["vendor-id"] == vendor_broadcom and i["class-code"] == binascii.unhexlify("00800200")]
            try:
                wifi_vendor = self.hexswap(binascii.hexlify(wifi_devices[0]["vendor-id"]).decode()[:4])
                wifi_device = self.hexswap(binascii.hexlify(wifi_devices[0]["device-id"]).decode()[:4])
                wifi_ioname = wifi_devices[0]["IOName"]
                if not self.constants.custom_model:
                    print(f"- Detected Wifi Card: {wifi_vendor}:{wifi_device}")
            except IndexError:
                wifi_devices = ""

        else:
            wifi_devices = ""
            print("- Can't run Wifi hardware detection on Snow Leopard and older")
        if self.constants.wifi_build is True:
            print("- Skipping Wifi patches on request")
        elif not self.constants.custom_model and wifi_devices:
            if wifi_vendor == self.constants.pci_broadcom:
                # This works around OCLP spoofing the Wifi card and therefore unable to actually detect the correct device
                if wifi_device in ModelArray.BCM4360Wifi and wifi_ioname not in ["pci14e4,4353", "pci14e4,4331"]:
                    self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                elif wifi_ioname in ["pci14e4,4353", "pci14e4,4331"] or wifi_device in ModelArray.BCM94331Wifi:
                    wifi_fake_id(self)
                elif wifi_device in ModelArray.BCM94322Wifi:
                    self.enable_kext("IO80211Mojave.kext", self.constants.io80211mojave_version, self.constants.io80211mojave_path)
                    self.get_kext_by_bundle_path("IO80211Mojave.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
                elif wifi_device in ModelArray.BCM94328Wifi:
                    self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                    self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                    self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
            elif wifi_vendor == self.constants.pci_atheros and wifi_device in ModelArray.AtherosWifi:
                self.enable_kext("IO80211HighSierra.kext", self.constants.io80211high_sierra_version, self.constants.io80211high_sierra_path)
                self.get_kext_by_bundle_path("IO80211HighSierra.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
        else:
            if self.model in ["iMac14,1", "iMac14,2", "iMac14,3"]:
                self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
            elif self.model in ModelArray.WifiBCM94331:
                wifi_fake_id(self)
            elif self.model in ModelArray.WifiBCM94322:
                self.enable_kext("IO80211Mojave.kext", self.constants.io80211mojave_version, self.constants.io80211mojave_path)
                self.get_kext_by_bundle_path("IO80211Mojave.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
            elif self.model in ModelArray.WifiBCM94328:
                self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
            elif self.model in ModelArray.WifiAtheros:
                self.enable_kext("IO80211HighSierra.kext", self.constants.io80211high_sierra_version, self.constants.io80211high_sierra_path)
                self.get_kext_by_bundle_path("IO80211HighSierra.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True

        # CPUFriend
        pp_map_path = Path(self.constants.platform_plugin_plist_path) / Path(f"{self.model}/Info.plist")
        if self.model not in ModelArray.NoAPFSsupport:
            Path(self.constants.pp_kext_folder).mkdir()
            Path(self.constants.pp_contents_folder).mkdir()
            shutil.copy(pp_map_path, self.constants.pp_contents_folder)
            self.get_kext_by_bundle_path("CPUFriendDataProvider.kext")["Enabled"] = True

        # HID patches
        if self.model in ModelArray.LegacyHID:
            print("- Adding IOHIDFamily patch")
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.iokit.IOHIDFamily")["Enabled"] = True

        # SSDT patches
        if self.model in ModelArray.pciSSDT:
            print("- Adding SSDT-CPBG.aml")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-CPBG.aml")["Enabled"] = True
            shutil.copy(self.constants.pci_ssdt_path, self.constants.acpi_path)

        # USB Map
        usb_map_path = Path(self.constants.plist_folder_path) / Path("AppleUSBMaps/Info.plist")
        # iMac7,1 kernel panics with USB map installed, remove for time being until properly debugged
        if usb_map_path.exists():
            print(f"- Adding USB-Map.kext")
            Path(self.constants.map_kext_folder).mkdir()
            Path(self.constants.map_contents_folder).mkdir()
            shutil.copy(usb_map_path, self.constants.map_contents_folder)
            self.get_kext_by_bundle_path("USB-Map.kext")["Enabled"] = True

        agdp_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsDevicePolicy/Info.plist")
        agpm_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsPowerManagement/Info.plist")
        amc_map_path = Path(self.constants.plist_folder_path) / Path("AppleMuxControl/Info.plist")

        if self.model == "MacBookPro9,1":
            print(f"- Adding Display Map Overrides")
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "vit9696"}
            Path(self.constants.agdp_kext_folder).mkdir()
            Path(self.constants.agdp_contents_folder).mkdir()
            Path(self.constants.agpm_kext_folder).mkdir()
            Path(self.constants.agpm_contents_folder).mkdir()
            Path(self.constants.amc_kext_folder).mkdir()
            Path(self.constants.amc_contents_folder).mkdir()

            shutil.copy(agdp_map_path, self.constants.agdp_contents_folder)
            shutil.copy(agpm_map_path, self.constants.agpm_contents_folder)
            shutil.copy(amc_map_path, self.constants.amc_contents_folder)
            self.get_kext_by_bundle_path("AGDP-Override.kext")["Enabled"] = True
            self.get_kext_by_bundle_path("AGPM-Override.kext")["Enabled"] = True
            self.get_kext_by_bundle_path("AMC-Override.kext")["Enabled"] = True

        # AGPM Patch
        if self.model in ModelArray.DualGPUPatch:
            print("- Adding dual GPU patch")
            if self.model in ModelArray.IntelNvidiaDRM and self.constants.drm_support is True:
                print("- Prioritizing DRM support over Intel QuickSync")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "pikera", "shikigva": 256}
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"disable-gpu-min": "20.0.0"}
            else:
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "pikera"}

        # HiDPI OpenCanopy and FileVault
        if self.model in ModelArray.HiDPIpicker:
            print("- Setting HiDPI picker")
            self.config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"]["UIScale"] = binascii.unhexlify("02")

        # Audio Patch
        if self.model in ModelArray.LegacyAudio:
            print("- Adding audio properties")
            hdef_path = "PciRoot(0x0)/Pci(0x8,0x0)" if self.model in ModelArray.nvidiaHDEF else "PciRoot(0x0)/Pci(0x1b,0x0)"
            # In AppleALC, MacPro3,1's original layout is already in use, forcing layout 13 instead
            if self.model == "MacPro3,1":
                self.config["DeviceProperties"]["Add"][hdef_path] = {"apple-layout-id": 90, "use-apple-layout-id": 1, "alc-layout-id": 13, }
            else:
                self.config["DeviceProperties"]["Add"][hdef_path] = {"apple-layout-id": 90, "use-apple-layout-id": 1, "use-layout-id": 1, }

        def backlight_path_detection(self):
            if not self.constants.custom_model:
                gfx0_path: str = subprocess.run([self.constants.gfxutil_path] + f"-f GFX0".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
                try:
                    self.gfx0_path = [line.strip().split("= ", 1)[1] for line in gfx0_path.split("\n") if "GFX0" in line.strip()][0]
                    print(f"- Found GFX0 device at {self.gfx0_path}")
                except IndexError:
                    print("- Failed to find GFX0 Device path, falling back on known logic")
                    if self.model == ["iMac11,1", "iMac11,3"]:
                        self.gfx0_path = "PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"
                    else:
                        self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"
            else:
                if self.model == ["iMac11,1", "iMac11,3"]:
                    self.gfx0_path = "PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"
                else:
                    self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"
                print(f"- Using known GFX0 path: {self.gfx0_path}")


        def nvidia_patch(self, backlight_path):
            self.constants.custom_mxm_gpu = True
            if self.model in ["iMac11,1", "iMac11,2", "iMac11,3"]:
                print("- Adding Nvidia Brightness Control and DRM patches")
                self.config["DeviceProperties"]["Add"][backlight_path] = {"@0,backlight-control": binascii.unhexlify("01000000"), "@0,built-in": binascii.unhexlify("01000000"), "shikigva": 256, "agdpmod": "vit9696"}
                shutil.copy(self.constants.backlight_path, self.constants.kexts_path)
                self.get_kext_by_bundle_path("AppleBacklightFixup.kext")["Enabled"] = True
            elif self.model in ["iMac12,1", "iMac12,2"]:
                print("- Adding Nvidia Brightness Control and DRM patches")
                self.config["DeviceProperties"]["Add"][backlight_path] = {"@0,backlight-control": binascii.unhexlify("01000000"), "@0,built-in": binascii.unhexlify("01000000"), "shikigva": 256}
                print("- Disabling unsupported iGPU")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"name": binascii.unhexlify("23646973706C6179"), "IOName": "#display", "class-code": binascii.unhexlify("FFFFFFFF")}
                shutil.copy(self.constants.backlight_path, self.constants.kexts_path)
                self.get_kext_by_bundle_path("AppleBacklightFixup.kext")["Enabled"] = True

        def amd_patch(self, backlight_path):
            self.constants.custom_mxm_gpu = True
            print("- Adding AMD DRM patches")
            self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 80, "unfairgva": 1}
            if self.model in ["iMac12,1", "iMac12,2"]:
                print("- Disabling unsupported iGPU")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"name": binascii.unhexlify("23646973706C6179"), "IOName": "#display", "class-code": binascii.unhexlify("FFFFFFFF")}
            elif self.model == "iMac10,1":
                self.enable_kext("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path)

        # Check GPU Vendor
        if self.constants.metal_build is True:
            backlight_path_detection(self)
            print("- Adding Metal GPU patches on request")
            if self.constants.imac_vendor == "AMD":
                amd_patch(self, self.gfx0_path)
            elif self.constants.imac_vendor == "Nvidia":
                nvidia_patch(self, self.gfx0_path)
            else:
                print("- Failed to find vendor")
        elif not self.constants.custom_model:
            self.check_pciid(True)
            if self.constants.dgpu_vendor == self.constants.pci_amd_ati and self.constants.dgpu_device in ModelArray.AMDMXMGPUs:
                backlight_path_detection(self)
                amd_patch(self, self.gfx0_path)
            elif self.constants.dgpu_vendor == self.constants.pci_nvidia and self.constants.dgpu_device in ModelArray.NVIDIAMXMGPUs:
                backlight_path_detection(self)
                nvidia_patch(self, self.gfx0_path)
        if self.model in ModelArray.MacPro71:
            print("- Adding Mac Pro, Xserve DRM patches")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 -wegtree"

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.constants.resources_path, onerror=rmtree_handler)
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        self.config["UEFI"]["Drivers"] = ["OpenCanopy.efi", "OpenRuntime.efi"]
        # Exfat check
        if self.model in ModelArray.NoExFat:
            print("- Adding ExFatDxeLegacy.efi")
            shutil.copy(self.constants.exfat_legacy_driver_path, self.constants.drivers_path)
            self.config["UEFI"]["Drivers"] += ["ExFatDxeLegacy.efi"]

        # Add UGA to GOP layer
        if self.model in ModelArray.UGAtoGOP:
            print("- Adding UGA to GOP Patch")
            self.config["UEFI"]["Output"]["GopPassThrough"] = True

        # ThirdPartDrives Check
        if self.model not in ModelArray.NoSATAPatch:
            print("- Adding SATA Hibernation Patch")
            self.config["Kernel"]["Quirks"]["ThirdPartyDrives"] = True

        # DEBUG Settings
        if self.constants.verbose_debug is True:
            print("- Enabling Verbose boot")
            self.config["Kernel"]["Quirks"]["PanicNoKextDump"] = True
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -v debug=0x100"
        if self.constants.kext_debug is True:
            print("- Enabling DEBUG Kexts")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -liludbgall"
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " msgbuf=1048576"
        if self.constants.opencore_debug is True:
            print("- Enabling DEBUG OpenCore")
            self.config["Misc"]["Debug"]["Target"] = 67
            self.config["Misc"]["Debug"]["DisplayLevel"] = 672151678018
        if self.constants.showpicker is True:
            print("- Enabling ShowPicker")
            self.config["Misc"]["Boot"]["ShowPicker"] = True
        else:
            print("- Hiding picker and enabling PollAppleHotKeys")
            self.config["Misc"]["Boot"]["ShowPicker"] = False
        if self.constants.vault is True:
            print("- Setting Vault configuration")
            self.config["Misc"]["Security"]["Vault"] = "Secure"
            self.get_tool_by__path("OpenShell.efi")["Enabled"] = False
        if self.constants.sip_status is False:
            print("- Disabling SIP")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = binascii.unhexlify("EF0F0000")
            self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["csr-active-config"]
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi_get_out_of_my_way=1"
        if self.constants.secure_status is False:
            print("- Disabling SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"
        if self.constants.serial_settings in ["Moderate", "Advanced"]:
            print("- Enabling USB Rename Patches")
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "XHC1 to SHC1")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC1 to EH01")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC2 to EH02")["Enabled"] = True


    def set_smbios(self):
        spoofed_model = self.model
        # TODO: Set check as global variable
        if self.model in ModelArray.MacBookAir61:
            print("- Spoofing to MacBookAir6,1")
            spoofed_model = "MacBookAir6,1"
            spoofed_board = "Mac-35C1E88140C3E6CF"
        elif self.model in ModelArray.MacBookAir62:
            print("- Spoofing to MacBookAir6,2")
            spoofed_model = "MacBookAir6,2"
            spoofed_board = "Mac-7DF21CB3ED6977E5"
        elif self.model in ModelArray.MacBookPro111:
            print("- Spoofing to MacBookPro11,1")
            spoofed_model = "MacBookPro11,1"
            spoofed_board = "Mac-189A3D4F975D5FFC"
        elif self.model in ModelArray.MacBookPro113:
            print("- Spoofing to MacBookPro11,3")
            spoofed_model = "MacBookPro11,3"
            spoofed_board = "Mac-2BD1B31983FE1663"
        elif self.model in ModelArray.Macmini71:
            print("- Spoofing to Macmini7,1")
            spoofed_model = "Macmini7,1"
            spoofed_board = "Mac-35C5E08120C7EEAF"
        elif self.model in ModelArray.iMacPro11:
            print("- Spoofing to iMacPro1,1")
            spoofed_model = "iMacPro1,1"
            spoofed_board = "Mac-7BA5B2D9E42DDD94"
        elif self.model in ModelArray.iMac151:
            # Check for upgraded GPUs on iMacs
            if self.constants.drm_support is True:
                print("- Spoofing to iMacPro1,1")
                spoofed_model = "iMacPro1,1"
                spoofed_board = "Mac-7BA5B2D9E42DDD94"
            else:
                print("- Spoofing to iMac15,1")
                spoofed_model = "iMac15,1"
                spoofed_board = "Mac-42FD25EABCABB274"
        elif self.model in ModelArray.iMac144:
            print("- Spoofing to iMac14,4")
            spoofed_model = "iMac14,4"
            spoofed_board = "Mac-81E3E92DD6088272"
        elif self.model in ModelArray.MacPro71:
            print("- Spoofing to MacPro7,1")
            spoofed_model = "MacPro7,1"
            spoofed_board = "Mac-27AD2F918AE68F61"
        self.spoofed_model = spoofed_model
        self.spoofed_board = spoofed_board
        self.config["#Revision"]["Spoofed-Model"] = self.spoofed_model

        # Setup menu
        def minimal_serial_patch(self):
            self.config["PlatformInfo"]["PlatformNVRAM"]["BID"] = self.spoofed_board
            self.config["PlatformInfo"]["SMBIOS"]["BoardProduct"] = self.spoofed_board
            self.config["PlatformInfo"]["UpdateNVRAM"] = True

        def moderate_serial_patch(self):
            self.config["PlatformInfo"]["Automatic"] = True
            self.config["PlatformInfo"]["UpdateDataHub"] = True
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
            self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model

        def advanced_serial_patch(self):
            macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {self.spoofed_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            macserial_output = macserial_output.stdout.decode().strip().split(" | ")
            self.config["PlatformInfo"]["Automatic"] = True
            self.config["PlatformInfo"]["UpdateDataHub"] = True
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
            self.config["PlatformInfo"]["Generic"]["ROM"] = binascii.unhexlify("0016CB445566")
            self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model
            self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = macserial_output[0]
            self.config["PlatformInfo"]["Generic"]["MLB"] = macserial_output[1]
            self.config["PlatformInfo"]["Generic"]["SystemUUID"] = str(uuid.uuid4()).upper()

        if self.constants.serial_settings == "Moderate":
            print("- Using Moderate SMBIOS patching")
            moderate_serial_patch(self)
        elif self.constants.serial_settings == "Advanced":
            print("- Using Advanced SMBIOS patching")
            advanced_serial_patch(self)
        else:
            print("- Using Minimal SMBIOS patching")
            self.spoofed_model = self.model
            minimal_serial_patch(self)

        # USB Map Patching
        new_map_ls = Path(self.constants.map_contents_folder) / Path("Info.plist")
        map_config = plistlib.load(Path(new_map_ls).open("rb"))

        for model_controller in ModelArray.ControllerTypes:
            model_patch = f"{self.model}{model_controller}"
            try:
                # Avoid erroring out when specific identity not found
                map_config["IOKitPersonalities_x86_64"][model_patch]["model"] = self.spoofed_model

                # Avoid ACPI renaming when not required
                if self.constants.serial_settings == "Minimal":
                    if map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] == "EH01":
                        map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] = "EHC1"
                    if map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] == "EH02":
                        map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] = "EHC2"
                    if map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] == "SHC1":
                        map_config["IOKitPersonalities_x86_64"][model_patch]["IONameMatch"] = "XHC1"

            except KeyError:
                continue

        plistlib.dump(map_config, Path(new_map_ls).open("wb"), sort_keys=True)

        if self.model == "MacBookPro9,1":
            new_agdp_ls = Path(self.constants.agdp_contents_folder) / Path("Info.plist")
            new_agpm_ls = Path(self.constants.agpm_contents_folder) / Path("Info.plist")
            new_amc_ls = Path(self.constants.amc_contents_folder) / Path("Info.plist")

            agdp_config = plistlib.load(Path(new_agdp_ls).open("rb"))
            agpm_config = plistlib.load(Path(new_agpm_ls).open("rb"))
            amc_config = plistlib.load(Path(new_amc_ls).open("rb"))

            agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"][self.spoofed_board] = agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"].pop(self.model)
            agpm_config["IOKitPersonalities"]["AGPM"]["Machines"][self.spoofed_board] = agpm_config["IOKitPersonalities"]["AGPM"]["Machines"].pop(self.model)
            amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"][self.spoofed_board] = amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"].pop(self.model)

            plistlib.dump(agdp_config, Path(new_agdp_ls).open("wb"), sort_keys=True)
            plistlib.dump(agpm_config, Path(new_agpm_ls).open("wb"), sort_keys=True)
            plistlib.dump(amc_config, Path(new_amc_ls).open("wb"), sort_keys=True)

        #if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
        #    print("- Disabling unsupported TeraScale 2 dGPU")
        #    self.config["NVRAM"]["Add"]["FA4CE28D-B62F-4C99-9CC3-6815686E30F9"]["gpu-power-prefs"] = binascii.unhexlify("01000000")
        #    self.config["NVRAM"]["Delete"]["FA4CE28D-B62F-4C99-9CC3-6815686E30F9"] += ["gpu-power-prefs"]
        #    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"name": binascii.unhexlify("23646973706C6179"), "IOName": "#display", "class-code": binascii.unhexlify("FFFFFFFF")}

    @staticmethod
    def get_item_by_kv(iterable, key, value):
        item = None
        for i in iterable:
            if i[key] == value:
                item = i
                break
        return item

    def get_kext_by_bundle_path(self, bundle_path):
        kext = self.get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", bundle_path)
        if not kext:
            print(f"- Could not find kext {bundle_path}!")
            raise IndexError
        return kext

    def get_tool_by__path(self, bundle_path):
        tool = self.get_item_by_kv(self.config["Misc"]["Tools"], "Path", bundle_path)
        if not tool:
            print(f"- Could not find Tool {bundle_path}!")
            raise IndexError
        return tool

    def enable_kext(self, kext_name, kext_version, kext_path, check=False):
        kext = self.get_kext_by_bundle_path(kext_name)

        if callable(check) and not check():
            # Check failed
            return

        print(f"- Adding {kext_name} {kext_version}")
        shutil.copy(kext_path, self.constants.kexts_path)
        kext["Enabled"] = True

    def cleanup(self):
        print("- Cleaning up files")
        # Remove unused kexts
        for kext in list(self.config["Kernel"]["Add"]):
            if not kext["Enabled"]:
                self.config["Kernel"]["Add"].remove(kext)
        plistlib.dump(self.config, Path(self.constants.plist_path).open("wb"), sort_keys=True)
        for kext in self.constants.kexts_path.rglob("*.zip"):
            with zipfile.ZipFile(kext) as zip_file:
                zip_file.extractall(self.constants.kexts_path)
            kext.unlink()

        for item in self.constants.oc_folder.rglob("*.zip"):
            with zipfile.ZipFile(item) as zip_file:
                zip_file.extractall(self.constants.oc_folder)
            item.unlink()

        for i in self.constants.build_path.rglob("__MACOSX"):
            shutil.rmtree(i)

        Path(self.constants.opencore_zip_copied).unlink()

    def sign_files(self):
        if self.constants.vault is True:
            print("- Vaulting EFI")
            subprocess.run([self.constants.vault_path] + f"{self.constants.oc_folder}/".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def build_opencore(self):
        self.build_efi()
        self.set_smbios()
        self.cleanup()
        self.sign_files()
        print("")
        print(f"Your OpenCore EFI for {self.model} has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to go back.\n")

    def copy_efi(self):
        Utilities.cls()
        Utilities.header(["Installing OpenCore to Drive"])

        if not self.constants.opencore_release_folder.exists():
            Utilities.TUIOnlyPrint(
                ["Installing OpenCore to Drive"],
                "Press [Enter] to go back.\n",
                [
                    """OpenCore folder missing!
Please build OpenCore first!"""
                ],
            ).start()
            return

        print("\nDisk picker is loading...")

        all_disks = {}
        # TODO: AllDisksAndPartitions is not supported in Snow Leopard and older
        try:
            # High Sierra and newer
            disks = plistlib.loads(subprocess.run("diskutil list -plist physical".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        except ValueError:
            # Sierra and older
            disks = plistlib.loads(subprocess.run("diskutil list -plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        for disk in disks["AllDisksAndPartitions"]:
            disk_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            try:
                all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info["DeviceNode"], "name": disk_info["MediaName"], "size": disk_info["TotalSize"], "partitions": {}}
                for partition in disk["Partitions"]:
                    partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {partition['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                    all_disks[disk["DeviceIdentifier"]]["partitions"][partition["DeviceIdentifier"]] = {
                        "fs": partition_info.get("FilesystemType", partition_info["Content"]),
                        "type": partition_info["Content"],
                        "name": partition_info.get("VolumeName", ""),
                        "size": partition_info["TotalSize"],
                    }
            except KeyError:
                # Avoid crashing with CDs installed
                continue
        # TODO: Advanced mode
        menu = Utilities.TUIMenu(
            ["Select Disk"],
            "Please select the disk you would like to install OpenCore to: ",
            in_between=["Missing disks? Ensure they have an EFI or FAT32 partition."],
            return_number_instead_of_direct_call=True,
            loop=True,
        )
        for disk in all_disks:
            if not any(all_disks[disk]["partitions"][partition]["fs"] in ("msdos", "EFI") for partition in all_disks[disk]["partitions"]):
                continue
            menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({human_fmt(all_disks[disk]['size'])})", key=disk[4:])

        response = menu.start()

        if response == -1:
            return

        disk_identifier = "disk" + response
        selected_disk = all_disks[disk_identifier]

        menu = Utilities.TUIMenu(
            ["Select Partition"],
            "Please select the partition you would like to install OpenCore to: ",
            return_number_instead_of_direct_call=True,
            loop=True,
            in_between=["Missing partitions? Ensure they are formatted as an EFI or FAT32.", "", "* denotes likely candidate."],
        )
        for partition in selected_disk["partitions"]:
            if selected_disk["partitions"][partition]["fs"] not in ("msdos", "EFI"):
                continue
            text = f"{partition}: {selected_disk['partitions'][partition]['name']} ({human_fmt(selected_disk['partitions'][partition]['size'])})"
            if selected_disk["partitions"][partition]["type"] == "EFI" or (
                selected_disk["partitions"][partition]["type"] == "Microsoft Basic Data" and selected_disk["partitions"][partition]["size"] < 1024 * 1024 * 512
            ):  # 512 megabytes:
                text += " *"
            menu.add_menu_option(text, key=partition[len(disk_identifier) + 1:])

        response = menu.start()

        if response == -1:
            return

        # TODO: Apple Script fails in Yosemite(?) and older
        args = [
            "osascript",
            "-e",
            f'''do shell script "diskutil mount {disk_identifier}s{response}"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to mount your EFI."'
            " with administrator privileges"
            " without altering line endings",
        ]

        if self.constants.detected_os > self.constants.yosemite:
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(f"diskutil mount {disk_identifier}s{response}".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            if "execution error" in result.stderr.decode() and result.stderr.decode().strip()[-5:-1] == "-128":
                # cancelled prompt
                return
            else:
                Utilities.TUIOnlyPrint(
                    ["Copying OpenCore"], "Press [Enter] to go back.\n", ["An error occurred!"] + result.stderr.decode().split("\n") + ["", "Please report this to the devs at GitHub."]
                ).start()
                return

        # TODO: Remount if readonly
        drive_host_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk_identifier}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk_identifier}s{response}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        sd_type = drive_host_info["MediaName"]
        try:
            ssd_type = drive_host_info["SolidState"]
        except KeyError:
            ssd_type = False
        mount_path = Path(partition_info["MountPoint"])
        disk_type = partition_info["BusProtocol"]
        Utilities.cls()
        Utilities.header(["Copying OpenCore"])

        if mount_path.exists():
            if (mount_path / Path("EFI/OC")).exists():
                print("- Removing preexisting EFI/OC folder")
                shutil.rmtree(mount_path / Path("EFI/OC"), onerror=rmtree_handler)
            if (mount_path / Path("System")).exists():
                print("- Removing preexisting System folder")
                shutil.rmtree(mount_path / Path("System"), onerror=rmtree_handler)
            print("- Copying OpenCore onto EFI partition")
            shutil.copytree(self.constants.opencore_release_folder / Path("EFI/OC"), mount_path / Path("EFI/OC"))
            shutil.copytree(self.constants.opencore_release_folder / Path("System"), mount_path / Path("System"))
            if self.constants.boot_efi is True:
                print("- Converting Bootstrap to BOOTx64.efi")
                if (mount_path / Path("EFI/BOOT")).exists():
                    shutil.rmtree(mount_path / Path("EFI/BOOT"), onerror=rmtree_handler)
                Path(mount_path / Path("EFI/BOOT")).mkdir()
                shutil.move(mount_path / Path("System/Library/CoreServices/boot.efi"), mount_path / Path("EFI/BOOT/BOOTx64.efi"))
                shutil.rmtree(mount_path / Path("System"), onerror=rmtree_handler)
            # Array filled with common SD Card names
            # Note most USB-based SD Card readers generally report as "Storage Device", and no reliable way to detect further
            if sd_type in ["SD Card Reader", "SD/MMC"]:
                print("- Adding SD Card icon")
                shutil.copy(self.constants.icon_path_sd, mount_path)
            elif ssd_type is True:
                print("- Adding SSD icon")
                shutil.copy(self.constants.icon_path_ssd, mount_path)
            elif disk_type == "USB":
                print("- Adding External USB Drive icon")
                shutil.copy(self.constants.icon_path_external, mount_path)
            else:
                print("- Adding Internal Drive icon")
                shutil.copy(self.constants.icon_path_internal, mount_path)
            print("- Cleaning install location")
            subprocess.run(f"dot_clean {mount_path}".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("- Unmounting EFI partition")
            subprocess.run(f"diskutil umount {mount_path}".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("- OpenCore transfer complete")
            print("\nPress [Enter] to continue.\n")
            input()
        else:
            Utilities.TUIOnlyPrint(["Copying OpenCore"], "Press [Enter] to go back.\n", ["EFI failed to mount!", "Please report this to the devs at GitHub."]).start()
