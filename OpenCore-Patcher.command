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

# Find SMBIOS of machine
#current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
#current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]

CustomSMBIOS=False
MainMenu=True

while MainMenu:
    os.system('clear')

    print("###################################################")
    print("        OpenCore Legacy patcher v%s" % patcher_version)
    print("           Current Model: %s" % BuildOpenCore.current_model)
    print("###################################################")
    print("")
    if BuildOpenCore.current_model not in ModelArray.SupportedSMBIOS:
        print("   Your model is not supported by this patcher!")
        print("")
        print(" If you plan to create the USB for another machine,")
        print("            please select option 5")
        print("---------------------------------------------------")
        print("")
    elif BuildOpenCore.current_model in ("MacPro3,1", "iMac7,1"):
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
            print("        Build OpenCore for model: %s" % BuildOpenCore.current_model)
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
                    print("      Building OpenCore for model: %s" % BuildOpenCore.current_model)
                    print("#######################################################")
                    print("")
                    print("The current working directory:")
                    print ("    %s" % Versions.current_path)
                    print("")
                    BuildOpenCore.BuildEFI()
                    BuildOpenCore.BuildSMBIOS()
                    # Save config.plist changes in memory
                    with open(Versions.plist_path_build_full, 'w') as file:
                        file.write(Versions.plist_data)
                    
                    BuildOpenCore.CleanBuildFolder()

                    print("")
                    print("Your OpenCore EFI has been built at:")
                    print("    %s" % Versions.opencore_path_done)
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
                BuildOpenCore.current_model = SMBIOSOption
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
