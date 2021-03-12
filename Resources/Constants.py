# pylint: disable=multiple-statements
# Define Files

from __future__ import print_function

from pathlib import Path


class Constants:
    def __init__(self):
        self.patcher_version = "0.0.18"
        self.opencore_commit = "7bb41aa - 2021-03-06"
        self.opencore_version = "0.6.8"
        self.lilu_version = "1.5.1"
        self.whatevergreen_version = "1.4.8"
        self.airportbcrmfixup_version = "2.1.2"
        self.bcm570_version = "1.0.0"
        self.marvel_version = "1.0.0"
        self.nforce_version = "1.0.0"
        self.mce_version = "1.0.0"
        self.mousse_version = "0.93"
        self.telemetrap_version = "1.0.0"
        self.io80211high_sierra_version = "1.0.0"
        self.io80211mojave_version = "1.0.0"
        self.voodoohda_version = "296"
        self.restrictevents_version = "1.0.0"
        self.piixata_version = "1.0.0"
        self.backlight_version = "1.0.0"
        self.cpufriend_version = "1.2.3"
        self.nightshift_version = "1.1.0"

        # Get resource path
        self.current_path = Path(__file__).parent.parent.resolve()
        self.payload_path = self.current_path / Path("payloads")

        self.custom_model: str = None
        self.custom_mxm_gpu: str = None
        self.current_gpuv: str = None
        self.current_gpud: str = None

        # Patcher Settings
        self.opencore_debug = False
        self.opencore_build = "RELEASE"
        self.kext_debug = False
        self.verbose_debug = True
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
        self.detected_os = 0.0

    # Payload Location
    # OpenCore
    @property
    def opencore_zip_source(self): return self.payload_path / Path(f"OpenCore/OpenCore-{self.opencore_build}-v{self.opencore_version}.zip")
    @property
    def plist_template(self): return self.payload_path / Path(f"Config/v{self.opencore_version}/config.plist")

    # ACPI
    @property
    def pci_ssdt_path(self): return self.payload_path / Path("ACPI/SSDT-CPBG.aml")

    # Drivers
    @property
    def nvme_driver_path(self): return self.payload_path / Path("Drivers/NvmExpressDxe.efi")

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
    def io80211high_sierra_path(self): return self.payload_kexts_path / Path(f"Wifi/IO80211HighSierra-v{self.io80211high_sierra_version}.zip")
    @property
    def io80211mojave_path(self): return self.payload_kexts_path / Path(f"Wifi/IO80211Mojave-v{self.io80211mojave_version}.zip")
    @property
    def voodoohda_path(self): return self.payload_kexts_path / Path(f"Audio/VoodooHDA-v{self.voodoohda_version}.zip")
    @property
    def piixata_path(self): return self.payload_kexts_path / Path(f"Misc/AppleIntelPIIXATA-v{self.piixata_version}.zip")
    @property
    def backlight_path(self): return self.payload_kexts_path / Path(f"Misc/AppleBacklightFixup-v{self.backlight_version}.zip")
    @property
    def cpufriend_path(self): return self.payload_kexts_path / Path(f"Acidanthera/CPUFriend-v{self.cpufriend_version}.zip")
    @property
    def nightshift_path(self): return self.payload_kexts_path / Path(f"Misc/NightShiftEnabler-v{self.nightshift_version}.zip")

    # Build Location
    @property
    def build_path(self): return self.current_path / Path("Build-Folder/")
    @property
    def opencore_release_folder(self): return self.build_path / Path(f"OpenCore-{self.opencore_build}-v{self.opencore_version}")
    @property
    def opencore_zip_copied(self): return self.build_path / Path(f"OpenCore-{self.opencore_build}-v{self.opencore_version}.zip")

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

    # Tools
    @property
    def macserial_path(self): return self.payload_path / Path("Tools/macserial")
    @property
    def vault_path(self): return self.payload_path / Path("Tools/CreateVault/sign.command")

    # Icons
    @property
    def app_icon_path(self): return self.current_path / Path("OC-Patcher.icns")
    @property
    def icon_path(self): return self.payload_path / Path("Icon/.VolumeIcon.icns")
    @property
    def gui_path(self): return self.payload_path / Path("Icon/Resources.zip")
