# pylint: disable=multiple-statements
# Define Files
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

from __future__ import print_function

from pathlib import Path


class Constants:
    def __init__(self):
        self.patcher_version = "0.1.1"
        self.opencore_commit = "c528597 - 2021-04-05"
        self.opencore_version = "0.6.8"
        self.lilu_version = "1.5.2"
        self.whatevergreen_version = "1.4.9"
        self.airportbcrmfixup_version = "2.1.2"
        self.bcm570_version = "1.0.1"
        self.marvel_version = "1.0.0"
        self.nforce_version = "1.0.0"
        self.mce_version = "1.0.0"
        self.mousse_version = "0.93"
        self.telemetrap_version = "1.0.0"
        self.corecaptureelcap_version = "1.0.0"
        self.io80211elcap_version = "1.0.0"
        self.io80211high_sierra_version = "1.0.0"
        self.io80211mojave_version = "1.0.0"
        self.applealc_version = "1.6.0"
        self.restrictevents_version = "1.0.0"
        self.restrictevents_mbp_version = "1.0.1"
        self.piixata_version = "1.0.0"
        self.backlight_version = "1.0.1"
        self.cpufriend_version = "1.2.3"
        self.nightshift_version = "1.1.0"
        self.smcspoof_version = "1.0.0"
        self.cputscsync = "1.0.3"
        self.hibernationfixup = "1.3.9"
        self.payload_version = "0.0.3"

        # Get resource path
        self.current_path = Path(__file__).parent.parent.resolve()
        self.payload_path = self.current_path / Path("payloads")

        self.custom_model: str = None
        self.custom_mxm_gpu: str = None
        self.current_gpuv: str = None
        self.current_gpud: str = None
        self.igpu_vendor = ""
        self.igpu_device = ""
        self.dgpu_vendor = ""
        self.dgpu_device = ""

        # Patcher Settings
        self.opencore_debug = False
        self.opencore_build = "RELEASE"
        self.kext_debug = False
        self.verbose_debug = False
        self.os_support = 11.0
        self.min_os_support = 11.0
        self.max_os_support = 11.0
        self.metal_build = False
        self.imac_vendor = "None"
        self.wifi_build = False
        self.gui_mode = False
        self.serial_settings = "Minimal"
        self.showpicker = True
        self.vault = False
        self.sip_status = True
        self.secure_status = True
        self.detected_os = 0
        self.boot_efi = False
        self.drm_support = False
        self.legacy_acceleration_patch = False

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

        # Vendor IDs
        self.pci_nvidia = "10DE"
        self.pci_amd_ati = "1002"
        self.pci_intel = "8086"
        self.pci_broadcom = "14E4"
        self.pci_atheros = "168C"

        # External Files
        self.url_apple_binaries = "https://github.com/dortania/Apple-Binaries-OCLP/archive/refs/tags/"

    # Payload Location
    # OpenCore
    @property
    def opencore_zip_source(self): return self.payload_path / Path(f"OpenCore/OpenCore-{self.opencore_build}.zip")
    @property
    def plist_template(self): return self.payload_path / Path(f"Config/config.plist")

    # ACPI
    @property
    def pci_ssdt_path(self): return self.payload_path / Path("ACPI/SSDT-CPBG.aml")

    # Drivers
    @property
    def nvme_driver_path(self): return self.payload_path / Path("Drivers/NvmExpressDxe.efi")
    @property
    def exfat_legacy_driver_path(self): return self.payload_path / Path("Drivers/ExFatDxeLegacy.efi")

    # Kexts
    @property
    def payload_kexts_path(self): return self.payload_path / Path("Kexts")
    @property
    def lilu_path(self): return self.payload_kexts_path / Path(f"Acidanthera/Lilu-v{self.lilu_version}.zip")
    @property
    def whatevergreen_path(self): return self.payload_kexts_path / Path(f"Acidanthera/WhateverGreen-v{self.whatevergreen_version}.zip")
    @property
    def airportbcrmfixup_path(self): return self.payload_kexts_path / Path(f"Acidanthera/AirportBrcmFixup-v{self.airportbcrmfixup_version}.zip")
    @property
    def restrictevents_path(self): return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-v{self.restrictevents_version}.zip")
    @property
    def restrictevents_mbp_path(self): return self.payload_kexts_path / Path(f"Acidanthera/RestrictEvents-MBP91-v{self.restrictevents_mbp_version}.zip")
    @property
    def bcm570_path(self): return self.payload_kexts_path / Path(f"Ethernet/CatalinaBCM5701Ethernet-v{self.bcm570_version}.zip")
    @property
    def marvel_path(self): return self.payload_kexts_path / Path(f"Ethernet/MarvelYukonEthernet-v{self.marvel_version}.zip")
    @property
    def nforce_path(self): return self.payload_kexts_path / Path(f"Ethernet/nForceEthernet-v{self.nforce_version}.zip")
    @property
    def mce_path(self): return self.payload_kexts_path / Path(f"Misc/AppleMCEReporterDisabler-v{self.mce_version}.zip")
    @property
    def mousse_path(self): return self.payload_kexts_path / Path(f"SSE/AAAMouSSE-v{self.mousse_version}.zip")
    @property
    def telemetrap_path(self): return self.payload_kexts_path / Path(f"SSE/telemetrap-v{self.telemetrap_version}.zip")
    @property
    def corecaptureelcap_path(self): return self.payload_kexts_path / Path(f"Wifi/corecaptureElCap-v{self.corecaptureelcap_version}.zip")
    @property
    def io80211elcap_path(self): return self.payload_kexts_path / Path(f"Wifi/IO80211ElCap-v{self.io80211elcap_version}.zip")
    @property
    def io80211high_sierra_path(self): return self.payload_kexts_path / Path(f"Wifi/IO80211HighSierra-v{self.io80211high_sierra_version}.zip")
    @property
    def io80211mojave_path(self): return self.payload_kexts_path / Path(f"Wifi/IO80211Mojave-v{self.io80211mojave_version}.zip")
    @property
    def applealc_path(self): return self.payload_kexts_path / Path(f"Acidanthera/AppleALC-v{self.applealc_version}.zip")
    @property
    def piixata_path(self): return self.payload_kexts_path / Path(f"Misc/AppleIntelPIIXATA-v{self.piixata_version}.zip")
    @property
    def backlight_path(self): return self.payload_kexts_path / Path(f"Misc/AppleBacklightFixup-v{self.backlight_version}.zip")
    @property
    def cpufriend_path(self): return self.payload_kexts_path / Path(f"Acidanthera/CPUFriend-v{self.cpufriend_version}.zip")
    @property
    def nightshift_path(self): return self.payload_kexts_path / Path(f"Misc/NightShiftEnabler-v{self.nightshift_version}.zip")
    @property
    def smcspoof_path(self): return self.payload_kexts_path / Path(f"Misc/SMC-Spoof-v{self.smcspoof_version}.zip")
    @property
    def cputscsync_path(self): return self.payload_kexts_path / Path(f"Acidanthera/CpuTscSync-v{self.cputscsync}.zip")
    @property
    def hibernationfixup_path(self): return self.payload_kexts_path / Path(f"Acidanthera/HibernationFixup-v{self.hibernationfixup}.zip")
    @property
    def plist_folder_path(self): return self.payload_kexts_path / Path(f"Plists")
    @property
    def platform_plugin_plist_path(self): return self.plist_folder_path / Path(f"PlatformPlugin")

    # Build Location
    @property
    def build_path(self): return self.current_path / Path("Build-Folder/")
    @property
    def opencore_release_folder(self): return self.build_path / Path(f"OpenCore-{self.opencore_build}")
    @property
    def opencore_zip_copied(self): return self.build_path / Path(f"OpenCore-{self.opencore_build}.zip")

    @property
    def oc_folder(self): return self.opencore_release_folder / Path("EFI/OC/")
    @property
    def plist_path(self): return self.oc_folder / Path("config.plist")
    @property
    def acpi_path(self): return self.oc_folder / Path("ACPI")
    @property
    def drivers_path(self): return self.oc_folder / Path("Drivers")
    @property
    def kexts_path(self): return self.oc_folder / Path("Kexts")
    @property
    def resources_path(self): return self.oc_folder / Path("Resources")
    @property
    def map_kext_folder(self): return self.kexts_path / Path("USB-Map.kext")
    @property
    def map_contents_folder(self): return self.map_kext_folder / Path("Contents")
    @property
    def pp_kext_folder(self): return self.kexts_path / Path("CPUFriendDataProvider.kext")
    @property
    def pp_contents_folder(self): return self.pp_kext_folder / Path("Contents")
    @property
    def agdp_kext_folder(self): return self.kexts_path / Path("AGDP-Override.kext")
    @property
    def agdp_contents_folder(self): return self.agdp_kext_folder / Path("Contents")
    @property
    def agpm_kext_folder(self): return self.kexts_path / Path("AGPM-Override.kext")
    @property
    def agpm_contents_folder(self): return self.agpm_kext_folder / Path("Contents")
    @property
    def amc_kext_folder(self): return self.kexts_path / Path("AMC-Override.kext")
    @property
    def amc_contents_folder(self): return self.amc_kext_folder / Path("Contents")

    # Tools
    @property
    def macserial_path(self): return self.payload_path / Path("Tools/macserial")
    @property
    def gfxutil_path(self): return self.payload_path / Path("Tools/gfxutil")
    @property
    def vault_path(self): return self.payload_path / Path("Tools/CreateVault/sign.command")

    # Icons
    @property
    def app_icon_path(self): return self.current_path / Path("OC-Patcher.icns")
    @property
    def icon_path_external(self): return self.payload_path / Path("Icon/External/.VolumeIcon.icns")
    @property
    def icon_path_internal(self): return self.payload_path / Path("Icon/Internal/.VolumeIcon.icns")
    @property
    def icon_path_sd(self): return self.payload_path / Path("Icon/SD-Card/.VolumeIcon.icns")
    @property
    def icon_path_ssd(self): return self.payload_path / Path("Icon/SSD/.VolumeIcon.icns")
    @property
    def gui_path(self): return self.payload_path / Path("Icon/Resources.zip")

    # Apple Paylods Paths
    @property
    def payload_apple_root_path_unzip(self): return self.payload_path / Path(f"Apple-Binaries-OCLP-{self.payload_version}")
    @property
    def payload_apple_root_path_zip(self): return self.payload_path / Path("Apple.zip")
    @property
    def payload_apple_root_path(self): return self.payload_path / Path("Apple")
    @property
    def payload_apple_kexts_path(self): return self.payload_apple_root_path / Path("Extensions")
    @property
    def payload_apple_frameworks_path(self): return self.payload_apple_root_path / Path("Frameworks")
    @property
    def payload_apple_frameworks_path_accel(self): return self.payload_apple_frameworks_path / Path("Graphics-Acceleration")
    @property
    def payload_apple_lauchd_path(self): return self.payload_apple_root_path / Path("LaunchDaemons")
    @property
    def payload_apple_lauchd_path_accel(self): return self.payload_apple_lauchd_path / Path("Graphics-Acceleration")
    @property
    def payload_apple_private_frameworks_path(self): return self.payload_apple_root_path / Path("PrivateFrameworks")
    @property
    def payload_apple_private_frameworks_path_accel(self): return self.payload_apple_private_frameworks_path / Path("Graphics-Acceleration")
    @property
    def payload_apple_private_frameworks_path_brightness(self): return self.payload_apple_private_frameworks_path / Path("Brightness-Control")

    # Apple Extensions
    @property
    def applehda_path(self): return self.payload_apple_kexts_path / Path("Audio/AppleHDA.kext")

    # GPU Kexts and Bundles

    @property
    def legacy_graphics(self): return self.payload_apple_kexts_path / Path("Graphics-Acceleration")
    @property
    def legacy_nvidia_path(self): return self.legacy_graphics / Path("Nvidia-Tesla-Fermi")
    @property
    def legacy_amd_path(self): return self.legacy_graphics / Path("AMD-ATI")
    @property
    def legacy_intel_gen1_path(self): return self.legacy_graphics / Path("Intel-Gen5-Ironlake")
    @property
    def legacy_intel_gen2_path(self): return self.legacy_graphics / Path("Intel-Gen6-SandyBridge")

    @property
    def legacy_brightness(self): return self.payload_apple_kexts_path / Path("Brightness-Control")

    # Apple Frameworks
    @property
    def coredisplay_path(self): return self.payload_apple_frameworks_path_accel / Path("CoreDisplay.framework")
    @property
    def iosurface_f_path(self): return self.payload_apple_frameworks_path_accel / Path("IOSurface.framework")
    @property
    def opengl_path(self): return self.payload_apple_frameworks_path_accel / Path("OpenGL.framework")

    # Apple LaunchDaemons
    @property
    def hiddhack_path(self): return self.payload_apple_lauchd_path_accel / Path("IOHID-Fixup.plist")
    @property
    def legacy_hiddhack_path(self): return self.payload_apple_lauchd_path_accel / Path("HiddHack.plist")

    # Apple PrivateFrameworks
    @property
    def gpusupport_path(self): return self.payload_apple_private_frameworks_path_accel / Path("GPUSupport.framework")
    @property
    def skylight_path(self): return self.payload_apple_private_frameworks_path_accel / Path("SkyLight.framework")

    csr_values = {
        "CSR_ALLOW_UNTRUSTED_KEXTS           ": False,  # 0x1   - Introduced in El Capitan
        "CSR_ALLOW_UNRESTRICTED_FS           ": False,  # 0x2   - Introduced in El Capitan
        "CSR_ALLOW_TASK_FOR_PID              ": False,  # 0x4   - Introduced in El Capitan
        "CSR_ALLOW_KERNEL_DEBUGGER           ": False,  # 0x8   - Introduced in El Capitan
        "CSR_ALLOW_APPLE_INTERNAL            ": False,  # 0x10  - Introduced in El Capitan
        "CSR_ALLOW_UNRESTRICTED_DTRACE       ": False,  # 0x20  - Introduced in El Capitan
        "CSR_ALLOW_UNRESTRICTED_NVRAM        ": False,  # 0x40  - Introduced in El Capitan
        "CSR_ALLOW_DEVICE_CONFIGURATION      ": False,  # 0x80  - Introduced in El Capitan
        "CSR_ALLOW_ANY_RECOVERY_OS           ": False,  # 0x100 - Introduced in Sierra
        "CSR_ALLOW_UNAPPROVED_KEXTS          ": False,  # 0x200 - Introduced in High Sierra
        "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE": False,  # 0x400 - Introduced in Mojave
        "CSR_ALLOW_UNAUTHENTICATED_ROOT      ": False,  # 0x800 - Introduced in Big Sur
    }

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
