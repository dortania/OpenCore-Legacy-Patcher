# Handle Misc patching for binaries during commit
# This includes Load Command Patching as well as Info.plist patching
# Copyright (C) 2022 - Mykola Grymalyuk
import sys
import plistlib
from pathlib import Path

def main():
    patch_load_command()
    patch_info_plist()

def patch_load_command():
    # Patches LC_VERSION_MIN_MACOSX in Load Command to report 10.10
    #
    # By default Pyinstaller will create binaries supporting 10.13+
    # However this limitation is entirely arbitrary for our libraries
    # and instead we're able to support 10.10 without issues.
    # 
    # To verify set version:
    #   otool -l ./dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher
    # 
    #       cmd LC_VERSION_MIN_MACOSX
    #   cmdsize 16
    #   version 10.13
    #       sdk 10.9
    print("- Patching LC_VERSION_MIN_MACOSX")
    path = './dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher'
    find = b'\x00\x0D\x0A\x00' # 10.13 (0xA0D)
    replace = b'\x00\x0A\x0A\x00' # 10.10 (0xA0A)
    with open(path, 'rb') as f:
        data = f.read()
        data = data.replace(find, replace, 1)
        with open(path, 'wb') as f:
            f.write(data)

def patch_info_plist():
    # Add Commit Data to Info.plist
    print("- Updating Info.plist")
    argsv = sys.argv
    argsv.pop(0)
    if argsv:
        plist_path = './dist/OpenCore-Patcher.app/Contents/Info.plist'
        plist = plistlib.load(Path(plist_path).open("rb"))
        print("- Adding Github Dictionary")
        plist["Github"] = {
            "Branch": argsv[0],
            "Commit URL": argsv[1],
            "Commit Date": argsv[2],
        }
        print("- Writing Plist")
        plistlib.dump(plist, Path(plist_path).open("wb"), sort_keys=True)
    else:
        print("- No commit data supplied, skipping") 
main()