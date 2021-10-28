# Installation of OpenCore files to ESP
# Usage soley for TUI
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk

import plistlib
import subprocess
import shutil
from pathlib import Path
from resources import utilities, constants
from data import os_data

class tui_disk_installation:
    def __init__(self, versions):
        self.constants: constants.Constants = versions
    
    def determine_sd_card(self, media_name):
        # Array filled with common SD Card names
        # Note most USB-based SD Card readers generally report as "Storage Device"
        # Thus no reliable way to detect further without parsing IOService output (kUSBProductString)
        if (
            "SD Card" in media_name or \
            "SD/MMC" in media_name or \
            "SDXC Reader" in media_name or \
            "SD Reader" in media_name or \
            "Card Reader" in media_name
        ):
            return True
        return False

    def copy_efi(self):
        utilities.cls()
        utilities.header(["Installing OpenCore to Drive"])

        if not self.constants.opencore_release_folder.exists():
            utilities.TUIOnlyPrint(
                ["Installing OpenCore to Drive"],
                "Press [Enter] to go back.\n",
                [
                    """OpenCore folder missing!
Please build OpenCore first!"""
                ],
            ).start()
            return

        print("\nDisk picker is loading...")

        all_disks = {}
        # TODO: AllDisksAndPartitions is not supported in Snow Leopard and older
        try:
            # High Sierra and newer
            disks = plistlib.loads(subprocess.run("diskutil list -plist physical".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        except ValueError:
            # Sierra and older
            disks = plistlib.loads(subprocess.run("diskutil list -plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        for disk in disks["AllDisksAndPartitions"]:
            disk_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            try:
                all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info["DeviceNode"], "name": disk_info["MediaName"], "size": disk_info["TotalSize"], "partitions": {}}
                for partition in disk["Partitions"]:
                    partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {partition['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                    all_disks[disk["DeviceIdentifier"]]["partitions"][partition["DeviceIdentifier"]] = {
                        "fs": partition_info.get("FilesystemType", partition_info["Content"]),
                        "type": partition_info["Content"],
                        "name": partition_info.get("VolumeName", ""),
                        "size": partition_info["TotalSize"],
                    }
            except KeyError:
                # Avoid crashing with CDs installed
                continue
        # TODO: Advanced mode
        menu = utilities.TUIMenu(
            ["Select Disk"],
            "Please select the disk you would like to install OpenCore to: ",
            in_between=["Missing disks? Ensure they have an EFI or FAT32 partition."],
            return_number_instead_of_direct_call=True,
            loop=True,
        )
        for disk in all_disks:
            if not any(all_disks[disk]["partitions"][partition]["fs"] in ("msdos", "EFI") for partition in all_disks[disk]["partitions"]):
                continue
            menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({utilities.human_fmt(all_disks[disk]['size'])})", key=disk[4:])

        response = menu.start()

        if response == -1:
            return

        disk_identifier = "disk" + response
        selected_disk = all_disks[disk_identifier]

        menu = utilities.TUIMenu(
            ["Select Partition"],
            "Please select the partition you would like to install OpenCore to: ",
            return_number_instead_of_direct_call=True,
            loop=True,
            in_between=["Missing partitions? Ensure they are formatted as an EFI or FAT32.", "", "* denotes likely candidate."],
        )
        for partition in selected_disk["partitions"]:
            if selected_disk["partitions"][partition]["fs"] not in ("msdos", "EFI"):
                continue
            text = f"{partition}: {selected_disk['partitions'][partition]['name']} ({utilities.human_fmt(selected_disk['partitions'][partition]['size'])})"
            if selected_disk["partitions"][partition]["type"] == "EFI" or (
                selected_disk["partitions"][partition]["type"] == "Microsoft Basic Data" and selected_disk["partitions"][partition]["size"] < 1024 * 1024 * 512
            ):  # 512 megabytes:
                text += " *"
            menu.add_menu_option(text, key=partition[len(disk_identifier) + 1 :])

        response = menu.start()

        if response == -1:
            return

        # TODO: Apple Script fails in Yosemite(?) and older
        args = [
            "osascript",
            "-e",
            f'''do shell script "diskutil mount {disk_identifier}s{response}"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to mount your EFI."'
            " with administrator privileges"
            " without altering line endings",
        ]

        if self.constants.detected_os >= os_data.os_data.el_capitan and not self.constants.recovery_status:
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(f"diskutil mount {disk_identifier}s{response}".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            if "execution error" in result.stderr.decode() and result.stderr.decode().strip()[-5:-1] == "-128":
                # cancelled prompt
                return
            else:
                utilities.TUIOnlyPrint(
                    ["Copying OpenCore"], "Press [Enter] to go back.\n", ["An error occurred!"] + result.stderr.decode().split("\n") + ["", "Please report this to the devs at GitHub."]
                ).start()
                return

        # TODO: Remount if readonly
        drive_host_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk_identifier}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk_identifier}s{response}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        sd_type = drive_host_info["MediaName"]
        try:
            ssd_type = drive_host_info["SolidState"]
        except KeyError:
            ssd_type = False
        mount_path = Path(partition_info["MountPoint"])
        disk_type = partition_info["BusProtocol"]
        utilities.cls()
        utilities.header(["Copying OpenCore"])

        if mount_path.exists():
            if (mount_path / Path("EFI/Microsoft")).exists():
                print("- Found Windows Boot Loader")
                print("\nWould you like to continue installing OpenCore?")
                print("Installing OpenCore onto this drive may make Windows unbootable until OpenCore")
                print("is removed from the partition")
                print("We highly recommend users partition 200MB off their drive with Disk Utility")
                print("    Name:\t\t OPENCORE")
                print("    Format:\t\t FAT32")
                print("    Size:\t\t 200MB")
                choice = input("\nWould you like to still install OpenCore to this drive?(y/n): ")
                if not choice in ["y", "Y", "Yes", "yes"]:
                    subprocess.run(["diskutil", "umount", mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                    return
            if (mount_path / Path("EFI/OC")).exists():
                print("- Removing preexisting EFI/OC folder")
                shutil.rmtree(mount_path / Path("EFI/OC"), onerror=rmtree_handler)
            if (mount_path / Path("System")).exists():
                print("- Removing preexisting System folder")
                shutil.rmtree(mount_path / Path("System"), onerror=rmtree_handler)
            print("- Copying OpenCore onto EFI partition")
            shutil.copytree(self.constants.opencore_release_folder / Path("EFI/OC"), mount_path / Path("EFI/OC"))
            shutil.copytree(self.constants.opencore_release_folder / Path("System"), mount_path / Path("System"))
            if self.constants.boot_efi is True:
                print("- Converting Bootstrap to BOOTx64.efi")
                if (mount_path / Path("EFI/BOOT")).exists():
                    shutil.rmtree(mount_path / Path("EFI/BOOT"), onerror=rmtree_handler)
                Path(mount_path / Path("EFI/BOOT")).mkdir()
                shutil.move(mount_path / Path("System/Library/CoreServices/boot.efi"), mount_path / Path("EFI/BOOT/BOOTx64.efi"))
                shutil.rmtree(mount_path / Path("System"), onerror=rmtree_handler)
            if self.determine_sd_card(sd_type) is True:
                print("- Adding SD Card icon")
                shutil.copy(self.constants.icon_path_sd, mount_path)
            elif ssd_type is True:
                print("- Adding SSD icon")
                shutil.copy(self.constants.icon_path_ssd, mount_path)
            elif disk_type == "USB":
                print("- Adding External USB Drive icon")
                shutil.copy(self.constants.icon_path_external, mount_path)
            else:
                print("- Adding Internal Drive icon")
                shutil.copy(self.constants.icon_path_internal, mount_path)
            print("- Cleaning install location")
            if not self.constants.recovery_status:
                print("- Unmounting EFI partition")
                subprocess.run(["diskutil", "umount", mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print("- OpenCore transfer complete")
            print("\nPress [Enter] to continue.\n")
            input()
        else:
            utilities.TUIOnlyPrint(["Copying OpenCore"], "Press [Enter] to go back.\n", ["EFI failed to mount!", "Please report this to the devs at GitHub."]).start()

def rmtree_handler(func, path, exc_info):
    if exc_info[0] == FileNotFoundError:
        return
    raise  # pylint: disable=misplaced-bare-raise