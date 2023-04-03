# Class for handling Misc Patches, invocation from build.py
# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

import shutil
import logging
import binascii

from pathlib import Path

from resources import constants, device_probe, generate_smbios, utilities
from resources.build import support
from data import model_array, smbios_data, cpu_data


class BuildMiscellaneous:
    """
    Build Library for Miscellaneous Hardware and Software Support

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants
        self.computer: device_probe.Computer = self.constants.computer

        self._build()


    def _build(self) -> None:
        """
        Kick off Misc Build Process
        """

        self._feature_unlock_handling()
        self._restrict_events_handling()
        self._firewire_handling()
        self._trackpad_handling()
        self._thunderbolt_handling()
        self._webcam_handling()
        self._usb_handling()
        self._debug_handling()
        self._cpu_friend_handling()
        self._general_oc_handling()


    def _feature_unlock_handling(self) -> None:
        """
        FeatureUnlock Handler
        """

        if self.constants.fu_status is False:
            return

        support.BuildSupport(self.model, self.constants, self.config).enable_kext("FeatureUnlock.kext", self.constants.featureunlock_version, self.constants.featureunlock_path)
        if self.constants.fu_arguments is not None:
            logging.info(f"- Adding additional FeatureUnlock args: {self.constants.fu_arguments}")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += self.constants.fu_arguments


    def _restrict_events_handling(self) -> None:
        """
        RestrictEvents Handler
        """

        block_args = ",".join(self._re_generate_block_arguments())
        patch_args = ",".join(self._re_generate_patch_arguments())

        if block_args != "":
            logging.info(f"- Setting RestrictEvents block arguments: {block_args}")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revblock"] = block_args

        if block_args != "" and patch_args == "":
            # Disable unneeded Userspace patching (cs_validate_page is quite expensive)
            patch_args = "none"

        if patch_args != "":
            logging.info(f"- Setting RestrictEvents patch arguments: {patch_args}")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revpatch"] = patch_args

        if support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
            # Ensure this is done at the end so all previous RestrictEvents patches are applied
            # RestrictEvents and EFICheckDisabler will conflict if both are injected
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("EFICheckDisabler.kext", "", self.constants.efi_disabler_path)


    def _re_generate_block_arguments(self) -> list:
        """
        Generate RestrictEvents block arguments

        Returns:
            list: RestrictEvents block arguments
        """

        re_block_args = []

        # Resolve GMUX switching in Big Sur+
        if self.model in ["MacBookPro6,1", "MacBookPro6,2", "MacBookPro9,1", "MacBookPro10,1"]:
            re_block_args.append("gmux")

        # Resolve memory error reporting on MacPro7,1 SMBIOS
        if self.model in model_array.MacPro:
            logging.info("- Disabling memory error reporting")
            re_block_args.append("pcie")

        # Resolve mediaanalysisd crashing on 3802 GPUs
        gpu_dict = [] if self.constants.custom_model else self.constants.computer.gpus
        if gpu_dict == []:
            gpu_dict = smbios_data.smbios_dictionary[self.model]["Stock GPUs"] if self.model in smbios_data.smbios_dictionary else []

        for gpu in gpu_dict:
            if not self.constants.custom_model:
                gpu = gpu.arch
            if gpu in [
                device_probe.Intel.Archs.Ivy_Bridge,
                device_probe.Intel.Archs.Haswell,
                device_probe.NVIDIA.Archs.Kepler,
            ]:
                logging.info("- Disabling mediaanalysisd")
                re_block_args.append("media")
                break

        return re_block_args


    def _re_generate_patch_arguments(self) -> list:
        """
        Generate RestrictEvents patch arguments

        Returns:
            list: Patch arguments
        """

        re_patch_args = []

        # Resolve content caching when kern.hv_vmm_present is set
        if support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] is True and self.constants.set_content_caching is True:
            logging.info("- Fixing Content Caching support")
            re_patch_args.append("asset")

        # Resolve CoreGraphics.framework crashing on Ivy Bridge in macOS 13.3+
        # Ref: https://github.com/acidanthera/RestrictEvents/pull/12
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.cpu_data.ivy_bridge.value:
            logging.info("- Fixing CoreGraphics support on Ivy Bridge")
            re_patch_args.append("f16c")

        return re_patch_args


    def _cpu_friend_handling(self) -> None:
        """
        CPUFriend Handler
        """

        if self.constants.allow_oc_everywhere is False and self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.disallow_cpufriend is False and self.constants.serial_settings != "None":
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("CPUFriend.kext", self.constants.cpufriend_version, self.constants.cpufriend_path)

            # CPUFriendDataProvider handling
            pp_map_path = Path(self.constants.platform_plugin_plist_path) / Path(f"{self.model}/Info.plist")
            if not pp_map_path.exists():
                raise Exception(f"{pp_map_path} does not exist!!! Please file an issue stating file is missing for {self.model}.")
            Path(self.constants.pp_kext_folder).mkdir()
            Path(self.constants.pp_contents_folder).mkdir()
            shutil.copy(pp_map_path, self.constants.pp_contents_folder)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("CPUFriendDataProvider.kext")["Enabled"] = True


    def _firewire_handling(self) -> None:
        """
        FireWire Handler
        """

        if self.constants.firewire_boot is False:
            return
        if generate_smbios.check_firewire(self.model) is False:
            return

        # Enable FireWire Boot Support
        # Applicable for both native FireWire and Thunderbolt to FireWire adapters
        logging.info("- Enabling FireWire Boot Support")
        support.BuildSupport(self.model, self.constants, self.config).enable_kext("IOFireWireFamily.kext", self.constants.fw_kext, self.constants.fw_family_path)
        support.BuildSupport(self.model, self.constants, self.config).enable_kext("IOFireWireSBP2.kext", self.constants.fw_kext, self.constants.fw_sbp2_path)
        support.BuildSupport(self.model, self.constants, self.config).enable_kext("IOFireWireSerialBusProtocolTransport.kext", self.constants.fw_kext, self.constants.fw_bus_path)
        support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("IOFireWireFamily.kext/Contents/PlugIns/AppleFWOHCI.kext")["Enabled"] = True


    def _trackpad_handling(self) -> None:
        """
        Trackpad Handler
        """

        # Pre-Force Touch trackpad support for macOS Ventura
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.skylake.value:
            if self.model.startswith("MacBook"):
                # These units got force touch early, so ignore them
                if self.model not in ["MacBookPro11,4", "MacBookPro11,5", "MacBookPro12,1", "MacBook8,1"]:
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleUSBTopCase.kext", self.constants.topcase_version, self.constants.top_case_path)
                    support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCButtons.kext")["Enabled"] = True
                    support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext")["Enabled"] = True
                    support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyEventDriver.kext")["Enabled"] = True
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleUSBMultitouch.kext", self.constants.multitouch_version, self.constants.multitouch_path)
        # Legacy Trackpad support
        if self.model in ["MacBook4,1", "MacBook5,2"]:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleUSBTrackpad.kext", self.constants.apple_trackpad, self.constants.apple_trackpad_path)


    def _thunderbolt_handling(self) -> None:
        """
        Thunderbolt Handler
        """

        if self.constants.disable_tb is True and self.model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3", "MacBookPro11,4", "MacBookPro11,5"]:
            logging.info("- Disabling 2013-2014 laptop Thunderbolt Controller")
            if self.model in ["MacBookPro11,3", "MacBookPro11,5"]:
                # 15" dGPU models: IOACPIPlane:/_SB/PCI0@0/PEG1@10001/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"
            else:
                # 13" and 15" iGPU 2013-2014 models: IOACPIPlane:/_SB/PCI0@0/P0P2@10000/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"

            self.config["DeviceProperties"]["Add"][tb_device_path] = {"class-code": binascii.unhexlify("FFFFFFFF"), "device-id": binascii.unhexlify("FFFF0000")}


    def _webcam_handling(self) -> None:
        """
        iSight Handler
        """

        if "Legacy iSight" in smbios_data.smbios_dictionary[self.model]:
            if smbios_data.smbios_dictionary[self.model]["Legacy iSight"] is True:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("LegacyUSBVideoSupport.kext", self.constants.apple_isight_version, self.constants.apple_isight_path)


    def _usb_handling(self) -> None:
        """
        USB Handler
        """

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
            logging.info("- Adding USB-Map.kext")
            Path(self.constants.map_kext_folder).mkdir()
            Path(self.constants.map_contents_folder).mkdir()
            shutil.copy(usb_map_path, self.constants.map_contents_folder)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB-Map.kext")["Enabled"] = True
            if self.model in model_array.Missing_USB_Map_Ventura and self.constants.serial_settings not in ["Moderate", "Advanced"]:
                support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB-Map.kext")["MinKernel"] = "22.0.0"

        # Add UHCI/OHCI drivers
        # All Penryn Macs lack an internal USB hub to route USB 1.1 devices to the EHCI controller
        # And MacPro4,1 and MacPro5,1 are the only post-Penryn Macs that lack an internal USB hub
        # - Ref: https://techcommunity.microsoft.com/t5/microsoft-usb-blog/reasons-to-avoid-companion-controllers/ba-p/270710
        #
        # To be paired for sys_patch_dict.py's 'Legacy USB 1.1' patchset
        if (
            smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value or \
            self.model in ["MacPro4,1", "MacPro5,1"]
        ):
            logging.info("- Adding UHCI/OHCI USB support")
            shutil.copy(self.constants.apple_usb_11_injector_path, self.constants.kexts_path)
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCI.kext")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCIPCI.kext")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCI.kext")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCIPCI.kext")["Enabled"] = True


    def _debug_handling(self) -> None:
        """
        Debug Handler for OpenCorePkg and Kernel Space
        """

        if self.constants.verbose_debug is True:
            logging.info("- Enabling Verbose boot")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -v"

        if self.constants.kext_debug is True:
            logging.info("- Enabling DEBUG Kexts")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -liludbgall liludump=90"
            # Disabled due to macOS Monterey crashing shortly after kernel init
            # Use DebugEnhancer.kext instead
            # self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " msgbuf=1048576"
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("DebugEnhancer.kext", self.constants.debugenhancer_version, self.constants.debugenhancer_path)

        if self.constants.opencore_debug is True:
            logging.info("- Enabling DEBUG OpenCore")
            self.config["Misc"]["Debug"]["Target"] = 0x43
            self.config["Misc"]["Debug"]["DisplayLevel"] = 0x80000042


    def _general_oc_handling(self) -> None:
        """
        General OpenCorePkg Handler
        """

        logging.info("- Adding OpenCanopy GUI")
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("OpenCanopy.efi", "UEFI", "Drivers")["Enabled"] = True
        support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("OpenRuntime.efi", "UEFI", "Drivers")["Enabled"] = True
        support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("OpenLinuxBoot.efi", "UEFI", "Drivers")["Enabled"] = True
        support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("ResetNvramEntry.efi", "UEFI", "Drivers")["Enabled"] = True

        if self.constants.showpicker is False:
            logging.info("- Hiding OpenCore picker")
            self.config["Misc"]["Boot"]["ShowPicker"] = False

        if self.constants.oc_timeout != 5:
            logging.info(f"- Setting custom OpenCore picker timeout to {self.constants.oc_timeout} seconds")
            self.config["Misc"]["Boot"]["Timeout"] = self.constants.oc_timeout

        if self.constants.vault is True and utilities.check_command_line_tools() is True:
            logging.info("- Setting Vault configuration")
            self.config["Misc"]["Security"]["Vault"] = "Secure"
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("OpenShell.efi", "Misc", "Tools")["Enabled"] = False