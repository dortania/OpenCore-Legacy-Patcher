#!/usr/bin/env python
from __future__ import print_function

from shutil import copy
from shutil import rmtree

import os
import json
import subprocess
import sys
import zipfile

from Resources import *

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

# Find SMBIOS of machine
current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]

CustomSMBIOS=False
MainMenu=True

while MainMenu:
    os.system('clear')

    print("###################################################")
    print("        OpenCore Legacy patcher v%s" % patcher_version)
    print("           Current Model: %s" % current_model)
    print("###################################################")
    print("")
    if current_model not in ModelArray.SupportedSMBIOS:
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
    print("    2.  Create macOS Installer                  - Not yet implemented")
    print("    3.  Install OpenCore to USB/internal drive  - Not yet implemented")
    print("    4.  Change model")
    print("    5.  Credits")
    print("    6.  Exit")
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
                    if current_model in ModelArray.DualSocket:
                        print("- Adding AppleMCEReporterDisabler v%s" % mce_version)
                        copy(mce_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--AppleMCEReporterDisabler-->",
                            "<true/><!--AppleMCEReporterDisabler-->"
                        )
                    
                    if current_model in ModelArray.SSEEmulator:
                        print("- Adding AAAMouSSE v%s" % mousse_version)
                        copy(mousse_version, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--AAAMouSSE-->",
                            "<true/><!--AAAMouSSE-->"
                        )
                    if current_model in ModelArray.MissingSSE42:
                        print("- Adding telemetrap %s" % telemetrap_version)
                        copy(telemetrap_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--telemetrap-->",
                            "<true/><!--telemetrap-->"
                        )
                    
                    # Ethernet Patches

                    if current_model in ModelArray.EthernetNvidia:
                        print("- Adding nForceEthernet v%s" % nforce_version)
                        copy(nforce_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--nForceEthernet-->",
                            "<true/><!--nForceEthernet-->"
                        )
                    if current_model in ModelArray.EthernetMarvell:
                        print("- Adding MarvelYukonEthernet v%s" % marvel_version)
                        copy(marvel_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--MarvelYukonEthernet-->",
                            "<true/><!--MarvelYukonEthernet-->"
                        )
                    if current_model in ModelArray.EthernetBroadcom:
                        print("- Adding CatalinaBCM5701Ethernet %s" % bcm570_version)
                        copy(bcm570_path, kext_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--CatalinaBCM5701Ethernet-->",
                            "<true/><!--CatalinaBCM5701Ethernet-->"
                        )
                    
                    # Wifi Patches

                    if current_model in ModelArray.WifiAtheros:
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
                    if current_model in ModelArray.WifiBCM94328:
                        print("- Wifi patches currently unsupported")
                        # TO-DO: Add El Capitan's IO80211
                    if current_model in ModelArray.WifiBCM94322:
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
                    if current_model in ModelArray.WifiBCM943224:
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
                    if current_model in ModelArray.WifiBCM94331:
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
                    
                    
                    usb_map_path = os.path.join(current_path, "payloads/Kexts/Maps/Zip/" "USB-Map-%s.zip" % current_model)
                    if os.path.exists(usb_map_path):
                        print("- Adding USB Map for %s" % current_model)
                        copy(usb_map_path, kext_path_build)
                        map_name = ("USB-Map-%s.kext" % current_model)
                        plist_data = plist_data.replace(
                            "USB-Map-SMBIOS.kext",
                            map_name
                        )
                    

                    # Checks for ACPI
                    # Add SSDTs
                    if current_model in ModelArray.pciSSDT:
                        print("- Adding SSDT-CPBG.aml")
                        copy(pci_ssdt_path, acpi_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--SSDT-CPBG-->",
                            "<true/><!--SSDT-CPBG-->"
                        )

                    # Check for Kernel Patches
                    if current_model in ModelArray.LegacyHID:
                        print("- Adding IOHIDFamily Patch")
                        copy(pci_ssdt_path, acpi_path_build)
                        plist_data = plist_data.replace(
                            "<false/><!--IOHIDFamily-->",
                            "<true/><!--IOHIDFamily-->"
                        )

                    # Check for EFI Drivers
                    if current_model in ModelArray.NVMePatch:
                        print("- Adding NVMe support")
                        copy(nvme_driver_path, drivers_path_build)
                        plist_data = plist_data.replace(
                            "<string>#NvmExpressDxe.efi</string>",
                            "<string>NvmExpressDxe.efi</string>"
                        )
                    
                    # Add new SMBIOS data
                    if current_model in ModelArray.MacBookAir61:
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
                    if current_model in ModelArray.MacBookAir62:
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
                    if current_model in ModelArray.MacBookPro111:
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
                    if current_model in ModelArray.MacBookPro112:
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
                    if current_model in ModelArray.Macmini71:
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
                    if current_model in ModelArray.iMac151:
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
                    if current_model in ModelArray.iMac144:
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
                    if current_model in ModelArray.MacPro71:
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
        OpenCoreInstallerMenu=True
        while OpenCoreInstallerMenu:
            os.system('clear')

            print("#######################################################")
            print("        Install OpenCore to drive")
            print("#######################################################")
            print("")
            print("   1.  Install to USB/internal drive            - Not yet implemented")
            print("   2.  Mount OpenCore drive                     - Not yet implemented")
            print("   3.  Move OpenCore from USB to internal drive - Not yet implemented")
            print("   4.  Return to main menu")
            print("")

            OpenCoreInstallerMenu = raw_input('Please select an option: ')

            if OpenCoreInstallerMenu=="1":
                print("\n Not yet implemented")
                # List all disks with GPT
                # Mount user selected drive's EFI
                # Copy OpenCore to EFI
            elif OpenCoreInstallerMenu=="2":
                print("\n Not yet implemented")
                # Mount OpenCore boot drive
                # sudo diskutil mount $(nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:boot-path | sed 's/.*GPT,\([^,]*\),.*/\1/')
            elif OpenCoreInstallerMenu=="3":
                print("\n Not yet implemented")
                # Mount OpenCore Boot drive
                # Copy EFI to Backup folder
                # Ask user for internal drive
                # sudo diskutil mount $(nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:boot-path | sed 's/.*GPT,\([^,]*\),.*/\1/')
            elif OpenCoreInstallerMenu=="4":
                print("\n Returning to main menu...")
                OpenCoreInstallerMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")

    elif MainMenu=="4":
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
    elif MainMenu=="5":
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

    elif MainMenu=="6":
        print("\n Closing program...")
        sys.exit(1) 
    else:
        print("\n Not Valid Choice Try again") 
