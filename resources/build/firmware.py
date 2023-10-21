# Class for handling CPU and Firmware Patches, invocation from build.py
# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

import shutil
import logging
import binascii

from pathlib import Path

from resources import constants, generate_smbios, device_probe
from resources.build import support
from data import smbios_data, cpu_data


class BuildFirmware:
    """
    Build Library for CPU and Firmware Support

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
        Kick off CPU and Firmware Build Process
        """

        self._cpu_compatibility_handling()
        self._power_management_handling()
        self._acpi_handling()
        self._firmware_driver_handling()
        self._firmware_compatibility_handling()


    def _power_management_handling(self) -> None:
        """
        Power Management Handling
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "CPU Generation" in smbios_data.smbios_dictionary[self.model]:
            return

        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value:
            # In macOS Ventura, Apple dropped AppleIntelCPUPowerManagement* kexts as they're unused on Haswell+
            # However re-injecting the AICPUPM kexts is not enough, as Ventura changed how 'intel_cpupm_matching' is set:
            #    macOS 12.5: https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.140.41/osfmk/i386/pal_routines.h#L153-L163
            #    macOS 13.0: https://github.com/apple-oss-distributions/xnu/blob/xnu-8792.41.9/osfmk/i386/pal_routines.h#L153-L164
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
            logging.info("- Enabling legacy power management support")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleIntelCPUPowerManagement.kext", self.constants.aicpupm_version, self.constants.aicpupm_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleIntelCPUPowerManagementClient.kext", self.constants.aicpupm_version, self.constants.aicpupm_client_path)

        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.sandy_bridge.value or self.constants.disable_fw_throttle is True:
            # With macOS 12.3 Beta 1, Apple dropped the 'plugin-type' check within X86PlatformPlugin
            # Because of this, X86PP will match onto the CPU instead of ACPI_SMC_PlatformPlugin
            # This causes power management to break on pre-Ivy Bridge CPUs as they don't have correct
            # power management tables provided.
            # This patch will simply increase ASPP's 'IOProbeScore' to outmatch X86PP
            logging.info("- Overriding ACPI SMC matching")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("ASPP-Override.kext", self.constants.aspp_override_version, self.constants.aspp_override_path)
            if self.constants.disable_fw_throttle is True:
                # Only inject on older OSes if user requests
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", "ASPP-Override.kext")["MinKernel"] = ""

        if self.constants.disable_fw_throttle is True and smbios_data.smbios_dictionary[self.model]["CPU Generation"] >= cpu_data.CPUGen.nehalem.value:
            logging.info("- Disabling Firmware Throttling")
            # Nehalem and newer systems force firmware throttling via MSR_POWER_CTL
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("SimpleMSR.kext", self.constants.simplemsr_version, self.constants.simplemsr_path)


    def _acpi_handling(self) -> None:
        """
        ACPI Table Handling
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "CPU Generation" in smbios_data.smbios_dictionary[self.model]:
            return

        # Resolves Big Sur support for consumer Nehalem
        # CPBG device in ACPI is a Co-Processor Bridge Device, which is not actually physically present
        # IOPCIFamily will error when enumerating this device, thus we'll power it off via _STA (has no effect in older OSes)
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.CPUGen.nehalem.value and not (self.model.startswith("MacPro") or self.model.startswith("Xserve")):
            logging.info("- Adding SSDT-CPBG.aml")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-CPBG.aml")["Enabled"] = True
            shutil.copy(self.constants.pci_ssdt_path, self.constants.acpi_path)

        if cpu_data.CPUGen.sandy_bridge <= smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value and self.model != "MacPro6,1":
            # Based on: https://egpu.io/forums/pc-setup/fix-dsdt-override-to-correct-error-12/
            # Applicable for Sandy and Ivy Bridge Macs
            logging.info("- Enabling Windows 10 UEFI Audio support")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-PCI.aml")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["ACPI"]["Patch"], "Comment", "BUF0 to BUF1")["Enabled"] = True
            shutil.copy(self.constants.windows_ssdt_path, self.constants.acpi_path)


    def _cpu_compatibility_handling(self) -> None:
        """
        CPU Compatibility Handling
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "CPU Generation" in smbios_data.smbios_dictionary[self.model]:
            return

        # SSE4,1 support (ie. Penryn)
        # Required for macOS Mojave and newer
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.penryn.value:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("telemetrap.kext", self.constants.telemetrap_version, self.constants.telemetrap_path)

        # Force Rosetta Cryptex installation in macOS Ventura
        # Restores support for CPUs lacking AVX2.0 support
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value:
            logging.info("- Enabling Rosetta Cryptex support in Ventura")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("CryptexFixup.kext", self.constants.cryptexfixup_version, self.constants.cryptexfixup_path)

        # i3 Ivy Bridge iMacs don't support RDRAND
        # However for prebuilt, assume they do
        if (not self.constants.custom_model and "RDRAND" not in self.computer.cpu.flags) or \
            (smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.sandy_bridge.value):
            # Ref: https://github.com/reenigneorcim/SurPlus
            # Enable for all systems missing RDRAND support
            logging.info("- Adding SurPlus Patch for Race Condition")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 1 of 2 - Patch read_erandom (inlined in _early_random)")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 2 of 2 - Patch register_and_init_prng")["Enabled"] = True
            if self.constants.force_surplus is True:
                # Syncretic forces SurPlus to only run on Beta 7 and older by default for saftey reasons
                # If users desires, allow forcing in newer OSes
                logging.info("- Allowing SurPlus on all newer OSes")
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 1 of 2 - Patch read_erandom (inlined in _early_random)")["MaxKernel"] = ""
                support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "SurPlus v1 - PART 2 of 2 - Patch register_and_init_prng")["MaxKernel"] = ""

        # In macOS 12.4 and 12.5 Beta 1, Apple added AVX1.0 usage in AppleFSCompressionTypeZlib
        # Pre-Sandy Bridge CPUs don't support AVX1.0, thus we'll downgrade the kext to 12.3.1's
        # Currently a (hopefully) temporary workaround for the issue, proper fix needs to be investigated
        # Ref:
        #    https://forums.macrumors.com/threads/macos-12-monterey-on-unsupported-macs-thread.2299557/post-31120235
        #    https://forums.macrumors.com/threads/monterand-probably-the-start-of-an-ongoing-saga.2320479/post-31123553

        # To verify the non-AVX kext is used, check IOService for 'com_apple_AppleFSCompression_NoAVXCompressionTypeZlib'
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.sandy_bridge.value:
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("NoAVXFSCompressionTypeZlib.kext", self.constants.apfs_zlib_version, self.constants.apfs_zlib_path)
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("NoAVXFSCompressionTypeZlib-AVXpel.kext", self.constants.apfs_zlib_v2_version, self.constants.apfs_zlib_v2_path)

        # HID patches
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.penryn.value:
            logging.info("- Adding IOHIDFamily patch")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.iokit.IOHIDFamily")["Enabled"] = True


    def _firmware_driver_handling(self) -> None:
        """
        Firmware Driver Handling (Drivers/*.efi)
        """

        if not self.model in smbios_data.smbios_dictionary:
            return
        if not "CPU Generation" in smbios_data.smbios_dictionary[self.model]:
            return

        # Exfat check
        if smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.sandy_bridge.value:
            # Sandy Bridge and newer Macs natively support ExFat
            logging.info("- Adding ExFatDxeLegacy.efi")
            shutil.copy(self.constants.exfat_legacy_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("ExFatDxeLegacy.efi", "UEFI", "Drivers")["Enabled"] = True

        # NVMe check
        if self.constants.nvme_boot is True:
            logging.info("- Enabling NVMe boot support")
            shutil.copy(self.constants.nvme_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("NvmExpressDxe.efi", "UEFI", "Drivers")["Enabled"] = True

        # USB check
        if self.constants.xhci_boot is True:
            logging.info("- Adding USB 3.0 Controller Patch")
            logging.info("- Adding XhciDxe.efi and UsbBusDxe.efi")
            shutil.copy(self.constants.xhci_driver_path, self.constants.drivers_path)
            shutil.copy(self.constants.usb_bus_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("XhciDxe.efi", "UEFI", "Drivers")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("UsbBusDxe.efi", "UEFI", "Drivers")["Enabled"] = True

        # PCIe Link Rate check
        if self.model == "MacPro3,1":
            logging.info("- Adding PCIe Link Rate Patch")
            shutil.copy(self.constants.link_rate_driver_path, self.constants.drivers_path)
            support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("FixPCIeLinkRate.efi", "UEFI", "Drivers")["Enabled"] = True

        # CSM check
        # For model support, check for GUID in firmware and as well as Bootcamp Assistant's Info.plist ('PreUEFIModels' key)
        # Ref: https://github.com/acidanthera/OpenCorePkg/blob/0.9.5/Platform/OpenLegacyBoot/OpenLegacyBoot.c#L19
        if Path(self.constants.drivers_path / Path("OpenLegacyBoot.efi")).exists():
            if smbios_data.smbios_dictionary[self.model]["CPU Generation"] <= cpu_data.CPUGen.ivy_bridge.value and self.model != "MacPro6,1":
                logging.info("- Enabling CSM support")
                support.BuildSupport(self.model, self.constants, self.config).get_efi_binary_by_path("OpenLegacyBoot.efi", "UEFI", "Drivers")["Enabled"] = True
            else:
                # Shipped alongside OpenCorePkg, so remove if unused
                (self.constants.drivers_path / Path("OpenLegacyBoot.efi")).unlink()

    def _firmware_compatibility_handling(self) -> None:
        """
        Firmware Compatibility Handling (Firmware and Kernel)
        """

        self._dual_dp_handling()

        # Patches IOPCIConfigurator.cpp's IOPCIIsHotplugPort to skip configRead16/32 calls
        # Credit to CaseySJ for original discovery:
        # - Patch: https://github.com/AMD-OSX/AMD_Vanilla/pull/196
        # - Source: https://github.com/apple-oss-distributions/IOPCIFamily/blob/IOPCIFamily-583.40.1/IOPCIConfigurator.cpp#L968-L1022
        #
        # Currently all pre-Sandy Bridge Macs lacking an iGPU benefit from this patch as well as MacPro6,1
        # Otherwise some graphics hardware will fail to wake, macOS will misreport hardware as ExpressCard-based,
        # prevents MacPro6,1 from both booting unaccelerated and breaks low power states.
        if (
            self.model in ["MacPro6,1", "MacBookPro4,1"] or
            (
                smbios_data.smbios_dictionary[self.model]["CPU Generation"] < cpu_data.CPUGen.sandy_bridge.value and \
                not self.model.startswith("MacBook")
            )
        ):
            logging.info("- Adding PCI Bus Enumeration Patch")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "CaseySJ - Fix PCI bus enumeration (Ventura)")["Enabled"] = True
            # Sonoma slightly adjusted this line specifically
            # - https://github.com/apple-oss-distributions/IOPCIFamily/blob/IOPCIFamily-583.40.1/IOPCIConfigurator.cpp#L1009
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Fix PCI bus enumeration (Sonoma)")["Enabled"] = True

        if self.constants.set_vmm_cpuid is True:
            logging.info("- Enabling VMM patch")
            self.config["Kernel"]["Emulate"]["Cpuid1Data"] = binascii.unhexlify("00000000000000000000008000000000")
            self.config["Kernel"]["Emulate"]["Cpuid1Mask"] = binascii.unhexlify("00000000000000000000008000000000")

        if (
            self.model.startswith("MacBook")
            and (
                smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.CPUGen.haswell.value or
                smbios_data.smbios_dictionary[self.model]["CPU Generation"] == cpu_data.CPUGen.broadwell.value
            )
        ):
            # Fix Virtual Machine support for non-macOS OSes
            # Haswell and Broadwell MacBooks lock out the VMX bit if booting UEFI Windows
            logging.info("- Enabling VMX Bit for non-macOS OSes")
            self.config["UEFI"]["Quirks"]["EnableVmx"] = True

        # Works-around Hibernation bug where connecting all firmware drivers breaks the transition from S4
        # Mainly applicable for MacBookPro9,1
        if self.constants.disable_connectdrivers is True:
            logging.info("- Disabling ConnectDrivers")
            self.config["UEFI"]["ConnectDrivers"] = False

        if self.constants.nvram_write is False:
            logging.info("- Disabling Hardware NVRAM Write")
            self.config["NVRAM"]["WriteFlash"] = False

        if self.constants.serial_settings != "None":
            # AppleMCEReporter is very picky about which models attach to the kext
            # Commonly it will kernel panic on multi-socket systems, however even on single-socket systems it may cause instability
            # To avoid any issues, we'll disable it if the spoof is set to an affected SMBIOS
            affected_smbios = ["MacPro6,1", "MacPro7,1", "iMacPro1,1"]
            if self.model not in affected_smbios:
                # If MacPro6,1 host spoofs, we can safely enable it
                if self.constants.override_smbios in affected_smbios or generate_smbios.set_smbios_model_spoof(self.model) in affected_smbios:
                    support.BuildSupport(self.model, self.constants, self.config).enable_kext("AppleMCEReporterDisabler.kext", self.constants.mce_version, self.constants.mce_path)


    def _dual_dp_handling(self) -> None:
        """
        Dual DisplayPort Stream Handler (ex. 5k iMac)

        Apple has 2 modes for display handling on 5K iMacs and iMac Pro
        If at any point in the boot chain an "unsupported" entry is loaded, the firmware will tell the
        Display Controller to enter a 4K compatible mode that only uses a single DisplayPort 1.2 stream internally.
        This is to prevent situations where the system would boot into an enviroment that cannot handle the custom
        dual DisplayPort 1.2 streams the 5k Display uses

        To work around this issue, we trick the firmware into loading OpenCore through Apple's Hardware Diagnostic Tests
        Specifically hiding as Product.efi under '/System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers/Product.efi'
        The reason chainloading via ./Drivers/HardwareDrivers is possible is thanks to it being loaded via an encrypted file buffer
        whereas other drivers like ./qa_logger.efi is invoked via Device Path.
        """

        if "5K Display" not in smbios_data.smbios_dictionary[self.model]:
            return

        logging.info("- Adding 5K Display Patch")
        # Set LauncherPath to '/boot.efi'
        # This is to ensure that only the Mac's firmware presents the boot option, but not OpenCore
        # https://github.com/acidanthera/OpenCorePkg/blob/0.7.6/Library/OcAppleBootPolicyLib/OcAppleBootPolicyLib.c#L50-L73
        self.config["Misc"]["Boot"]["LauncherPath"] = "\\boot.efi"

        # Setup diags.efi chainloading
        Path(self.constants.opencore_release_folder / Path("System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers")).mkdir(parents=True, exist_ok=True)
        if self.constants.boot_efi is True:
            path_oc_loader = self.constants.opencore_release_folder / Path("EFI/BOOT/BOOTx64.efi")
        else:
            path_oc_loader = self.constants.opencore_release_folder / Path("System/Library/CoreServices/boot.efi")
        shutil.move(path_oc_loader, self.constants.opencore_release_folder / Path("System/Library/CoreServices/.diagnostics/Drivers/HardwareDrivers/Product.efi"))
        shutil.copy(self.constants.diags_launcher_path, self.constants.opencore_release_folder)
        shutil.move(self.constants.opencore_release_folder / Path("diags.efi"), self.constants.opencore_release_folder / Path("boot.efi"))