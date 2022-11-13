# Commands for building the EFI and SMBIOS
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import binascii
import copy
import pickle
import plistlib
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import date

from resources import constants, utilities, device_probe, generate_smbios
from resources.build import bluetooth, firmware, graphics_audio, support, storage, smbios, security
from resources.build.networking import wired, wireless
from data import smbios_data, cpu_data, os_data, model_array


def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise


class build_opencore:
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.constants: constants.Constants = versions
        self.computer = self.constants.computer
        self.gfx0_path = None

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
        utilities.cls()
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
        self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Model"] = self.model

        for name, version, path, check in [
            # Essential kexts
            ("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path, lambda: True),
            ("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path, lambda: self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None"),
            ("SMC-Spoof.kext", self.constants.smcspoof_version, self.constants.smcspoof_path, lambda: self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None"),
            (
                "CPUFriend.kext",
                self.constants.cpufriend_version,
                self.constants.cpufriend_path,
                lambda: self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.disallow_cpufriend is False and self.constants.serial_settings != "None",
            ),
            # Misc
            ("DebugEnhancer.kext", self.constants.debugenhancer_version, self.constants.debugenhancer_path, lambda: self.constants.kext_debug is True),
            ("AppleUSBTrackpad.kext", self.constants.apple_trackpad, self.constants.apple_trackpad_path, lambda: self.model in ["MacBook4,1", "MacBook5,2"]),
        ]:
            support.build_support(self.model, self.constants, self.config).enable_kext(name, version, path, check)

        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True:
            if self.constants.serial_settings == "None":
                # Credit to Parrotgeek1 for boot.efi and hv_vmm_present patch sets
                # print("- Enabling Board ID exemption patch")
                # support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Booter"]["Patch"], "Comment", "Skip Board ID check")["Enabled"] = True

                print("- Enabling VMM exemption patch")
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Legacy")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Ventura")["Enabled"] = True

                # Patch HW_BID to OC_BID
                # Set OC_BID to iMac18,1 Board ID (Mac-F60DEB81FF30ACF6)
                # Goal is to only allow OS booting through OCLP, otherwise failing
                print("- Enabling HW_BID reroute")
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Booter"]["Patch"], "Comment", "Reroute HW_BID to OC_BID")["Enabled"] = True
                self.config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"]["OC_BID"] = "Mac-BE088AF8C5EB4FA2"
                self.config["NVRAM"]["Delete"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"] += ["OC_BID"]
            else:
                print("- Enabling SMC exemption patch")
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.driver.AppleSMC")["Enabled"] = True

        if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("Lilu.kext")["Enabled"] is True:
            # Required for Lilu in 11.0+
            self.config["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True



        if self.constants.fu_status is True:
            # Enable FeatureUnlock.kext
            support.build_support(self.model, self.constants, self.config).enable_kext("FeatureUnlock.kext", self.constants.featureunlock_version, self.constants.featureunlock_path)
            if self.constants.fu_arguments is not None:
                print(f"- Adding additional FeatureUnlock args: {self.constants.fu_arguments}")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += self.constants.fu_arguments

        firmware.build_firmware(self.model, self.constants, self.config).build()
        wired.build_wired(self.model, self.constants, self.config).build()
        wireless.build_wireless(self.model, self.constants, self.config).build()
        graphics_audio.build_graphics_audio(self.model, self.constants, self.config).build()
        bluetooth.build_bluetooth(self.model, self.constants, self.config).build()
        storage.build_storage(self.model, self.constants, self.config).build()

        # CPUFriend
        if self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.serial_settings != "None":
            pp_map_path = Path(self.constants.platform_plugin_plist_path) / Path(f"{self.model}/Info.plist")
            if not pp_map_path.exists():
                raise Exception(f"{pp_map_path} does not exist!!! Please file an issue stating file is missing for {self.model}.")
            Path(self.constants.pp_kext_folder).mkdir()
            Path(self.constants.pp_contents_folder).mkdir()
            shutil.copy(pp_map_path, self.constants.pp_contents_folder)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("CPUFriendDataProvider.kext")["Enabled"] = True


        # Legacy iSight patches
        try:
            if smbios_data.smbios_dictionary[self.model]["Legacy iSight"] is True:
                support.build_support(self.model, self.constants, self.config).enable_kext("LegacyUSBVideoSupport.kext", self.constants.apple_isight_version, self.constants.apple_isight_path)
        except KeyError:
            pass



        # USB Map
        usb_map_path = Path(self.constants.plist_folder_path) / Path("AppleUSBMaps/Info.plist")
        if (
            usb_map_path.exists()
            and (self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True)
            and self.model not in ["Xserve2,1", "Dortania1,1"]
            and (
                (self.model in model_array.Missing_USB_Map or self.model in model_array.Missing_USB_Map_Ventura)
                or self.constants.serial_settings in ["Moderate", "Advanced"])
        ):
            print("- Adding USB-Map.kext")
            Path(self.constants.map_kext_folder).mkdir()
            Path(self.constants.map_contents_folder).mkdir()
            shutil.copy(usb_map_path, self.constants.map_contents_folder)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("USB-Map.kext")["Enabled"] = True
            if self.model in model_array.Missing_USB_Map_Ventura and self.constants.serial_settings not in ["Moderate", "Advanced"]:
                support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("USB-Map.kext")["MinKernel"] = "22.0.0"


        if self.constants.firewire_boot is True and generate_smbios.check_firewire(self.model) is True:
            # Enable FireWire Boot Support
            # Applicable for both native FireWire and Thunderbolt to FireWire adapters
            print("- Enabling FireWire Boot Support")
            support.build_support(self.model, self.constants, self.config).enable_kext("IOFireWireFamily.kext", self.constants.fw_kext, self.constants.fw_family_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IOFireWireSBP2.kext", self.constants.fw_kext, self.constants.fw_sbp2_path)
            support.build_support(self.model, self.constants, self.config).enable_kext("IOFireWireSerialBusProtocolTransport.kext", self.constants.fw_kext, self.constants.fw_bus_path)
            support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("IOFireWireFamily.kext/Contents/PlugIns/AppleFWOHCI.kext")["Enabled"] = True



        if self.constants.disable_tb is True and self.model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3", "MacBookPro11,4", "MacBookPro11,5"]:
            print("- Disabling 2013-2014 laptop Thunderbolt Controller")
            if self.model in ["MacBookPro11,3", "MacBookPro11,5"]:
                # 15" dGPU models: IOACPIPlane:/_SB/PCI0@0/PEG1@10001/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"
            else:
                # 13" and 15" iGPU 2013-2014 models: IOACPIPlane:/_SB/PCI0@0/P0P2@10000/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"

            self.config["DeviceProperties"]["Add"][tb_device_path] = {"class-code": binascii.unhexlify("FFFFFFFF"), "device-id": binascii.unhexlify("FFFF0000")}



        # Pre-Force Touch trackpad support for macOS Ventura
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.skylake.value:
            if self.model.startswith("MacBook"):
                # These units got force touch early, so ignore them
                if self.model not in ["MacBookPro11,4", "MacBookPro11,5", "MacBookPro12,1", "MacBook8,1"]:
                    support.build_support(self.model, self.constants, self.config).enable_kext("AppleUSBTopCase.kext", self.constants.topcase_version, self.constants.top_case_path)
                    support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCButtons.kext")["Enabled"] = True
                    support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext")["Enabled"] = True
                    support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyEventDriver.kext")["Enabled"] = True
                    support.build_support(self.model, self.constants, self.config).enable_kext("AppleUSBMultitouch.kext", self.constants.multitouch_version, self.constants.multitouch_path)

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.constants.resources_path, onerror=rmtree_handler)
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("OpenCanopy.efi", "UEFI", "Drivers")["Enabled"] = True
        support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("OpenRuntime.efi", "UEFI", "Drivers")["Enabled"] = True
        support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("OpenLinuxBoot.efi", "UEFI", "Drivers")["Enabled"] = True
        support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("ResetNvramEntry.efi", "UEFI", "Drivers")["Enabled"] = True


        # RestrictEvents handling
        block_args = ""
        if self.model in ["MacBookPro6,1", "MacBookPro6,2", "MacBookPro9,1", "MacBookPro10,1"]:
            block_args += "gmux,"
        if self.model in model_array.MacPro:
            print("- Disabling memory error reporting")
            block_args += "pcie,"
        gpu_dict = []
        if not self.constants.custom_model:
            gpu_dict = self.constants.computer.gpus
        else:
            if self.model in smbios_data.smbios_dictionary:
                gpu_dict = smbios_data.smbios_dictionary[self.model]["Stock GPUs"]
        for gpu in gpu_dict:
            if not self.constants.custom_model:
                gpu = gpu.arch
            if gpu in [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.NVIDIA.Archs.Kepler,
            ]:
                print("- Disabling mediaanalysisd")
                block_args += "media,"
                break
        if block_args.endswith(","):
            block_args = block_args[:-1]

        if block_args != "":
            print(f"- Setting RestrictEvents block arguments: {block_args}")
            if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
                support.build_support(self.model, self.constants, self.config).enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revblock"] = block_args

        patch_args = ""
        if support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] is True and self.constants.set_content_caching is True:
            print("- Fixing Content Caching support")
            patch_args += "content-caching,"

        if patch_args.endswith(","):
            patch_args = patch_args[:-1]

        if block_args != "" and patch_args == "":
            # Disable unneeded Userspace patching (cs_validate_page is quite expensive)
            patch_args = "none"

        if patch_args != "":
            print(f"- Setting RestrictEvents patch arguments: {patch_args}")
            if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
                support.build_support(self.model, self.constants, self.config).enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revpatch"] = patch_args

        # DEBUG Settings
        if self.constants.verbose_debug is True:
            print("- Enabling Verbose boot")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -v"
        if self.constants.kext_debug is True:
            print("- Enabling DEBUG Kexts")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -liludbgall liludump=90"
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
            print("- Hiding OpenCore picker")
            self.config["Misc"]["Boot"]["ShowPicker"] = False
        if self.constants.oc_timeout != 5:
            print(f"- Setting custom OpenCore picker timeout to {self.constants.oc_timeout} seconds")
            self.config["Misc"]["Boot"]["Timeout"] = self.constants.oc_timeout
        if self.constants.vault is True:
            print("- Setting Vault configuration")
            self.config["Misc"]["Security"]["Vault"] = "Secure"
            support.build_support(self.model, self.constants, self.config).get_efi_binary_by_path("OpenShell.efi", "Misc", "Tools")["Enabled"] = False
        if self.constants.sip_status is False or self.constants.custom_sip_value:
            # Work-around 12.3 bug where Electron apps no longer launch with SIP lowered
            # Unknown whether this is intended behavior or not, revisit with 12.4
            print("- Adding ipc_control_port_options=0 to boot-args")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ipc_control_port_options=0"
            # Adds AutoPkgInstaller for Automatic OpenCore-Patcher installation
            # Only install if running the GUI (AutoPkg-Assets.pkg requires the GUI)
            if self.constants.wxpython_variant is True:
                support.build_support(self.model, self.constants, self.config).enable_kext("AutoPkgInstaller.kext", self.constants.autopkg_version, self.constants.autopkg_path)
            if self.constants.custom_sip_value:
                print(f"- Setting SIP value to: {self.constants.custom_sip_value}")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = utilities.string_to_hex(self.constants.custom_sip_value.lstrip("0x"))
            elif self.constants.sip_status is False:
                print("- Set SIP to allow Root Volume patching")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = binascii.unhexlify("03080000")

            # apfs.kext has an undocumented boot-arg that allows FileVault usage on broken APFS seals (-arv_allow_fv)
            # This is however hidden behind kern.development, thus we patch _apfs_filevault_allowed to always return true
            # Note this function was added in 11.3 (20E232, 20.4), older builds do not support this (ie. 11.2.3)
            print("- Allowing FileVault on Root Patched systems")
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Force FileVault on Broken Seal")["Enabled"] = True
            # Lets us check in sys_patch.py if config supports FileVault
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_fv"

        if self.constants.disable_cs_lv is True:
            print("- Disabling Library Validation")
            # In Ventura, LV patch broke. For now, add AMFI arg
            # Before merging into mainline, this needs to be resolved
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable Library Validation Enforcement")["Enabled"] = True
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable _csr_check() in _vnode_check_signature")["Enabled"] = True
            if self.constants.disable_amfi is True:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi=0x80"
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_amfi"
            # CSLVFixup simply patches out __RESTRICT and __restrict out of the Music.app Binary
            # Ref: https://pewpewthespells.com/blog/blocking_code_injection_on_ios_and_os_x.html
            support.build_support(self.model, self.constants, self.config).enable_kext("CSLVFixup.kext", self.constants.cslvfixup_version, self.constants.cslvfixup_path)
        if self.constants.secure_status is False:
            print("- Disabling SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"
            if self.constants.force_vmm is True:
                print("- Forcing VMM patchset to support OTA updates")
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Legacy")["Enabled"] = True
                support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Ventura")["Enabled"] = True
        if self.constants.serial_settings in ["Moderate", "Advanced"]:
            print("- Enabling USB Rename Patches")
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "XHC1 to SHC1")["Enabled"] = True
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC1 to EH01")["Enabled"] = True
            support.build_support(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "EHC2 to EH02")["Enabled"] = True
        if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpu"] = self.constants.custom_cpu_model
            if self.constants.custom_cpu_model_value != "":
                print(f"- Adding custom CPU Name: {self.constants.custom_cpu_model_value}")
                self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpuname"] = self.constants.custom_cpu_model_value
            else:
                print("- Adding CPU Name Patch")
            if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
                support.build_support(self.model, self.constants, self.config).enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
        if self.model == self.constants.override_smbios:
            print("- Adding -no_compat_check")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -no_compat_check"
        if self.constants.disk != "":
            self.disk_type()
        if self.constants.validate is False:
            print("- Adding bootmgfw.efi BlessOverride")
            self.config["Misc"]["BlessOverride"] += ["\\EFI\\Microsoft\\Boot\\bootmgfw.efi"]


        if support.build_support(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
            # Ensure this is done at the end so all previous RestrictEvents patches are applied
            # RestrictEvents and EFICheckDisabler will conflict if both are injected
            support.build_support(self.model, self.constants, self.config).enable_kext("EFICheckDisabler.kext", "", self.constants.efi_disabler_path)


    def build_opencore(self):
        self.build_efi()
        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True or (self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != ""):
            smbios.build_smbios(self.model, self.constants, self.config).set_smbios()
        support.build_support(self.model, self.constants, self.config).cleanup()
        support.build_support(self.model, self.constants, self.config).sign_files()
        support.build_support(self.model, self.constants, self.config).validate_pathing()
        print("")
        print(f"Your OpenCore EFI for {self.model} has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to continue\n")
