# Commands for building the EFI and SMBIOS
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
from __future__ import print_function

import binascii
import copy
import pickle
import plistlib
import shutil
import subprocess
import uuid
import zipfile
import ast
from pathlib import Path
from datetime import date

from Resources import Constants, ModelArray, Utilities, device_probe


def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise


class BuildOpenCore:
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.constants: Constants.Constants = versions
        self.computer = self.constants.computer

        self.gfx0_path = None

    def smbios_set(self, model):
        print("- Setting macOS Monterey Supported SMBIOS")
        if model in ModelArray.MacBookAir_11:
            return "MacBookAir7,1"
        elif model in ModelArray.MacBookAir_13:
            return "MacBookAir7,2"
        elif model in ModelArray.MacBook_12:
            return "MacBook9,1"
        elif model in ModelArray.MacBookPro_13:
            return "MacBookPro12,1"
        elif model in ModelArray.MacBookPro_15_iGPU:
            return "MacBookPro11,4"
        elif model in ModelArray.MacBookPro_15_dGPU:
            return "MacBookPro11,5"
        elif model in ModelArray.Macmini:
            return "Macmini7,1"
        elif model in ModelArray.iMac_iGPUless:
            return "iMacPro1,1"
        elif model in ModelArray.iMac_dGPU:
            # Check for upgraded GPUs on iMacs
            if self.constants.drm_support is True:
                return "iMacPro1,1"
            else:
                return "iMac17,1"
        elif model in ModelArray.iMac_iGPU:
            return "iMac16,1"
        elif model in ModelArray.MacPro:
            return "iMacPro1,1"
        else:
            return model

    def fw_feature_detect(self, model):
        # Values based off OpenCorePkg's Firmwarefeatures and FirmwarefeaturesMask
        # Additionally, APFS bit(19) flipped
        # https://github.com/acidanthera/OpenCorePkg/blob/0.6.9/Include/Apple/IndustryStandard/AppleFeatures.h#L136
        if model == "iMac7,1":
            fw_feature = b"\x07\x14\x08\xc0\x00\x00\x00\x00"
            fw_mask = b"\xff\x1f\x08\xc0\x00\x00\x00\x00"
        elif model in ["MacPro4,1", "Xserve3,1"]:
            fw_feature = b"7\xf5\t\xe0\x00\x00\x00\x00"
            fw_mask = b"7\xff\x0b\xc0\x00\x00\x00\x00"
        else:
            fw_feature = b"\x03\x14\x08\xc0\x00\x00\x00\x00"
            fw_mask = b"\xff\x3f\x08\xc0\x00\x00\x00\x00"
        return fw_feature, fw_mask

    def disk_type(self):
        drive_host_info = plistlib.loads(subprocess.run(f"diskutil info -plist {self.constants.disk}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        sd_type = drive_host_info["MediaName"]
        try:
            ssd_type = drive_host_info["SolidState"]
        except KeyError:
            ssd_type = False
        # Array filled with common SD Card names
        # Note most USB-based SD Card readers generally report as "Storage Device", and no reliable way to detect further
        if sd_type in ["SD Card Reader", "SD/MMC"]:
            print("- Adding SD Card icon")
            shutil.copy(self.constants.icon_path_sd, self.constants.opencore_release_folder)
        elif ssd_type is True:
            print("- Adding SSD icon")
            shutil.copy(self.constants.icon_path_ssd, self.constants.opencore_release_folder)
        elif drive_host_info["BusProtocol"] == "USB":
            print("- Adding External USB Drive icon")
            shutil.copy(self.constants.icon_path_external, self.constants.opencore_release_folder)
        else:
            print("- Adding Internal Drive icon")
            shutil.copy(self.constants.icon_path_internal, self.constants.opencore_release_folder)

    def build_efi(self):
        Utilities.cls()
        if not self.constants.custom_model:
            print(f"Building Configuration on model: {self.model}")
        else:
            print(f"Building Configuration for external model: {self.model}")
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
            shutil.rmtree(self.constants.opencore_release_folder, onerror=rmtree_handler, ignore_errors=True)

        print(f"\n- Adding OpenCore v{self.constants.opencore_version} {self.constants.opencore_build}")
        shutil.copy(self.constants.opencore_zip_source, self.constants.build_path)
        zipfile.ZipFile(self.constants.opencore_zip_copied).extractall(self.constants.build_path)

        print("- Adding config.plist for OpenCore")
        # Setup config.plist for editing
        shutil.copy(self.constants.plist_template, self.constants.oc_folder)
        self.config = plistlib.load(Path(self.constants.plist_path).open("rb"))

        # Set revision in config
        self.config["#Revision"]["Build-Version"] = f"{self.constants.patcher_version} - {date.today()}"
        if not self.constants.custom_model:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built on Target Machine"
            computer_copy = copy.copy(self.computer)
            computer_copy.ioregistry = None
            self.config["#Revision"]["Hardware-Probe"] = pickle.dumps(computer_copy)
        else:
            self.config["#Revision"]["Build-Type"] = "OpenCore Built for External Machine"
        self.config["#Revision"]["OpenCore-Version"] = f"{self.constants.opencore_version} - {self.constants.opencore_build} - {self.constants.opencore_commit}"
        self.config["#Revision"]["Original-Model"] = self.model
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Version"] = f"{self.constants.patcher_version}"

        for name, version, path, check in [
            # Essential kexts
            ("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path, lambda: True),
            ("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path, lambda: self.constants.allow_oc_everywhere is False),
            ("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path, lambda: self.model in ModelArray.MacPro),
            # Modded RestrictEvents with displaypolicyd blocked to fix dGPU switching
            ("RestrictEvents.kext", self.constants.restrictevents_mbp_version, self.constants.restrictevents_mbp_path, lambda: self.model in ["MacBookPro6,1", "MacBookPro6,2", "MacBookPro9,1"]),
            ("SMC-Spoof.kext", self.constants.smcspoof_version, self.constants.smcspoof_path, lambda: self.constants.allow_oc_everywhere is False),
            # CPU patches
            ("AppleMCEReporterDisabler.kext", self.constants.mce_version, self.constants.mce_path, lambda: self.model in ModelArray.DualSocket),
            ("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path, lambda: self.model in ModelArray.SSEEmulator),
            ("telemetrap.kext", self.constants.telemetrap_version, self.constants.telemetrap_path, lambda: self.model in ModelArray.MissingSSE42),
            (
                "CPUFriend.kext",
                self.constants.cpufriend_version,
                self.constants.cpufriend_path,
                lambda: self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.allow_oc_everywhere is False and self.constants.disallow_cpufriend is False,
            ),
            # Ethernet patches
            ("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path, lambda: self.model in ModelArray.EthernetNvidia),
            ("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path, lambda: self.model in ModelArray.EthernetMarvell),
            ("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path, lambda: self.model in ModelArray.EthernetBroadcom),
            # Legacy audio
            ("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path, lambda: self.model in ModelArray.LegacyAudio or self.model in ModelArray.MacPro),
            # IDE patch
            ("AppleIntelPIIXATA.kext", self.constants.piixata_version, self.constants.piixata_path, lambda: self.model in ModelArray.IDEPatch),
            # Misc
            ("FeatureUnlock.kext", self.constants.featureunlock_version, self.constants.featureunlock_path, lambda: self.model in ModelArray.SidecarPatch),
            ("DebugEnhancer.kext", self.constants.debugenhancer_version, self.constants.debugenhancer_path, lambda: self.constants.kext_debug is True),
            ("latebloom.kext", self.constants.latebloom_version, self.constants.latebloom_path, lambda: self.model in ModelArray.PCIRaceCondition),
        ]:
            self.enable_kext(name, version, path, check)

        if self.constants.allow_oc_everywhere is False:
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.driver.AppleSMC")["Enabled"] = True

        if self.get_kext_by_bundle_path("latebloom.kext")["Enabled"] is True:
            print(f"- Setting latebloom delay of {self.constants.latebloom_delay}ms, range {self.constants.latebloom_range}ms, debug {bool(self.constants.latebloom_debug)}")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"][
                "boot-args"
            ] += f" latebloom={self.constants.latebloom_delay} lb_range={self.constants.latebloom_range} lb_debug={self.constants.latebloom_debug}"

        if not self.constants.custom_model and (self.constants.allow_oc_everywhere is True or self.model in ModelArray.MacPro):
            # Use Innie's same logic:
            # https://github.com/cdf/Innie/blob/v1.3.0/Innie/Innie.cpp#L90-L97
            for i, controller in enumerate(self.computer.storage):
                print(f"- Fixing PCIe Storage Controller ({i + 1}) reporting")
                if controller.pci_path:
                    self.config["DeviceProperties"]["Add"][controller.pci_path] = {"built-in": 1}
                else:
                    print(f"- Failed to find Device path for PCIe Storage Controller {i}, falling back to Innie")
                    if self.get_kext_by_bundle_path("Innie.kext")["Enabled"] is False:
                        self.enable_kext("Innie.kext", self.constants.innie_version, self.constants.innie_path)
            if not self.computer.storage:
                print("- No PCIe Storage Controllers found to fix")

        if not self.constants.custom_model:
            nvme_devices = [i for i in self.computer.storage if isinstance(i, device_probe.NVMeController)]
            for i, controller in enumerate(nvme_devices):
                print(f"- Found 3rd Party NVMe SSD ({i + 1}): {Utilities.friendly_hex(controller.vendor_id)}:{Utilities.friendly_hex(controller.device_id)}")
                self.config["#Revision"][f"Hardware-NVMe-{i}"] = f"{Utilities.friendly_hex(controller.vendor_id)}:{Utilities.friendly_hex(controller.device_id)}"

                # Disable Bit 0 (L0s), enable Bit 1 (L1)
                nvme_aspm = (controller.aspm & (~0b11)) | 0b10

                if controller.pci_path:
                    print(f"- Found NVMe ({i}) at {controller.pci_path}")
                    self.config["DeviceProperties"]["Add"].setdefault(controller.pci_path, {})["pci-aspm-default"] = nvme_aspm
                    self.config["DeviceProperties"]["Add"][controller.pci_path.rpartition("/")[0]] = {"pci-aspm-default": nvme_aspm}
                else:
                    if "-nvmefaspm" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                        print("- Falling back to -nvmefaspm")
                        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -nvmefaspm"

                if self.get_kext_by_bundle_path("NVMeFix.kext")["Enabled"] is False:
                    self.enable_kext("NVMeFix.kext", self.constants.nvmefix_version, self.constants.nvmefix_path)

            if not nvme_devices:
                print("- No 3rd Party NVMe drives found")

        def wifi_fake_id(self):
            self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
            self.get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True
            if not self.constants.custom_model and self.computer.wifi and self.computer.wifi.pci_path:
                arpt_path = self.computer.wifi.pci_path
                print(f"- Found ARPT device at {arpt_path}")
            else:
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
            # self.config["DeviceProperties"]["Add"][arpt_path] = {"device-id": binascii.unhexlify("ba430000"), "compatible": "pci14e4,43ba"}
            if not self.constants.custom_model and self.computer.wifi and self.constants.validate is False and self.computer.wifi.country_code:
                print(f"- Applying fake ID for WiFi, setting Country Code: {self.computer.wifi.country_code}")
                self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}
            if self.constants.enable_wake_on_wlan is True:
                print("- Enabling Wake on WLAN support")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"

        # WiFi patches
        # TODO: -a is not supported in Lion and older, need to add proper fix
        if self.constants.detected_os > self.constants.lion and not self.constants.custom_model:
            if self.computer.wifi:
                print(f"- Found Wireless Device {Utilities.friendly_hex(self.computer.wifi.vendor_id)}:{Utilities.friendly_hex(self.computer.wifi.device_id)}")
                self.config["#Revision"]["Hardware-Wifi"] = f"{Utilities.friendly_hex(self.computer.wifi.vendor_id)}:{Utilities.friendly_hex(self.computer.wifi.device_id)}"
        else:
            print("- Unable to run Wireless hardware detection")

        if self.constants.wifi_build is True:
            print("- Skipping Wifi patches on request")
        elif not self.constants.custom_model and self.computer.wifi:
            if isinstance(self.computer.wifi, device_probe.Broadcom):
                # This works around OCLP spoofing the Wifi card and therefore unable to actually detect the correct device
                if self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirportBrcmNIC and self.constants.validate is False and self.computer.wifi.country_code:
                    self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                    print(f"- Setting Wireless Card's Country Code: {self.computer.wifi.country_code}")
                    if self.computer.wifi.pci_path:
                        arpt_path = self.computer.wifi.pci_path
                        print(f"- Found ARPT device at {arpt_path}")
                        self.config["DeviceProperties"]["Add"][arpt_path] = {"brcmfx-country": self.computer.wifi.country_code}
                    else:
                        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" brcmfx-country={self.computer.wifi.country_code}"
                    if self.constants.enable_wake_on_wlan is True:
                        print("- Enabling Wake on WLAN support")
                        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"
                elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                    wifi_fake_id(self)
                elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
                    self.enable_kext("IO80211Mojave.kext", self.constants.io80211mojave_version, self.constants.io80211mojave_path)
                    self.get_kext_by_bundle_path("IO80211Mojave.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
                elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
                    self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                    self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                    self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
            elif isinstance(self.computer.wifi, device_probe.Atheros) and self.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40:
                self.enable_kext("IO80211HighSierra.kext", self.constants.io80211high_sierra_version, self.constants.io80211high_sierra_path)
                self.get_kext_by_bundle_path("IO80211HighSierra.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
        else:
            if self.model in ModelArray.WifiBCM94331:
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
            else:
                self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                # print(f"- Setting Wireless Card's Country Code: {self.computer.wifi.country_code}")
                # self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" brcmfx-country={self.computer.wifi.country_code}"
                if self.constants.enable_wake_on_wlan is True:
                    print("- Enabling Wake on WLAN support")
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"

        # CPUFriend
        pp_map_path = Path(self.constants.platform_plugin_plist_path) / Path(f"{self.model}/Info.plist")
        if self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.allow_oc_everywhere is False:
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

        if self.model in ModelArray.windows_audio:
            # Based on: https://egpu.io/forums/pc-setup/fix-dsdt-override-to-correct-error-12/
            print("- Enabling Windows 10 UEFI Audio support")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-PCI.aml")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "BUF0 to BUF1")["Enabled"] = True
            shutil.copy(self.constants.windows_ssdt_path, self.constants.acpi_path)

        # USB Map
        usb_map_path = Path(self.constants.plist_folder_path) / Path("AppleUSBMaps/Info.plist")
        # iMac7,1 kernel panics with USB map installed, remove for time being until properly debugged
        if (
            usb_map_path.exists()
            and self.constants.allow_oc_everywhere is False
            and self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"]
            and (self.model in ModelArray.Missing_USB_Map or self.constants.serial_settings in ["Moderate", "Advanced"])
        ):
            print("- Adding USB-Map.kext")
            Path(self.constants.map_kext_folder).mkdir()
            Path(self.constants.map_contents_folder).mkdir()
            shutil.copy(usb_map_path, self.constants.map_contents_folder)
            self.get_kext_by_bundle_path("USB-Map.kext")["Enabled"] = True

        if self.constants.allow_oc_everywhere is False:
            if self.model == "MacBookPro9,1":
                print("- Adding AppleMuxControl Override")
                amc_map_path = Path(self.constants.plist_folder_path) / Path("AppleMuxControl/Info.plist")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "vit9696"}
                Path(self.constants.amc_kext_folder).mkdir()
                Path(self.constants.amc_contents_folder).mkdir()
                shutil.copy(amc_map_path, self.constants.amc_contents_folder)
                self.get_kext_by_bundle_path("AMC-Override.kext")["Enabled"] = True

            if self.model not in ModelArray.NoAGPMSupport:
                print("- Adding AppleGraphicsPowerManagement Override")
                agpm_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsPowerManagement/Info.plist")
                Path(self.constants.agpm_kext_folder).mkdir()
                Path(self.constants.agpm_contents_folder).mkdir()
                shutil.copy(agpm_map_path, self.constants.agpm_contents_folder)
                self.get_kext_by_bundle_path("AGPM-Override.kext")["Enabled"] = True

            if self.model in ModelArray.AGDPSupport:
                print("- Adding AppleGraphicsDevicePolicy Override")
                agdp_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsDevicePolicy/Info.plist")
                Path(self.constants.agdp_kext_folder).mkdir()
                Path(self.constants.agdp_contents_folder).mkdir()
                shutil.copy(agdp_map_path, self.constants.agdp_contents_folder)
                self.get_kext_by_bundle_path("AGDP-Override.kext")["Enabled"] = True

        # AGPM Patch
        if self.model in ModelArray.DualGPUPatch:
            print("- Adding dual GPU patch")
            if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
                self.gfx0_path = self.computer.dgpu.pci_path
                print(f"- Found GFX0 Device Path: {self.gfx0_path}")
            else:
                if not self.constants.custom_model:
                    print("- Failed to find GFX0 Device path, falling back on known logic")
                self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

            if self.model in ModelArray.IntelNvidiaDRM and self.constants.drm_support is True:
                print("- Prioritizing DRM support over Intel QuickSync")
                self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696", "shikigva": 256}
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
            else:
                self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696"}

        if self.model in ["iMac13,1", "iMac13,2", "iMac13,3"]:
            if not self.constants.custom_model and self.computer.dgpu:
                if self.constants.allow_ivy_igpu is False:
                    print("- Disabling iGPU to fix sleep support in macOS 12")
                    self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696", "shikigva": 256}
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                        "name": binascii.unhexlify("23646973706C6179"),
                        "IOName": "#display",
                        "class-code": binascii.unhexlify("FFFFFFFF"),
                    }
                else:
                    print("- Enabling iGPU upon request")

        # Audio Patch
        if self.model in ModelArray.LegacyAudio:
            print("- Adding audio properties")
            hdef_path = "PciRoot(0x0)/Pci(0x8,0x0)" if self.model in ModelArray.nvidiaHDEF else "PciRoot(0x0)/Pci(0x1b,0x0)"
            # In AppleALC, MacPro3,1's original layout is already in use, forcing layout 13 instead
            if self.model == "MacPro3,1":
                self.config["DeviceProperties"]["Add"][hdef_path] = {
                    "apple-layout-id": 90,
                    "use-apple-layout-id": 1,
                    "alc-layout-id": 13,
                }
            else:
                self.config["DeviceProperties"]["Add"][hdef_path] = {
                    "apple-layout-id": 90,
                    "use-apple-layout-id": 1,
                    "use-layout-id": 1,
                }

        # Enable FireWire Boot Support
        if self.constants.firewire_boot is True and self.model not in ModelArray.NoFireWireSupport:
            print("- Enabling FireWire Boot Support")
            self.enable_kext("IOFireWireFamily.kext", self.constants.fw_kext, self.constants.fw_family_path)
            self.enable_kext("IOFireWireSBP2.kext", self.constants.fw_kext, self.constants.fw_sbp2_path)
            self.enable_kext("IOFireWireSerialBusProtocolTransport.kext", self.constants.fw_kext, self.constants.fw_bus_path)
            self.get_kext_by_bundle_path("IOFireWireFamily.kext/Contents/PlugIns/AppleFWOHCI.kext")["Enabled"] = True

        def backlight_path_detection(self):
            if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
                self.gfx0_path = self.computer.dgpu.pci_path
                print(f"- Found GFX0 Device Path: {self.gfx0_path}")
            else:
                if not self.constants.custom_model:
                    print("- Failed to find GFX0 Device path, falling back on known logic")
                if self.model in ["iMac11,1", "iMac11,3"]:
                    self.gfx0_path = "PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"
                elif self.model == "iMac10,1":
                    self.gfx0_path = "PciRoot(0x0)/Pci(0xc,0x0)/Pci(0x0,0x0)"
                else:
                    self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

        def nvidia_patch(self, backlight_path):
            self.constants.custom_mxm_gpu = True
            if self.model in ["iMac11,1", "iMac11,2", "iMac11,3", "iMac10,1"]:
                print("- Adding Nvidia Brightness Control and DRM patches")
                self.config["DeviceProperties"]["Add"][backlight_path] = {
                    "applbkl": binascii.unhexlify("01000000"),
                    "@0,backlight-control": binascii.unhexlify("01000000"),
                    "@0,built-in": binascii.unhexlify("01000000"),
                    "shikigva": 256,
                    "agdpmod": "vit9696",
                }
                if self.constants.custom_model and self.model == "iMac11,2":
                    # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
                    # Set both properties when we cannot run hardware detection
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {
                        "applbkl": binascii.unhexlify("01000000"),
                        "@0,backlight-control": binascii.unhexlify("01000000"),
                        "@0,built-in": binascii.unhexlify("01000000"),
                        "shikigva": 256,
                        "agdpmod": "vit9696",
                    }
            elif self.model in ["iMac12,1", "iMac12,2"]:
                print("- Adding Nvidia Brightness Control and DRM patches")
                self.config["DeviceProperties"]["Add"][backlight_path] = {
                    "applbkl": binascii.unhexlify("01000000"),
                    "@0,backlight-control": binascii.unhexlify("01000000"),
                    "@0,built-in": binascii.unhexlify("01000000"),
                    "shikigva": 256,
                    "agdpmod": "vit9696",
                }
                print("- Disabling unsupported iGPU")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
            shutil.copy(self.constants.backlight_injector_path, self.constants.kexts_path)
            self.get_kext_by_bundle_path("BacklightInjector.kext")["Enabled"] = True
            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

        def amd_patch(self, backlight_path):
            self.constants.custom_mxm_gpu = True
            print("- Adding AMD DRM patches")
            self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 80, "unfairgva": 1}
            if self.constants.custom_model and self.model == "iMac11,2":
                # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
                # Set both properties when we cannot run hardware detection
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {"shikigva": 80, "unfairgva": 1}
            if self.model in ["iMac12,1", "iMac12,2"]:
                print("- Disabling unsupported iGPU")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
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
        elif not self.constants.custom_model and self.model in ModelArray.LegacyGPU and self.computer.dgpu:
            print(f"- Detected dGPU: {Utilities.friendly_hex(self.computer.dgpu.vendor_id)}:{Utilities.friendly_hex(self.computer.dgpu.device_id)}")
            if self.computer.dgpu.arch in [
                device_probe.AMD.Archs.Legacy_GCN,
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                backlight_path_detection(self)
                amd_patch(self, self.gfx0_path)
            elif self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                backlight_path_detection(self)
                nvidia_patch(self, self.gfx0_path)
        if self.model in ModelArray.MacPro:
            if not self.constants.custom_model:
                for i, device in enumerate(self.computer.gpus):
                    print(f"- Found dGPU ({i + 1}): {Utilities.friendly_hex(device.vendor_id)}:{Utilities.friendly_hex(device.device_id)}")
                    self.config["#Revision"][f"Hardware-MacPro-dGPU-{i + 1}"] = f"{Utilities.friendly_hex(device.vendor_id)}:{Utilities.friendly_hex(device.device_id)}"

                    if device.pci_path:
                        print(f"- Found dGPU ({i + 1}) at {device.pci_path}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"shikigva": 128, "unfairgva": 1, "rebuild-device-tree": 1}
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"rebuild-device-tree": 1}
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                    else:
                        print(f"- Failed to find Device path for dGPU {i + 1}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            if "shikigva=128 unfairgva=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1" + (
                                    " -wegtree" if "-wegtree" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] else ""
                                )
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            if "-wegtree" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -wegtree"
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                if not self.computer.gpus:
                    print("- No socketed dGPU found")

            else:
                print("- Adding Mac Pro, Xserve DRM patches")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 -wegtree"
        
        if self.constants.disable_thunderbolt is True and self.model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3", "MacBookPro11,4", "MacBookPro11,5"]:
            print("- Disabling 2013-2014 laptop Thunderbolt Controller")
            if self.model in ["MacBookPro11,3", "MacBookPro11,5"]:
                # 15" dGPU models: IOACPIPlane:/_SB/PCI0@0/PEG1@10001/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"
            else:
                # 13" and 15" iGPU 2013-2014 models: IOACPIPlane:/_SB/PCI0@0/P0P2@10000/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"
            
            self.config["DeviceProperties"]["Add"][tb_device_path] = {"class-code": binascii.unhexlify("FFFFFFFF"), "device-id": binascii.unhexlify("FFFF0000")}

        # Add XhciDxe if firmware doesn't have XHCI controller support and XCHI controller detected
        # TODO: Fix XhciDxe to work on pre UEFI 2.0 Macs
        # Ref: https://github.com/acidanthera/bugtracker/issues/1663
        # if self.model not in ModelArray.XhciSupport and not self.constants.custom_model:
        #    devices = plistlib.loads(subprocess.run("ioreg -c IOPCIDevice -r -d2 -a".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        #    try:
        #        devices = [i for i in devices if i["class-code"] == binascii.unhexlify(self.constants.classcode_xhci)]
        #        vendor_id = Utilities.hexswap(binascii.hexlify(devices[0]["vendor-id"]).decode()[:4])
        #        device_id = Utilities.hexswap(binascii.hexlify(devices[0]["device-id"]).decode()[:4])
        #        print("- Found XHCI Controller, adding Boot Support")
        #        shutil.copy(self.constants.xhci_driver_path, self.constants.drivers_path)
        #        self.config["UEFI"]["Drivers"] += ["XhciDxe.efi"]
        #    except ValueError:
        #        print("- No XHCI Controller Found (V)")
        #    except IndexError:
        #        print("- No XHCI Controller Found (I)")

        if self.constants.nvme_boot is True:
            print("- Enabling NVMe boot support")
            shutil.copy(self.constants.nvme_driver_path, self.constants.drivers_path)
            self.config["UEFI"]["Drivers"] += ["NvmExpressDxe.efi"]

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.constants.resources_path, onerror=rmtree_handler)
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        self.config["UEFI"]["Drivers"] += ["OpenCanopy.efi", "OpenRuntime.efi"]
        # Exfat check
        if self.model in ModelArray.NoExFat:
            print("- Adding ExFatDxeLegacy.efi")
            shutil.copy(self.constants.exfat_legacy_driver_path, self.constants.drivers_path)
            self.config["UEFI"]["Drivers"] += ["ExFatDxeLegacy.efi"]

        # Add UGA to GOP layer
        if self.model in ModelArray.UGAtoGOP:
            print("- Adding UGA to GOP Patch")
            self.config["UEFI"]["Output"]["GopPassThrough"] = "Apple"

        # ThirdPartDrives Check
        if self.model in ModelArray.SATAPatch and self.constants.allow_oc_everywhere is False:
            print("- Adding SATA Hibernation Patch")
            self.config["Kernel"]["Quirks"]["ThirdPartyDrives"] = True

        # DEBUG Settings
        if self.constants.verbose_debug is True:
            print("- Enabling Verbose boot")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -v"
        if self.constants.kext_debug is True:
            print("- Enabling DEBUG Kexts")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -liludbgall"
            # Disabled due to macOS Monterey crashing shortly after kernel init
            # Use DebugEnhancer.kext instead
            # self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " msgbuf=1048576"
        if self.constants.opencore_debug is True:
            print("- Enabling DEBUG OpenCore")
            self.config["Misc"]["Debug"]["Target"] = 0x43
            self.config["Misc"]["Debug"]["DisplayLevel"] = 0x80000042
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
        if self.constants.disable_amfi is True:
            print("- Disabling AMFI")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi_get_out_of_my_way=1"
        if self.constants.secure_status is False:
            print("- Disabling SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"
        if self.constants.serial_settings in ["Moderate", "Advanced"]:
            print("- Enabling USB Rename Patches")
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "XHC1 to SHC1")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC1 to EH01")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC2 to EH02")["Enabled"] = True
        if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpu"] = self.constants.custom_cpu_model
            if self.constants.custom_cpu_model_value != "":
                print(f"- Adding custom CPU Name: {self.constants.custom_cpu_model_value}")
                self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpuname"] = self.constants.custom_cpu_model_value
            else:
                print("- Adding CPU Name Patch")
            if self.get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
                self.enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
        if self.model == self.constants.override_smbios:
            print("- Adding -no_compat_check")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -no_compat_check"
        if self.constants.disk != "":
            self.disk_type()
        if self.constants.validate is False:
            print("- Adding bootmgfw.efi BlessOverride")
            self.config["Misc"]["BlessOverride"] += ["\\EFI\\Microsoft\\Boot\\bootmgfw.efi"]
        if self.model in ModelArray.dGPU_switch:
            print("- Allowing GMUX switching in Windows")
            self.config["Booter"]["Quirks"]["SignalAppleOS"] = True

    def set_smbios(self):
        spoofed_model = self.model
        if self.constants.override_smbios == "Default":
            spoofed_model = self.smbios_set(self.model)
        else:
            spoofed_model = self.constants.override_smbios
        print(f"- Using Model ID: {spoofed_model}")
        try:
            spoofed_board = self.constants.board_id[spoofed_model]
            print(f"- Using Board ID: {spoofed_board}")
        except KeyError:
            spoofed_board = ""
        self.spoofed_model = spoofed_model
        self.spoofed_board = spoofed_board
        if self.constants.allow_oc_everywhere is False:
            self.config["#Revision"]["Spoofed-Model"] = f"{self.spoofed_model} - {self.constants.serial_settings}"

        # Setup menu
        def minimal_serial_patch(self):
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["SMBIOS"]["ProcessorType"] = 1537
            if self.model in ModelArray.NoAPFSsupport:
                fw_feature, fw_mask = self.fw_feature_detect(self.model)
                self.config["PlatformInfo"]["PlatformNVRAM"]["FirmwareFeatures"] = fw_feature
                self.config["PlatformInfo"]["SMBIOS"]["FirmwareFeatures"] = fw_feature
                self.config["PlatformInfo"]["PlatformNVRAM"]["FirmwareFeaturesMask"] = fw_mask
                self.config["PlatformInfo"]["SMBIOS"]["FirmwareFeaturesMask"] = fw_mask
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
            self.config["PlatformInfo"]["PlatformNVRAM"]["BID"] = self.spoofed_board
            self.config["PlatformInfo"]["SMBIOS"]["BoardProduct"] = self.spoofed_board
            self.config["PlatformInfo"]["SMBIOS"]["BIOSVersion"] = "9999.999.999.999.999"
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["PlatformInfo"]["UpdateSMBIOS"] = True

        def moderate_serial_patch(self):
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
            self.config["PlatformInfo"]["Automatic"] = True
            self.config["PlatformInfo"]["UpdateDataHub"] = True
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["PlatformInfo"]["UpdateSMBIOS"] = True
            self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
            self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model

        def advanced_serial_patch(self):
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537
            macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {self.spoofed_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            macserial_output = macserial_output.stdout.decode().strip().split(" | ")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
            self.config["PlatformInfo"]["Automatic"] = True
            self.config["PlatformInfo"]["UpdateDataHub"] = True
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["PlatformInfo"]["UpdateSMBIOS"] = True
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
        elif self.constants.serial_settings == "Minimal":
            print("- Using Minimal SMBIOS patching")
            self.spoofed_model = self.model
            minimal_serial_patch(self)

        # USB Map and CPUFriend Patching
        if (
            self.constants.allow_oc_everywhere is False
            and self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"]
            and (self.model in ModelArray.Missing_USB_Map or self.constants.serial_settings in ["Moderate", "Advanced"])
        ):
            new_map_ls = Path(self.constants.map_contents_folder) / Path("Info.plist")
            map_config = plistlib.load(Path(new_map_ls).open("rb"))
            # Strip unused USB maps
            for entry in list(map_config["IOKitPersonalities_x86_64"]):
                if not entry.startswith(self.model):
                    map_config["IOKitPersonalities_x86_64"].pop(entry)
                else:
                    try:
                        map_config["IOKitPersonalities_x86_64"][entry]["model"] = self.spoofed_model
                        if self.constants.serial_settings == "Minimal":
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "EH01":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "EHC1"
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "EH02":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "EHC2"
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "SHC1":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "XHC1"
                    except KeyError:
                        continue
            plistlib.dump(map_config, Path(new_map_ls).open("wb"), sort_keys=True)
        if self.constants.allow_oc_everywhere is False and self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.disallow_cpufriend is False:
            # Adjust CPU Friend Data to correct SMBIOS
            new_cpu_ls = Path(self.constants.pp_contents_folder) / Path("Info.plist")
            cpu_config = plistlib.load(Path(new_cpu_ls).open("rb"))
            string_stuff = str(cpu_config["IOKitPersonalities"]["CPUFriendDataProvider"]["cf-frequency-data"])
            string_stuff = string_stuff.replace(self.model, self.spoofed_model)
            string_stuff = ast.literal_eval(string_stuff)
            cpu_config["IOKitPersonalities"]["CPUFriendDataProvider"]["cf-frequency-data"] = string_stuff
            plistlib.dump(cpu_config, Path(new_cpu_ls).open("wb"), sort_keys=True)

        if self.constants.allow_oc_everywhere is False:
            if self.model == "MacBookPro9,1":
                new_amc_ls = Path(self.constants.amc_contents_folder) / Path("Info.plist")
                amc_config = plistlib.load(Path(new_amc_ls).open("rb"))
                amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"][self.spoofed_board] = amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"].pop(self.model)
                plistlib.dump(amc_config, Path(new_amc_ls).open("wb"), sort_keys=True)
            if self.model not in ModelArray.NoAGPMSupport:
                new_agpm_ls = Path(self.constants.agpm_contents_folder) / Path("Info.plist")
                agpm_config = plistlib.load(Path(new_agpm_ls).open("rb"))
                agpm_config["IOKitPersonalities"]["AGPM"]["Machines"][self.spoofed_board] = agpm_config["IOKitPersonalities"]["AGPM"]["Machines"].pop(self.model)
                plistlib.dump(agpm_config, Path(new_agpm_ls).open("wb"), sort_keys=True)
            if self.model in ModelArray.AGDPSupport:
                new_agdp_ls = Path(self.constants.agdp_contents_folder) / Path("Info.plist")
                agdp_config = plistlib.load(Path(new_agdp_ls).open("rb"))
                agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"][self.spoofed_board] = agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"].pop(
                    self.model
                )
                plistlib.dump(agdp_config, Path(new_agdp_ls).open("wb"), sort_keys=True)

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
        # Remove unused entries
        for entry in list(self.config["ACPI"]["Add"]):
            if not entry["Enabled"]:
                self.config["ACPI"]["Add"].remove(entry)
        for entry in list(self.config["ACPI"]["Patch"]):
            if not entry["Enabled"]:
                self.config["ACPI"]["Patch"].remove(entry)
        for entry in list(self.config["Kernel"]["Add"]):
            if not entry["Enabled"]:
                self.config["Kernel"]["Add"].remove(entry)
        for entry in list(self.config["Kernel"]["Patch"]):
            if not entry["Enabled"]:
                self.config["Kernel"]["Patch"].remove(entry)

        plistlib.dump(self.config, Path(self.constants.plist_path).open("wb"), sort_keys=True)
        for kext in self.constants.kexts_path.rglob("*.zip"):
            with zipfile.ZipFile(kext) as zip_file:
                zip_file.extractall(self.constants.kexts_path)
            kext.unlink()

        for item in self.constants.oc_folder.rglob("*.zip"):
            with zipfile.ZipFile(item) as zip_file:
                zip_file.extractall(self.constants.oc_folder)
            item.unlink()

        if not self.constants.recovery_status:
            # Crashes in RecoveryOS for unknown reason
            for i in self.constants.build_path.rglob("__MACOSX"):
                shutil.rmtree(i)

        Path(self.constants.opencore_zip_copied).unlink()

    def sign_files(self):
        if self.constants.vault is True:
            print("- Vaulting EFI")
            subprocess.run([str(self.constants.vault_path), f"{self.constants.oc_folder}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
            menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({Utilities.human_fmt(all_disks[disk]['size'])})", key=disk[4:])

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
            text = f"{partition}: {selected_disk['partitions'][partition]['name']} ({Utilities.human_fmt(selected_disk['partitions'][partition]['size'])})"
            if selected_disk["partitions"][partition]["type"] == "EFI" or (
                selected_disk["partitions"][partition]["type"] == "Microsoft Basic Data" and selected_disk["partitions"][partition]["size"] < 1024 * 1024 * 512
            ):  # 512 megabytes:
                text += " *"
            menu.add_menu_option(text, key=partition[len(disk_identifier) + 1 :])

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

        if self.constants.detected_os >= self.constants.el_capitan and not self.constants.recovery_status:
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
            if (mount_path / Path("EFI/Microsoft")).exists():
                print("- Found Windows Boot Loader")
                print("\nWould you like to continue installing OpenCore?")
                print("Installing OpenCore onto this drive may make Windows unbootable until OpenCore")
                print("is removed from the partition")
                print("We highly recommend users partition 200MB off their drive with Disk Utility")
                print("    Name:\t\t OPENCORE")
                print("    Format:\t\t FAT32")
                print("    Size:\t\t 200MB")
                choice = input("\nWould you like to still install OpenCore to this drive?(y/n): ")
                if not choice in ["y", "Y", "Yes", "yes"]:
                    subprocess.run(["diskutil", "umount", mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                    return
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
            if not self.constants.recovery_status:
                # RecoveryOS doesn't support dot_clean
                # Remove dot_clean, requires full disk access
                # subprocess.run(["dot_clean", mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                print("- Unmounting EFI partition")
                subprocess.run(["diskutil", "umount", mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print("- OpenCore transfer complete")
            print("\nPress [Enter] to continue.\n")
            input()
        else:
            Utilities.TUIOnlyPrint(["Copying OpenCore"], "Press [Enter] to go back.\n", ["EFI failed to mount!", "Please report this to the devs at GitHub."]).start()
