#!/usr/bin/env python3
# Simple script to delete unnecessary files from OpenCore and move into place
# To use, simply :
# - Download an OpenCore build
# - Place the X64 folder in the /payloads/OpenCore folder
# - Rename to OpenCore-VERSION (ie. DEBUG or RELEASE)
# - Run script
# - Rename folders to appropriate versions (ie. OpenCore-Build)
# - Zip folders
# TODO:
# - Download latest builds from dortania.github.io

import subprocess
from pathlib import Path

build_types = [
    "DEBUG",
    "RELEASE",
]

bad_drivers = [
    "AudioDxe.efi",
    "BiosVideo.efi",
    "CrScreenshotDxe.efi",
    "Ext4Dxe.efi",
    "HiiDatabase.efi",
    "NvmExpressDxe.efi",
    "OpenHfsPlus.efi",
    "OpenNtfsDxe.efi",
    "OpenPartitionDxe.efi",
    "OpenUsbKbDxe.efi",
    "OpenVariableRuntimeDxe.efi",
    "Ps2KeyboardDxe.efi",
    "Ps2MouseDxe.efi",
    "ToggleSipEntry.efi",
    "UsbMouseDxe.efi",
    "XhciDxe.efi",
    "Udp4Dxe.efi",
    "TcpDxe.efi",
    "SnpDxe.efi",
    "MnpDxe.efi",
    "Ip4Dxe.efi",
    "HttpUtilitiesDxe.efi",
    "HttpDxe.efi",
    "HttpBootDxe.efi",
    "DpcDxe.efi",
    "DnsDxe.efi",
    "Dhcp4Dxe.efi",
    "ArpDxe.efi",
]

bad_tools = [
    "ChipTune.efi",
    "CleanNvram.efi",
    "ControlMsrE2.efi",
    "GopStop.efi",
    "KeyTester.efi",
    "MmapDump.efi",
    "OpenControl.efi",
    "ResetSystem.efi",
    "RtcRw.efi",
    "CsrUtil.efi",
    "TpmInfo.efi",
]

for version in build_types:
    print("- Creating S/L/C")
    subprocess.run(f"mkdir -p ./OpenCore-{version}/System/Library/CoreServices".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
    print("- Creating boot.efi Bootstrap")
    subprocess.run(f"cp ./OpenCore-{version}/EFI/BOOT/BOOTx64.efi ./OpenCore-{version}/System/Library/CoreServices/boot.efi".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
    print("- Deleting old BOOTx64.efi")
    subprocess.run(f"rm -R ./OpenCore-{version}/EFI/BOOT/".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
    for delete_drivers in bad_drivers:
        if Path(f"./OpenCore-{version}/EFI/OC/Drivers/{delete_drivers}").exists():
            print(f"- Deleting {delete_drivers}")
            subprocess.run(f"rm ./OpenCore-{version}/EFI/OC/Drivers/{delete_drivers}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        else:
            print(f"- Unable to find {delete_drivers}, skipping")
    for delete_tools in bad_tools:
        if Path(f".//OpenCore-{version}/EFI/OC/Tools/{delete_tools}").exists():
            print(f"- Deleting {delete_tools}")
            subprocess.run(f"rm ./OpenCore-{version}/EFI/OC/Tools/{delete_tools}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        else:
            print(f"- Unable to find {delete_tools}, skipping")

    print("- Renaming folder to OpenCore-Build and zipping")
    subprocess.run(f"mv ./OpenCore-{version} ./OpenCore-Build".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
    subprocess.run(f"zip -r ./OpenCore-{version}.zip ./OpenCore-Build".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
    subprocess.run(f"rm -rf ./OpenCore-Build".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
