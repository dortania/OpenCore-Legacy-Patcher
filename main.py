from __future__ import print_function
from shutil import copy
from shutil import rmtree

import os
import json
import subprocess
import sys
import zipfile

# Lists all models and required patches

SupportedSMBIOS = [
    # MacBook
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    # MacBook Air
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    # MacBook Pro
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro9,2",
    "MacBookPro10,1",
    "MacBookPro10,2",
    # Mac Mini
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2",
    # iMac
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "iMac13,1",
    "iMac13,2",
    "iMac14,1",
    "iMac14,2",
    "iMac14,3",
    # Mac Pro
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    # Xserve
    "Xserve3,1"
]

## CPU patches

MissingSSE42 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "MacPro3,1"
]

SSEEmulator = [
    "MacPro3,1"
]

DualSocket = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve3,1"
]

pciSSDT = [
    "MacBookPro6,1",
    "MacBookPro6,2",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3"
]

## Ethernet patches

EthernetNvidia = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac9,1",
    "iMac10,1"
]
EthernetMarvell = [
    "MacBookPro3,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1"
]
EthernetBroadcom = [
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2"
]

## Wifi patches

WifiAtheros = [
    "MacBookPro3,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "MacPro3,1",
    "MacPro4,1"
]

WifiBCM94328 = [
    "MacBookAir2,1",
    "MacBookPro4,1",
    "iMac7,1",
    "iMac8,1"

]

WifiBCM94322 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookAir5,1",
    "MacBookAir5,2",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
]

WifiBCM943224 = [
    "MacBook6,1",
    "MacBook7,1",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "Macmini3,1",
    "Macmini4,1",
]

WifiBCM94331 = [
    "MacBookPro8,1", # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro8,2", # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro8,3", # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro9,1", # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro9,2", # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro10,1",# PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "MacBookPro10,2",# PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "Macmini5,1",    # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "Macmini5,2",    # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "Macmini5,3",    # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "Macmini6,1",    # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "Macmini6,2",    # PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)
    "iMac13,1",      # PciRoot(0x0)/Pci(0x1C,0x3)Pci(0x0,0x0)
    "iMac13,2"       # PciRoot(0x0)/Pci(0x1C,0x3)Pci(0x0,0x0)
]

## Audio

LegacyAudio = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "MacPro3,1"
]

## GPU

LegacyGPU = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookAir3,2",
    "MacBookAir4,1",
    "MacBookAir4,2",
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2"
]

LegacyHID = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,1",
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro5,5",
    "MacBookPro7,1",
    "Macmini3,1",
    "Macmini4,1",
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
]

NVMePatch = [
    "MacPro3,1"
    "MacPro4,1"
    "Xserve3,1"
]

# 11" Air
MacBookAir61 = [
    "MacBookAir3,1",
    "MacBookAir4,1",
    "MacBookAir5,1"
]

# MacBook and 13" Air
MacBookAir62 = [
    "MacBook5,1",
    "MacBook5,2",
    "MacBook6,1",
    "MacBook7,1",
    "MacBookAir2,1",
    "MacBookAir3,2",
    "MacBookAir4,2",
    "MacBookAir5,2"
]

# MacBook Pro 13"

MacBookPro111 = [
    "MacBookPro5,5",
    "MacBookPro7,1",
    "MacBookPro8,1",
    "MacBookPro9,2",
    "MacBookPro10,2",
]

# MacBook Pro 15" and 17"

MacBookPro112 = [
    "MacBookPro3,1",
    "MacBookPro4,1",
    "MacBookPro5,1",
    "MacBookPro5,2",
    "MacBookPro5,3",
    "MacBookPro5,4",
    "MacBookPro6,1",
    "MacBookPro6,2",
    "MacBookPro8,2",
    "MacBookPro8,3",
    "MacBookPro9,1",
    "MacBookPro10,1",
]

# Mac Mini

Macmini71 = [
    "Macmini3,1",
    "Macmini4,1",
    "Macmini5,1",
    "Macmini5,2",
    "Macmini5,3",
    "Macmini6,1",
    "Macmini6,2"
]

# iMac = AMD and Nvidia GPU
iMac151 = [
    "iMac7,1",
    "iMac8,1",
    "iMac9,1",
    "iMac10,1",
    "iMac11,1",
    "iMac11,2",
    "iMac11,3",
    "iMac12,1",
    "iMac12,2",
    "iMac13,2",
    "iMac14,2",
    "iMac14,3"
]
# iMac = Intel iGPU
iMac144 = [
    "iMac13,1",
    "iMac14,1"
]

# Mac Pro and Xserve

MacPro71 = [
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve3,1"
]

# List build versions
patcher_version = "0.0.1"
opencore_version = "0.6.3"
lilu_version = "1.4.9"
whatevergreen_version = "1.4.4"
airportbcrmfixup_version = "2.1.1"
bcm570_version = "1.0.0"
marvel_version = "1.0.0"
nforce_version = "1.0.0"
mce_version = "1.0.0"
mousse_version = "0.93"
telemetrap_version = "1.0.0"
io80211high_sierra_version = "1.0.0"
io80211mojave_version = "1.0.0"

# Setup file locations
current_path = os.getcwd()

# Payload Location
# OpenCore
opencore_path = os.path.join(current_path, "payloads/OpenCore/" "OpenCore-v%s.zip" % opencore_version)
plist_path = os.path.join(current_path, "payloads/Config/v%s/" "config.plist" % opencore_version)

# ACPI
pci_ssdt_path = os.path.join(current_path, "payloads/ACPI/" "SSDT-CPBG.aml")

# Drivers
nvme_driver_path = os.path.join(current_path, "payloads/Drivers/" "NvmExpressDxe.efi")

# Kexts
lilu_path = os.path.join(current_path, "payloads/Kexts/Acidanthera/" "Lilu-v%s.zip" % lilu_version)
whatevergreen_path = os.path.join(current_path, "payloads/Kexts/Acidanthera/" "WhateverGreen-v%s.zip" % whatevergreen_version)
airportbcrmfixup_path = os.path.join(current_path, "payloads/Kexts/Acidanthera/" "AirportBrcmFixup-v%s.zip" % airportbcrmfixup_version)
bcm570_path = os.path.join(current_path, "payloads/Kexts/Ethernet/" "CatalinaBCM5701Ethernet-v%s.zip" % bcm570_version)
marvel_path = os.path.join(current_path, "payloads/Kexts/Ethernet/" "MarvelYukonEthernet-v%s.zip" % marvel_version)
nforce_path = os.path.join(current_path, "payloads/Kexts/Ethernet/" "nForceEthernet-v%s.zip" % nforce_version)
mce_path = os.path.join(current_path, "payloads/Kexts/Misc/" "AppleMCEReporterDisabler-v%s.zip" % mce_version)
mousse_path = os.path.join(current_path, "payloads/Kexts/SSE/" "AAAMouSSE-v%s.zip" % mousse_version)
telemetrap_path = os.path.join(current_path, "payloads/Kexts/SSE/" "telemetrap-v%s.zip" % telemetrap_version)
io80211high_sierra_path = os.path.join(current_path, "payloads/Kexts/Wifi/" "IO80211HighSierra-v%s.zip" % io80211high_sierra_version)
io80211mojave_path = os.path.join(current_path, "payloads/Kexts/Wifi/" "IO80211Mojave-v%s.zip" % io80211mojave_version)

# Build Location
opencore_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s.zip" % opencore_version)
plist_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/" % opencore_version)
plist_path_build_full = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/config.plist" % opencore_version)
acpi_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/ACPI" % opencore_version)
drivers_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/Drivers" % opencore_version)
kext_path_build = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s/EFI/OC/Kexts" % opencore_version)
opencore_path_done = os.path.join(current_path, "Build-Folder/" "OpenCore-v%s" % opencore_version)

# Tools
macserial_path = os.path.join(current_path, "payloads/" "Tools")

# Load models.json
#models = json.load(open("models.json"))

# Find SMBIOS of machine
current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]

CustomSMBIOS=False
patches = None
MainMenu=True

while MainMenu:
    os.system('clear')

    print("###################################################")
    print("        OpenCore Legacy patcher v%s" % patcher_version)
    print("           Current Model: %s" % current_model)
    print("###################################################")
    print("")
    if current_model not in SupportedSMBIOS:
        print("   Your model is not supported by this patcher!")
        print("")
        print(" If you plan to create the USB for another machine,")
        print("            please select option 5")
        print("---------------------------------------------------")
        print("")
    elif current_model in ("MacPro3,1", "iMac7,1"):
        print("           This model is supported")
        print(" However please ensure the CPU have been upgraded")
        print("             to support SSE4.1+")
        print("---------------------------------------------------")
        print("")
    else:
        print("            This model is supported")
        print("---------------------------------------------------")
        print("")
    print("    1.  Build OpenCore")
    print("    2.  Create macOS Installer              - Not yet implemented")
    print("    3.  Install OpenCore to USB drive       - Not yet implemented")
    print("    4.  Install OpenCore to internal drive  - Not yet implemented")
    print("    5.  Change model")
    print("    6.  Credits")
    print("    7.  Exit")
    print("")

    MainMenu = raw_input('Please select an option: ')

    if MainMenu=="1":
        OpenCoreBuilderMenu=True
        while OpenCoreBuilderMenu:
            os.system('clear')

            print("#######################################################")
            print("        Build OpenCore for model: %s" % current_model)
            print("#######################################################")
            print("")
            print("   1.  Auto build OpenCore")
            print("      - This script determines what patches you require")
            print("      - Recommended for novices")
            print("   2.  Return to main menu")
            print("")

            OpenCoreBuilderMenu = raw_input('Please select an option: ')

            if OpenCoreBuilderMenu=="1":
                AutoBuilderMenu=True
                while AutoBuilderMenu:
                    os.system('clear')
                    print("#######################################################")
                    print("      Building OpenCore for model: %s" % current_model)
                    print("#######################################################")
                    print("")
                    print("The current working directory:")
                    print ("    %s" % current_path)
                    print("")
                    build_path = os.path.join(current_path, r'Build-Folder/')
                    if not os.path.exists(build_path):
                        os.makedirs(build_path)
                        print("Created Build Folder")
                    else:
                        print("Build Folder already present, skipping")
                    # Copy OpenCore into Build Folder
                    
                    if os.path.exists(opencore_path_build):
                        print("Deleting old copy of OpenCore zip")
                        os.remove(opencore_path_build)
                    if os.path.exists(opencore_path_done):
                        print("Deleting old copy of OpenCore folder")
                        rmtree(opencore_path_done)
                    print("")
                    print("- Adding OpenCore v%s" % opencore_version)
                    copy(opencore_path, build_path)
                    zipfile.ZipFile(opencore_path_build).extractall(build_path)

                    print("- Adding config.plist v%s" % opencore_version)
                    # Setup config.plist for editing
                    copy(plist_path, plist_path_build)
                    with open(plist_path_build_full, 'r') as file :
                        plist_data = file.read()

                    print("- Adding Lilu %s" % lilu_version)
                    copy(lilu_path, kext_path_build)
                    print("- Adding WhateverGreen %s" % whatevergreen_version)
                    copy(whatevergreen_path, kext_path_build)
                    
                    # Checks for kexts
                    # CPU Kext Patches
                    if current_model in DualSocket:
                        print("- Adding AppleMCEReporterDisabler v%s" % mce_version)
                        copy(mce_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--AppleMCEReporterDisabler-->",
                            "<true/><!--AppleMCEReporterDisabler-->"
                        )
                    
                    if current_model in SSEEmulator:
                        print("- Adding AAAMouSSE v%s" % mousse_version)
                        copy(mousse_version, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--AAAMouSSE-->",
                            "<true/><!--AAAMouSSE-->"
                        )
                    if current_model in MissingSSE42:
                        print("- Adding telemetrap %s" % telemetrap_version)
                        copy(telemetrap_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--telemetrap-->",
                            "<true/><!--telemetrap-->"
                        )
                    
                    # Ethernet Patches

                    if current_model in EthernetNvidia:
                        print("- Adding nForceEthernet v%s" % nforce_version)
                        copy(nforce_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--nForceEthernet-->",
                            "<true/><!--nForceEthernet-->"
                        )
                    if current_model in EthernetMarvell:
                        print("- Adding MarvelYukonEthernet v%s" % marvel_version)
                        copy(marvel_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--MarvelYukonEthernet-->",
                            "<true/><!--MarvelYukonEthernet-->"
                        )
                    if current_model in EthernetBroadcom:
                        print("- Adding CatalinaBCM5701Ethernet %s" % bcm570_version)
                        copy(bcm570_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--CatalinaBCM5701Ethernet-->",
                            "<true/><!--CatalinaBCM5701Ethernet-->"
                        )
                    
                    # Wifi Patches

                    if current_model in WifiAtheros:
                        print("- Adding IO80211HighSierra v%s" % io80211high_sierra_version)
                        copy(io80211high_sierra_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--IO80211HighSierra-->",
                            "<true/><!--IO80211HighSierra-->"
                        )
                        plist_data = plist_data.replace(
                            "<false/><!--AirPortAtheros40-->",
                            "<true/><!--AirPortAtheros40-->"
                        )
                    if current_model in WifiBCM94328:
                        print("- Wifi patches currently unsupported")
                        # TO-DO: Add El Capitan's IO80211
                    if current_model in WifiBCM94322:
                        print("- Adding IO80211Mojave %s" % io80211mojave_version)
                        copy(io80211mojave_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--IO80211Mojave-->",
                            "<true/><!--IO80211Mojave-->"
                        )
                        plist_data = plist_data.replace(
                            "<false/><!--AirPortBrcm4331-->",
                            "<true/><!--AirPortBrcm4331-->"
                        )
                    if current_model in WifiBCM943224:
                        print("- Adding IO80211Mojave %s" % io80211mojave_version)
                        copy(io80211mojave_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--IO80211Mojave-->",
                            "<true/><!--IO80211Mojave-->"
                        )
                        plist_data = plist_data.replace(
                            "<false/><!--AirPortBrcm4331-->",
                            "<true/><!--AirPortBrcm4331-->"
                        )
                    if current_model in WifiBCM94331:
                        print("- Adding AirportBrcmFixup and appling fake ID")
                        copy(airportbcrmfixup_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--AirportBrcmFixup-->",
                            "<true/><!--AirportBrcmFixup-->"
                        )
                        plist_data = plist_data.replace(
                            "<false/><!--AirPortBrcmNIC_Injector-->",
                            "<true/><!--AirPortBrcmNIC_Injector-->"
                        )
                        if current_model in ("iMac13,1", "iMac13,2"):
                            plist_data = plist_data.replace(
                                "#PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)",
                                "PciRoot(0x0)/Pci(0x1C,0x3)Pci(0x0,0x0)"
                            )
                        else:
                            plist_data = plist_data.replace(
                                "#PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)",
                                "PciRoot(0x0)/Pci(0x1C,0x1)Pci(0x0,0x0)"
                            )

                    # Checks for ACPI
                    # Add SSDTs
                    if current_model in pciSSDT:
                        print("- Adding SSDT-CPBG.aml")
                        copy(pci_ssdt_path, acpi_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--SSDT-CPBG-->",
                            "<true/><!--SSDT-CPBG-->"
                        )

                    # Check for Kernel Patches
                    if current_model in LegacyHID:
                        print("- Adding IOHIDFamily Patch")
                        copy(pci_ssdt_path, acpi_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--IOHIDFamily-->",
                            "<true/><!--IOHIDFamily-->"
                        )

                    # Check for EFI Drivers
                    if current_model in NVMePatch:
                        print("- Adding NVMe support")
                        copy(nvme_driver_path, drivers_path_build)
                        plist_data = plist_data.replace(
                            "<string>#NvmExpressDxe.efi</string>",
                            "<string>NvmExpressDxe.efi</string>"
                        )
                    
                    # Add new SMBIOS data
                    if current_model in MacBookAir61:
                        print("- Spoofing to MacBookAir6,1")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "MacBookAir6,1"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in MacBookAir62:
                        print("- Spoofing to MacBookAir6,2")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "MacBookAir6,2"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in MacBookPro111:
                        print("- Spoofing to MacBookPro11,1")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "MacBookPro11,1"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in MacBookPro112:
                        print("- Spoofing to MacBookPro11,2")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "MacBookPro11,2"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in Macmini71:
                        print("- Spoofing to Macmini7,1")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            " Macmini7,1"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in iMac151:
                        print("- Spoofing to iMac15,1")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "iMac15,1"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in iMac144:
                        print("- Spoofing to iMac14,4")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "iMac14,4"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                    if current_model in MacPro71:
                        print("- Spoofing to MacPro7,1")
                        # Patch SMBIOS
                        
                        plist_data = plist_data.replace(
                            "iMac19,1",
                            "MacPro7,1"
                        )
                        # Patch Number Serial
                        plist_data = plist_data.replace(
                            "W00000000001",
                            "Dortania-SN"
                        )
                        # Patch MLB
                        plist_data = plist_data.replace(
                            "M0000000000000001",
                            "Dortania-MLB"
                        )
                        
                    # Patch UUID
                    uuidGen = subprocess.Popen(["uuidgen"], stdout=subprocess.PIPE).communicate()[0]
                    plist_data = plist_data.replace(
                        "00000000-0000-0000-0000-000000000000",
                        uuidGen
                    )

                    # Save config.plist changes in memory
                    with open(plist_path_build_full, 'w') as file:
                        file.write(plist_data)
                    
                    # Clean up Build Folder
                    print("")
                    print("Cleaning build folder")
                    os.chdir(kext_path_build)
                    extension = ".zip"
                    for item in os.listdir(kext_path_build): # loop through items in dir
                        if item.endswith(extension): # check for ".zip" extension
                            file_name = os.path.abspath(item) # get full path of files
                            zip_ref = zipfile.ZipFile(file_name) # create zipfile object
                            zip_ref.extractall(kext_path_build) # extract file to dir
                            zip_ref.close() # close file
                            os.remove(file_name) # delete zipped file
                    rmtree("__MACOSX")
                    os.chdir(build_path)
                    rmtree("__MACOSX")
                    os.remove(opencore_path_build)
                    os.chdir(current_path)
                    print("")
                    print("Your OpenCore EFI has been built at:")
                    print("    %s" % opencore_path_done)
                    print("")
                    AutoBuilderMenu = raw_input("Press any key to return to previous menu: ")
                    if AutoBuilderMenu=="1":
                        print("Returning to previous menu...")
                        AutoBuilderMenu=False
                        OpenCoreBuilderMenu=False

            elif OpenCoreBuilderMenu=="2":
                print("\n Returning to main menu...")
                OpenCoreBuilderMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")


    if MainMenu=="2":
        macOSInstallerMenu=True
        while macOSInstallerMenu:
            os.system('clear')

            print("#######################################################")
            print("        Create macOS Installer")
            print("#######################################################")
            print("")
            print("  Supported OSes:")
            print("")
            print("   1.  macOS 11, Big Sur     - Not yet implemented")
            print("   2.  Return to main menu")
            print("")

            macOSInstallerMenu = raw_input('Please select an option: ')

            if macOSInstallerMenu=="1":
                print("\n Not yet implemented")
            elif macOSInstallerMenu=="2":
                print("\n Returning to main menu...")
                macOSInstallerMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")
            
    elif MainMenu=="3":
        print("\n Not yet implemented") 
    elif MainMenu=="4":
        print("\n Not yet implemented")
    elif MainMenu=="5":
        SMBIOSMenu=True
        while SMBIOSMenu:
            os.system('clear')

            print("#######################################################")
            print("        Enter a new SMBIOS")
            print("#######################################################")
            print("")
            print("  Tip: Run this command on the machine to find the SMBIOS")
            print("")
            print("  system_profiler SPHardwareDataType | grep 'Model Identifier'")
            print("")
            SMBIOSOption = raw_input('Please enter the SMBIOS of your machine: ')
            print("")
            print("  New SMBIOS: %s" % SMBIOSOption)
            print("")
            SMBIOSMenuYN = raw_input("Is this correcy?(y/n)")
            if SMBIOSMenuYN in {"y", "Y", "yes", "Yes"}:
                SMBIOSMenu=False
                current_model = SMBIOSOption
                MainMenu=True
                # Set variabel to show we're not patching the system
                # Ensures we don't use logic for determining the Wifi card model
                CustomSMBIOS=True
    elif MainMenu=="6":
        CreditMenu=True
        while CreditMenu:
            os.system('clear')

            print("#######################################################")
            print("                    Credits")
            print("#######################################################")
            print("")
            print(" Many thanks to the following:")
            print("")
            print("  - Acidanthera:  OpenCore, kexts and other tools")
            print("  - DhinakG:      Writing and maintaining this Patcher")
            print("  - Khronokernel: Writing and maintaining this Patcher")
            print("  - Syncretic:    AAAMouSSE and telemetrap")
            print("")
            CreditMenu = raw_input(" Press any key to exit: ")
            if CreditMenu=="1":
                print("Returning to main menu...")
                CreditMenu=False
                MainMenu=True

    elif MainMenu=="7":
        print("\n Closing program...")
        sys.exit(1) 
    else:
        print("\n Not Valid Choice Try again") 
