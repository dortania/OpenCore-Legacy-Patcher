"""
constants.py: Defines versioning, file paths and other settings for the patcher
"""

from pathlib   import Path
from typing    import Optional
from packaging import version

from .datasets import os_data
from .detections import device_probe


class Constants:
    def __init__(self) -> None:
        # Patcher Versioning
        self.patcher_version:                 str = "2.3.0"  # OpenCore-Legacy-Patcher
        self.patcher_support_pkg_version:     str = "1.9.1"  # PatcherSupportPkg
        self.copyright_date:                  str = "Copyright © 2020-2024 Dortania"
        self.patcher_name:                    str = "OpenCore Legacy Patcher"

        # URLs
        self.url_patcher_support_pkg:         str = "https://github.com/dortania/PatcherSupportPkg/releases/download/"
        self.discord_link:                    str = "https://discord.gg/rqdPgH8xSN"
        self.guide_link:                      str = "https://dortania.github.io/OpenCore-Legacy-Patcher/"
        self.repo_link:                       str = "https://github.com/dortania/OpenCore-Legacy-Patcher"
        self.installer_pkg_url:               str = f"{self.repo_link}/releases/download/{self.patcher_version}/AutoPkg-Assets.pkg"
        self.installer_pkg_url_nightly:       str = "http://nightly.link/dortania/OpenCore-Legacy-Patcher/workflows/build-app-wxpython/main/AutoPkg-Assets.pkg.zip"

        # OpenCore Versioning
        # https://github.com/acidanthera/OpenCorePkg
        self.opencore_version: str = "1.0.1"

        # Kext Versioning
        ## Acidanthera
        ## https://github.com/acidanthera
        self.lilu_version:               str = "1.6.8"  #      Lilu
        self.whatevergreen_version:      str = "1.6.7"  #      WhateverGreen
        self.whatevergreen_navi_version: str = "1.6.7-Navi"  # WhateverGreen (Navi Patch)
        self.airportbcrmfixup_version:   str = "2.1.8"  #      AirPortBrcmFixup
        self.nvmefix_version:            str = "1.1.1"  #      NVMeFix
        self.applealc_version:           str = "1.6.3"  #      AppleALC
        self.restrictevents_version:     str = "1.1.4"  #      RestrictEvents
        self.featureunlock_version:      str = "1.1.6"  #      FeatureUnlock
        self.debugenhancer_version:      str = "1.0.9"  #      DebugEnhancer
        self.cpufriend_version:          str = "1.2.8"  #      CPUFriend
        self.bluetool_version:           str = "2.6.8"  #      BlueToolFixup (BrcmPatchRAM)
        self.cslvfixup_version:          str = "2.6.1"  #      CSLVFixup
        self.autopkg_version:            str = "1.0.4"  #      AutoPkgInstaller
        self.cryptexfixup_version:       str = "1.0.3"  #      CryptexFixup

        ## Apple
        ## https://www.apple.com
        self.marvel_version:        str = "1.0.1"  #  MarvelYukonEthernet
        self.nforce_version:        str = "1.0.1"  #  nForceEthernet
        self.piixata_version:       str = "1.0.1"  #  AppleIntelPIIXATA
        self.fw_kext:               str = "1.0.1"  #  IOFireWireFamily
        self.apple_trackpad:        str = "1.0.1"  #  AppleUSBTrackpad
        self.apple_isight_version:  str = "1.0.0"  #  AppleiSight
        self.apple_raid_version:    str = "1.0.0"  #  AppleRAIDCard
        self.apfs_zlib_version:     str = "12.3.1"  # NoAVXFSCompressionTypeZlib
        self.apfs_zlib_v2_version:  str = "12.6"  #   NoAVXFSCompressionTypeZlib (patched with AVXpel)
        self.multitouch_version:    str = "1.0.0"  #  AppleUSBMultitouch
        self.topcase_version:       str = "1.0.0"  #  AppleUSBTopCase
        self.topcase_inj_version:   str = "1.0.0"  #  AppleTopCaseInjector
        self.intel_82574l_version:  str = "1.0.0"  #  Intel82574L
        self.intel_8254x_version:   str = "1.0.0"  #  AppleIntel8254XEthernet
        self.apple_usb_11_injector: str = "1.0.0"  #  AppleUSBUHCI/OHCI
        self.aicpupm_version:       str = "1.0.0"  #  AppleIntelCPUPowerManagement/Client
        self.s3x_nvme_version:      str = "1.0.0"  #  IONVMeFamily (14.0 Beta 1, S1X and S3X classes)
        self.apple_camera_version:  str = "1.0.0"  #  AppleCameraInterface (14.0 Beta 1)
        self.t1_sse_version:        str = "1.1.0"  #  AppleSSE      (13.6 - T1 support)
        self.t1_key_store_version:  str = "1.1.0"  #  AppleKeyStore (13.6 - T1 support)
        self.t1_credential_version: str = "1.0.0"  #  AppleCredentialManager (13.6 - T1 support)
        self.t1_corecrypto_version: str = "1.0.1"  #  corecrypto    (13.6 - T1 support)
        self.apple_spi_version:     str = "1.0.0"  #  AppleHSSPISupport   (14.4 Beta 1)
        self.apple_spi_hid_version: str = "1.0.0"  #  AppleHSSPIHIDDriver (14.4 Beta 1)
        self.kernel_relay_version:  str = "1.0.0"  #  KernelRelayHost (15.0 Beta 3)

        ## Apple - Dortania Modified
        self.bcm570_version:           str = "1.0.2"  # CatalinaBCM5701Ethernet
        self.i210_version:             str = "1.0.0"  # CatalinaIntelI210Ethernet
        self.corecaptureelcap_version: str = "1.0.2"  # corecaptureElCap
        self.io80211elcap_version:     str = "2.0.1"  # IO80211ElCap
        self.io80211legacy_version:    str = "1.0.0"  # IO80211FamilyLegacy (Ventura)
        self.ioskywalk_version:        str = "1.2.0"  # IOSkywalkFamily (Ventura)
        self.bigsursdxc_version:       str = "1.0.0"  # BigSurSDXC
        self.monterey_ahci_version:    str = "1.0.0"  # CatalinaAHCI

        ## Apple - Jazzzny Modified
        self.aquantia_version: str = "1.1.0"  # AppleEthernetAbuantiaAqtion

        ## Dortania
        ## https://github.com/dortania
        self.backlight_injector_version:     str = "1.1.0"  # BacklightInjector
        self.backlight_injectorA_version:    str = "1.0.0"  # BacklightInjector (iMac9,1)
        self.smcspoof_version:               str = "1.0.0"  # SMC-Spoof
        self.mce_version:                    str = "1.0.0"  # AppleMCEReporterDisabler
        self.btspoof_version:                str = "1.0.0"  # Bluetooth-Spoof
        self.aspp_override_version:          str = "1.0.1"  # ACPI_SMC_PlatformPlugin Override
        self.ecm_override_version:           str = "1.0.0"  # AppleUSBECM Override
        self.rsrhelper_version:              str = "1.0.2"  # RSRHelper
        self.amfipass_version:               str = "1.4.1"  # AMFIPass
        self.amfipass_compatibility_version: str = "1.2.1"  # Minimum AMFIPass version required

        ## Syncretic
        ## https://forums.macrumors.com/members/syncretic.1173816/
        ## https://github.com/reenigneorcim/latebloom
        self.mousse_version:     str = "0.95-Dortania"  # MouSSE
        self.telemetrap_version: str = "1.0.0"  #         telemetrap

        ## cdf
        ## https://github.com/cdf/Innie
        self.innie_version: str = "1.3.1"  # Innie

        ## arter97
        ## https://github.com/arter97/SimpleMSR/
        self.simplemsr_version: str = "1.0.0"  # SimpleMSR

        ## blackgate
        ## https://github.com/blackgate/AMDGPUWakeHandler
        self.gpu_wake_version: str = "1.0.0"

        ## flagersgit
        ## https://github.com/flagersgit/KDKlessWorkaround
        self.kdkless_version: str = "1.0.0"

        ## Jazzzny
        self.legacy_keyboard: str = "1.0.0"  # LegacyKeyboardInjector - Jazzzny

        # Get resource path
        self.current_path:  Path = Path(__file__).parent.parent.resolve()
        self.original_path: Path = Path(__file__).parent.parent.resolve()
        self.payload_path:  Path = self.current_path / Path("payloads")


        # Patcher Settings
        ## Internal settings
        self.allow_oc_everywhere:       bool = False  # Set whether Patcher can be run on unsupported Macs
        self.gui_mode:                  bool = False  # Determine whether running in a GUI or TUI
        self.cli_mode:                  bool = True  #  Determine if running in CLI mode
        self.validate:                  bool = False  # Enable validation testing for CI
        self.recovery_status:           bool = False  # Detect if booted into RecoveryOS
        self.ignore_updates:            bool = False  # Ignore OCLP updates
        self.wxpython_variant:          bool = False  # Determine if using wxPython variant
        self.has_checked_updates:       bool = False  # Determine if check for updates has been run
        self.root_patcher_succeeded:    bool = False  # Determine if root patcher succeeded
        self.start_build_install:       bool = False  # Determine if build install should be started
        self.host_is_non_metal:         bool = False  # Determine if host is non-metal (ie. enable UI hacks)
        self.needs_to_open_preferences: bool = False  # Determine if preferences need to be opened
        self.host_is_hackintosh:        bool = False  # Determine if host is Hackintosh
        self.should_nuke_kdks:          bool = True  #  Determine if KDKs should be nuked if unused in /L*/D*/KDKs
        self.launcher_binary:            str = None  #  Determine launch binary path (ie. Python vs PyInstaller)
        self.launcher_script:            str = None  #  Determine launch file path   (None if PyInstaller)
        self.booted_oc_disk:             str = None  #  Determine current disk OCLP booted from
        self.unpack_thread                   = None  #  Determine if unpack thread finished (threading.Thread)
        self.update_stage:               int = 0  #     Determine update stage (see gui_support.py)
        self.log_filepath:              Path = None  #  Path to log file

        self.commit_info: tuple = (None, None, None)  # Commit info (Branch, Commit Date, Commit URL)

        ## Hardware
        self.computer: device_probe.Computer = None  # type: ignore
        self.custom_model:     Optional[str] = None

        ## OpenCore Settings
        self.opencore_debug: bool = False # Enable OpenCore debug
        self.boot_efi:       bool = False # Use EFI/BOOT/BOOTx64.efi vs boot.efi bootstrap
        self.showpicker:     bool = True  # Show or Hide OpenCore's Boot Picker
        self.nvram_write:    bool = True  # Write to hardware NVRAM
        self.oc_timeout:      int = 5  #    Set OpenCore timeout

        ## Kext Settings
        self.kext_debug:  bool = False  # Enables Lilu debug and DebugEnhancer
        self.kext_variant: str = "RELEASE"

        ## NVRAM Settings
        self.verbose_debug: bool = False  # -v

        ## SMBIOS Settings
        self.serial_settings:     str  = "None"  #    Set SMBIOS level used
        self.override_smbios:     str  = "Default"  # Set SMBIOS model used
        self.allow_native_spoofs: bool = False  #     Allow native models to receive spoofs

        ### Serial Number Overrides
        self.custom_serial_number:       str = ""  # Set SMBIOS serial number
        self.custom_board_serial_number: str = ""  # Set SMBIOS board serial number

        ## FeatureUnlock Settings
        self.fu_status:    bool = False  # Enable FeatureUnlock
        self.fu_arguments: str  = None   # Set FeatureUnlock arguments

        ## Security Settings
        self.sip_status:     bool = True  #  System Integrity Protection
        self.secure_status:  bool = False  # Secure Boot Model
        self.vault:          bool = False  # EFI Vault
        self.disable_cs_lv:  bool = False  # Disable Library validation
        self.disable_amfi:   bool = False  # Disable AMFI

        ## OS Settings
        self.os_support:        float = 12.0
        self.detected_os:         int = 0  #  Major Kernel Version
        self.detected_os_minor:   int = 0  #  Minor Kernel Version
        self.detected_os_build:   str = ""  # OS Build
        self.detected_os_version: str = ""  # OS Version

        ## Boot Volume Settings
        self.firewire_boot: bool = False  # Allow macOS FireWire Boot (kernel)
        self.nvme_boot:     bool = False  # Allow UEFI NVMe Boot
        self.xhci_boot:     bool = False  # Allow UEFI XHCI Boot

        ## Graphics Settings
        self.allow_ts2_accel:             bool = True  #  Set TeraScale 2 Acceleration support
        self.drm_support:                 bool = False  # Set iMac14,x DRM support
        self.force_nv_web:                bool = False  # Force Nvidia Web Drivers on Tesla and Kepler
        self.force_output_support:        bool = False  # Force Output support for Mac Pros with PC VBIOS
        self.amd_gop_injection:           bool = False  # Set GOP Injection support
        self.nvidia_kepler_gop_injection: bool = False  # Set Kepler GOP Injection support

        ### MXM GPU Support
        self.metal_build: bool = False  # Set MXM Build support
        self.imac_vendor: str = "None"  # Set MXM GPU vendor
        self.imac_model:  str = "" #      Set MXM GPU model

        ## Miscellaneous build settings
        self.disallow_cpufriend:     bool = False  # Disable CPUFriend
        self.enable_wake_on_wlan:    bool = False  # Allow Wake on WLAN for modern Broadcom
        self.disable_tb:             bool = False  # Disable Thunderbolt Controller
        self.dGPU_switch:            bool = False  # Set Display GPU Switching for Windows
        self.force_surplus:          bool = False  # Force SurPlus patch in newer OSes
        self.force_latest_psp:       bool = False  # Force latest PatcherSupportPkg
        self.disable_fw_throttle:    bool = False  # Disable MSR Power Control and XCPM
        self.software_demux:         bool = False  # Enable Software Demux patch set
        self.force_vmm:              bool = False  # Force VMM patch
        self.disable_connectdrivers: bool = False  # Disable ConnectDrivers (hibernation)
        self.set_vmm_cpuid:          bool = False  # Set VMM bit inside CPUID
        self.disable_mediaanalysisd: bool = False  # Set mediaanalysisd to spawn
        self.force_quad_thread:      bool = False #  Force quad thread mode (cpus=4)
        self.set_alc_usage:          bool = True  #  Set AppleALC usage
        self.allow_3rd_party_drives: bool = True  #  Allow ThridPartyDrives quirk
        self.allow_nvme_fixing:      bool = True  #  Allow NVMe Kernel Space Patches
        self.apfs_trim_timeout:      bool = True  #  Set APFS Trim timeout
        self.custom_sip_value:        int = None  #  Set custom SIP value

        ## Non-Metal OS support
        self.legacy_accel_support = [
            os_data.os_data.big_sur,
            os_data.os_data.monterey,
            os_data.os_data.ventura,
            os_data.os_data.sonoma,
            os_data.os_data.sequoia,
        ]

    @property
    def special_build(self):
        """
        Special builds are used for testing. They do not get updates through the updater
        """

        try:
            version.parse(self.patcher_version)
            return False
        except version.InvalidVersion:
            return True

    # Payload Location

    # Support Disk Images
    @property
    def payload_path_dmg(self):
        return self.original_path / Path("payloads.dmg")

    @property
    def payload_local_binaries_root_path_dmg(self):
        return self.original_path / Path("Universal-Binaries.dmg")

    @property
    def overlay_psp_path_dmg(self):
        return self.original_path / Path("DortaniaInternalResources.dmg")

    # OpenCore
    @property
    def opencore_zip_source(self):
        return self.payload_path / Path(f"OpenCore/OpenCore-{'DEBUG' if self.opencore_debug is True else 'RELEASE'}.zip")

    @property
    def plist_template(self):
        return self.payload_path / Path("Config/config.plist")

    # Launch Services
    @property
    def launch_services_path(self):
        return self.payload_path / Path("Launch Services")

    @property
    def auto_patch_launch_agent_path(self):
        return self.launch_services_path / Path("com.dortania.opencore-legacy-patcher.auto-patch.plist")

    @property
    def rsr_monitor_launch_daemon_path(self):
        return self.launch_services_path / Path("com.dortania.opencore-legacy-patcher.rsr-monitor.plist")

    @property
    def update_launch_daemon_path(self):
        return self.launch_services_path / Path("com.dortania.opencore-legacy-patcher.macos-update.plist")

    @property
    def kdk_launch_daemon_path(self):
        return self.launch_services_path / Path("com.dortania.opencore-legacy-patcher.os-caching.plist")

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
    def amd_gop_driver_path(self):
        return self.payload_path / Path("Drivers/AMDGOP.efi")

    @property
    def nvidia_kepler_gop_driver_path(self):
        return self.payload_path / Path("Drivers/NVGOP_GK.efi")

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
    def link_rate_driver_path(self):
        return self.payload_path / Path("Drivers/FixPCIeLinkRate.efi")

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
    def whatevergreen_navi_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/WhateverGreen-v{self.whatevergreen_navi_version}-{self.kext_variant}.zip")

    @property
    def airportbcrmfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AirportBrcmFixup-v{self.airportbcrmfixup_version}-{self.kext_variant}.zip")

    @property
    def restrictevents_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-v{self.restrictevents_version}-{self.kext_variant}.zip")

    @property
    def efi_disabler_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/EFICheckDisabler.zip")

    @property
    def bcm570_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/CatalinaBCM5701Ethernet-v{self.bcm570_version}.zip")

    @property
    def aquantia_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/AppleEthernetAbuantiaAqtion-v{self.aquantia_version}.zip")

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
    def top_case_inj_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleTopCaseInjector-v{self.topcase_inj_version}.zip")

    @property
    def t1_key_store_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleKeyStore-v{self.t1_key_store_version}.zip")

    @property
    def t1_credential_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleCredentialManager-v{self.t1_credential_version}.zip")

    @property
    def t1_sse_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleSSE-v{self.t1_sse_version}.zip")

    @property
    def t1_corecrypto_path(self):
        return self.payload_kexts_path / Path(f"Misc/corecrypto_T1-v{self.t1_corecrypto_version}.zip")

    @property
    def apple_spi_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleHSSPISupport-v{self.apple_spi_version}.zip")

    @property
    def apple_spi_hid_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleHSSPIHIDDriver-v{self.apple_spi_hid_version}.zip")

    @property
    def kernel_relay_path(self):
        return self.payload_kexts_path / Path(f"Misc/KernelRelayHost-v{self.kernel_relay_version}.zip")

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
    def io80211legacy_path(self):
        return self.payload_kexts_path / Path(f"Wifi/IO80211FamilyLegacy-v{self.io80211legacy_version}.zip")

    @property
    def ioskywalk_path(self):
        return self.payload_kexts_path / Path(f"Wifi/IOSkywalkFamily-v{self.ioskywalk_version}.zip")

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
    def backlight_injectorA_path(self):
        return self.payload_kexts_path / Path(f"Misc/BacklightInjectorA-v{self.backlight_injectorA_version}.zip")

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
    def ecm_override_path(self):
        return self.payload_kexts_path / Path(f"Misc/ECM-Override-v{self.ecm_override_version}.zip")

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
    def rsrhelper_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RSRHelper-v{self.rsrhelper_version}-{self.kext_variant}.zip")

    @property
    def amfipass_path(self):
        # AMFIPass is release only
        return self.payload_kexts_path / Path(f"Acidanthera/AMFIPass-v{self.amfipass_version}-RELEASE.zip")

    @property
    def innie_path(self):
        return self.payload_kexts_path / Path(f"Misc/Innie-v{self.innie_version}-{self.kext_variant}.zip")

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
    def legacy_keyboard_path(self):
        return self.payload_kexts_path / Path(f"Misc/LegacyKeyboardInjector-v{self.legacy_keyboard}.zip")

    @property
    def apple_raid_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleRAIDCard-v{self.apple_raid_version}.zip")

    @property
    def kdkless_path(self):
        return self.payload_kexts_path / Path(f"Misc/KDKlessWorkaround-v{self.kdkless_version}-{self.kext_variant}.zip")

    @property
    def s3x_nvme_path(self):
        return self.payload_kexts_path / Path(f"Misc/IOS3XeFamily-v{self.s3x_nvme_version}.zip")

    @property
    def apple_camera_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleCameraInterface-v{self.apple_camera_version}.zip")

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
        return self.build_path / Path(f"OpenCore-{'DEBUG' if self.opencore_debug is True else 'RELEASE'}.zip")

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
        return self.payload_path / Path("OpenCore/macserial")

    @property
    def vault_path(self):
        return self.payload_path / Path("Tools/CreateVault/sign.command")

    @property
    def ocvalidate_path(self):
        return self.payload_path / Path(f"OpenCore/ocvalidate")

    @property
    def oclp_helper_path(self):
        return self.payload_path / Path("Tools/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher")

    @property
    def rsrrepair_userspace_path(self):
        return self.payload_path / Path("Tools/RSRRepair")

    # Icons
    @property
    def icns_resource_path(self):
        if self.launcher_script:
            return self.payload_path / Path("Icon/AppIcons")
        return Path(self.launcher_binary).parent.parent / Path("Resources")


    @property
    def app_icon_path(self):
        return self.payload_path / Path("Icon/AppIcons/OC-Patcher.icns")

    @property
    def icon_path_external(self):
        return self.payload_path / Path("Icon/DriveIcons/External/.VolumeIcon.icns")

    @property
    def icon_path_internal(self):
        return self.payload_path / Path("Icon/DriveIcons/Internal/.VolumeIcon.icns")

    @property
    def icon_path_sd(self):
        return self.payload_path / Path("Icon/DriveIcons/SD-Card/.VolumeIcon.icns")

    @property
    def icon_path_ssd(self):
        return self.payload_path / Path("Icon/DriveIcons/SSD/.VolumeIcon.icns")

    @property
    def icon_path_macos_generic(self):
        return self.icns_resource_path / Path("Generic.icns")

    @property
    def icon_path_macos_big_sur(self):
        return self.icns_resource_path / Path("BigSur.icns")

    @property
    def icon_path_macos_monterey(self):
        return self.icns_resource_path / Path("Monterey.icns")

    @property
    def icon_path_macos_ventura(self):
        return self.icns_resource_path / Path("Ventura.icns")

    @property
    def icon_path_macos_sonoma(self):
        return self.icns_resource_path / Path("Sonoma.icns")

    @property
    def icon_path_macos_sequoia(self):
        return self.icns_resource_path / Path("Sequoia.icns")

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
    def kdk_download_path(self):
        return self.payload_path / Path("KDK.dmg")

    @property
    def metallib_download_path(self):
        return self.payload_path / Path("MetallibSupportPkg.pkg")

    @property
    def icons_path(self):
        return [
            str(self.icon_path_macos_generic),
            str(self.icon_path_macos_big_sur),
            str(self.icon_path_macos_monterey),
            str(self.icon_path_macos_ventura),
            str(self.icon_path_macos_sonoma),
            str(self.icon_path_macos_sequoia),
        ]

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