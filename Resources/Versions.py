# Define Files

from __future__ import print_function

from shutil import copy
from shutil import rmtree

import os
import json
import subprocess
import sys
from pathlib import Path


class Versions:
    def __init__(self):
        self.default_opencore_version = "0.6.6"
        self.opencore_version = "0.6.6"
        self.available_opencore_versions = ["0.6.6"]
        self.lilu_version = "1.5.0"
        self.whatevergreen_version = "1.4.6"
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

        # Get resource path
        self.current_path = Path(__file__).parent.parent.resolve()
        self.payload_path = self.current_path / Path("payloads")

    # Payload Location
    # OpenCore
    @property
    def opencore_path(self): return self.current_path / Path(f"payloads/OpenCore/OpenCore-v{self.opencore_version}.zip")
    @property
    def plist_path(self): return self.current_path / Path(f"payloads/Config/v{self.opencore_version}/config.plist")

    # ACPI
    @property
    def pci_ssdt_path(self): return self.current_path / Path("payloads/ACPI/SSDT-CPBG.aml")

    # Drivers
    @property
    def nvme_driver_path(self): return self.current_path / Path("payloads/Drivers/NvmExpressDxe.efi")

    # Kexts
    @property
    def lilu_path(self): return self.current_path / Path(f"payloads/Kexts/Acidanthera/Lilu-v{self.lilu_version}.zip")
    @property
    def whatevergreen_path(self): return self.current_path / Path(f"payloads/Kexts/Acidanthera/WhateverGreen-v{self.whatevergreen_version}.zip")
    @property
    def airportbcrmfixup_path(self): return self.current_path / Path(f"payloads/Kexts/Acidanthera/AirportBrcmFixup-v{self.airportbcrmfixup_version}.zip")
    @property
    def restrictevents_path(self): return self.current_path / Path(f"payloads/Kexts/Acidanthera/RestrictEvents-v{self.restrictevents_version}.zip")
    @property
    def bcm570_path(self): return self.current_path / Path(f"payloads/Kexts/Ethernet/CatalinaBCM5701Ethernet-v{self.bcm570_version}.zip")
    @property
    def marvel_path(self): return self.current_path / Path(f"payloads/Kexts/Ethernet/MarvelYukonEthernet-v{self.marvel_version}.zip")
    @property
    def nforce_path(self): return self.current_path / Path(f"payloads/Kexts/Ethernet/nForceEthernet-v{self.nforce_version}.zip")
    @property
    def mce_path(self): return self.current_path / Path(f"payloads/Kexts/Misc/AppleMCEReporterDisabler-v{self.mce_version}.zip")
    @property
    def mousse_path(self): return self.current_path / Path(f"payloads/Kexts/SSE/AAAMouSSE-v{self.mousse_version}.zip")
    @property
    def telemetrap_path(self): return self.current_path / Path(f"payloads/Kexts/SSE/telemetrap-v{self.telemetrap_version}.zip")
    @property
    def io80211high_sierra_path(self): return self.current_path / Path(f"payloads/Kexts/Wifi/IO80211HighSierra-v{self.io80211high_sierra_version}.zip")
    @property
    def io80211mojave_path(self): return self.current_path / Path(f"payloads/Kexts/Wifi/IO80211Mojave-v{self.io80211mojave_version}.zip")
    @property
    def voodoohda_path(self): return self.current_path / Path(f"payloads/Kexts/Audio/VoodooHDA-v{self.voodoohda_version}.zip")

    # Build Location
    @property
    def opencore_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}.zip")
    @property
    def plist_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/")
    @property
    def plist_path_build_full(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/config.plist")
    @property
    def acpi_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/ACPI")
    @property
    def drivers_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/Drivers")
    @property
    def kext_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/Kexts")
    @property
    def opencore_path_done(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}")
    @property
    def build_path(self): return self.current_path / Path("Build-Folder/")
    @property
    def gui_path_build(self): return self.current_path / Path(f"Build-Folder/OpenCore-v{self.opencore_version}/EFI/OC/Resources")

    # Tools
    @property
    def macserial_path(self): return self.current_path / Path("payloads/Tools")

    # Icons
    @property
    def app_icon_path(self): return self.current_path / Path("OC-Patcher.icns")
    @property
    def icon_path(self): return self.current_path / Path(f"payloads/Icon/.VolumeIcon.icns")
    @property
    def gui_path(self): return self.current_path / Path(f"payloads/Icon/Resources.zip")
