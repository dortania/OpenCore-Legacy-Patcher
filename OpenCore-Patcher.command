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


# Allow py2 and 3 support
try:
    input = raw_input
except NameError:
    pass

# List build versions
patcher_version = "0.0.4"

CustomSMBIOS=False
MainMenu=True
MenuWidth = 52
header = '#' * MenuWidth
subheader = '-' * MenuWidth

while MainMenu:
    os.system('clear')

    print(header)
    print("          OpenCore Legacy patcher v%s" % patcher_version)
    print("             Current Model: %s" % BuildOpenCore.current_model)
    print(header)
    print("")
    if BuildOpenCore.current_model not in ModelArray.SupportedSMBIOS:
        print("   Your model is not supported by this patcher!")
        print("")
        print(" If you plan to create the USB for another machine,")
        print("            please select option 5")
        print(subheader)
        print("")
    elif BuildOpenCore.current_model in ("MacPro3,1", "iMac7,1"):
        print("           This model is supported")
        print(" However please ensure the CPU have been upgraded")
        print("             to support SSE4.1+")
        print(subheader)
        print("")
    else:
        print("            This model is supported")
        print(subheader)
        print("")
    print("    1.  Build OpenCore")
    print("    2.  Install OpenCore to USB/internal drive")
    print("    3.  Change model")
    print("    4.  Credits")
    print("    5.  Exit")
    print("")

    MainMenu = input('Please select an option: ')

    if MainMenu=="1":
        OpenCoreBuilderMenu=True
        while OpenCoreBuilderMenu:
            os.system('clear')

            print(header)
            print("     Build OpenCore v%s for model: %s" % (Versions.opencore_version, BuildOpenCore.current_model))
            print(header)
            print("")
            print("   1.  Auto build OpenCore")
            print("   2.  Change OpenCore version")
            print("   3.  Return to main menu")
            print("")

            OpenCoreBuilderMenu = input('Please select an option: ')

            if OpenCoreBuilderMenu=="1":
                AutoBuilderMenu=True
                while AutoBuilderMenu:
                    os.system('clear')
                    print(header)
                    print("      Building OpenCore for model: %s" % BuildOpenCore.current_model)
                    print(header)
                    print("")
                    print("The current working directory:")
                    print ("    %s" % Versions.current_path)
                    print("")
                    BuildOpenCore.BuildEFI()
                    #BuildOpenCore.BuildGUI()
                    BuildOpenCore.BuildSMBIOS()
                    BuildOpenCore.SavePlist()
                    BuildOpenCore.CleanBuildFolder()
                    print("")
                    print("Your OpenCore EFI has been built at:")
                    print("    %s" % Versions.opencore_path_done)
                    print("")
                    AutoBuilderMenu = input("Press any key to return to previous menu: ")
                    if AutoBuilderMenu=="1":
                        print("Returning to previous menu...")
                        AutoBuilderMenu=False
                        OpenCoreBuilderMenu=False
            elif OpenCoreBuilderMenu=="2":
                ChangeOCversion=True
                while ChangeOCversion:
                    os.system('clear')
                    print(header)
                    print("    Current OpenCore version: %s" % Versions.opencore_version)
                    print(header)
                    print("")
                    print("  Supported versions: 0.6.3, 0.6.4")
                    print("")
                    OpenCoreOption = input('Please enter the OpenCore you want (Press enter to exit): ')
                    if OpenCoreOption == "":
                        print("Exiting...")
                        ChangeOCversion=False
                        MainMenu=True
                    else:
                        print("")
                        print("  New SMBIOS: %s" % OpenCoreOption)
                        print("")
                        ChangeOCversionYN = input("Is this correct? (y/n)")
                        if ChangeOCversionYN in {"y", "Y", "yes", "Yes"}:
                            ChangeOCversion=False
                            Versions.opencore_version = OpenCoreOption
                            MainMenu=True
            elif OpenCoreBuilderMenu=="3":
                print("\n Returning to main menu...")
                OpenCoreBuilderMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")
                OpenCoreBuilderMenu = True

            
    elif MainMenu=="2":
        print("\n Not yet implemented")
        OpenCoreInstallerMenu=True
        while OpenCoreInstallerMenu:
            os.system('clear')

            print(header)
            print("        Install OpenCore to drive")
            print(header)
            print("")
            print("   1.  Install to USB/internal drive")
            print("   2.  Return to main menu")
            print("")

            OpenCoreInstallerMenu = input('Please select an option: ')

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
                OpenCoreInstallerMenu = input("Press any key to exit: ")
                if OpenCoreInstallerMenu=="1":
                    print("Returning to main menu...")
                    OpenCoreInstallerMenu=False
            elif OpenCoreInstallerMenu=="2":
                print("\n Returning to main menu...")
                OpenCoreInstallerMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")
                OpenCoreInstallerMenu = True

    elif MainMenu=="3":
        SMBIOSMenu=True
        while SMBIOSMenu:
            os.system('clear')

            print(header)
            print("        Enter a new SMBIOS")
            print(header)
            print("")
            print("  Tip: Run this command on the machine to find the SMBIOS")
            print("")
            print("  system_profiler SPHardwareDataType | grep 'Model Identifier'")
            print("")
            SMBIOSOption = input('Please enter the SMBIOS of your machine (Press enter to exit): ')
            if SMBIOSOption == "":
                print("Exiting...")
                SMBIOSMenu=False
                MainMenu=True
            else:
                print("")
                print("  New SMBIOS: %s" % SMBIOSOption)
                print("")
                SMBIOSMenuYN = input("Is this correct? (y/n)")
                if SMBIOSMenuYN in {"y", "Y", "yes", "Yes"}:
                    SMBIOSMenu=False
                    BuildOpenCore.current_model = SMBIOSOption
                    MainMenu=True
                    CustomSMBIOS=True
    elif MainMenu=="4":
        CreditMenu=True
        while CreditMenu:
            os.system('clear')

            print(header)
            print("                    Credits")
            print(header)
            print("")
            print(" Many thanks to the following:")
            print("")
            print("  - Acidanthera:  OpenCore, kexts and other tools")
            print("  - DhinakG:      Writing and maintaining this Patcher")
            print("  - Khronokernel: Writing and maintaining this Patcher")
            print("  - Syncretic:    AAAMouSSE and telemetrap")
            print("")
            CreditMenu = input(" Press any key to exit: ")
            print("Returning to main menu...")
            CreditMenu=False
            MainMenu=True

    elif MainMenu=="5":
        print("\n Closing program...")
        sys.exit(1) 
    else:
        print("\n Not Valid Choice Try again")
        MainMenu=True

