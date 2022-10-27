# Commands for building the EFI and SMBIOS
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

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

from resources import constants, utilities, device_probe, generate_smbios
from data import smbios_data, bluetooth_data, cpu_data, os_data, model_array


def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise


class BuildOpenCore:
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

    def chainload_diags(self):
        Path(self.constants.opencore_release_folder / Path("System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers")).mkdir(parents=True, exist_ok=True)
        if self.constants.boot_efi is True:
            path_oc_loader = self.constants.opencore_release_folder / Path("EFI/BOOT/BOOTx64.efi")
        else:
            path_oc_loader = self.constants.opencore_release_folder / Path("System/Library/CoreServices/boot.efi")
        shutil.move(path_oc_loader, self.constants.opencore_release_folder / Path("System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers/Product.efi"))
        shutil.copy(self.constants.diags_launcher_path, self.constants.opencore_release_folder)
        shutil.move(self.constants.opencore_release_folder / Path("diags.efi"), self.constants.opencore_release_folder / Path("boot.efi"))

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
            ("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path, lambda: self.model in model_array.MacPro),
            ("SMC-Spoof.kext", self.constants.smcspoof_version, self.constants.smcspoof_path, lambda: self.constants.allow_oc_everywhere is False and self.constants.serial_settings != "None"),
            # CPU patches
            ("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path, lambda: smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value),
            (
                "telemetrap.kext",
                self.constants.telemetrap_version,
                self.constants.telemetrap_path,
                lambda: smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value,
            ),
            (
                "CPUFriend.kext",
                self.constants.cpufriend_version,
                self.constants.cpufriend_path,
                lambda: self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.disallow_cpufriend is False and self.constants.serial_settings != "None",
            ),
            # Legacy audio
            (
                "AppleALC.kext",
                self.constants.applealc_version,
                self.constants.applealc_path,
                lambda: (self.model in model_array.LegacyAudio or self.model in model_array.MacPro) and self.constants.set_alc_usage is True,
            ),
            # IDE patch
            ("AppleIntelPIIXATA.kext", self.constants.piixata_version, self.constants.piixata_path, lambda: "PATA" in smbios_data.smbios_dictionary[self.model]["Stock Storage"]),
            # Misc
            ("DebugEnhancer.kext", self.constants.debugenhancer_version, self.constants.debugenhancer_path, lambda: self.constants.kext_debug is True),
            ("AppleUSBTrackpad.kext", self.constants.apple_trackpad, self.constants.apple_trackpad_path, lambda: self.model in ["MacBook4,1", "MacBook5,2"]),
        ]:
            self.enable_kext(name, version, path, check)

        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True:
            if self.constants.serial_settings == "None":
                # Credit to Parrotgeek1 for boot.efi and hv_vmm_present patch sets
                # print("- Enabling Board ID exemption patch")
                # self.get_item_by_kv(self.config["Booter"]["Patch"], "Comment", "Skip Board ID check")["Enabled"] = True

                print("- Enabling VMM exemption patch")
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] = True
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Legacy")["Enabled"] = True
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Ventura")["Enabled"] = True

                # Patch HW_BID to OC_BID
                # Set OC_BID to iMac18,1 Board ID (Mac-F60DEB81FF30ACF6)
                # Goal is to only allow OS booting through OCLP, otherwise failing
                print("- Enabling HW_BID reroute")
                self.get_item_by_kv(self.config["Booter"]["Patch"], "Comment", "Reroute HW_BID to OC_BID")["Enabled"] = True
                self.config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"]["OC_BID"] = "Mac-BE088AF8C5EB4FA2"
                self.config["NVRAM"]["Delete"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"] += ["OC_BID"]
            else:
                print("- Enabling SMC exemption patch")
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.driver.AppleSMC")["Enabled"] = True

        if self.get_kext_by_bundle_path("Lilu.kext")["Enabled"] is True:
            # Required for Lilu in 11.0+
            self.config["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True

        if self.constants.serial_settings != "None":
            # AppleMCEReporter is very picky about which models attach to the kext
            # Commonly it will kernel panic on multi-socket systems, however even on single-socket systems it may cause instability
            # To avoid any issues, we'll disable it if the spoof is set to an affected SMBIOS
            affected_smbios = ["MacPro6,1", "MacPro7,1", "iMacPro1,1"]
            if self.model not in affected_smbios:
                # If MacPro6,1 host spoofs, we can safely enable it
                if self.constants.override_smbios in affected_smbios or generate_smbios.set_smbios_model_spoof(self.model) in affected_smbios:
                    self.enable_kext("AppleMCEReporterDisabler.kext", self.constants.mce_version, self.constants.mce_path)

        if self.constants.fu_status is True:
            # Enable FeatureUnlock.kext
            self.enable_kext("FeatureUnlock.kext", self.constants.featureunlock_version, self.constants.featureunlock_path)
            if self.constants.fu_arguments is not None:
                print(f"- Adding additional FeatureUnlock args: {self.constants.fu_arguments}")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += self.constants.fu_arguments

        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge.value or self.constants.disable_xcpm is True:
            # With macOS 12.3 Beta 1, Apple dropped the 'plugin-type' check within X86PlatformPlugin
            # Because of this, X86PP will match onto the CPU instead of ACPI_SMC_PlatformPlugin
            # This causes power management to break on pre-Ivy Bridge CPUs as they don't have correct
            # power management tables provided.
            # This patch will simply increase ASPP's 'IOProbeScore' to outmatch X86PP
            print("- Overriding ACPI SMC matching")
            self.enable_kext("ASPP-Override.kext", self.constants.aspp_override_version, self.constants.aspp_override_path)
            if self.constants.disable_xcpm is True:
                # Only inject on older OSes if user requests
                self.get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", "ASPP-Override.kext")["MinKernel"] = ""

        if self.model in ["MacBookPro6,1", "MacBookPro6,2", "MacBookPro9,1", "MacBookPro10,1"]:
            # Modded RestrictEvents with displaypolicyd blocked to fix dGPU switching
            self.enable_kext("RestrictEvents.kext", self.constants.restrictevents_mbp_version, self.constants.restrictevents_mbp_path)

        if not self.constants.custom_model and self.constants.computer.ethernet:
            for controller in self.constants.computer.ethernet:
                if isinstance(controller, device_probe.BroadcomEthernet) and controller.chipset == device_probe.BroadcomEthernet.Chipsets.AppleBCM5701Ethernet:
                    if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                        # Required due to Big Sur's BCM5701 requiring VT-D support
                        # Applicable for pre-Ivy Bridge models
                        if self.get_kext_by_bundle_path("CatalinaBCM5701Ethernet.kext")["Enabled"] is False:
                            self.enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
                elif isinstance(controller, device_probe.IntelEthernet):
                    if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                        # Apple's IOSkywalkFamily in DriverKit requires VT-D support
                        # Applicable for pre-Ivy Bridge models
                        if controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntelI210Ethernet:
                            if self.get_kext_by_bundle_path("CatalinaIntelI210Ethernet.kext")["Enabled"] is False:
                                self.enable_kext("CatalinaIntelI210Ethernet.kext", self.constants.i210_version, self.constants.i210_path)
                        elif controller.chipset == device_probe.IntelEthernet.Chipsets.AppleIntel8254XEthernet:
                            if self.get_kext_by_bundle_path("AppleIntel8254XEthernet.kext")["Enabled"] is False:
                                self.enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
                        elif controller.chipset == device_probe.IntelEthernet.Chipsets.Intel82574L:
                            if self.get_kext_by_bundle_path("Intel82574L.kext")["Enabled"] is False:
                                self.enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)
                elif isinstance(controller, device_probe.NVIDIAEthernet):
                    if self.get_kext_by_bundle_path("nForceEthernet.kext")["Enabled"] is False:
                        self.enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
                elif isinstance(controller, device_probe.Marvell) or  isinstance(controller, device_probe.SysKonnect):
                    if self.get_kext_by_bundle_path("MarvelYukonEthernet.kext")["Enabled"] is False:
                        self.enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)
        else:
            if smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Broadcom":
                if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.ivy_bridge.value:
                    # Required due to Big Sur's BCM5701 requiring VT-D support
                    # Applicable for pre-Ivy Bridge models
                    self.enable_kext("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path)
            elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Nvidia":
                self.enable_kext("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path)
            elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Marvell":
                self.enable_kext("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path)
            elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 80003ES2LAN":
                self.enable_kext("AppleIntel8254XEthernet.kext", self.constants.intel_8254x_version, self.constants.intel_8254x_path)
            elif smbios_data.smbios_dictionary[self.model]["Ethernet Chipset"] == "Intel 82574L":
                self.enable_kext("Intel82574L.kext", self.constants.intel_82574l_version, self.constants.intel_82574l_path)


        # i3 Ivy Bridge iMacs don't support RDRAND
        # However for prebuilt, assume they do
        if (not self.constants.custom_model and "RDRAND" not in self.computer.cpu.flags) or \
            (smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge.value):
            # Ref: https://github.com/reenigneorcim/SurPlus
            # Enable for all systems missing RDRAND support
            print("- Adding SurPlus Patch for Race Condition")
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 1 of 2 - Patch read_erandom (inlined in _early_random)")["Enabled"] = True
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 2 of 2 - Patch register_and_init_prng")["Enabled"] = True
            if self.constants.force_surplus is True:
                # Syncretic forces SurPlus to only run on Beta 7 and older by default for saftey reasons
                # If users desires, allow forcing in newer OSes
                print("- Allowing SurPlus on all newer OSes")
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 1 of 2 - Patch read_erandom (inlined in _early_random)")["MaxKernel"] = ""
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 2 of 2 - Patch register_and_init_prng")["MaxKernel"] = ""

        # In macOS 12.4 and 12.5 Beta 1, Apple added AVX1.0 usage in AppleFSCompressionTypeZlib
        # Pre-Sandy Bridge CPUs don't support AVX1.0, thus we'll downgrade the kext to 12.3.1's
        # Currently a (hopefully) temporary workaround for the issue, proper fix needs to be investigated
        # Ref:
        #    https://forums.macrumors.com/threads/macos-12-monterey-on-unsupported-macs-thread.2299557/post-31120235
        #    https://forums.macrumors.com/threads/monterand-probably-the-start-of-an-ongoing-saga.2320479/post-31123553

        # To verify the non-AVX kext is used, check IOService for 'com_apple_AppleFSCompression_NoAVXCompressionTypeZlib'
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.sandy_bridge.value:
            self.enable_kext("NoAVXFSCompressionTypeZlib.kext", self.constants.apfs_zlib_version, self.constants.apfs_zlib_path)
            self.enable_kext("NoAVXFSCompressionTypeZlib-AVXpel.kext", self.constants.apfs_zlib_v2_version, self.constants.apfs_zlib_v2_path)

        if not self.constants.custom_model and (self.constants.allow_oc_everywhere is True or self.model in model_array.MacPro):
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

        if not self.constants.custom_model and self.constants.allow_nvme_fixing is True:
            nvme_devices = [i for i in self.computer.storage if isinstance(i, device_probe.NVMeController)]
            for i, controller in enumerate(nvme_devices):
                print(f"- Found 3rd Party NVMe SSD ({i + 1}): {utilities.friendly_hex(controller.vendor_id)}:{utilities.friendly_hex(controller.device_id)}")
                self.config["#Revision"][f"Hardware-NVMe-{i}"] = f"{utilities.friendly_hex(controller.vendor_id)}:{utilities.friendly_hex(controller.device_id)}"

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

                if (controller.vendor_id != 0x144D and controller.device_id != 0xA804):
                    # Avoid injecting NVMeFix when a native Apple NVMe drive is present
                    # https://github.com/acidanthera/NVMeFix/blob/1.0.9/NVMeFix/NVMeFix.cpp#L220-L225
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
                try:
                    smbios_data.smbios_dictionary[self.model]["nForce Chipset"]
                    # Nvidia chipsets all have the same path to ARPT
                    arpt_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
                except KeyError:
                    if self.model in ("iMac7,1", "iMac8,1", "MacPro3,1", "MacBookPro4,1"):
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
        if not self.constants.custom_model:
            if self.computer.wifi:
                print(f"- Found Wireless Device {utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}")
                self.config["#Revision"]["Hardware-Wifi"] = f"{utilities.friendly_hex(self.computer.wifi.vendor_id)}:{utilities.friendly_hex(self.computer.wifi.device_id)}"
        else:
            print("- Unable to run Wireless hardware detection")

        if not self.constants.custom_model:
            if self.computer.wifi:
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
                        self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                        self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                        self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
                    elif self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
                        self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                        self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                        self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
                elif isinstance(self.computer.wifi, device_probe.Atheros) and self.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40:
                    self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                    self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                    self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
        else:
            if smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                print("- Enabling BCM943224 and BCM94331 Networking Support")
                wifi_fake_id(self)
            elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm4331:
                print("- Enabling BCM94328 Networking Support")
                self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortBrcm4331.kext")["Enabled"] = True
            elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirPortBrcm43224:
                print("- Enabling BCM94328 Networking Support")
                self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AppleAirPortBrcm43224.kext")["Enabled"] = True
            elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Atheros.Chipsets.AirPortAtheros40:
                print("- Enabling Atheros Networking Support")
                self.enable_kext("corecaptureElCap.kext", self.constants.corecaptureelcap_version, self.constants.corecaptureelcap_path)
                self.enable_kext("IO80211ElCap.kext", self.constants.io80211elcap_version, self.constants.io80211elcap_path)
                self.get_kext_by_bundle_path("IO80211ElCap.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True
            elif smbios_data.smbios_dictionary[self.model]["Wireless Model"] == device_probe.Broadcom.Chipsets.AirportBrcmNIC:
                self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
                # print(f"- Setting Wireless Card's Country Code: {self.computer.wifi.country_code}")
                # self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" brcmfx-country={self.computer.wifi.country_code}"
                if self.constants.enable_wake_on_wlan is True:
                    print("- Enabling Wake on WLAN support")
                    self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += f" -brcmfxwowl"

        # CPUFriend
        if self.model not in ["iMac7,1", "Xserve2,1", "Dortania1,1"] and self.constants.serial_settings != "None":
            pp_map_path = Path(self.constants.platform_plugin_plist_path) / Path(f"{self.model}/Info.plist")
            if not pp_map_path.exists():
                raise Exception(f"{pp_map_path} does not exist!!! Please file an issue stating file is missing for {self.model}.")
            Path(self.constants.pp_kext_folder).mkdir()
            Path(self.constants.pp_contents_folder).mkdir()
            shutil.copy(pp_map_path, self.constants.pp_contents_folder)
            self.get_kext_by_bundle_path("CPUFriendDataProvider.kext")["Enabled"] = True

        # HID patches
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.penryn.value:
            print("- Adding IOHIDFamily patch")
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.iokit.IOHIDFamily")["Enabled"] = True

        # Legacy iSight patches
        try:
            if smbios_data.smbios_dictionary[self.model]["Legacy iSight"] is True:
                self.enable_kext("LegacyUSBVideoSupport.kext", self.constants.apple_isight_version, self.constants.apple_isight_path)
        except KeyError:
            pass

        # SSDT patches
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.cpu_data.nehalem.value and not (self.model.startswith("MacPro") or self.model.startswith("Xserve")):
            # Applicable for consumer Nehalem
            print("- Adding SSDT-CPBG.aml")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-CPBG.aml")["Enabled"] = True
            shutil.copy(self.constants.pci_ssdt_path, self.constants.acpi_path)

        if cpu_data.cpu_data.sandy_bridge <= smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.ivy_bridge.value and self.model != "MacPro6,1":
            # Based on: https://egpu.io/forums/pc-setup/fix-dsdt-override-to-correct-error-12/
            # Applicable for Sandy and Ivy Bridge Macs
            print("- Enabling Windows 10 UEFI Audio support")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-PCI.aml")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "BUF0 to BUF1")["Enabled"] = True
            shutil.copy(self.constants.windows_ssdt_path, self.constants.acpi_path)

        # In macOS Ventura, Apple dropped AppleIntelCPUPowerManagement* kexts as they're unused on Haswell+
        # However re-injecting the AICPUPM kexts is not enough, as Ventura changed how 'intel_cpupm_matching' is set:
        #    https://github.com/apple-oss-distributions/xnu/blob/e7776783b89a353188416a9a346c6cdb4928faad/osfmk/i386/pal_routines.h#L153-L163
        #
        # Specifically Apple has this logic for power management:
        #  - 0: Kext Based Power Management
        #  - 3: Kernel Based Power Management (For Haswell+ and Virtual Machines)
        #  - 4: Generic Virtual Machine Power Management
        #
        # Apple determines which to use by verifying whether 'plugin-type' exists in ACPI (with a value of 1 for Haswell, 2 for VMs)
        # By default however, the plugin-type is not set, and thus the default value of '0' is used
        #    https://github.com/apple-oss-distributions/xnu/blob/e7776783b89a353188416a9a346c6cdb4928faad/osfmk/i386/pal_native.h#L62
        #
        # With Ventura, Apple no longer sets '0' as the default value, and instead sets it to '3'
        # This breaks AppleIntelCPUPowerManagement.kext matching as it no longer matches against the correct criteria
        #
        # To resolve, we patched AICPUPM to attach regardless of the value of 'intel_cpupm_matching'
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.ivy_bridge.value:
            print("- Enabling legacy power management support")
            self.enable_kext("AppleIntelCPUPowerManagement.kext", self.constants.aicpupm_version, self.constants.aicpupm_path)
            self.enable_kext("AppleIntelCPUPowerManagementClient.kext", self.constants.aicpupm_version, self.constants.aicpupm_client_path)

        # With macOS Monterey, Apple's SDXC driver requires the system to support VT-D
        # However pre-Ivy Bridge don't support this feature
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge.value:
            if (self.constants.computer.sdxc_controller and not self.constants.custom_model) or (self.model.startswith("MacBookPro8") or self.model.startswith("Macmini5")):
                self.enable_kext("BigSurSDXC.kext", self.constants.bigsursdxc_version, self.constants.bigsursdxc_path)

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
            self.get_kext_by_bundle_path("USB-Map.kext")["Enabled"] = True
            if self.model in model_array.Missing_USB_Map_Ventura and self.constants.serial_settings not in ["Moderate", "Advanced"]:
                self.get_kext_by_bundle_path("USB-Map.kext")["MinKernel"] = "22.0.0"

        if self.constants.allow_oc_everywhere is False:
            if self.constants.serial_settings != "None":
                if self.model == "MacBookPro9,1":
                    print("- Adding AppleMuxControl Override")
                    amc_map_path = Path(self.constants.plist_folder_path) / Path("AppleMuxControl/Info.plist")
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"agdpmod": "vit9696"}
                    Path(self.constants.amc_kext_folder).mkdir()
                    Path(self.constants.amc_contents_folder).mkdir()
                    shutil.copy(amc_map_path, self.constants.amc_contents_folder)
                    self.get_kext_by_bundle_path("AMC-Override.kext")["Enabled"] = True

                if self.model not in model_array.NoAGPMSupport:
                    print("- Adding AppleGraphicsPowerManagement Override")
                    agpm_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsPowerManagement/Info.plist")
                    Path(self.constants.agpm_kext_folder).mkdir()
                    Path(self.constants.agpm_contents_folder).mkdir()
                    shutil.copy(agpm_map_path, self.constants.agpm_contents_folder)
                    self.get_kext_by_bundle_path("AGPM-Override.kext")["Enabled"] = True

                if self.model in model_array.AGDPSupport:
                    print("- Adding AppleGraphicsDevicePolicy Override")
                    agdp_map_path = Path(self.constants.plist_folder_path) / Path("AppleGraphicsDevicePolicy/Info.plist")
                    Path(self.constants.agdp_kext_folder).mkdir()
                    Path(self.constants.agdp_contents_folder).mkdir()
                    shutil.copy(agdp_map_path, self.constants.agdp_contents_folder)
                    self.get_kext_by_bundle_path("AGDP-Override.kext")["Enabled"] = True

        if self.constants.serial_settings != "None":
            # AGPM Patch
            if self.model in model_array.DualGPUPatch:
                print("- Adding dual GPU patch")
                if not self.constants.custom_model and self.computer.dgpu and self.computer.dgpu.pci_path:
                    self.gfx0_path = self.computer.dgpu.pci_path
                    print(f"- Found GFX0 Device Path: {self.gfx0_path}")
                else:
                    if not self.constants.custom_model:
                        print("- Failed to find GFX0 Device path, falling back on known logic")
                    self.gfx0_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

                if self.model in model_array.IntelNvidiaDRM and self.constants.drm_support is True:
                    print("- Prioritizing DRM support over Intel QuickSync")
                    self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696", "shikigva": 256}
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                        "name": binascii.unhexlify("23646973706C6179"),
                        "IOName": "#display",
                        "class-code": binascii.unhexlify("FFFFFFFF"),
                    }
                elif self.constants.serial_settings != "None":
                    self.config["DeviceProperties"]["Add"][self.gfx0_path] = {"agdpmod": "vit9696"}
            if self.model.startswith("iMac14,"):
                if self.computer.igpu and not self.computer.dgpu:
                    # Ensure that agdpmod is applied to iMac14,x with iGPU only
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {"agdpmod": "vit9696"}

        # Audio Patch
        if self.constants.set_alc_usage is True:
            if smbios_data.smbios_dictionary[self.model]["Max OS Supported"] <= os_data.os_data.high_sierra:
                # Models dropped in Mojave also lost Audio support
                # Xserves and MacPro4,1 are exceptions
                # iMac7,1 and iMac8,1 require AppleHDA/IOAudioFamily downgrade
                if not (self.model.startswith("Xserve") or self.model in ["MacPro4,1", "iMac7,1", "iMac8,1"]):
                    try:
                        smbios_data.smbios_dictionary[self.model]["nForce Chipset"]
                        hdef_path = "PciRoot(0x0)/Pci(0x8,0x0)"
                    except KeyError:
                        hdef_path = "PciRoot(0x0)/Pci(0x1b,0x0)"
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
                    self.enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)
            elif (self.model.startswith("MacPro") and self.model != "MacPro6,1") or self.model.startswith("Xserve"):
                # Used to enable Audio support for non-standard dGPUs
                self.enable_kext("AppleALC.kext", self.constants.applealc_version, self.constants.applealc_path)


        if self.constants.firewire_boot is True and generate_smbios.check_firewire(self.model) is True:
            # Enable FireWire Boot Support
            # Applicable for both native FireWire and Thunderbolt to FireWire adapters
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
            if not self.get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                # Ensure WEG is enabled as we need if for Backlight patching
                self.enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
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
            print("- Adding AMD DRM patches")
            if not self.get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                # Ensure WEG is enabled as we need if for Backlight patching
                self.enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
            self.config["DeviceProperties"]["Add"][backlight_path] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
            if self.constants.custom_model and self.model == "iMac11,2":
                # iMac11,2 can have either PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0) or PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
                # Set both properties when we cannot run hardware detection
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"] = {"shikigva": 128, "unfairgva": 1, "agdpmod": "pikera", "rebuild-device-tree": 1, "enable-gva-support": 1}
            if self.model in ["iMac12,1", "iMac12,2"]:
                print("- Disabling unsupported iGPU")
                self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
                    "name": binascii.unhexlify("23646973706C6179"),
                    "IOName": "#display",
                    "class-code": binascii.unhexlify("FFFFFFFF"),
                }
            elif self.model == "iMac10,1":
                if self.get_kext_by_bundle_path("AAAMouSSE.kext")["Enabled"] is False:
                    self.enable_kext("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path)
            if self.computer and self.computer.dgpu:
                if self.computer.dgpu.arch == device_probe.AMD.Archs.Legacy_GCN_7000:
                    print("- Adding Legacy GCN Power Gate Patches")
                    self.config["DeviceProperties"]["Add"][backlight_path].update({
                        "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                        "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                        "CAIL,CAIL_DisableUVDPowerGating": 1,
                        "CAIL,CAIL_DisableVCEPowerGating": 1,
                    })
            if self.constants.imac_model == "Legacy GCN":
                print("- Adding Legacy GCN Power Gate Patches")
                self.config["DeviceProperties"]["Add"][backlight_path].update({
                    "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                    "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                    "CAIL,CAIL_DisableUVDPowerGating": 1,
                    "CAIL,CAIL_DisableVCEPowerGating": 1,
                })
                if self.model == "iMac11,2":
                    self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x3,0x0)/Pci(0x0,0x0)"].update({
                        "CAIL,CAIL_DisableDrmdmaPowerGating": 1,
                        "CAIL,CAIL_DisableGfxCGPowerGating": 1,
                        "CAIL,CAIL_DisableUVDPowerGating": 1,
                        "CAIL,CAIL_DisableVCEPowerGating": 1,
                    })

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
        elif not self.constants.custom_model and self.model in model_array.LegacyGPU and self.computer.dgpu:
            print(f"- Detected dGPU: {utilities.friendly_hex(self.computer.dgpu.vendor_id)}:{utilities.friendly_hex(self.computer.dgpu.device_id)}")
            if self.computer.dgpu.arch in [
                device_probe.AMD.Archs.Legacy_GCN_7000,
                device_probe.AMD.Archs.Legacy_GCN_8000,
                device_probe.AMD.Archs.Legacy_GCN_9000,
                device_probe.AMD.Archs.Polaris,
                device_probe.AMD.Archs.Vega,
                device_probe.AMD.Archs.Navi,
            ]:
                backlight_path_detection(self)
                amd_patch(self, self.gfx0_path)
            elif self.computer.dgpu.arch == device_probe.NVIDIA.Archs.Kepler:
                backlight_path_detection(self)
                nvidia_patch(self, self.gfx0_path)
        if self.model in model_array.MacPro:
            if not self.constants.custom_model:
                for i, device in enumerate(self.computer.gpus):
                    print(f"- Found dGPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                    self.config["#Revision"][f"Hardware-MacPro-dGPU-{i + 1}"] = f"{utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}"

                    if device.pci_path and device.acpi_path:
                        print(f"- Found dGPU ({i + 1}) at {device.pci_path}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"shikigva": 128, "unfairgva": 1, "rebuild-device-tree": 1, "agdpmod": "pikera", "enable-gva-support": 1}
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            self.config["DeviceProperties"]["Add"][device.pci_path] = {"rebuild-device-tree": 1, "agdpmod": "vit9696"}
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                    else:
                        print(f"- Failed to find Device path for dGPU {i + 1}")
                        if isinstance(device, device_probe.AMD):
                            print("- Adding Mac Pro, Xserve DRM patches")
                            if "shikigva=128 unfairgva=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 agdpmod=pikera radgva=1" + (
                                    " -wegtree" if "-wegtree" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] else ""
                                )
                        elif isinstance(device, device_probe.NVIDIA):
                            print("- Enabling Nvidia Output Patch")
                            if "-wegtree agdpmod=vit9696" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                print("- Falling back to boot-args")
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -wegtree agdpmod=vit9696"
                            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
                            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

                if not self.computer.gpus:
                    print("- No socketed dGPU found")

            else:
                print("- Adding Mac Pro, Xserve DRM patches")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " shikigva=128 unfairgva=1 -wegtree"

            if not self.get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is True:
                self.enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)

        if not self.constants.custom_model:
            for i, device in enumerate(self.computer.gpus):
                if isinstance(device, device_probe.NVIDIA):
                    if (
                        device.arch in [device_probe.NVIDIA.Archs.Fermi, device_probe.NVIDIA.Archs.Maxwell, device_probe.NVIDIA.Archs.Pascal] or
                        (self.constants.force_nv_web is True and device.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Kepler])
                    ):
                        print(f"- Enabling Web Driver Patches for GPU ({i + 1}): {utilities.friendly_hex(device.vendor_id)}:{utilities.friendly_hex(device.device_id)}")
                        if device.pci_path and device.acpi_path:
                            if device.pci_path in self.config["DeviceProperties"]["Add"]:
                                self.config["DeviceProperties"]["Add"][device.pci_path].update({"disable-metal": 1, "force-compat": 1})
                            else:
                                self.config["DeviceProperties"]["Add"][device.pci_path] = {"disable-metal": 1, "force-compat": 1}
                            if self.get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is False:
                                self.enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]
                        else:
                            if "ngfxgl=1 ngfxcompat=1" not in self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]:
                                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ngfxgl=1 ngfxcompat=1"
                            if self.get_kext_by_bundle_path("WhateverGreen.kext")["Enabled"] is False:
                                self.enable_kext("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path)
                            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].update({"nvda_drv": binascii.unhexlify("31")})
                            if "nvda_drv" not in self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]:
                                self.config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] += ["nvda_drv"]


        if self.constants.disable_tb is True and self.model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3", "MacBookPro11,4", "MacBookPro11,5"]:
            print("- Disabling 2013-2014 laptop Thunderbolt Controller")
            if self.model in ["MacBookPro11,3", "MacBookPro11,5"]:
                # 15" dGPU models: IOACPIPlane:/_SB/PCI0@0/PEG1@10001/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x1)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"
            else:
                # 13" and 15" iGPU 2013-2014 models: IOACPIPlane:/_SB/PCI0@0/P0P2@10000/UPSB@0/DSB0@0/NHI0@0
                tb_device_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)"

            self.config["DeviceProperties"]["Add"][tb_device_path] = {"class-code": binascii.unhexlify("FFFFFFFF"), "device-id": binascii.unhexlify("FFFF0000")}

        if self.constants.software_demux is True and self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
            print("- Enabling software demux")
            # Add ACPI patches
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-DGPU.aml")["Enabled"] = True
            self.get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "_INI to XINI")["Enabled"] = True
            shutil.copy(self.constants.demux_ssdt_path, self.constants.acpi_path)
            # Disable dGPU
            # IOACPIPlane:/_SB/PCI0@0/P0P2@10000/GFX0@0
            self.config["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = {"class-code": binascii.unhexlify("FFFFFFFF"), "device-id": binascii.unhexlify("FFFF0000"), "IOName": "Dortania Disabled Card", "name": "Dortania Disabled Card"}
            self.config["DeviceProperties"]["Delete"]["PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"] = ["class-code", "device-id", "IOName", "name"]
            # Add AMDGPUWakeHandler
            self.enable_kext("AMDGPUWakeHandler.kext", self.constants.gpu_wake_version, self.constants.gpu_wake_path)

        # Pre-Force Touch trackpad support for macOS Ventura
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.skylake.value:
            if self.model.startswith("MacBook"):
                # These units got force touch early, so ignore them
                if self.model not in ["MacBookPro11,4", "MacBookPro11,5", "MacBook8,1"]:
                    self.enable_kext("AppleUSBTopCase.kext", self.constants.topcase_version, self.constants.top_case_path)
                    self.get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCButtons.kext")["Enabled"] = True
                    self.get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext")["Enabled"] = True
                    self.get_kext_by_bundle_path("AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyEventDriver.kext")["Enabled"] = True
                    self.enable_kext("AppleUSBMultitouch.kext", self.constants.multitouch_version, self.constants.multitouch_path)

        # Bluetooth Detection
        if not self.constants.custom_model and self.computer.bluetooth_chipset:
            if self.computer.bluetooth_chipset in ["BRCM2070 Hub", "BRCM2046 Hub"]:
                print("- Fixing Legacy Bluetooth for macOS Monterey")
                self.enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
                self.enable_kext("Bluetooth-Spoof.kext", self.constants.btspoof_version, self.constants.btspoof_path)
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -btlfxallowanyaddr"
            elif self.computer.bluetooth_chipset == "BRCM20702 Hub":
                # BCM94331 can include either BCM2070 or BRCM20702 v1 Bluetooth chipsets
                # Note Monterey only natively supports BRCM20702 v2 (found with BCM94360)
                # Due to this, BlueToolFixup is required to resolve Firmware Uploading on legacy chipsets
                if self.computer.wifi:
                    if self.computer.wifi.chipset == device_probe.Broadcom.Chipsets.AirPortBrcm4360:
                        print("- Fixing Legacy Bluetooth for macOS Monterey")
                        self.enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
            elif self.computer.bluetooth_chipset == "3rd Party Bluetooth 4.0 Hub":
                print("- Detected 3rd Party Chipset")
                self.enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
                print("- Enabling Bluetooth FeatureFlags")
                self.config["Kernel"]["Quirks"]["ExtendBTFeatureFlags"] = True
        elif smbios_data.smbios_dictionary[self.model]["Bluetooth Model"] <= bluetooth_data.bluetooth_data.BRCM20702_v1.value:
            print("- Fixing Legacy Bluetooth for macOS Monterey")
            self.enable_kext("BlueToolFixup.kext", self.constants.bluetool_version, self.constants.bluetool_path)
            if smbios_data.smbios_dictionary[self.model]["Bluetooth Model"] <= bluetooth_data.bluetooth_data.BRCM2070.value:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -btlfxallowanyaddr"
                self.enable_kext("Bluetooth-Spoof.kext", self.constants.btspoof_version, self.constants.btspoof_path)

        if self.constants.nvme_boot is True:
            print("- Enabling NVMe boot support")
            shutil.copy(self.constants.nvme_driver_path, self.constants.drivers_path)
            self.get_efi_binary_by_path("NvmExpressDxe.efi", "UEFI", "Drivers")["Enabled"] = True

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.constants.resources_path, onerror=rmtree_handler)
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        self.get_efi_binary_by_path("OpenCanopy.efi", "UEFI", "Drivers")["Enabled"] = True
        self.get_efi_binary_by_path("OpenRuntime.efi", "UEFI", "Drivers")["Enabled"] = True
        self.get_efi_binary_by_path("OpenLinuxBoot.efi", "UEFI", "Drivers")["Enabled"] = True
        self.get_efi_binary_by_path("ResetNvramEntry.efi", "UEFI", "Drivers")["Enabled"] = True
        # Exfat check
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.cpu_data.sandy_bridge.value:
            # Sandy Bridge and newer Macs natively support ExFat
            print("- Adding ExFatDxeLegacy.efi")
            shutil.copy(self.constants.exfat_legacy_driver_path, self.constants.drivers_path)
            self.get_efi_binary_by_path("ExFatDxeLegacy.efi", "UEFI", "Drivers")["Enabled"] = True

        # Add UGA to GOP layer
        try:
            smbios_data.smbios_dictionary[self.model]["UGA Graphics"]
            print("- Adding UGA to GOP Patch")
            self.config["UEFI"]["Output"]["GopPassThrough"] = "Apple"
        except KeyError:
            pass

        # MacBookAir6,x ship with an AHCI over PCIe SSD model 'APPLE SSD TS0128F' and 'APPLE SSD TS0256F'
        # This controller is not supported properly in macOS Ventura, instead populating itself as 'Media' with no partitions
        # To work-around this, use Monterey's AppleAHCI driver to force
        if self.model in ["MacBookAir6,1", "MacBookAir6,2"]:
            print("- Enabling AHCI SSD patch")
            self.enable_kext("MonteAHCIPort.kext", self.constants.monterey_ahci_version, self.constants.monterey_ahci_path)

        # Force VMM as a temporary solution to getting the MacPro6,1 booting in Ventura
        # With macOS Ventura, Apple removed AppleIntelCPUPowerManagement.kext and assumed XCPM support across all Macs
        # This change resulted in broken OS booting as the machine had no power management support
        # Currently the AICPUPM fix is not fully functional, thus forcing VMM is a temporary solution
        # Waiting for XNU source to be released to fix this properly
        if self.model == "MacPro6,1":
            print("- Enabling VMM patch")
            self.config["Kernel"]["Emulate"]["Cpuid1Data"] = binascii.unhexlify("00000000000000000000008000000000")
            self.config["Kernel"]["Emulate"]["Cpuid1Mask"] = binascii.unhexlify("00000000000000000000008000000000")
            self.config["Kernel"]["Emulate"]["MinKernel"] =  "22.0.0"

        # Check if model has 5K display
        # Apple has 2 modes for display handling on 5K iMacs and iMac Pro
        # If at any point in the boot chain an "unsupported" entry is loaded, the firmware will tell the
        # Display Controller to enter a 4K compatible mode that only uses a single DisplayPort 1.2 stream internally.
        # This is to prevent situations where the system would boot into an enviroment that cannot handle the custom
        # dual DisplayPort 1.2 streams the 5k Display uses

        # To work around this issue, we trick the firmware into loading OpenCore through Apple's Hardware Diagnostic Tests
        # Specifically hiding as Product.efi under '/System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers/Product.efi'
        # The reason chainloading via ./Drivers/HardwareDrivers is possible is thanks to it being loaded via an encrypted file buffer
        # whereas other drivers like ./qa_logger.efi is invoked via Device Path.

        try:
            smbios_data.smbios_dictionary[self.model]["5K Display"]
            print("- Adding 5K Display Patch")
            # Set LauncherPath to '/boot.efi'
            # This is to ensure that only the Mac's firmware presents the boot option, but not OpenCore
            # https://github.com/acidanthera/OpenCorePkg/blob/0.7.6/Library/OcAppleBootPolicyLib/OcAppleBootPolicyLib.c#L50-L73
            self.config["Misc"]["Boot"]["LauncherPath"] = "\\boot.efi"
            # Setup diags.efi chainloading
            self.chainload_diags()
        except KeyError:
            pass

        # With macOS 13, Ventura, Apple removed the Skylake graphics stack. However due to the lack of inovation
        # with the Kaby lake and Coffee Lake iGPUs, we're able to spoof ourselves to natively support them

        # Currently the following iGPUs we need to be considerate of:
        # - HD530 (mobile):  0x191B0006


        # | GPU      | Model            | Device ID | Platform ID | New Device ID | New Platform ID |
        # | -------- | ---------------- | --------- | ----------- | ------------- | --------------- |
        # | HD 515   | MacBook9,1       | 0x191E    | 0x131E0003  |
        # | Iris 540 | MacBookPro13,1/2 | 0x1926    | 0x19160002  | 0x5926        | 0x59260002
        # | HD 530   | MacBookPro13,3   | 0x191B    | 0x191B0006  | 0x591B        | 0x591B0006      |
        # | HD 530   | iMac17,1         | 0x1912    | 0x19120001  | 0x5912        | 0x59120003      |




        if self.constants.xhci_boot is True:
            print("- Adding USB 3.0 Controller Patch")
            print("- Adding XhciDxe.efi and UsbBusDxe.efi")
            shutil.copy(self.constants.xhci_driver_path, self.constants.drivers_path)
            shutil.copy(self.constants.usb_bus_driver_path, self.constants.drivers_path)
            self.get_efi_binary_by_path("XhciDxe.efi", "UEFI", "Drivers")["Enabled"] = True
            self.get_efi_binary_by_path("UsbBusDxe.efi", "UEFI", "Drivers")["Enabled"] = True

        # # Add UHCI/OHCI drivers
        # if not self.constants.custom_model:
        #     if self.constants.computer.usb_controllers:
        #         for controller in self.constants.computer.usb_controllers:
        #             if isinstance(controller, device_probe.UHCIController) or isinstance(controller, device_probe.OHCIController):
        #                 print("- Adding UHCI/OHCI USB support")
        #                 shutil.copy(self.constants.apple_usb_11_injector_path, self.constants.kexts_path)
        #                 self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCI.kext")["Enabled"] = True
        #                 self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCIPCI.kext")["Enabled"] = True
        #                 self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCI.kext")["Enabled"] = True
        #                 self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCIPCI.kext")["Enabled"] = True
        #                 break
        # else:
        #     if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.sandy_bridge.value:
        #         print("- Adding UHCI/OHCI USB support")
        #         shutil.copy(self.constants.apple_usb_11_injector_path, self.constants.kexts_path)
        #         self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCI.kext")["Enabled"] = True
        #         self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBOHCIPCI.kext")["Enabled"] = True
        #         self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCI.kext")["Enabled"] = True
        #         self.get_kext_by_bundle_path("USB1.1-Injector.kext/Contents/PlugIns/AppleUSBUHCIPCI.kext")["Enabled"] = True

        # ThirdPartDrives Check
        if self.constants.allow_3rd_party_drives is True:
            for drive in ["SATA 2.5", "SATA 3.5", "mSATA"]:
                if drive in smbios_data.smbios_dictionary[self.model]["Stock Storage"]:
                    if not self.constants.custom_model:
                        if self.computer.third_party_sata_ssd is True:
                            print("- Adding SATA Hibernation Patch")
                            self.config["Kernel"]["Quirks"]["ThirdPartyDrives"] = True
                            break
                    else:
                        print("- Adding SATA Hibernation Patch")
                        self.config["Kernel"]["Quirks"]["ThirdPartyDrives"] = True
                        break

        # Apple RAID Card check
        if not self.constants.custom_model:
            if self.computer.storage:
                for storage_controller in self.computer.storage:
                    if storage_controller.vendor_id == 0x106b and storage_controller.device_id == 0x008A:
                        # AppleRAIDCard.kext only supports pci106b,8a
                        self.enable_kext("AppleRAIDCard.kext", self.constants.apple_raid_version, self.constants.apple_raid_path)
                        break
        elif self.model.startswith("Xserve"):
            # For Xserves, assume RAID is present
            # Namely due to Xserve2,1 being limited to 10.7, thus no hardware detection
            self.enable_kext("AppleRAIDCard.kext", self.constants.apple_raid_version, self.constants.apple_raid_path)

        # Force Output support PC VBIOS on Mac Pros
        if self.constants.force_output_support is True:
            print("- Forcing GOP Support")
            self.config["UEFI"]["Quirks"]["ForgeUefiSupport"] = True
            self.config["UEFI"]["Quirks"]["ReloadOptionRoms"] = True

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
        print("- Enable Beta Lilu support")
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -lilubetaall"
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
            self.get_efi_binary_by_path("OpenShell.efi", "Misc", "Tools")["Enabled"] = False
        if self.constants.sip_status is False or self.constants.custom_sip_value:
            # Work-around 12.3 bug where Electron apps no longer launch with SIP lowered
            # Unknown whether this is intended behavior or not, revisit with 12.4
            print("- Adding ipc_control_port_options=0 to boot-args")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ipc_control_port_options=0"
            # Adds AutoPkgInstaller for Automatic OpenCore-Patcher installation
            # Only install if running the GUI (AutoPkg-Assets.pkg requires the GUI)
            if self.constants.wxpython_variant is True:
                self.enable_kext("AutoPkgInstaller.kext", self.constants.autopkg_version, self.constants.autopkg_path)
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
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Force FileVault on Broken Seal")["Enabled"] = True
            # Lets us check in sys_patch.py if config supports FileVault
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_fv"

        if self.constants.disable_cs_lv is True:
            print("- Disabling Library Validation")
            # In Ventura, LV patch broke. For now, add AMFI arg
            # Before merging into mainline, this needs to be resolved
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable Library Validation Enforcement")["Enabled"] = True
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable _csr_check() in _vnode_check_signature")["Enabled"] = True
            if self.constants.disable_amfi is True:
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi=0x80"
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_amfi"
            # CSLVFixup simply patches out __RESTRICT and __restrict out of the Music.app Binary
            # Ref: https://pewpewthespells.com/blog/blocking_code_injection_on_ios_and_os_x.html
            self.enable_kext("CSLVFixup.kext", self.constants.cslvfixup_version, self.constants.cslvfixup_path)
        if self.constants.secure_status is False:
            print("- Disabling SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"
            if self.constants.force_vmm is True:
                print("- Forcing VMM patchset to support OTA updates")
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] = True
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Legacy")["Enabled"] = True
                self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (2) Ventura")["Enabled"] = True
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
        try:
            if self.constants.dGPU_switch is True:
                smbios_data.smbios_dictionary[self.model]["Switchable GPUs"]
                print("- Allowing GMUX switching in Windows")
                self.config["Booter"]["Quirks"]["SignalAppleOS"] = True
        except KeyError:
            pass
        if (
            self.model.startswith("MacBook")
            and (
                smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.cpu_data.haswell.value or
                smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.cpu_data.broadwell.value
            )
        ):
            # Fix Virtual Machine support for non-macOS OSes
            # Haswell and Broadwell MacBooks lock out the VMX bit if booting UEFI Windows
            print("- Enabling VMX Bit for non-macOS OSes")
            self.config["UEFI"]["Quirks"]["EnableVmx"] = True
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.ivy_bridge.value:
            print("- Enabling Rosetta Cryptex support in Ventura")
            self.enable_kext("CryptexFixup.kext", self.constants.cryptexfixup_version, self.constants.cryptexfixup_path)
        if self.constants.disable_msr_power_ctl is True:
            print("- Disabling Firmware Throttling")
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.cpu_data.nehalem.value:
                # Nehalem and newer systems force firmware throttling via MSR_POWER_CTL
                self.enable_kext("SimpleMSR.kext", self.constants.simplemsr_version, self.constants.simplemsr_path)
        if self.constants.disable_connectdrivers is True:
            print("- Disabling ConnectDrivers")
            self.config["UEFI"]["ConnectDrivers"] = False
        if self.constants.nvram_write is False:
            print("- Disabling Hardware NVRAM Write")
            self.config["NVRAM"]["WriteFlash"] = False
        if self.get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Reroute kern.hv_vmm_present patch (1)")["Enabled"] is True and self.constants.set_content_caching is True:
            # Add Content Caching patch
            print("- Fixing Content Caching support")
            if self.get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
                self.enable_kext("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path)
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -revasset"
        if self.get_kext_by_bundle_path("RestrictEvents.kext")["Enabled"] is False:
            # Ensure this is done at the end so all previous RestrictEvents patches are applied
            # RestrictEvents and EFICheckDisabler will conflict if both are injected
            self.enable_kext("EFICheckDisabler.kext", self.constants.restrictevents_version, self.constants.efi_disabler_path)
        if self.constants.set_vmm_cpuid is True:
            # Should be unneeded with our sysctl VMM patch, however for reference purposes we'll leave it here
            # Ref: https://forums.macrumors.com/threads/opencore-on-the-mac-pro.2207814/
            self.config["Kernel"]["Emulate"]["Cpuid1Data"] = binascii.unhexlify("00000000000000000000008000000000")
            self.config["Kernel"]["Emulate"]["Cpuid1Mask"] = binascii.unhexlify("00000000000000000000008000000000")

    def set_smbios(self):
        spoofed_model = self.model
        if self.constants.override_smbios == "Default":
            if self.constants.serial_settings != "None":
                print("- Setting macOS Monterey Supported SMBIOS")
                if self.constants.allow_native_spoofs is True:
                    spoofed_model = self.model
                else:
                    spoofed_model = generate_smbios.set_smbios_model_spoof(self.model)
        else:
            spoofed_model = self.constants.override_smbios
        print(f"- Using Model ID: {spoofed_model}")
        try:
            spoofed_board = smbios_data.smbios_dictionary[spoofed_model]["Board ID"]
            print(f"- Using Board ID: {spoofed_board}")
        except KeyError:
            spoofed_board = ""
        self.spoofed_model = spoofed_model
        self.spoofed_board = spoofed_board
        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True:
            self.config["#Revision"]["Spoofed-Model"] = f"{self.spoofed_model} - {self.constants.serial_settings}"

        # Setup menu
        def minimal_serial_patch(self):
            # Generate Firmware Features
            fw_feature = generate_smbios.generate_fw_features(self.model, self.constants.custom_model)
            # fw_feature = self.patch_firmware_feature()
            fw_feature = hex(fw_feature).lstrip("0x").rstrip("L").strip()
            print(f"- Setting Firmware Feature: {fw_feature}")
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

            # ProcessorType (when RestrictEvent's CPU naming is used)
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["SMBIOS"]["ProcessorType"] = 1537

            # Avoid incorrect Firmware Updates
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["run-efi-updater"] = "No"
            self.config["PlatformInfo"]["SMBIOS"]["BIOSVersion"] = "9999.999.999.999.999"

            # Update tables
            self.config["PlatformInfo"]["UpdateNVRAM"] = True
            self.config["PlatformInfo"]["UpdateSMBIOS"] = True
            self.config["PlatformInfo"]["UpdateDataHub"] = True

            if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
                print("- Adding custom serial numbers")
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



        def moderate_serial_patch(self):
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537
            if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
                print("- Adding custom serial numbers")
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

        def advanced_serial_patch(self):
            if self.constants.custom_cpu_model == 0 or self.constants.custom_cpu_model == 1:
                self.config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537
            if self.constants.custom_serial_number == "" or self.constants.custom_board_serial_number == "":
                macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {self.spoofed_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        else:
            # Update DataHub to resolve Lilu Race Condition
            # macOS Monterey will sometimes not present the boardIdentifier in the DeviceTree on UEFI 1.2 or older Mac,
            # Thus resulting in an infinite loop as Lilu tries to request the Board ID
            # To resolve this, set PlatformInfo -> DataHub -> BoardProduct and enable UpdateDataHub

            # Note 1: Only apply if system is UEFI 1.2, this is generally Ivy Bridge and older, excluding MacPro6,1
            # Note 2: Flipping 'UEFI -> ProtocolOverrides -> DataHub' will break hibernation
            if (smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.cpu_data.ivy_bridge.value and self.model != "MacPro6,1"):
                print("- Detected UEFI 1.2 or older Mac, updating BoardProduct")
                self.config["PlatformInfo"]["DataHub"]["BoardProduct"] = self.spoofed_board
                self.config["PlatformInfo"]["UpdateDataHub"] = True

            if self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != "":
                print("- Adding custom serial numbers")
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
                    print("- Patching G State for MacBookPro6,2")
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

    def get_efi_binary_by_path(self, bundle_path, entry_location, efi_type):
        efi_binary = self.get_item_by_kv(self.config[entry_location][efi_type], "Path", bundle_path)
        if not efi_binary:
            print(f"- Could not find {efi_type}: {bundle_path}!")
            raise IndexError
        return efi_binary

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
        entries_to_clean = {
            "ACPI":   ["Add", "Delete", "Patch"],
            "Booter": ["Patch"],
            "Kernel": ["Add", "Block", "Force", "Patch"],
            "Misc":   ["Tools"],
            "UEFI":   ["Drivers"],
        }

        for entry in entries_to_clean:
            for sub_entry in entries_to_clean[entry]:
                for item in list(self.config[entry][sub_entry]):
                    if item["Enabled"] is False:
                        self.config[entry][sub_entry].remove(item)

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

        # Remove unused plugins inside of kexts
        # Following plugins are sometimes unused as there's different variants machines need
        known_unused_plugins = [
            "AirPortBrcm4331.kext",
            "AirPortAtheros40.kext",
            "AppleAirPortBrcm43224.kext",
            "AirPortBrcm4360_Injector.kext",
            "AirPortBrcmNIC_Injector.kext"
        ]
        for kext in Path(self.constants.opencore_release_folder / Path("EFI/OC/Kexts")).glob("*.kext"):
            for plugin in Path(kext / "Contents/PlugIns/").glob("*.kext"):
                should_remove = True
                for enabled_kexts in self.config["Kernel"]["Add"]:
                    if enabled_kexts["BundlePath"].endswith(plugin.name):
                        should_remove = False
                        break
                if should_remove:
                    if plugin.name not in known_unused_plugins:
                        raise Exception(f" - Unknown plugin found: {plugin.name}")
                    shutil.rmtree(plugin)

        Path(self.constants.opencore_zip_copied).unlink()

    def sign_files(self):
        if self.constants.vault is True:
            if utilities.check_command_line_tools() is True:
                # sign.command checks for the existence of '/usr/bin/strings' however does not verify whether it's executable
                # sign.command will continue to run and create an unbootable OpenCore.efi due to the missing strings binary
                # macOS has dummy binaries that just reroute to the actual binaries after you install Xcode's Command Line Tools
                print("- Vaulting EFI")
                subprocess.run([str(self.constants.vault_path), f"{self.constants.oc_folder}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                print("- Missing Command Line tools, skipping Vault for saftey reasons")
                print("- Install via 'xcode-select --install' and rerun OCLP if you wish to vault this config")

    def validate_pathing(self):
        print("- Validating generated config")
        if not Path(self.constants.opencore_release_folder / Path("EFI/OC/config.plist")):
            print("- OpenCore config file missing!!!")
            raise Exception("OpenCore config file missing")

        config_plist = plistlib.load(Path(self.constants.opencore_release_folder / Path("EFI/OC/config.plist")).open("rb"))

        for acpi in config_plist["ACPI"]["Add"]:
            # print(f"    - Validating {acpi['Path']}")
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/ACPI") / Path(acpi["Path"])).exists():
                print(f"  - Missing ACPI Table: {acpi['Path']}")
                raise Exception(f"Missing ACPI Table: {acpi['Path']}")

        for kext in config_plist["Kernel"]["Add"]:
            # print(f"    - Validating {kext['BundlePath']}")
            kext_path = Path(self.constants.opencore_release_folder / Path("EFI/OC/Kexts") / Path(kext["BundlePath"]))
            kext_binary_path = Path(kext_path / Path(kext["ExecutablePath"]))
            kext_plist_path = Path(kext_path / Path(kext["PlistPath"]))
            if not kext_path.exists():
                print(f"- Missing kext: {kext_path}")
                raise Exception(f"Missing {kext_path}")
            if not kext_binary_path.exists():
                print(f"- Missing {kext['BundlePath']}'s binary: {kext_binary_path}")
                raise Exception(f"Missing {kext_binary_path}")
            if not kext_plist_path.exists():
                print(f"- Missing {kext['BundlePath']}'s plist: {kext_plist_path}")
                raise Exception(f"Missing {kext_plist_path}")

        for tool in config_plist["Misc"]["Tools"]:
            # print(f"    - Validating {tool['Path']}")
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/Tools") / Path(tool["Path"])).exists():
                print(f"  - Missing tool: {tool['Path']}")
                raise Exception(f"Missing tool: {tool['Path']}")

        for driver in config_plist["UEFI"]["Drivers"]:
            # print(f"    - Validating {driver['Path']}")
            if not Path(self.constants.opencore_release_folder / Path("EFI/OC/Drivers") / Path(driver["Path"])).exists():
                print(f"  - Missing driver: {driver['Path']}")
                raise Exception(f"Missing driver: {driver['Path']}")

        # Validating local files
        # Validate Tools
        for tool_files in Path(self.constants.opencore_release_folder / Path("EFI/OC/Tools")).glob("*"):
            if tool_files.name not in [x["Path"] for x in config_plist["Misc"]["Tools"]]:
                print(f"  - Missing tool from config: {tool_files.name}")
                raise Exception(f"Missing tool from config: {tool_files.name}")

        for driver_file in Path(self.constants.opencore_release_folder / Path("EFI/OC/Drivers")).glob("*"):
            if driver_file.name not in [x["Path"] for x in config_plist["UEFI"]["Drivers"]]:
                print(f"- Found extra driver: {driver_file.name}")
                raise Exception(f"Found extra driver: {driver_file.name}")

    def build_opencore(self):
        self.build_efi()
        if self.constants.allow_oc_everywhere is False or self.constants.allow_native_spoofs is True or (self.constants.custom_serial_number != "" and self.constants.custom_board_serial_number != ""):
            self.set_smbios()
        self.cleanup()
        self.sign_files()
        self.validate_pathing()
        print("")
        print(f"Your OpenCore EFI for {self.model} has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to continue\n")
