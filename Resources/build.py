# Commands for building the EFI and SMBIOS

from __future__ import print_function

import binascii
import plistlib
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path

from Resources import Constants, ModelArray, utilities


def human_fmt(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, "EB")


class BuildOpenCore:
    def __init__(self, model, versions):
        self.model = model
        self.config = None
        self.constants: Constants.Constants = versions

    def build_efi(self):
        utilities.cls()
        if not Path(self.constants.build_path).exists():
            Path(self.constants.build_path).mkdir()
            print("Created build folder")
        else:
            print("Build folder already present, skipping")

        if Path(self.constants.opencore_zip_copied).exists():
            print("Deleting old copy of OpenCore zip")
            Path(self.constants.opencore_zip_copied).unlink()
        if Path(self.constants.opencore_release_folder).exists():
            print("Deleting old copy of OpenCore folder")
            shutil.rmtree(self.constants.opencore_release_folder)

        print()
        print("- Adding OpenCore v" + self.constants.opencore_version)
        shutil.copy(self.constants.opencore_zip_source, self.constants.build_path)
        zipfile.ZipFile(self.constants.opencore_zip_copied).extractall(self.constants.build_path)

        print("- Adding config.plist for OpenCore")
        # Setup config.plist for editing
        shutil.copy(self.constants.plist_template, self.constants.oc_folder)
        self.config = plistlib.load(Path(self.constants.plist_path).open("rb"))

        for name, version, path, check in [
            # Essential kexts
            ("Lilu.kext", self.constants.lilu_version, self.constants.lilu_path, lambda: True),
            ("WhateverGreen.kext", self.constants.whatevergreen_version, self.constants.whatevergreen_path, lambda: True),
            ("RestrictEvents.kext", self.constants.restrictevents_version, self.constants.restrictevents_path, lambda: self.model in ModelArray.MacPro71),
            # CPU patches
            ("AppleMCEReporterDisabler.kext", self.constants.mce_version, self.constants.mce_path, lambda: self.model in ModelArray.DualSocket),
            ("AAAMouSSE.kext", self.constants.mousse_version, self.constants.mousse_path, lambda: self.model in ModelArray.SSEEmulator),
            ("telemetrap.kext", self.constants.telemetrap_version, self.constants.telemetrap_path, lambda: self.model in ModelArray.MissingSSE42),
            # Ethernet patches
            ("nForceEthernet.kext", self.constants.nforce_version, self.constants.nforce_path, lambda: self.model in ModelArray.EthernetNvidia),
            ("MarvelYukonEthernet.kext", self.constants.marvel_version, self.constants.marvel_path, lambda: self.model in ModelArray.EthernetMarvell),
            ("CatalinaBCM5701Ethernet.kext", self.constants.bcm570_version, self.constants.bcm570_path, lambda: self.model in ModelArray.EthernetBroadcom),
            # Legacy audio
            ("VoodooHDA.kext", self.constants.voodoohda_version, self.constants.voodoohda_path, lambda: self.model in ModelArray.LegacyAudio),
            # IDE patch
            ("AppleIntelPIIXATA.kext", self.constants.piixata_version, self.constants.piixata_path, lambda: self.model in ModelArray.IDEPatch),
        ]:
            self.enable_kext(name, version, path, check)

        # WiFi patches

        if self.model in ModelArray.WifiAtheros:
            self.enable_kext("IO80211HighSierra.kext", self.constants.io80211high_sierra_version, self.constants.io80211high_sierra_path)
            self.get_kext_by_bundle_path("IO80211HighSierra.kext/Contents/PlugIns/AirPortAtheros40.kext")["Enabled"] = True

        if self.model in ModelArray.WifiBCM94331:
            self.enable_kext("AirportBrcmFixup.kext", self.constants.airportbcrmfixup_version, self.constants.airportbcrmfixup_path)
            self.get_kext_by_bundle_path("AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext")["Enabled"] = True

            if self.model in ModelArray.EthernetNvidia:
                # Nvidia chipsets all have the same path to ARPT
                property_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            if self.model in ("MacBookAir2,1", "MacBookAir3,1", "MacBookAir3,2"):
                property_path = "PciRoot(0x0)/Pci(0x15,0x0)/Pci(0x0,0x0)"
            elif self.model in ("iMac7,1", "iMac8,1"):
                property_path = "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x0)"
            elif self.model in ("iMac13,1", "iMac13,2"):
                property_path = "PciRoot(0x0)/Pci(0x1C,0x3)/Pci(0x0,0x0)"
            elif self.model == "MacPro5,1":
                property_path = "PciRoot(0x0)/Pci(0x1C,0x5)/Pci(0x0,0x0)"
            else:
                # Assumes we have a laptop with Intel chipset
                property_path = "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"
            print("- Applying fake ID for WiFi")
            self.config["DeviceProperties"]["Add"][property_path] = {"device-id": binascii.unhexlify("ba430000"), "compatible": "pci14e4,43ba"}

        # HID patches
        if self.model in ModelArray.LegacyHID:
            print("- Adding IOHIDFamily patch")
            self.get_item_by_kv(self.config["Kernel"]["Patch"], "Identifier", "com.apple.iokit.IOHIDFamily")["Enabled"] = True

        # SSDT patches
        if self.model in ModelArray.pciSSDT:
            print("- Adding SSDT-CPBG.aml")
            self.get_item_by_kv(self.config["ACPI"]["Add"], "Path", "SSDT-CPBG.aml")["Enabled"] = True

        # USB map
        map_name = f"USB-Map-{self.model}.zip"
        map_entry = f"USB-Map-{self.model}.kext"
        usb_map_path = Path(self.constants.current_path) / Path(f"payloads/Kexts/Maps/Zip/{map_name}")
        if usb_map_path.exists():
            print(f"- Adding {map_entry}")
            shutil.copy(usb_map_path, self.constants.kexts_path)
            self.get_kext_by_bundle_path("USB-Map-SMBIOS.kext")["Enabled"] = True
            self.get_kext_by_bundle_path("USB-Map-SMBIOS.kext")["BundlePath"] = map_entry

        if self.model in ModelArray.DualGPUPatch:
            print("- Adding dual GPU patch")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " agdpmod=pikera"

        if self.model in ModelArray.HiDPIpicker:
            print("- Setting HiDPI picker")
            self.config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"]["UIScale"] = binascii.unhexlify("02")

        # Add OpenCanopy
        print("- Adding OpenCanopy GUI")
        shutil.rmtree(self.constants.resources_path)
        shutil.copy(self.constants.gui_path, self.constants.oc_folder)
        self.config["UEFI"]["Drivers"] = ["OpenCanopy.efi", "OpenRuntime.efi"]

        plistlib.dump(self.config, Path(self.constants.plist_path).open("wb"), sort_keys=True)

    def set_smbios(self):
        spoofed_model = self.model
        if self.model in ModelArray.MacBookAir61:
            print("- Spoofing to MacBookAir6,1")
            spoofed_model = "MacBookAir6,1"
        elif self.model in ModelArray.MacBookAir62:
            print("- Spoofing to MacBookAir6,2")
            spoofed_model = "MacBookAir6,2"
        elif self.model in ModelArray.MacBookPro111:
            print("- Spoofing to MacBookPro11,1")
            spoofed_model = "MacBookPro11,1"
        elif self.model in ModelArray.MacBookPro113:
            print("- Spoofing to MacBookPro11,3")
            spoofed_model = "MacBookPro11,3"
        elif self.model in ModelArray.Macmini71:
            print("- Spoofing to Macmini7,1")
            spoofed_model = "Macmini7,1"
        elif self.model in ModelArray.iMac151:
            print("- Spoofing to iMac15,1")
            spoofed_model = "iMac15,1"
        elif self.model in ModelArray.iMac144:
            print("- Spoofing to iMac14,4")
            spoofed_model = "iMac14,4"
        elif self.model in ModelArray.MacPro71:
            print("- Spoofing to MacPro7,1")
            spoofed_model = "MacPro7,1"
        macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {spoofed_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        macserial_output = macserial_output.stdout.decode().strip().split(" | ")
        self.config["PlatformInfo"]["Generic"]["SystemProductName"] = spoofed_model
        self.config["PlatformInfo"]["Generic"]["SystemSerialNumber"] = macserial_output[0]
        self.config["PlatformInfo"]["Generic"]["MLB"] = macserial_output[1]
        self.config["PlatformInfo"]["Generic"]["SystemUUID"] = str(uuid.uuid4()).upper()

    @staticmethod
    def get_item_by_kv(iterable, key, value):
        item = None
        for i in iterable:
            if i[key] == value:
                item = i
                break
        return item

    def get_kext_by_bundle_path(self, bundle_path):
        kext = self.get_item_by_kv(self.config["Kernel"]["Add"], "BundlePath", bundle_path)
        if not kext:
            print(f"- Could not find kext {bundle_path}!")
            raise IndexError
        return kext

    def enable_kext(self, kext_name, kext_version, kext_path, check=False):
        kext = self.get_kext_by_bundle_path(kext_name)

        if callable(check) and not check():
            # Check failed
            return

        print(f"- Adding {kext_name} {kext_version}")
        shutil.copy(kext_path, self.constants.kexts_path)
        kext["Enabled"] = True

    def cleanup(self):
        print("- Cleaning up files")
        for kext in Path(self.constants.kexts_path).rglob("*.zip"):
            with zipfile.ZipFile(kext) as zip_file:
                zip_file.extractall(self.constants.kexts_path)
            kext.unlink()
        shutil.rmtree((Path(self.constants.kexts_path) / Path("__MACOSX")), ignore_errors=True)

        for item in Path(self.constants.oc_folder).glob("*.zip"):
            with zipfile.ZipFile(item) as zip_file:
                zip_file.extractall(self.constants.oc_folder)
            item.unlink()
        shutil.rmtree((Path(self.constants.build_path) / Path("__MACOSX")), ignore_errors=True)
        Path(self.constants.opencore_zip_copied).unlink()

    def build_opencore(self):
        self.build_efi()
        self.set_smbios()
        self.cleanup()
        print("")
        print("Your OpenCore EFI has been built at:")
        print(f"    {self.constants.opencore_release_folder}")
        print("")
        input("Press enter to go back")

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
        disks = plistlib.loads(subprocess.run("diskutil list -plist physical".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        for disk in disks["AllDisksAndPartitions"]:
            disk_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())

            all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info['DeviceNode'], "name": disk_info['MediaName'], "size": disk_info['Size'], "partitions": {}}

            for partition in disk["Partitions"]:
                partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {partition['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                all_disks[disk["DeviceIdentifier"]]["partitions"][partition["DeviceIdentifier"]] = {
                    "fs": partition_info.get("FilesystemType", partition_info["Content"]),
                    "type": partition_info["Content"],
                    "name": partition_info.get("VolumeName", ""),
                    "size": partition_info["Size"],
                }
        # TODO: Advanced mode
        menu = utilities.TUIMenu(["Select Disk"], "Please select the disk you would like to install OpenCore to: ", in_between=["Missing disks? Ensure they have an EFI or FAT32 partition."], return_number_instead_of_direct_call=True, loop=True)
        for disk in all_disks:
            if not any(all_disks[disk]["partitions"][partition]["fs"] == "msdos" for partition in all_disks[disk]["partitions"]):
                continue
            menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({human_fmt(all_disks[disk]['size'])})", key=disk[4:])

        response = menu.start()

        if response == -1:
            return

        disk_identifier = "disk" + response
        selected_disk = all_disks[disk_identifier]

        menu = utilities.TUIMenu(["Select Partition"], "Please select the partition you would like to install OpenCore to: ", return_number_instead_of_direct_call=True, loop=True, in_between=["Missing partitions? Ensure they are formatted as an EFI or FAT32.", "", "* denotes likely candidate."])
        for partition in selected_disk["partitions"]:
            if selected_disk["partitions"][partition]["fs"] != "msdos":
                continue
            text = f"{partition}: {selected_disk['partitions'][partition]['name']} ({human_fmt(selected_disk['partitions'][partition]['size'])})"
            if selected_disk["partitions"][partition]["type"] == "EFI" or (selected_disk["partitions"][partition]["type"] == "Microsoft Basic Data" and selected_disk["partitions"][partition]["size"] < 1024 * 1024 * 512):  # 512 megabytes:
                text += " *"
            menu.add_menu_option(text, key=partition[len(disk_identifier) + 1:])

        response = menu.start()

        if response == -1:
            return

        args = [
            "osascript",
            "-e",
            f'''do shell script "diskutil mount {disk_identifier}s{response}"'''
            ' with prompt "OpenCore Legacy Patcher needs administrator privileges to mount your EFI."'
            " with administrator privileges"
            " without altering line endings"
        ]

        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            if "execution error" in result.stderr.decode() and result.stderr.decode()[-5:-1] == "-128":
                # cancelled prompt
                return
            else:
                utilities.TUIOnlyPrint(["Copying OpenCore"], "Press [Enter] to continue", ["An error occurred!"] + result.stderr.decode().split("\n") + ["", "Please report this to the devs at GitHub."]).start()
                return

        # TODO: Remount if readonly
        partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk_identifier}s{response}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        mount_path = Path(partition_info["MountPoint"])

        utilities.cls()
        utilities.header(["Copying OpenCore"])

        if mount_path.exists():
            print("- Coping OpenCore onto EFI partition")
            if (mount_path / Path("EFI")).exists():
                print("Removing preexisting EFI folder")
                shutil.rmtree(mount_path / Path("EFI"))

            shutil.copytree(self.constants.opencore_release_folder, mount_path / Path("EFI"))
            shutil.copy(self.constants.icon_path, mount_path)
            print("OpenCore transfer complete")
            print("\nPress [Enter] to continue")
            input()
        else:
            utilities.TUIOnlyPrint(["Copying OpenCore"], "Press [Enter] to continue", ["EFI failed to mount!", "Please report this to the devs at GitHub."]).start()
