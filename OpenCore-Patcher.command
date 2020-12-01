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
    print("    2.  Install OpenCore to USB/internal drive")
    print("    3.  Change model")
    print("    4.  Credits")
    print("    5.  Exit")
    macserialoutput = subprocess.Popen(["./payloads/tools/macserial", "-m", "MacBookAir6,1"], stdout=subprocess.PIPE).communicate()[0]
    print(macserialoutput)
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
                    BuildOpenCore.SavePlist()
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

            
    elif MainMenu=="2":
        print("\n Not yet implemented")
        OpenCoreInstallerMenu=True
        while OpenCoreInstallerMenu:
            os.system('clear')

            print("#######################################################")
            print("        Install OpenCore to drive")
            print("#######################################################")
            print("")
            print("   1.  Install to USB/internal drive")
            print("   2.  Return to main menu")
            print("")

            OpenCoreInstallerMenu = raw_input('Please select an option: ')

            if OpenCoreInstallerMenu=="1":
                os.system('clear')
                if os.path.exists(Versions.opencore_path_done):
                    print("Found OpenCore in Build Folder")
                    BuildOpenCore.ListDiskutil()
                    BuildOpenCore.MoveOpenCore()
                else:
                    print("OpenCore folder missing!")
                    print("Please build OpenCore first")
                    print("")
                OpenCoreInstallerMenu = raw_input("Press any key to exit: ")
                if OpenCoreInstallerMenu=="1":
                    print("Returning to main menu...")
                    OpenCoreInstallerMenu=False
            elif OpenCoreInstallerMenu=="2":
                print("\n Returning to main menu...")
                OpenCoreInstallerMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")

    elif MainMenu=="3":
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
    elif MainMenu=="4":
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

    elif MainMenu=="5":
        print("\n Closing program...")
        sys.exit(1) 
    else:
        print("\n Not Valid Choice Try again") 
