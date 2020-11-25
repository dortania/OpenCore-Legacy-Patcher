from __future__ import print_function

import os
import json
import subprocess
import sys

patcher_version = "0.0.1"
opencore_version = "0.6.3"
models = json.load(open("models.json"))

current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]
print(current_model)

#if current_model not in models:
#    print("Your model is not supported by this patcher!")
#    sys.exit(1)

MainMenu=True
while MainMenu:
    os.system('clear')

    print("#######################################################")
    print("        OpenCore Legacy patcher v%s" % patcher_version)
    print("           Detected Model: %s" % current_model)
    print("#######################################################")
    print("")
    if current_model not in models:
        # TO-DO
        # Figure out why this always fails
        print("   Your model is not supported by this patcher!")
        print("")
        print("   If you plan to create the USB for another machine,")
        print("   please select option 5")
        print("-------------------------------------------------------")
        print("")
    print("    1.  Create macOS Installer              - Not yet implemented")
    print("    2.  Install OpenCore to macOS Installer - Not yet implemented")
    print("    3.  Install OpenCore to internal drive  - Not yet implemented")
    print("    4.  Credits")
    print("    5.  Change model")
    print("    6.  Exit")
    print("")

    MainMenu = raw_input('Please select an option: ')

    if MainMenu=="1":
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
            print("   2.  macOS 10.15, Catalina - Not yet implemented")
            print("   3.  macOS 10.14, Mojave   - Not yet implemented")
            print("   4.  Return to main menu")
            print("")

            macOSInstallerMenu = raw_input('Please select an option: ')

            if macOSInstallerMenu=="1":
                print("\n Not yet implemented")
            elif macOSInstallerMenu=="2":
                print("\n Not yet implemented") 
            elif macOSInstallerMenu=="3":
                print("\n Not yet implemented")
            elif macOSInstallerMenu=="4":
                print("\n Returning to main menu...")
                macOSInstallerMenu=False
                MainMenu=True
            else:
                print("\n Not Valid Choice Try again")
            
    elif MainMenu=="2":
        print("\n Not yet implemented") 
    elif MainMenu=="3":
        print("\n Not yet implemented")
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
            print("")
            CreditMenu = raw_input(" Press 1 to exit: ")
            if CreditMenu=="1":
                print("Returning to main menu...")
                CreditMenu=False
                MainMenu=True
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
            print("New SMBIOS: %s" % SMBIOSOption)
            SMBIOSMenuYN = raw_input("Is this correcy?(y/n)")
            if SMBIOSMenuYN in {"y", "Y", "yes", "Yes"}:
                SMBIOSMenu=False
                current_model = SMBIOSOption
                MainMenu=True
                

    elif MainMenu=="6":
        print("\n Closing program...")
        sys.exit(1) 
    else:
        print("\n Not Valid Choice Try again") 
