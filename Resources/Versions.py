# Define Files

from __future__ import print_function

from shutil import copy
from shutil import rmtree

import os
import json
import subprocess
import sys
from pathlib import Path

# List build versions
opencore_version = "0.6.6"
lilu_version = "1.5.0"
whatevergreen_version = "1.4.6"
airportbcrmfixup_version = "2.1.2"
bcm570_version = "1.0.0"
marvel_version = "1.0.0"
nforce_version = "1.0.0"
mce_version = "1.0.0"
mousse_version = "0.93"
telemetrap_version = "1.0.0"
io80211high_sierra_version = "1.0.0"
io80211mojave_version = "1.0.0"
voodoohda_version = "296"
restrictevents_version = "1.0.0"

# List current location
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")
resource_path = os.getcwd()
current_path = Path(sys.executable).parent

# Payload Location
# OpenCore
opencore_path = os.path.join(resource_path, "payloads/OpenCore/" "OpenCore-v%s.zip" % opencore_version)
plist_path = os.path.join(resource_path, "payloads/Config/v%s/" "config.plist" % opencore_version)

# ACPI
pci_ssdt_path = os.path.join(resource_path, "payloads/ACPI/" "SSDT-CPBG.aml")

# Drivers
nvme_driver_path = os.path.join(resource_path, "payloads/Drivers/" "NvmExpressDxe.efi")

# Kexts
lilu_path = os.path.join(resource_path, "payloads/Kexts/Acidanthera/" "Lilu-v%s.zip" % lilu_version)
whatevergreen_path = os.path.join(resource_path, "payloads/Kexts/Acidanthera/" "WhateverGreen-v%s.zip" % whatevergreen_version)
airportbcrmfixup_path = os.path.join(resource_path, "payloads/Kexts/Acidanthera/" "AirportBrcmFixup-v%s.zip" % airportbcrmfixup_version)
restrictevents_path = os.path.join(resource_path, "payloads/Kexts/Acidanthera/" "RestrictEvents-v%s.zip" % restrictevents_version)
bcm570_path = os.path.join(resource_path, "payloads/Kexts/Ethernet/" "CatalinaBCM5701Ethernet-v%s.zip" % bcm570_version)
marvel_path = os.path.join(resource_path, "payloads/Kexts/Ethernet/" "MarvelYukonEthernet-v%s.zip" % marvel_version)
nforce_path = os.path.join(resource_path, "payloads/Kexts/Ethernet/" "nForceEthernet-v%s.zip" % nforce_version)
mce_path = os.path.join(resource_path, "payloads/Kexts/Misc/" "AppleMCEReporterDisabler-v%s.zip" % mce_version)
mousse_path = os.path.join(resource_path, "payloads/Kexts/SSE/" "AAAMouSSE-v%s.zip" % mousse_version)
telemetrap_path = os.path.join(resource_path, "payloads/Kexts/SSE/" "telemetrap-v%s.zip" % telemetrap_version)
io80211high_sierra_path = os.path.join(resource_path, "payloads/Kexts/Wifi/" "IO80211HighSierra-v%s.zip" % io80211high_sierra_version)
io80211mojave_path = os.path.join(resource_path, "payloads/Kexts/Wifi/" "IO80211Mojave-v%s.zip" % io80211mojave_version)
voodoohda_path = os.path.join(resource_path, "payloads/Kexts/Audio/" "VoodooHDA-v%s.zip" % voodoohda_version)

# Build Location
opencore_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s.zip" % opencore_version)
plist_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/" % opencore_version)
plist_path_build_full = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/config.plist" % opencore_version)
acpi_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/ACPI" % opencore_version)
drivers_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/Drivers" % opencore_version)
kext_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/Kexts" % opencore_version)
opencore_path_done = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s" % opencore_version)
build_path = os.path.join(current_path, "Build-Folder/")
gui_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/Resources" % opencore_version)

# Tools
macserial_path = os.path.join(resource_path, "payloads/" "Tools")

# Icons
app_icon_path = os.path.join(resource_path, "OC-Patcher.icns")
icon_path = os.path.join(resource_path, "payloads/Icon/" ".VolumeIcon.icns")
gui_path = os.path.join(resource_path, "payloads/Icon/" "Resources.zip")
