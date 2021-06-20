# pylint: disable=multiple-statements
# Define Files
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

from pathlib import Path
from typing import Optional

from Resources import device_probe


class Constants:
    def __init__(self):
        self.patcher_version = "0.2.0"
        self.opencore_commit = "4e0ff2d - 05-23-2021"
        self.opencore_version = "0.7.0"
        self.lilu_version = "1.5.4"
        self.whatevergreen_version = "1.5.1"
        self.airportbcrmfixup_version = "2.1.3"
        self.bcm570_version = "1.0.1"
        self.marvel_version = "1.0.0"
        self.nforce_version = "1.0.0"
        self.mce_version = "1.0.0"
        self.mousse_version = "0.95"
        self.telemetrap_version = "1.0.0"
        self.corecaptureelcap_version = "1.0.0"
        self.io80211elcap_version = "1.0.0"
        self.io80211high_sierra_version = "1.0.0"
        self.io80211mojave_version = "1.0.0"
        self.applealc_version = "1.6.2"
        self.restrictevents_version = "1.0.3"
        self.restrictevents_mbp_version = "1.0.3"
        self.piixata_version = "1.0.0"
        self.backlight_version = "1.0.1"
        self.backlight_injector_version = "1.0.0"
        self.cpufriend_version = "1.2.4"
        self.nightshift_version = "1.1.0"
        self.smcspoof_version = "1.0.0"
        self.nvmefix_version = "1.0.9"
        self.sidecarfixup_version = "1.0.2"
        self.debugenhancer_version = "1.0.3"
        self.innie_version = "1.3.0"
        self.fw_kext = "1.0.0"
        self.patcher_support_pkg_version = "0.0.7"  # PatcherSupportPkg

        # Get resource path
        self.current_path = Path(__file__).parent.parent.resolve()
        self.payload_path = self.current_path / Path("payloads")

        # Hardware
        self.computer: device_probe.Computer = None  # type: ignore

        self.custom_model: Optional[str] = None
        self.custom_mxm_gpu: bool = False

        # Patcher Settings
        self.opencore_debug = False
        self.opencore_build = "RELEASE"
        self.kext_debug = False
        self.verbose_debug = False
        self.os_support = 12.0
        self.metal_build = False
        self.imac_vendor = "None"
        self.wifi_build = False
        self.gui_mode = False
        self.serial_settings = "Minimal"
        self.showpicker = True
        self.vault = False
        self.sip_status = True
        self.secure_status = False
        self.detected_os = 0
        self.boot_efi = False
        self.drm_support = False
        self.allow_oc_everywhere = False
        self.custom_cpu_model = 2
        self.custom_cpu_model_value = ""
        self.custom_color = ""
        self.download_ram = False
        self.disallow_cpufriend = False
        self.recovery_status = False
        self.override_smbios = "Default"
        self.apecid_support = False
        self.firewire_boot = False
        self.nvme_boot = False
        self.disable_amfi = False
        self.terascale_2_patch = False

        # OS Versions
        self.tiger = 8
        self.leopard = 9
        self.snow_leopard = 10
        self.lion = 11
        self.mountain_lion = 12
        self.mavericks = 13
        self.yosemite = 14
        self.el_capitan = 15
        self.sierra = 16
        self.high_sierra = 17
        self.mojave = 18
        self.catalina = 19
        self.big_sur = 20
        self.monterey = 21

        # Vendor IDs
        self.pci_nvidia = "10DE"
        self.pci_amd_ati = "1002"
        self.pci_intel = "8086"
        self.pci_broadcom = "14E4"
        self.pci_atheros = "168C"
        self.pci_apple = "106B"

        # Class Codes
        # https://pci-ids.ucw.cz/read/PD
        self.classcode_sata = "01060100"
        self.classcode_nvme = "02080100"
        self.classcode_nvme_generic = "02800100"
        self.classcode_wifi = "00800200"
        self.classcode_gpu = "00000300"
        self.classcode_gpu_variant = "00800300"
        self.classcode_xhci = "30030C00"

        # Nvidia GPU Architecture
        self.arch_tesla = "NV50"
        self.arch_fermi = "GF100"
        self.arch_kepler = "GK100"

        # External Files
        self.url_patcher_support_pkg = "https://github.com/dortania/PatcherSupportPkg/releases/download/"

    # Payload Location
    # OpenCore
    @property
    def opencore_zip_source(self):
        return self.payload_path / Path(f"OpenCore/OpenCore-{self.opencore_build}.zip")

    @property
    def plist_template(self):
        return self.payload_path / Path("Config/config.plist")

    # Mount Location
    @property
    def payload_mnt1_path(self):
        return self.payload_path / Path("mnt1")

    # ACPI
    @property
    def pci_ssdt_path(self):
        return self.payload_path / Path("ACPI/SSDT-CPBG.aml")

    @property
    def windows_ssdt_path(self):
        return self.payload_path / Path("ACPI/SSDT-PCI.aml")

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

    # Kexts
    @property
    def payload_kexts_path(self):
        return self.payload_path / Path("Kexts")

    @property
    def lilu_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/Lilu-v{self.lilu_version}.zip")

    @property
    def whatevergreen_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/WhateverGreen-v{self.whatevergreen_version}.zip")

    @property
    def airportbcrmfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AirportBrcmFixup-v{self.airportbcrmfixup_version}.zip")

    @property
    def restrictevents_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-v{self.restrictevents_version}.zip")

    @property
    def restrictevents_mbp_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-MBP91-v{self.restrictevents_mbp_version}.zip")

    @property
    def bcm570_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/CatalinaBCM5701Ethernet-v{self.bcm570_version}.zip")

    @property
    def marvel_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/MarvelYukonEthernet-v{self.marvel_version}.zip")

    @property
    def nforce_path(self):
        return self.payload_kexts_path / Path(f"Ethernet/nForceEthernet-v{self.nforce_version}.zip")

    @property
    def mce_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleMCEReporterDisabler-v{self.mce_version}.zip")

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
    def io80211high_sierra_path(self):
        return self.payload_kexts_path / Path(f"Wifi/IO80211HighSierra-v{self.io80211high_sierra_version}.zip")

    @property
    def io80211mojave_path(self):
        return self.payload_kexts_path / Path(f"Wifi/IO80211Mojave-v{self.io80211mojave_version}.zip")

    @property
    def applealc_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/AppleALC-v{self.applealc_version}.zip")

    @property
    def piixata_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleIntelPIIXATA-v{self.piixata_version}.zip")

    @property
    def backlight_path(self):
        return self.payload_kexts_path / Path(f"Misc/AppleBacklightFixup-v{self.backlight_version}.zip")

    @property
    def backlight_injector_path(self):
        return self.payload_kexts_path / Path(f"Misc/BacklightInjector-v{self.backlight_injector_version}.zip")

    @property
    def cpufriend_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/CPUFriend-v{self.cpufriend_version}.zip")

    @property
    def nightshift_path(self):
        return self.payload_kexts_path / Path(f"Misc/NightShiftEnabler-v{self.nightshift_version}.zip")

    @property
    def smcspoof_path(self):
        return self.payload_kexts_path / Path(f"Misc/SMC-Spoof-v{self.smcspoof_version}.zip")

    @property
    def nvmefix_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/NVMeFix-v{self.nvmefix_version}.zip")

    @property
    def sidecarfixup_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/SidecarFixup-v{self.sidecarfixup_version}.zip")

    @property
    def debugenhancer_path(self):
        return self.payload_kexts_path / Path(f"Acidanthera/DebugEnhancer-v{self.debugenhancer_version}.zip")

    @property
    def innie_path(self):
        return self.payload_kexts_path / Path(f"Misc/Innie-v{self.innie_version}.zip")

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
        return self.build_path / Path(f"OpenCore-{self.opencore_build}")

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

    # Icons
    @property
    def app_icon_path(self):
        return self.current_path / Path("OC-Patcher.icns")

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

    # Apple Payloads Paths

    @property
    def payload_apple_root_path_zip(self):
        return self.payload_path / Path("Apple.zip")

    @property
    def payload_apple_root_path(self):
        return self.payload_path / Path("Apple")

    @property
    def payload_apple_kexts_path(self):
        return self.payload_apple_root_path / Path("Extensions")

    @property
    def payload_apple_frameworks_path(self):
        return self.payload_apple_root_path / Path("Frameworks")

    @property
    def payload_apple_frameworks_path_accel(self):
        return self.payload_apple_frameworks_path / Path("Graphics-Acceleration")

    @property
    def payload_apple_frameworks_path_accel_ts2(self):
        return self.payload_apple_frameworks_path / Path("Graphics-Acceleration-TeraScale-2")

    @property
    def payload_apple_frameworks_path_accel_ivy(self):
        return self.payload_apple_frameworks_path / Path("Graphics-Acceleration-Ivy-Bridge")

    @property
    def payload_apple_lauchd_path(self):
        return self.payload_apple_root_path / Path("LaunchDaemons")

    @property
    def payload_apple_lauchd_path_accel(self):
        return self.payload_apple_lauchd_path / Path("Graphics-Acceleration")

    @property
    def payload_apple_private_frameworks_path(self):
        return self.payload_apple_root_path / Path("PrivateFrameworks")

    @property
    def payload_apple_private_frameworks_path_accel(self):
        return self.payload_apple_private_frameworks_path / Path("Graphics-Acceleration")

    @property
    def payload_apple_private_frameworks_path_accel_ts2(self):
        return self.payload_apple_private_frameworks_path / Path("Graphics-Acceleration-TeraScale-2")

    @property
    def payload_apple_private_frameworks_path_brightness(self):
        return self.payload_apple_private_frameworks_path / Path("Brightness-Control")

    # Apple Extensions
    @property
    def audio_path(self):
        return self.payload_apple_kexts_path / Path("Audio")

    # GPU Kexts and Bundles

    @property
    def legacy_graphics(self):
        return self.payload_apple_kexts_path / Path("Graphics-Acceleration")

    @property
    def legacy_nvidia_path(self):
        return self.legacy_graphics / Path("Nvidia-Tesla-Fermi")

    @property
    def legacy_nvidia_kepler_path(self):
        return self.legacy_graphics / Path("Nvidia-Kepler")

    @property
    def legacy_amd_path(self):
        return self.legacy_graphics / Path("AMD-TeraScale")

    @property
    def legacy_amd_path_ts2(self):
        return self.legacy_graphics / Path("AMD-TeraScale-2")

    @property
    def legacy_intel_gen1_path(self):
        return self.legacy_graphics / Path("Intel-Gen5-Ironlake")

    @property
    def legacy_intel_gen2_path(self):
        return self.legacy_graphics / Path("Intel-Gen6-SandyBridge")

    @property
    def legacy_intel_gen3_path(self):
        return self.legacy_graphics / Path("Intel-Gen7-IvyBridge")

    @property
    def legacy_general_path(self):
        return self.legacy_graphics / Path("General-Patches")

    @property
    def legacy_brightness(self):
        return self.payload_apple_kexts_path / Path("Brightness-Control")

    csr_values = {
        "CSR_ALLOW_UNTRUSTED_KEXTS": False,  # 0x1   - Allows Unsigned Kexts           - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_FS": False,  # 0x2   - File System Access              - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_TASK_FOR_PID": False,  # 0x4   - Unrestricted Debugging          - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_KERNEL_DEBUGGER": False,  # 0x8   - Allow Kernel Debugger           - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_APPLE_INTERNAL": False,  # 0x10  - Set AppleInternal Features      - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_DTRACE": False,  # 0x20  - Unrestricted DTrace usage       - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_UNRESTRICTED_NVRAM": False,  # 0x40  - Unrestricted NVRAM write        - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_DEVICE_CONFIGURATION": False,  # 0x80  - Allow Device Configuration(?)   - Introduced in El Capitan  # noqa: E241
        "CSR_ALLOW_ANY_RECOVERY_OS": False,  # 0x100 - Disable BaseSystem Verification - Introduced in Sierra      # noqa: E241
        "CSR_ALLOW_UNAPPROVED_KEXTS": False,  # 0x200 - Allow Unapproved Kexts          - Introduced in High Sierra # noqa: E241
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE": False,  # 0x400 - Override Executable Policy      - Introduced in Mojave      # noqa: E241
        "CSR_ALLOW_UNAUTHENTICATED_ROOT": False,  # 0x800 - Allow Root Volume Mounting      - Introduced in Big Sur     # noqa: E241
    }

    root_patch_sip_mojave = [
        # Variables required to root patch in Mojave and Catalina
        "CSR_ALLOW_UNTRUSTED_KEXTS",
        "CSR_ALLOW_UNRESTRICTED_FS",
        "CSR_ALLOW_UNAPPROVED_KEXTS",
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",
    ]

    root_patch_sip_big_sur = [
        # Variables required to root patch in Big Sur and Monterey
        "CSR_ALLOW_UNTRUSTED_KEXTS",
        "CSR_ALLOW_UNRESTRICTED_FS",
        "CSR_ALLOW_UNAPPROVED_KEXTS",
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",
        "CSR_ALLOW_UNAUTHENTICATED_ROOT",
    ]

    sbm_values = [
        "j137",
        "j680",
        "j132",
        "j174",
        "j140k",
        "j780",
        "j213",
        "j140a",
        "j152f",
        "j160",
        "j230k",
        "j214k",
        "j223",
        "j215",
        "j185",
        "j185f",
    ]

    board_id = {
        "MacBook1,1": "Mac-F4208CC8",
        "MacBook2,1": "Mac-F4208CA9",
        "MacBook3,1": "Mac-F22788C8",
        "MacBook4,1": "Mac-F22788A9",
        "MacBook5,1": "Mac-F42D89C8",
        "MacBook5,2": "Mac-F22788AA",
        "MacBook6,1": "Mac-F22C8AC8",
        "MacBook7,1": "Mac-F22C89C8",
        "MacBook8,1": "Mac-BE0E8AC46FE800CC",
        "MacBook9,1": "Mac-9AE82516C7C6B903",
        "MacBook10,1": "Mac-EE2EBD4B90B839A8",
        "MacBookAir1,1": "Mac-F42C8CC8",
        "MacBookAir2,1": "Mac-F42D88C8",
        "MacBookAir3,1": "Mac-942452F5819B1C1B",
        "MacBookAir3,2": "Mac-942C5DF58193131B",
        "MacBookAir4,1": "Mac-C08A6BB70A942AC2",
        "MacBookAir4,2": "Mac-742912EFDBEE19B3",
        "MacBookAir5,1": "Mac-66F35F19FE2A0D05",
        "MacBookAir5,2": "Mac-2E6FAB96566FE58C",
        "MacBookAir6,1": "Mac-35C1E88140C3E6CF",
        "MacBookAir6,2": "Mac-7DF21CB3ED6977E5",
        "MacBookAir7,1": "Mac-9F18E312C5C2BF0B",
        "MacBookAir7,2": "Mac-937CB26E2E02BB01",
        "MacBookAir8,1": "Mac-827FAC58A8FDFA22",
        "MacBookAir8,2": "Mac-226CB3C6A851A671",
        "MacBookAir9,1": "Mac-0CFF9C7C2B63DF8D",
        "MacBookPro1,1": "Mac-F425BEC8",
        "MacBookPro1,2": "Mac-F42DBEC8",
        "MacBookPro2,1": "Mac-F42189C8",
        "MacBookPro2,2": "Mac-F42187C8",
        "MacBookPro3,1": "Mac-F4238BC8",
        "MacBookPro4,1": "Mac-F42C89C8",
        "MacBookPro5,1": "Mac-F42D86C8",
        "MacBookPro5,2": "Mac-F2268EC8",
        "MacBookPro5,3": "Mac-F22587C8",
        "MacBookPro5,4": "Mac-F22587A1",
        "MacBookPro5,5": "Mac-F2268AC8",
        "MacBookPro6,1": "Mac-F22589C8",
        "MacBookPro6,2": "Mac-F22586C8",
        "MacBookPro7,1": "Mac-F222BEC8",
        "MacBookPro8,1": "Mac-94245B3640C91C81",
        "MacBookPro8,2": "Mac-94245A3940C91C80",
        "MacBookPro8,3": "Mac-942459F5819B171B",
        "MacBookPro9,1": "Mac-4B7AC7E43945597E",
        "MacBookPro9,2": "Mac-6F01561E16C75D06",
        "MacBookPro10,1": "Mac-C3EC7CD22292981F",
        "MacBookPro10,2": "Mac-AFD8A9D944EA4843",
        "MacBookPro11,1": "Mac-189A3D4F975D5FFC",
        "MacBookPro11,2": "Mac-3CBD00234E554E41",
        "MacBookPro11,3": "Mac-2BD1B31983FE1663",
        "MacBookPro11,4": "Mac-06F11FD93F0323C5",
        "MacBookPro11,5": "Mac-06F11F11946D27C5",
        "MacBookPro12,1": "Mac-E43C1C25D4880AD6",
        "MacBookPro13,1": "Mac-473D31EABEB93F9B",
        "MacBookPro13,2": "Mac-66E35819EE2D0D05",
        "MacBookPro13,3": "Mac-A5C67F76ED83108C",
        "MacBookPro14,1": "Mac-B4831CEBD52A0C4C",
        "MacBookPro14,2": "Mac-CAD6701F7CEA0921",
        "MacBookPro14,3": "Mac-551B86E5744E2388",
        "MacBookPro15,1": "Mac-937A206F2EE63C01",
        "MacBookPro15,2": "Mac-827FB448E656EC26",
        "MacBookPro15,3": "Mac-1E7E29AD0135F9BC",
        "MacBookPro15,4": "Mac-53FDB3D8DB8CA971",
        "MacBookPro16,1": "Mac-E1008331FDC96864",
        "MacBookPro16,2": "Mac-5F9802EFE386AA28",
        "MacBookPro16,3": "Mac-E7203C0F68AA0004",
        "MacBookPro16,4": "Mac-A61BADE1FDAD7B05",
        "Macmini1,1": "Mac-F4208EC8",
        "Macmini2,1": "Mac-F4208EAA",
        "Macmini3,1": "Mac-F22C86C8",
        "Macmini4,1": "Mac-F2208EC8",
        "Macmini5,1": "Mac-8ED6AF5B48C039E1",
        "Macmini5,2": "Mac-4BC72D62AD45599E",
        "Macmini5,3": "Mac-7BA5B2794B2CDB12",
        "Macmini6,1": "Mac-031AEE4D24BFF0B1",
        "Macmini6,2": "Mac-F65AE981FFA204ED",
        "Macmini7,1": "Mac-35C5E08120C7EEAF",
        "Macmini8,1": "Mac-7BA5B2DFE22DDD8C",
        "iMac4,1": "Mac-F42786C8",
        "iMac4,2": "Mac-F4218EC8",
        "iMac5,1": "Mac-F4228EC8",
        "iMac5,2": "Mac-F4218EC8",
        "iMac6,1": "Mac-F4218FC8",
        "iMac7,1": "Mac-F42386C8",
        "iMac8,1": "Mac-F227BEC8",
        "iMac9,1": "Mac-F2218FA9",
        "iMac10,1": "Mac-F221DCC8",
        # "iMac10,1": "Mac-F2268CC8",
        "iMac11,1": "Mac-F2268DAE",
        "iMac11,2": "Mac-F2238AC8",
        "iMac11,3": "Mac-F2238BAE",
        "iMac12,1": "Mac-942B5BF58194151B",
        "iMac12,2": "Mac-942B59F58194171B",
        "iMac13,1": "Mac-00BE6ED71E35EB86",
        "iMac13,2": "Mac-FC02E91DDD3FA6A4",
        "iMac13,3": "Mac-7DF2A3B5E5D671ED",
        "iMac14,1": "Mac-031B6874CF7F642A",
        "iMac14,2": "Mac-27ADBB7B4CEE8E61",
        "iMac14,3": "Mac-77EB7D7DAF985301",
        "iMac14,4": "Mac-81E3E92DD6088272",
        "iMac15,1": "Mac-42FD25EABCABB274",
        "iMac16,1": "Mac-A369DDC4E67F1C45",
        "iMac16,2": "Mac-FFE5EF870D7BA81A",
        "iMac17,1": "Mac-DB15BD556843C820",
        "iMac18,1": "Mac-4B682C642B45593E",
        "iMac18,2": "Mac-77F17D7DA9285301",
        "iMac18,3": "Mac-BE088AF8C5EB4FA2",
        "iMac19,1": "Mac-AA95B1DDAB278B95",
        "iMac19,2": "Mac-63001698E7A34814",
        "iMac20,1": "Mac-CFF7D910A743CAAF",
        "iMac20,2": "Mac-AF89B6D9451A490B",
        "iMacPro1,1": "Mac-7BA5B2D9E42DDD94",
        "MacPro1,1": "Mac-F4208DC8",
        "MacPro2,1": "Mac-F4208DA9",
        "MacPro3,1": "Mac-F42C88C8",
        "MacPro4,1": "Mac-F221BEC8",
        "MacPro5,1": "Mac-F221BEC8",
        "MacPro6,1": "Mac-F60DEB81FF30ACF6",
        "MacPro7,1": "Mac-27AD2F918AE68F61",
        "Xserve1,1": "Mac-F4208AC8",
        "Xserve2,1": "Mac-F42289C8",
        "Xserve3,1": "Mac-F223BEC8",
    }
