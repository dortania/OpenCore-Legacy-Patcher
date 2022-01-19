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
import sys
import plistlib
from pathlib import Path

def main():
    patch_load_command()
    patch_info_plist()


def patch_load_command():
    print("- Patching LC_VERSION_MIN_MACOSX")
    path = './dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher'
    find = b'\x00\x0D\x0A\x00' # 10.13 (0xA0D)
    replace = b'\x00\x0A\x0A\x00' # 10.10 (0xA0A)
    with open(path, 'rb') as f:
        data = f.read()
        data = data.replace(find, replace)
        with open(path, 'wb') as f:
            f.write(data)

def patch_info_plist():
    print("- Updating Info.plist")
    # Github Actions will supply us with the following environment variables:
    # - Commit Message
    # - Commit ID
    # - Branch
    # - Commit URL
    # - Commit Date

    argsv = sys.argv
    argsv.pop(0)
    plist_path = './dist/OpenCore-Patcher.app/Contents/Info.plist'
    plist = plistlib.load(Path(plist_path).open("rb"))
    print("- Loaded Plist")
    # Add Github Dictonary
    print("- Adding Github Dictionary")
    plist["Github"] = {
        "Commit Message": argsv[0],
        "Commit ID": argsv[1],
        "Branch": argsv[2],
        "Commit URL": argsv[3],
        "Commit Date": argsv[4],
    }
    print("- Writing Plist")
    plistlib.dump(plist, Path(plist_path).open("wb"), sort_keys=True)


main()