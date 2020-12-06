# Commands for building the EFI and SMBIOS

from __future__ import print_function

from shutil import copy
from shutil import rmtree
from distutils.dir_util import copy_tree

import os
import json
import subprocess
import sys
import zipfile

from Resources import Versions
from Resources import ModelArray

# Allow py2 and 3 support
try:
    input = raw_input
except NameError:
    pass

# Find SMBIOS of machine
opencore_model = subprocess.Popen(["NVRAM", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product"], stdout=subprocess.PIPE).communicate()[0]
if opencore_model not in ("NVRAM: Error getting variable - '4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product': (iokit/common) data was not found"):
    print("Detected OpenCore machine")
    opencore_model = subprocess.Popen("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product".split(), stdout=subprocess.PIPE)
    opencore_model = [line.strip().split(":oem-product	", 1)[1] for line in opencore_model.stdout.read().split("\n")  if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
    current_model = opencore_model
else:
    print("No OpenCore detected")
    current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
    current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]
    print("Current Model: %s" % current_model)

OCExist = False

def BuildEFI():
    
    if not os.path.exists(Versions.build_path):
        os.makedirs(Versions.build_path)
        print("Created Build Folder")
    else:
        print("Build Folder already present, skipping")
    # Copy OpenCore into Build Folder
    
    if os.path.exists(Versions.opencore_path_build):
        print("Deleting old copy of OpenCore zip")
        os.remove(Versions.opencore_path_build)
    if os.path.exists(Versions.opencore_path_done):
        print("Deleting old copy of OpenCore folder")
        rmtree(Versions.opencore_path_done)
    print("")
    print("- Adding OpenCore v%s" % Versions.opencore_version)
    copy(Versions.opencore_path, Versions.build_path)
    zipfile.ZipFile(Versions.opencore_path_build).extractall(Versions.build_path)

    print("- Adding config.plist v%s" % Versions.opencore_version)
    # Setup config.plist for editing
    copy(Versions.plist_path, Versions.plist_path_build)
    with open(Versions.plist_path_build_full, 'r') as file :
        Versions.plist_data = file.read()

    print("- Adding Lilu %s" % Versions.lilu_version)
    copy(Versions.lilu_path, Versions.kext_path_build)
    
    print("- Adding WhateverGreen %s" % Versions.whatevergreen_version)
    copy(Versions.whatevergreen_path, Versions.kext_path_build)
    
    # Checks for kexts
    # CPU Kext Patches
    if current_model in ModelArray.DualSocket:
        print("- Adding AppleMCEReporterDisabler v%s" % Versions.mce_version)
        copy(Versions.mce_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--AppleMCEReporterDisabler-->",
            "<true/><!--AppleMCEReporterDisabler-->"
        )
    
    if current_model in ModelArray.SSEEmulator:
        print("- Adding AAAMouSSE v%s" % Versions.mousse_version)
        copy(Versions.mousse_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--AAAMouSSE-->",
            "<true/><!--AAAMouSSE-->"
        )
    if current_model in ModelArray.MissingSSE42:
        print("- Adding telemetrap %s" % Versions.telemetrap_version)
        copy(Versions.telemetrap_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--telemetrap-->",
            "<true/><!--telemetrap-->"
        )
    
    # Ethernet Patches

    if current_model in ModelArray.EthernetNvidia:
        print("- Adding nForceEthernet v%s" % Versions.nforce_version)
        copy(Versions.nforce_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--nForceEthernet-->",
            "<true/><!--nForceEthernet-->"
        )
    if current_model in ModelArray.EthernetMarvell:
        print("- Adding MarvelYukonEthernet v%s" % Versions.marvel_version)
        copy(Versions.marvel_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--MarvelYukonEthernet-->",
            "<true/><!--MarvelYukonEthernet-->"
        )
    if current_model in ModelArray.EthernetBroadcom:
        print("- Adding CatalinaBCM5701Ethernet %s" % Versions.bcm570_version)
        copy(Versions.bcm570_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--CatalinaBCM5701Ethernet-->",
            "<true/><!--CatalinaBCM5701Ethernet-->"
        )
    
    # Wifi Patches

    if current_model in ModelArray.WifiAtheros:
        print("- Adding IO80211HighSierra v%s" % Versions.io80211high_sierra_version)
        copy(Versions.io80211high_sierra_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--IO80211HighSierra-->",
            "<true/><!--IO80211HighSierra-->"
        )
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--AirPortAtheros40-->",
            "<true/><!--AirPortAtheros40-->"
        )
    #if current_model in ModelArray.WifiBCM94328:
    #    print("- Wifi patches currently unsupported")
    #if current_model in ModelArray.WifiBCM94322:
    #    print("- Adding IO80211Mojave %s" % Versions.io80211mojave_version)
    #    copy(Versions.io80211mojave_path, Versions.kext_path_build)
    #    Versions.plist_data = Versions.plist_data.replace(
    #        "<false/><!--IO80211Mojave-->",
    #        "<true/><!--IO80211Mojave-->"
    #    )
    #    Versions.plist_data = Versions.plist_data.replace(
    #        "<false/><!--AirPortBrcm4331-->",
    #        "<true/><!--AirPortBrcm4331-->"
    #    )
    #if current_model in ModelArray.WifiBCM943224:
    #    print("- Adding IO80211Mojave %s" % Versions.io80211mojave_version)
    #    copy(Versions.io80211mojave_path, Versions.kext_path_build)
    #    Versions.plist_data = Versions.plist_data.replace(
    #        "<false/><!--IO80211Mojave-->",
    #        "<true/><!--IO80211Mojave-->"
    #    )
    #    Versions.plist_data = Versions.plist_data.replace(
    #        "<false/><!--AirPortBrcm4331-->",
    #        "<true/><!--AirPortBrcm4331-->"
    #    )
    if current_model in ModelArray.WifiBCM94331:
        print("- Adding AirportBrcmFixup and appling fake ID")
        copy(Versions.airportbcrmfixup_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--AirportBrcmFixup-->",
            "<true/><!--AirportBrcmFixup-->"
        )
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--AirPortBrcmNIC_Injector-->",
            "<true/><!--AirPortBrcmNIC_Injector-->"
        )
        if current_model in ModelArray.EthernetNvidia:
            # Nvidia chipsets all have the same path to ARPT
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            )
        if current_model in ("MacBookAir2,1", "MacBookAir3,1", "MacBookAir3,2" ):
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            )
        elif current_model in ("iMac7,1", "iMac8,1" ):
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)"
            )
        elif current_model in ("iMac13,1", "iMac13,2"):
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)"
            )
        elif current_model in ("MacPro5,1"):
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)"
            )
        else:
            # Assumes we have a laptop with Intel chipset
            Versions.plist_data = Versions.plist_data.replace(
                "#PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)",
                "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"
            )
    if current_model in ModelArray.LegacyHID:
        print("- Adding legacy IOHIDFamily Patch")
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--IOHIDFamily-->",
            "<true/><!--IOHIDFamily-->"
        )
    
    if current_model in ModelArray.LegacyAudio:
        print("- Adding VoodooHDA v%s" % Versions.voodoohda_version)
        copy(Versions.voodoohda_path, Versions.kext_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--VoodooHDA-->",
            "<true/><!--VoodooHDA-->"
        )
    
    if current_model in ModelArray.pciSSDT:
        print("- Adding SSDT-CPBG")
        copy(Versions.pci_ssdt_path, Versions.acpi_path_build)
        Versions.plist_data = Versions.plist_data.replace(
            "<false/><!--SSDT-CPBG-->",
            "<true/><!--SSDT-CPBG-->"
        )
    
    usb_map_path = os.path.join(Versions.current_path, "payloads/Kexts/Maps/Zip/" "USB-Map-%s.zip" % current_model)
    if os.path.exists(usb_map_path):
        print("- Adding USB Map for %s" % current_model)
        copy(usb_map_path, Versions.kext_path_build)
        map_name = ("USB-Map-%s.kext" % current_model)
        Versions.plist_data = Versions.plist_data.replace(
            "<<false/><!--USBmap-->",
            "<true/><!--USBmap-->"
        )
        Versions.plist_data = Versions.plist_data.replace(
            "USB-Map-SMBIOS.kext",
            map_name
        )
    
    if current_model in ModelArray.DualGPUPatch:
        print("- Adding dual GPU patch")
        Versions.plist_data = Versions.plist_data.replace(
            "debug=0x100",
            "debug=0x100 agdpmod=pikera"
        )


def BuildGUI():
    print("- Adding OpenCanopy GUI")
    rmtree(Versions.gui_path_build)
    copy(Versions.gui_path, Versions.plist_path_build)
    Versions.plist_data = Versions.plist_data.replace(
        "#OpenCanopy.efi",
        "OpenCanopy.efi"
    )

def BuildSMBIOS():
    # Set new SMBIOS
    new_model = current_model
    if current_model in ModelArray.MacBookAir61:
        print("- Spoofing to MacBookAir6,1")
        new_model = "MacBookAir6,1"
    elif current_model in ModelArray.MacBookAir62:
        print("- Spoofing to MacBookAir6,2")
        new_model = "MacBookAir6,2"
    elif current_model in ModelArray.MacBookPro111:
        print("- Spoofing to MacBookPro11,1")
        new_model = "MacBookPro11,1"
    elif current_model in ModelArray.MacBookPro112:
        print("- Spoofing to MacBookPro11,2")
        new_model = "MacBookPro11,2"
    elif current_model in ModelArray.Macmini71:
        print("- Spoofing to Macmini7,1")
        new_model = "Macmini7,1"
    elif current_model in ModelArray.iMac151:
        print("- Spoofing to iMac15,1")
        new_model = "iMac15,1"
    elif current_model in ModelArray.iMac144:
        print("- Spoofing to iMac14,4")
        new_model = "iMac14,4"
    elif current_model in ModelArray.MacPro71:
        print("- Spoofing to MacPro7,1")
        new_model = "MacPro7,1"

    # Grab serials from macserial
    serialPatch = subprocess.Popen(["xattr", "-cr", "./payloads/tools/macserial"], stdout=subprocess.PIPE).communicate()[0]
    print(serialPatch)
    serialData = subprocess.Popen((r"./payloads/tools/macserial -g -m " + new_model + " -n 1").split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    serialData = serialData.stdout.read().strip().split(" | ")

    # Patch SMBIOS
    Versions.plist_data = Versions.plist_data.replace(
        "iMac19,1",
        new_model
    )

    if serialData == "['']":
        # Used as a backup for when macserial fails
        print("Failed to load macserial")
    else:
        # Patch Number Serial
        Versions.plist_data = Versions.plist_data.replace(
            "W00000000001",
            serialData[0]
        )
        # Patch MLB
        Versions.plist_data = Versions.plist_data.replace(
            "M0000000000000001",
            serialData[1]
        )
        
    # Patch UUID
    uuidGen = subprocess.Popen(["uuidgen"], stdout=subprocess.PIPE).communicate()[0]
    Versions.plist_data = Versions.plist_data.replace(
        "00000000-0000-0000-0000-000000000000",
        uuidGen
    )

def SavePlist():
    with open(Versions.plist_path_build_full, 'w') as file:
        file.write(Versions.plist_data)

def CleanBuildFolder():
    # Clean up Build Folder
    print("")
    print("Cleaning build folder")
    os.chdir(Versions.kext_path_build)
    for item in os.listdir(Versions.kext_path_build):
        if item.endswith(".zip"):
            file_name = os.path.abspath(item)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(Versions.kext_path_build)
            zip_ref.close()
            os.remove(file_name)
    # Clean up Python's unzip
    if os.path.exists("__MACOSX"):
        rmtree("__MACOSX")
    os.chdir(Versions.plist_path_build)
    os.chdir(Versions.plist_path_build)
    for item in os.listdir(Versions.plist_path_build):
        if item.endswith(".zip"):
            file_name = os.path.abspath(item)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(Versions.plist_path_build)
            zip_ref.close()
            os.remove(file_name)
    if os.path.exists("__MACOSX"):
        rmtree("__MACOSX")
    os.chdir(Versions.build_path)
    if os.path.exists("__MACOSX"):
        rmtree("__MACOSX")
    os.remove(Versions.opencore_path_build)
    os.chdir(Versions.current_path)

def ListDiskutil():
    DiskMenu = True
    while DiskMenu:
        os.system('clear')
        print("Loading diskutil...(This may take some time)")
        diskList = subprocess.Popen(["diskutil", "list"], stdout=subprocess.PIPE).communicate()[0]
        print(diskList)
        ChosenDisk = input('Please select the disk you want to install OpenCore to(ie. disk1): ')
        ChosenDisk = ChosenDisk + "s1"
        print("Trying to mount %s" % ChosenDisk)
        diskMount = subprocess.Popen(["sudo", "diskutil", "mount", ChosenDisk], stdout=subprocess.PIPE).communicate()[0]
        print(diskMount)
        DiskMenu = input("Press any key to continue: ")

def MoveOpenCore():
    print("")
    efiVol = "/Volumes/EFI"
    if os.path.exists(efiVol):
        print("Coping OpenCore onto Volumes/EFI")
        if os.path.exists("/Volumes/EFI/EFI"):
            print("Cleaning EFI folder")
            rmtree("/Volumes/EFI/EFI")
        if os.path.exists(Versions.opencore_path_done):
            copy_tree(Versions.opencore_path_done, efiVol)
            copy(Versions.icon_path, efiVol)
            print("OpenCore transfer complete")
            print("")
    else:
        print("Couldn't find EFI partition")
        print("Please ensure your drive is formatted as GUID Partition Table")
        print("")

def MountOpenCore():
    subprocess.Popen((r"sudo diskutil mount $(nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:boot-path | sed 's/.*GPT,\([^,]*\),.*/\1/')").split())