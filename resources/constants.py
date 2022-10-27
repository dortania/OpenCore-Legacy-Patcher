# pylint: disable=multiple-statements
# Define Files
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

from pathlib import Path
from typing import Optional

from resources import device_probe
from data import os_data


class Constants:
    def __init__(self):
        # Patcher Versioning
        self.patcher_version = "0.5.2"  # OpenCore-Legacy-Patcher
        self.patcher_support_pkg_version = "0.7.1"  #  PatcherSupportPkg
        self.url_patcher_support_pkg = "https://github.com/dortania/PatcherSupportPkg/releases/download/"
        self.nightly_url_patcher_support_pkg = "https://nightly.link/dortania/PatcherSupportPkg/workflows/build/master/"
        self.discord_link = "https://discord.gg/rqdPgH8xSN"
        self.guide_link = "https://dortania.github.io/OpenCore-Legacy-Patcher/"
        self.repo_link = "https://github.com/dortania/OpenCore-Legacy-Patcher"
        self.repo_link_latest = f"{self.repo_link}/releases/tag/{self.patcher_version}"
        self.copyright_date = "Copyright © 2020-2022 Dortania"
        self.installer_pkg_url = f"{self.repo_link}/releases/download/{self.patcher_version}/AutoPkg-Assets.pkg"
        self.installer_pkg_url_nightly = "http://nightly.link/dortania/OpenCore-Legacy-Patcher/workflows/build-app-wxpython/main/AutoPkg-Assets.pkg.zip"

        # OpenCore Versioning
        # https://github.com/acidanthera/OpenCorePkg
        self.opencore_commit = "c14b2ab - 10-04-2022"
        self.opencore_version = "0.8.5"

        # Kext Versioning
        ## Acidanthera
        ## https://github.com/acidanthera
        self.lilu_version = "1.6.2"  #               Lilu
        self.whatevergreen_version = "1.5.8"  #      WhateverGreen
        self.airportbcrmfixup_version = "2.1.3"  #   AirPortBrcmFixup
        self.nvmefix_version = "1.0.9"  #            NVMeFix
        self.applealc_version = "1.6.3"  #           AppleALC
        self.restrictevents_version = "1.0.6"  #     RestrictEvents
        self.restrictevents_mbp_version = "1.0.6"  # RestrictEvents blocking displaypolicyd (see RestrictEvents-MBP91.patch)
        self.featureunlock_version = "1.0.9"  #      FeatureUnlock
        self.debugenhancer_version = "1.0.4"  #      DebugEnhancer
        self.cpufriend_version = "1.2.5"  #          CPUFriend
        self.bluetool_version = "2.6.4"  #           BlueToolFixup (BrcmPatchRAM)
        self.cslvfixup_version = "2.6.1"  #          CSLVFixup
        self.autopkg_version = "1.0.1"  #            AutoPkgInstaller
        self.cryptexfixup_version = "1.0.1"  #       CryptexFixup

        ## Apple
        ## https://www.apple.com
        self.marvel_version = "1.0.1"  #       MarvelYukonEthernet
        self.nforce_version = "1.0.1"  #       nForceEthernet
        self.piixata_version = "1.0.1"  #      AppleIntelPIIXATA
        self.fw_kext = "1.0.1"  #              IOFireWireFamily
        self.apple_trackpad = "1.0.1"  #       AppleUSBTrackpad
        self.apple_isight_version = "1.0.0"  # AppleiSight
        self.apple_raid_version = "1.0.0"  #   AppleRAIDCard
        self.apfs_zlib_version = "12.3.1"  #   NoAVXFSCompressionTypeZlib
        self.apfs_zlib_v2_version = "12.6"  #  NoAVXFSCompressionTypeZlib (patched with AVXpel)
        self.multitouch_version = "1.0.0"  #   AppleUSBMultitouch
        self.topcase_version = "1.0.0"  #      AppleUSBTopCase
        self.intel_82574l_version = "1.0.0" #  Intel82574L
        self.intel_8254x_version = "1.0.0" #   AppleIntel8254XEthernet
        self.apple_usb_11_injector = "1.0.0" # AppleUSBUHCI/OHCI
        self.aicpupm_version = "1.0.0" #       AppleIntelCPUPowerManagement/Client

        ## Apple - Dortania Modified
        self.bcm570_version = "1.0.2"  #             CatalinaBCM5701Ethernet
        self.i210_version = "1.0.0"  #               CatalinaIntelI210Ethernet
        self.corecaptureelcap_version = "1.0.1"  #   corecaptureElCap
        self.io80211elcap_version = "2.0.0"  #       IO80211ElCap
        self.bigsursdxc_version = "1.0.0"  #         BigSurSDXC
        self.monterey_ahci_version = "1.0.0"  #      CatalinaAHCI

        ## Dortania
        ## https://github.com/dortania
        self.backlight_injector_version = "1.1.0"  # BacklightInjector
        self.smcspoof_version = "1.0.0"  #           SMC-Spoof
        self.mce_version = "1.0.0"  #                AppleMCEReporterDisabler
        self.btspoof_version = "1.0.0"  #            Bluetooth-Spoof
        self.aspp_override_version = "1.0.1"  #      ACPI_SMC_PlatformPlugin Override

        ## Syncretic
        ## https://forums.macrumors.com/members/syncretic.1173816/
        ## https://github.com/reenigneorcim/latebloom
        self.mousse_version = "0.95-Dortania"  # MouSSE
        self.telemetrap_version = "1.0.0"  #     telemetrap

        ## cdf
        ## https://github.com/cdf/Innie
        self.innie_version = "1.3.0"  # Innie

        ## arter97
        ## https://github.com/arter97/SimpleMSR/
        self.simplemsr_version = "1.0.0"  # SimpleMSR

        ## blackgate
        ## https://github.com/blackgate/AMDGPUWakeHandler
        self.gpu_wake_version = "1.0.0"

        # Get resource path
        self.current_path = Path(__file__).parent.parent.resolve()
        self.payload_path = self.current_path / Path("payloads")

        # Patcher Settings
        self.allow_oc_everywhere = False  # Set whether Patcher can be run on unsupported Macs
        self.gui_mode = False  #            Determine whether running in a GUI or TUI
        self.disk = ""  #                   Set installation ESP
        self.patch_disk = ""  #             Set Root Volume to patch
        self.validate = False  #            Enable validation testing for CI
        self.recovery_status = False  #     Detect if booted into RecoveryOS
        self.launcher_binary = None #       Determine launch binary (ie. Python vs PyInstaller)
        self.launcher_script = None  #      Determine launch file (if run via Python)
        self.ignore_updates = False  #      Ignore OCLP updates
        self.wxpython_variant = False #     Determine if using wxPython variant
        self.unpack_thread = None  #        Determine if unpack thread finished
        self.cli_mode = False  #            Determine if running in CLI mode
        self.should_nuke_kdks = True  #       Determine if KDKs should be nuked if unused in /L*/D*/KDKs

        ## Hardware
        self.computer: device_probe.Computer = None  # type: ignore
        self.custom_model: Optional[str] = None

        ## OpenCore Settings
        self.opencore_debug = False
        self.opencore_build = "RELEASE"
        self.showpicker = True  #  Show or Hide OpenCore's Boot Picker
        self.boot_efi = False  #   Use EFI/BOOT/BOOTx64.efi bootstrap
        self.nvram_write = True  # Write to hardware NVRAM

        ## Kext Settings
        self.kext_debug = False  # Enables Lilu debug and DebugEnhancer
        self.kext_variant = "RELEASE"

        ## NVRAM Settings
        self.verbose_debug = False  # -v

        ## SMBIOS Settings
        self.custom_cpu_model = 2  #            Patch type value
        self.custom_cpu_model_value = ""  #     New CPU name within About This Mac
        self.serial_settings = "None"  #        Set SMBIOS level used
        self.override_smbios = "Default"  #     Set SMBIOS model used
        self.allow_native_spoofs = False  #     Allow native models to recieve spoofs
        self.custom_serial_number = ""  #       Set SMBIOS serial number
        self.custom_board_serial_number = ""  # Set SMBIOS board serial number

        ## FeatureUnlock Settings
        self.fu_status = True   #   Enable FeatureUnlock
        self.fu_arguments = None  # Set FeatureUnlock arguments

        ## Security Settings
        self.apecid_support = False  #    ApECID
        self.sip_status = True  #         System Integrity Protection
        self.secure_status = False  #     Secure Boot Model
        self.vault = False  #             EFI Vault
        self.disable_cs_lv = False  #     Disable Library validation
        self.disable_amfi = False  #      Disable AMFI

        ## OS Settings
        self.os_support = 12.0
        self.detected_os = 0  #          Major Kernel Version
        self.detected_os_minor = 0  #    Minor Kernel Version
        self.detected_os_build = ""  #   OS Build
        self.detected_os_version = ""  # OS Version

        ## Boot Volume Settings
        self.firewire_boot = False  # Allow macOS FireWire Boot
        self.nvme_boot = False  #     Allow UEFI NVMe Boot
        self.xhci_boot = False

        ## Graphics Settings
        self.metal_build = False  #          Set MXM Build support
        self.imac_vendor = "None"  #         Set MXM GPU vendor
        self.imac_model = "" #               Set MXM GPU model
        self.drm_support = False  #          Set iMac14,x DRM support
        self.allow_ts2_accel = True  #       Set TeraScale 2 Acceleration support
        self.force_nv_web = False  #         Force Nvidia Web Drivers on Tesla and Kepler
        self.force_output_support = False  # Force Output support for Mac Pros with PC VBIOS

        ## Miscellaneous
        self.disallow_cpufriend = False  #     Disable CPUFriend
        self.enable_wake_on_wlan = False  #    Allow Wake on WLAN for modern Broadcom
        self.disable_tb = False  #             Disable Thunderbolt Controller
        self.set_alc_usage = True  #           Set AppleALC usage
        self.dGPU_switch = False  #            Set Display GPU Switching for Windows
        self.force_surplus = False  #          Force SurPlus patch in newer OSes
        self.force_latest_psp = False  #       Force latest PatcherSupportPkg
        self.disable_msr_power_ctl = False  #  Disable MSR Power Control (missing battery throttling)
        self.software_demux = False  #         Enable Software Demux patch set
        self.force_vmm = False  #              Force VMM patch
        self.custom_sip_value = None  #        Set custom SIP value
        self.walkthrough = False  #            Enable Walkthrough
        self.disable_connectdrivers = False  # Disable ConnectDrivers (hibernation)
        self.allow_3rd_party_drives = True   # Allow ThridPartyDrives quirk
        self.set_content_caching = False  #    Set Content Caching
        self.allow_nvme_fixing = True  #       Allow NVMe Kernel Space Patches
        self.disable_xcpm = False  #           Disable XCPM (X86PlatformPlugin.kext)
        self.root_patcher_succeeded = False  #  Determine if root patcher succeeded
        self.booted_oc_disk = None  #          Determine current disk OCLP booted from
        self.start_build_install = False  #    Determine if build install should be started
        self.host_is_non_metal = False  #      Determine if host is non-metal (ie. enable UI hacks)
        self.needs_to_open_preferences = False  # Determine if preferences need to be opened
        self.host_is_hackintosh = False #     Determine if host is Hackintosh
        self.commit_info = (None, None, None)
        self.set_vmm_cpuid = False  #          Set VMM bit inside CPUID
        self.oc_timeout = 5  #                 Set OpenCore timeout

        self.legacy_accel_support = [
            os_data.os_data.big_sur,
            os_data.os_data.monterey,
        ]

    # Payload Location
    # OpenCore
    @property
    def opencore_zip_source(self):
        return self.payload_path / Path(f"OpenCore/OpenCore-{self.opencore_build}.zip")

    @property
    def plist_template(self):
        return self.payload_path / Path("Config/config.plist")

    # Launch Agent
    @property
    def auto_patch_launch_agent_path(self):
        return self.payload_path / Path("com.dortania.opencore-legacy-patcher.auto-patch.plist")

    # ACPI
    @property
    def pci_ssdt_path(self):
        return self.payload_path / Path("ACPI/SSDT-CPBG.aml")

    @property
    def windows_ssdt_path(self):
        return self.payload_path / Path("ACPI/SSDT-PCI.aml")

    @property
    def demux_ssdt_path(self):
        return self.payload_path / Path("ACPI/SSDT-DGPU.aml")

    # Drivers
    @property
    def nvme_driver_path(self):
        return self.payload_path / Path("Drivers/NvmExpressDxe.efi")

    @property
    def exfat_legacy_driver_path(self):
        return self.payload_path / Path("Drivers/ExFatDxeLegacy.efi")

    @property
    def xhci_driver_path(self):
        return self.payload_path / Path("Drivers/XhciDxe.efi")

    @property
    def usb_bus_driver_path(self):
        return self.payload_path / Path("Drivers/UsbBusDxe.efi")

    @property
    def diags_launcher_path(self):
        return self.payload_path / Path("Drivers/diags.efi")

    @property
    def list_txt_path(self):
        return self.payload_path / Path("List.txt")

    @property
    def installer_sh_path(self):
        return self.payload_path / Path("Installer.sh")

    # Kexts
    @property
    def payload_kexts_path(self):
        return self.payload_path / Path("Kexts")

    @property
    def lilu_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/Lilu-v{self.lilu_version}-{self.kext_variant}.zip")

    @property
    def whatevergreen_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/WhateverGreen-v{self.whatevergreen_version}-{self.kext_variant}.zip")

    @property
    def airportbcrmfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AirportBrcmFixup-v{self.airportbcrmfixup_version}-{self.kext_variant}.zip")

    @property
    def restrictevents_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-v{self.restrictevents_version}-{self.kext_variant}.zip")

    @property
    def efi_disabler_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/EFICheckDisabler-v{self.restrictevents_version}.zip")

    @property
    def restrictevents_mbp_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-MBP91-v{self.restrictevents_mbp_version}-{self.kext_variant}.zip")

    @property
    def bcm570_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/CatalinaBCM5701Ethernet-v{self.bcm570_version}.zip")

    @property
    def i210_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/CatalinaIntelI210Ethernet-v{self.i210_version}.zip")

    @property
    def marvel_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/MarvelYukonEthernet-v{self.marvel_version}.zip")

    @property
    def nforce_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/nForceEthernet-v{self.nforce_version}.zip")

    @property
    def intel_82574l_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/Intel82574L-v{self.intel_82574l_version}.zip")

    @property
    def intel_8254x_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/AppleIntel8254XEthernet-v{self.intel_8254x_version}.zip")

    @property
    def apple_usb_11_injector_path(self):
        return self.payload_kexts_path / Path(f"USB/USB1.1-Injector-v{self.apple_usb_11_injector}.zip")

    @property
    def aicpupm_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleIntelCPUPowerManagement-v{self.aicpupm_version}.zip")

    @property
    def aicpupm_client_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleIntelCPUPowerManagementClient-v{self.aicpupm_version}.zip")

    @property
    def mce_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleMCEReporterDisabler-v{self.mce_version}.zip")

    @property
    def bigsursdxc_path(self):
        return self.payload_kexts_path / Path(f"Misc/BigSurSDXC-v{self.bigsursdxc_version}.zip")

    @property
    def monterey_ahci_path(self):
        return self.payload_kexts_path / Path(f"Misc/MonteAHCIPort-v{self.monterey_ahci_version}.zip")

    @property
    def apfs_zlib_path(self):
        return self.payload_kexts_path / Path(f"Misc/NoAVXFSCompressionTypeZlib-v{self.apfs_zlib_version}.zip")

    @property
    def apfs_zlib_v2_path(self):
        return self.payload_kexts_path / Path(f"Misc/NoAVXFSCompressionTypeZlib-AVXpel-v{self.apfs_zlib_v2_version}.zip")

    @property
    def multitouch_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleUSBMultitouch-v{self.multitouch_version}.zip")

    @property
    def top_case_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleUSBTopCase-v{self.topcase_version}.zip")

    @property
    def mousse_path(self):
        return self.payload_kexts_path / Path(f"SSE/AAAMouSSE-v{self.mousse_version}.zip")

    @property
    def telemetrap_path(self):
        return self.payload_kexts_path / Path(f"SSE/telemetrap-v{self.telemetrap_version}.zip")

    @property
    def corecaptureelcap_path(self):
        return self.payload_kexts_path / Path(f"Wifi/corecaptureElCap-v{self.corecaptureelcap_version}.zip")

    @property
    def io80211elcap_path(self):
        return self.payload_kexts_path / Path(f"Wifi/IO80211ElCap-v{self.io80211elcap_version}.zip")

    @property
    def applealc_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AppleALC-v{self.applealc_version}-{self.kext_variant}.zip")

    @property
    def piixata_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleIntelPIIXATA-v{self.piixata_version}.zip")

    @property
    def backlight_injector_path(self):
        return self.payload_kexts_path / Path(f"Misc/BacklightInjector-v{self.backlight_injector_version}.zip")

    @property
    def cpufriend_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/CPUFriend-v{self.cpufriend_version}-{self.kext_variant}.zip")

    @property
    def smcspoof_path(self):
        return self.payload_kexts_path / Path(f"Misc/SMC-Spoof-v{self.smcspoof_version}.zip")

    @property
    def btspoof_path(self):
        return self.payload_kexts_path / Path(f"Misc/Bluetooth-Spoof-v{self.btspoof_version}.zip")

    @property
    def aspp_override_path(self):
        return self.payload_kexts_path / Path(f"Misc/ASPP-Override-v{self.aspp_override_version}.zip")

    @property
    def nvmefix_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/NVMeFix-v{self.nvmefix_version}-{self.kext_variant}.zip")

    @property
    def featureunlock_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/FeatureUnlock-v{self.featureunlock_version}-{self.kext_variant}.zip")

    @property
    def debugenhancer_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/DebugEnhancer-v{self.debugenhancer_version}-{self.kext_variant}.zip")

    @property
    def bluetool_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/BlueToolFixup-v{self.bluetool_version}-{self.kext_variant}.zip")

    @property
    def cslvfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/CSLVFixup-v{self.cslvfixup_version}.zip")

    @property
    def autopkg_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AutoPkgInstaller-v{self.autopkg_version}-{self.kext_variant}.zip")

    @property
    def cryptexfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/CryptexFixup-v{self.cryptexfixup_version}-{self.kext_variant}.zip")

    @property
    def innie_path(self):
        return self.payload_kexts_path / Path(f"Misc/Innie-v{self.innie_version}.zip")

    @property
    def simplemsr_path(self):
        return self.payload_kexts_path / Path(f"Misc/SimpleMSR-v{self.simplemsr_version}.zip")

    @property
    def gpu_wake_path(self):
        return self.payload_kexts_path / Path(f"Misc/AMDGPUWakeHandler-v{self.gpu_wake_version}.zip")

    @property
    def apple_trackpad_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleUSBTrackpad-v{self.apple_trackpad}.zip")

    @property
    def apple_isight_path(self):
        return self.payload_kexts_path / Path(f"Misc/LegacyUSBVideoSupport-v{self.apple_isight_version}.zip")

    @property
    def apple_raid_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleRAIDCard-v{self.apple_raid_version}.zip")

    @property
    def plist_folder_path(self):
        return self.payload_kexts_path / Path("Plists")

    @property
    def platform_plugin_plist_path(self):
        return self.plist_folder_path / Path("PlatformPlugin")

    @property
    def fw_family_path(self):
        return self.payload_kexts_path / Path(f"FireWire/IOFireWireFamily-v{self.fw_kext}.zip")

    @property
    def fw_sbp2_path(self):
        return self.payload_kexts_path / Path(f"FireWire/IOFireWireSBP2-v{self.fw_kext}.zip")

    @property
    def fw_bus_path(self):
        return self.payload_kexts_path / Path(f"FireWire/IOFireWireSerialBusProtocolTransport-v{self.fw_kext}.zip")

    # Build Location
    @property
    def build_path(self):
        return self.current_path / Path("Build-Folder/")

    @property
    def opencore_release_folder(self):
        return self.build_path / Path(f"OpenCore-Build")

    @property
    def opencore_zip_copied(self):
        return self.build_path / Path(f"OpenCore-{self.opencore_build}.zip")

    @property
    def oc_folder(self):
        return self.opencore_release_folder / Path("EFI/OC/")

    @property
    def plist_path(self):
        return self.oc_folder / Path("config.plist")

    @property
    def acpi_path(self):
        return self.oc_folder / Path("ACPI")

    @property
    def drivers_path(self):
        return self.oc_folder / Path("Drivers")

    @property
    def kexts_path(self):
        return self.oc_folder / Path("Kexts")

    @property
    def resources_path(self):
        return self.oc_folder / Path("Resources")

    @property
    def map_kext_folder(self):
        return self.kexts_path / Path("USB-Map.kext")

    @property
    def map_contents_folder(self):
        return self.map_kext_folder / Path("Contents")

    @property
    def pp_kext_folder(self):
        return self.kexts_path / Path("CPUFriendDataProvider.kext")

    @property
    def pp_contents_folder(self):
        return self.pp_kext_folder / Path("Contents")

    @property
    def agdp_kext_folder(self):
        return self.kexts_path / Path("AGDP-Override.kext")

    @property
    def agdp_contents_folder(self):
        return self.agdp_kext_folder / Path("Contents")

    @property
    def agpm_kext_folder(self):
        return self.kexts_path / Path("AGPM-Override.kext")

    @property
    def agpm_contents_folder(self):
        return self.agpm_kext_folder / Path("Contents")

    @property
    def amc_kext_folder(self):
        return self.kexts_path / Path("AMC-Override.kext")

    @property
    def amc_contents_folder(self):
        return self.amc_kext_folder / Path("Contents")

    # Tools
    @property
    def macserial_path(self):
        return self.payload_path / Path("Tools/macserial")

    @property
    def gfxutil_path(self):
        return self.payload_path / Path("Tools/gfxutil")

    @property
    def vault_path(self):
        return self.payload_path / Path("Tools/CreateVault/sign.command")

    @property
    def ocvalidate_path(self):
        return self.payload_path / Path(f"Tools/ocvalidate-{self.opencore_version}")

    @property
    def oclp_helper_path(self):
        return self.payload_path / Path("Tools/OCLP-Helper")

    # Icons
    @property
    def app_icon_path(self):
        return self.payload_path / Path("OC-Patcher.icns")

    @property
    def icon_path_external(self):
        return self.payload_path / Path("Icon/External/.VolumeIcon.icns")

    @property
    def icon_path_internal(self):
        return self.payload_path / Path("Icon/Internal/.VolumeIcon.icns")

    @property
    def icon_path_sd(self):
        return self.payload_path / Path("Icon/SD-Card/.VolumeIcon.icns")

    @property
    def icon_path_ssd(self):
        return self.payload_path / Path("Icon/SSD/.VolumeIcon.icns")

    @property
    def gui_path(self):
        return self.payload_path / Path("Icon/Resources.zip")

    @property
    def installer_pkg_path(self):
        return self.payload_path / Path("AutoPkg-Assets.pkg")

    @property
    def installer_pkg_zip_path(self):
        return self.payload_path / Path("AutoPkg-Assets.pkg.zip")

    # Apple Payloads Paths
    @property
    def payload_local_binaries_root_path(self):
        return self.payload_path / Path("Universal-Binaries")

    @property
    def payload_local_binaries_root_path_zip(self):
        return self.payload_path / Path("Universal-Binaries.zip")

    @property
    def kdk_download_path(self):
        return self.payload_path / Path("KDK.dmg")


    sbm_values = [
        "j137ap",  #  iMacPro1,1
        "j680ap",  #  MacBookPro15,1
        "j132ap",  #  MacBookPro15,2
        "j174ap",  #  Macmini8,1
        "j140kap",  # MacBookAir8,1
        "j780ap",  #  MacBookPro15,3
        "j213ap",  #  MacBookPro15,4
        "j140aap",  # MacBookAir8,2
        "j152fap",  # MacBookPro16,1
        "j160ap",  #  MacPro7,1
        "j230kap",  # MacBookAir9,1
        "j214kap",  # MacBookPro16,2
        "j223ap",  #  MacBookPro16,3
        "j215ap",  #  MacBookPro16,4
        "j185ap",  #  iMac20,1
        "j185fap",  # iMac20,2
        # "x86legacy",  # non-T2 Macs/VMs, Monterey's boot.efi enforces this on all Macs
    ]

    sandy_board_id_stock = [
        "Mac-94245B3640C91C81",  # MacBookPro8,1
        "Mac-94245A3940C91C80",  # MacBookPro8,2
        "Mac-942459F5819B171B",  # MacBookPro8,3
        "Mac-C08A6BB70A942AC2",  # MacBookAir4,1
        "Mac-742912EFDBEE19B3",  # MacBookAir4,2
        "Mac-8ED6AF5B48C039E1",  # Macmini5,1
        "Mac-4BC72D62AD45599E",  # Macmini5,2
        "Mac-7BA5B2794B2CDB12",  # Macmini5,3
        "Mac-942B5BF58194151B",  # iMac12,1
        "Mac-942B59F58194171B",  # iMac12,2
        "Mac-94245AF5819B141B",  # AppleInternal MacBookPro8,3
        "Mac-942B5B3A40C91381",  # AppleInternal iMac12,2
    ]
