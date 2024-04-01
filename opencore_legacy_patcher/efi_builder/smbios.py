"""
smbios.py: Class for handling SMBIOS Patches, invocation from build.py
"""

import ast
import uuid
import logging
import binascii
import plistlib
import subprocess

from pathlib import Path

from . import support

from .. import constants

from ..support import (
    utilities,
    generate_smbios
)
from ..datasets import (
    smbios_data,
    cpu_data,
    model_array
)


class BuildSMBIOS:
    """
    Build Library for SMBIOS Support

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants

        self._build()


    def _build(self) -> None:
        """
        Kick off SMBIOS Build Process
        """

        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True:
            if self.constants.serial_settings == "None":
                # Credit to Parrotgeek1 for boot.efi and hv_vmm_present patch sets
                logging.info("- Enabling Board ID exemption patch")
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Booter"]["Patch"], "Comment", "Skip Board ID check")["Enabled"] = True

            else:
                logging.info("- Enabling SMC exemption patch")
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.driver.AppleSMC")["Enabled"] = True
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("SMC-Spoof.kext", self.constants.smcspoof_version, self.constants.smcspoof_path)

        if self.constants.serial_settings in ["Moderate", "Advanced"]:
            logging.info("- Enabling USB Rename Patches")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "XHC1 to SHC1")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC1 to EH01")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC2 to EH02")["Enabled"] = True

        if self.model == self.constants.override_smbios:
            logging.info("- Adding -no_compat_check")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -no_compat_check"


    def set_smbios(self) -> None:
        """
        SMBIOS Handler
        """

        spoofed_model = self.model

        if self.constants.override_smbios == "Default":
            if self.constants.serial_settings != "None":
                logging.info("- Setting macOS Monterey Supported SMBIOS")
                if self.constants.allow_native_spoofs is True:
                    spoofed_model = self.model
                else:
                    spoofed_model = generate_smbios.set_smbios_model_spoof(self.model)
        else:
            spoofed_model = self.constants.override_smbios
        logging.info(f"- Using Model ID: {spoofed_model}")

        spoofed_board = ""
        if spoofed_model in smbios_data.smbios_dictionary:
            if "Board ID" in smbios_data.smbios_dictionary[spoofed_model]:
                spoofed_board = smbios_data.smbios_dictionary[spoofed_model]["Board ID"]
        logging.info(f"- Using Board ID: {spoofed_board}")

        self.spoofed_model = spoofed_model
        self.spoofed_board = spoofed_board

        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True:
            self.config["#Revision"]["Spoofed-Model"] = f"{self.spoofed_model} - {self.constants.serial_settings}"

        if self.constants.serial_settings == "Moderate":
            logging.info("- Using Moderate SMBIOS patching")
            self._moderate_serial_patch()
        elif self.constants.serial_settings == "Advanced":
            logging.info("- Using Advanced SMBIOS patching")
            self._advanced_serial_patch()
        elif self.constants.serial_settings == "Minimal":
            logging.info("- Using Minimal SMBIOS patching")
            self.spoofed_model = self.model
            self._minimal_serial_patch()
        else:
            # Update DataHub to resolve Lilu Race Condition
            # macOS Monterey will sometimes not present the boardIdentifier in the DeviceTree on UEFI 1.2 or older Mac,
            # Thus resulting in an infinite loop as Lilu tries to request the Board ID
            # To resolve this, set PlatformInfo -> DataHub -> BoardProduct and enable UpdateDataHub

            # Note 1: Only apply if system is UEFI 1.2, this is generally Ivy Bridge and older
            # Note 2: Flipping 'UEFI -> ProtocolOverrides -> DataHub' will break hibernation
            if (smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value and self.model):
                logging.info("- Detected UEFI 1.2 or older Mac, updating BoardProduct")
                self.config["PlatformInfo"]["DataHub"]["BoardProduct"] = self.spoofed_board
                self.config["PlatformInfo"]["UpdateDataHub"] = True

            if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
                logging.info("- Adding custom serial numbers")
                self.config["PlatformInfo"]["Automatic"] = True
                self.config["PlatformInfo"]["UpdateDataHub"] = True
                self.config["PlatformInfo"]["UpdateNVRAM"] = True
                self.config["PlatformInfo"]["UpdateSMBIOS"] = True
                self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
                self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = self.constants.custom_serial_number
                self.config["PlatformInfo"]["Generic"]["MLB"] = self.constants.custom_board_serial_number
                self.config["PlatformInfo"]["Generic"]["MaxBIOSVersion"] = False
                self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model
                self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-SN"] = self.constants.custom_serial_number
                self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-MLB"] = self.constants.custom_board_serial_number

        # USB Map and CPUFriend Patching
        if (
            self.constants.allow_oc_everywhere is False
            and self.model not in ["Xserve2,1", "Dortania1,1"]
            and ((self.model in model_array.Missing_USB_Map or self.model in model_array.Missing_USB_Map_Ventura) or self.constants.serial_settings in ["Moderate", "Advanced"])
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
                        if self.constants.serial_settings in ["Minimal", "None"]:
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "EH01":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "EHC1"
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "EH02":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "EHC2"
                            if map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] == "SHC1":
                                map_config["IOKitPersonalities_x86_64"][entry]["IONameMatch"] = "XHC1"
                    except KeyError:
                        continue
            plistlib.dump(map_config, Path(new_map_ls).open("wb"), sort_keys=True)
        if self.constants.allow_oc_everywhere is False and self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.disallow_cpufriend is False and self.constants.serial_settings != "None":
            # Adjust CPU Friend Data to correct SMBIOS
            new_cpu_ls = Path(self.constants.pp_contents_folder) / Path("Info.plist")
            cpu_config = plistlib.load(Path(new_cpu_ls).open("rb"))
            string_stuff = str(cpu_config["IOKitPersonalities"]["CPUFriendDataProvider"]["cf-frequency-data"])
            string_stuff = string_stuff.replace(self.model, self.spoofed_model)
            string_stuff = ast.literal_eval(string_stuff)
            cpu_config["IOKitPersonalities"]["CPUFriendDataProvider"]["cf-frequency-data"] = string_stuff
            plistlib.dump(cpu_config, Path(new_cpu_ls).open("wb"), sort_keys=True)

        if self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None":
            if self.model == "MacBookPro9,1":
                new_amc_ls = Path(self.constants.amc_contents_folder) / Path("Info.plist")
                amc_config = plistlib.load(Path(new_amc_ls).open("rb"))
                amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"][self.spoofed_board] = amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"].pop(self.model)
                for entry in list(amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"]):
                    if not entry.startswith(self.spoofed_board):
                        amc_config["IOKitPersonalities"]["AppleMuxControl"]["ConfigMap"].pop(entry)
                plistlib.dump(amc_config, Path(new_amc_ls).open("wb"), sort_keys=True)
            if self.model not in model_array.NoAGPMSupport:
                new_agpm_ls = Path(self.constants.agpm_contents_folder) / Path("Info.plist")
                agpm_config = plistlib.load(Path(new_agpm_ls).open("rb"))
                agpm_config["IOKitPersonalities"]["AGPM"]["Machines"][self.spoofed_board] = agpm_config["IOKitPersonalities"]["AGPM"]["Machines"].pop(self.model)
                if self.model == "MacBookPro6,2":
                    # Force G State to not exceed moderate state
                    # Ref: https://github.com/fabioiop/MBP-2010-GPU-Panic-fix
                    logging.info("- Patching G State for MacBookPro6,2")
                    for gpu in ["Vendor10deDevice0a34", "Vendor10deDevice0a29"]:
                        agpm_config["IOKitPersonalities"]["AGPM"]["Machines"][self.spoofed_board][gpu]["BoostPState"] = [2, 2, 2, 2]
                        agpm_config["IOKitPersonalities"]["AGPM"]["Machines"][self.spoofed_board][gpu]["BoostTime"] = [2, 2, 2, 2]

                for entry in list(agpm_config["IOKitPersonalities"]["AGPM"]["Machines"]):
                    if not entry.startswith(self.spoofed_board):
                        agpm_config["IOKitPersonalities"]["AGPM"]["Machines"].pop(entry)

                plistlib.dump(agpm_config, Path(new_agpm_ls).open("wb"), sort_keys=True)
            if self.model in model_array.AGDPSupport:
                new_agdp_ls = Path(self.constants.agdp_contents_folder) / Path("Info.plist")
                agdp_config = plistlib.load(Path(new_agdp_ls).open("rb"))
                agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"][self.spoofed_board] = agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"].pop(
                    self.model
                )
                for entry in list(agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"]):
                    if not entry.startswith(self.spoofed_board):
                        agdp_config["IOKitPersonalities"]["AppleGraphicsDevicePolicy"]["ConfigMap"].pop(entry)
                plistlib.dump(agdp_config, Path(new_agdp_ls).open("wb"), sort_keys=True)


    def _minimal_serial_patch(self) -> None:
        """
        Minimal SMBIOS Spoofing Handler

        This function will only spoof the following:
        - Board ID
        - Firmware Features
        - BIOS Version
        - Serial Numbers (if override requested)
        """

        # Generate Firmware Features
        fw_feature = generate_smbios.generate_fw_features(self.model, self.constants.custom_model)
        # fw_feature = self.patch_firmware_feature()
        fw_feature = hex(fw_feature).lstrip("0x").rstrip("L").strip()
        logging.info(f"- Setting Firmware Feature: {fw_feature}")
        fw_feature = utilities.string_to_hex(fw_feature)

        # FirmwareFeatures
        self.config["PlatformInfo"]["PlatformNVRAM"]["FirmwareFeatures"] = fw_feature
        self.config["PlatformInfo"]["PlatformNVRAM"]["FirmwareFeaturesMask"] = fw_feature
        self.config["PlatformInfo"]["SMBIOS"]["FirmwareFeatures"] = fw_feature
        self.config["PlatformInfo"]["SMBIOS"]["FirmwareFeaturesMask"] = fw_feature

        # Board ID
        self.config["PlatformInfo"]["DataHub"]["BoardProduct"] = self.spoofed_board
        self.config["PlatformInfo"]["PlatformNVRAM"]["BID"] = self.spoofed_board
        self.config["PlatformInfo"]["SMBIOS"]["BoardProduct"] = self.spoofed_board

        # Model (ensures tables are not mismatched, even if we're not spoofing)
        self.config["PlatformInfo"]["DataHub"]["SystemProductName"] = self.model
        self.config["PlatformInfo"]["SMBIOS"]["SystemProductName"] = self.model
        self.config["PlatformInfo"]["SMBIOS"]["BoardVersion"] = self.model

        # Avoid incorrect Firmware Updates
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
        self.config["PlatformInfo"]["SMBIOS"]["BIOSVersion"] = "9999.999.999.999.999"

        # Update tables
        self.config["PlatformInfo"]["UpdateNVRAM"] = True
        self.config["PlatformInfo"]["UpdateSMBIOS"] = True
        self.config["PlatformInfo"]["UpdateDataHub"] = True

        if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
            logging.info("- Adding custom serial numbers")
            sn = self.constants.custom_serial_number
            mlb = self.constants.custom_board_serial_number

            # Serial Number
            self.config["PlatformInfo"]["SMBIOS"]["ChassisSerialNumber"] = sn
            self.config["PlatformInfo"]["SMBIOS"]["SystemSerialNumber"] = sn
            self.config["PlatformInfo"]["DataHub"]["SystemSerialNumber"] = sn
            self.config["PlatformInfo"]["PlatformNVRAM"]["SystemSerialNumber"] = sn
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-SN"] = sn

            # Board Serial Number
            self.config["PlatformInfo"]["SMBIOS"]["BoardSerialNumber"] = mlb
            self.config["PlatformInfo"]["PlatformNVRAM"]["BoardSerialNumber"] = mlb
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-MLB"] = mlb


    def _moderate_serial_patch(self) -> None:
        """
        Moderate SMBIOS Spoofing Handler

        Implements a full SMBIOS replacement, however retains original serial numbers (unless override requested)
        """

        if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
            logging.info("- Adding custom serial numbers")
            self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = self.constants.custom_serial_number
            self.config["PlatformInfo"]["Generic"]["MLB"] = self.constants.custom_board_serial_number
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-SN"] = self.constants.custom_serial_number
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-MLB"] = self.constants.custom_board_serial_number
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
        self.config["PlatformInfo"]["Automatic"] = True
        self.config["PlatformInfo"]["UpdateDataHub"] = True
        self.config["PlatformInfo"]["UpdateNVRAM"] = True
        self.config["PlatformInfo"]["UpdateSMBIOS"] = True
        self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
        self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model


    def _advanced_serial_patch(self) -> None:
        """
        Advanced SMBIOS Spoofing Handler

        Implements a full SMBIOS replacement, including serial numbers
        """

        if self.constants.custom_serial_number == "" or self.constants.custom_board_serial_number == "":
            macserial_output = subprocess.run([self.constants.macserial_path, "--generate", "--model", self.spoofed_model, "--num", "1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            macserial_output = macserial_output.stdout.decode().strip().split(" | ")
            sn = macserial_output[0]
            mlb = macserial_output[1]
        else:
            sn = self.constants.custom_serial_number
            mlb = self.constants.custom_board_serial_number
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
        self.config["PlatformInfo"]["Automatic"] = True
        self.config["PlatformInfo"]["UpdateDataHub"] = True
        self.config["PlatformInfo"]["UpdateNVRAM"] = True
        self.config["PlatformInfo"]["UpdateSMBIOS"] = True
        self.config["UEFI"]["ProtocolOverrides"]["DataHub"] = True
        self.config["PlatformInfo"]["Generic"]["ROM"] = binascii.unhexlify("0016CB445566")
        self.config["PlatformInfo"]["Generic"]["SystemProductName"] = self.spoofed_model
        self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = sn
        self.config["PlatformInfo"]["Generic"]["MLB"] = mlb
        self.config["PlatformInfo"]["Generic"]["SystemUUID"] = str(uuid.uuid4()).upper()
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-SN"] = sn
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Spoofed-MLB"] = mlb