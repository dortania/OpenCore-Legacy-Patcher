# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
# Missing Features:
# - Full System/Library Snapshotting (need to research how Apple achieves this)
#   - Temporary Work-around: sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot
# - Work-around battery throttling on laptops with no battery (IOPlatformPluginFamily.kext/Contents/PlugIns/ACPI_SMC_PlatformPlugin.kext/Contents/Resources/)

import os
import plistlib
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from Resources import Constants, DeviceProbe, ModelArray, PCIIDArray, Utilities


class PatchSysVolume:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions
        self.sip_patch_status = True
        self.root_mount_path = None
        self.sip_status = None

        # TODO: Put this in a better place
        if self.constants.recovery_status is True:
            if not Path("/Volumes/mnt1").exists:
                self.elevated(["mkdir", "/Volumes/mnt1"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            self.mount_location = "/Volumes/mnt1"
        else:
            self.mount_location = "/System/Volumes/Update/mnt1"
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
        self.mount_frameworks = f"{self.mount_location}/System/Library/Frameworks"
        self.mount_lauchd = f"{self.mount_location}/System/Library/LaunchDaemons"
        self.mount_private_frameworks = f"{self.mount_location}/System/Library/PrivateFrameworks"

    def elevated(self, *args, **kwargs) -> subprocess.CompletedProcess([Any], returncode=0):
        if os.getuid() == 0:
            return subprocess.run(*args, **kwargs)
        else:
            return subprocess.run(["sudo"] + [args[0][0]] + args[0][1:], **kwargs)

    def csr_decode(self, print_status):
        sip_int = int.from_bytes(self.sip_status, byteorder="little")
        i = 0
        for current_sip_bit in self.constants.csr_values:
            if sip_int & (1 << i):
                temp = True
                self.constants.csr_values[current_sip_bit] = True
            else:
                temp = False
            if print_status is True:
                print(f"- {current_sip_bit}\t {temp}")
            i = i + 1

        sip_needs_change = all(
            self.constants.csr_values[i]
            for i in [
                "CSR_ALLOW_UNTRUSTED_KEXTS",
                "CSR_ALLOW_UNRESTRICTED_FS",
                "CSR_ALLOW_UNRESTRICTED_DTRACE",
                "CSR_ALLOW_UNRESTRICTED_NVRAM",
                "CSR_ALLOW_DEVICE_CONFIGURATION",
                "CSR_ALLOW_UNAPPROVED_KEXTS",
                "CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE",
                "CSR_ALLOW_UNAUTHENTICATED_ROOT",
            ]
        )
        if sip_needs_change is True:
            self.sip_patch_status = False
        else:
            self.sip_patch_status = True

    def recovery_root_mount(self):
        def human_fmt(num):
            for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
                if abs(num) < 1000.0:
                    return "%3.1f %s" % (num, unit)
                num /= 1000.0
            return "%.1f %s" % (num, "EB")

        print("- Starting Root Volume Picker")
        # Planned logic:
        # Load "diskutil list -plist"
        # Find all APFSVolumes entries where VolumeName is not named Update, VM, Recovery or Preboot
        # Omit any VolumeName entries containing "- Data"
        # Parse remianing options for macOS 11.x with /Volumes/$disk/System/Library/CoreServices/SystemVersion.plist
        # List remaining drives as user options
        all_disks = {}
        disks = plistlib.loads(subprocess.run("diskutil list -plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        for disk in disks["AllDisksAndPartitions"]:
            disk_info = plistlib.loads(subprocess.run(f"diskutil info -plist {disk['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            try:
                all_disks[disk["DeviceIdentifier"]] = {"identifier": disk_info["DeviceNode"], "name": disk_info["MediaName"], "size": disk_info["TotalSize"], "partitions": {}}
                for partition in disk["Partitions"] + disk.get("APFSVolumes", []):
                    partition_info = plistlib.loads(subprocess.run(f"diskutil info -plist {partition['DeviceIdentifier']}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                    all_disks[disk["DeviceIdentifier"]]["partitions"][partition["DeviceIdentifier"]] = {
                        "fs": partition_info.get("FilesystemType", partition_info["Content"]),
                        "type": partition_info["Content"],
                        "name": partition_info.get("VolumeName", ""),
                        "size": partition_info["TotalSize"],
                        "sealed": partition_info.get("Sealed", "No"),
                    }
            except KeyError:
                # Avoid crashing with CDs installed
                continue
        menu = Utilities.TUIMenu(
            ["Select Disk"],
            "Please select the disk you would like to patch: ",
            in_between=["Missing disks? Ensure they have a macOS Big Sur install present."],
            return_number_instead_of_direct_call=True,
            loop=True,
        )
        for disk in all_disks:
            if not any(all_disks[disk]["partitions"][partition]["fs"] == "apfs" for partition in all_disks[disk]["partitions"]):
                continue
            menu.add_menu_option(f"{disk}: {all_disks[disk]['name']} ({human_fmt(all_disks[disk]['size'])})", key=disk[4:])

        response = menu.start()

        if response == -1:
            return

        disk_identifier = "disk" + response
        selected_disk = all_disks[disk_identifier]

        menu = Utilities.TUIMenu(
            ["Select Partition"],
            "Please select the partition you would like to install OpenCore to: ",
            return_number_instead_of_direct_call=True,
            loop=True,
            in_between=["Missing disks? Ensure they have a macOS Big Sur install present.", "", "* denotes likely candidate."],
        )
        # TODO: check if Big Sur, when macOS 12 comes out
        for partition in selected_disk["partitions"]:
            if selected_disk["partitions"][partition]["fs"] != "apfs":
                continue
            text = f"{partition}: {selected_disk['partitions'][partition]['name']} ({human_fmt(selected_disk['partitions'][partition]['size'])})"
            if selected_disk["partitions"][partition]["sealed"] != "No":
                text += " *"
            menu.add_menu_option(text, key=partition[len(disk_identifier) + 1 :])

        response = menu.start()

        if response == -1:
            return
        else:
            return f"{disk_identifier}s{response}"

    def find_mount_root_vol(self, patch):
        if self.constants.recovery_status is True:
            print("- Running RecoveryOS logic")
            self.root_mount_path = self.recovery_root_mount()
            if not self.root_mount_path:
                return
            print(f"- Root Mount Path: {self.root_mount_path}")
            if not Path(self.constants.payload_mnt1_path).exists():
                print("- Creating mnt1 folder")
                Path(self.constants.payload_mnt1_path).mkdir()
        else:
            root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
            self.root_mount_path = root_partition_info["DeviceIdentifier"]

        if self.root_mount_path.startswith("disk"):
            if self.constants.recovery_status is False:
                self.root_mount_path = self.root_mount_path[:-2] if self.root_mount_path.count("s") > 1 else self.root_mount_path
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                if patch is True:
                    self.patch_root_vol()
                    return True
                else:
                    self.unpatch_root_vol()
                    return True
            else:
                if self.constants.recovery_status is True:
                    print("- Mounting drive as writable in Recovery")

                    umount_drive = plistlib.loads(subprocess.run(f"diskutil info -plist {self.root_mount_path}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
                    umount_drive = umount_drive["VolumeName"]
                    self.elevated(["umount", f'/Volumes/{umount_drive}'], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                    self.elevated(["mount", "-t", "apfs", "-rw", f"/dev/{self.root_mount_path}", self.mount_location], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                else:
                    print("- Mounting drive as writable in OS")
                    self.elevated(["mount", "-o", "nobrowse", "-t", "apfs", f"/dev/{self.root_mount_path}", self.mount_location], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                if Path(self.mount_extensions).exists():
                    print("- Successfully mounted the Root Volume")
                    if patch is True:
                        self.patch_root_vol()
                        return True
                    else:
                        self.unpatch_root_vol()
                        return True
                else:
                    print("- Failed to mount the Root Volume")
                    print("- Recommend rebooting the machine and trying to patch again")
                    input("- Press [ENTER] to exit")
        else:
            print("- Could not find root volume")
            input("- Press [ENTER] to exit")

    def delete_old_binaries(self, vendor_patch):
        for delete_current_kext in vendor_patch:
            delete_path = Path(self.mount_extensions) / Path(delete_current_kext)
            if Path(delete_path).exists():
                print(f"- Deleting {delete_current_kext}")
                self.elevated(["sudo", "rm", "-R", delete_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            else:
                print(f"- Couldn't find {delete_current_kext}, skipping")

    def add_new_binaries(self, vendor_patch, vendor_location):
        for add_current_kext in vendor_patch:
            existing_path = Path(self.mount_extensions) / Path(add_current_kext)
            if Path(existing_path).exists():
                print(f"- Found conflicting kext, Deleting Root Volume's {add_current_kext}")
                self.elevated(["rm", "-R", existing_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print(f"- Adding {add_current_kext}")
            self.elevated(["cp", "-R", f"{vendor_location}/{add_current_kext}", self.mount_extensions], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            self.elevated(["chmod", "-Rf", "755", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            self.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def add_brightness_patch(self):
        print("- Merging legacy Brightness Control Patches")
        self.delete_old_binaries(ModelArray.DeleteBrightness)
        self.add_new_binaries(ModelArray.AddBrightness, self.constants.legacy_brightness)
        self.elevated(["ditto", self.constants.payload_apple_private_frameworks_path_brightness, self.mount_private_frameworks], stdout=subprocess.PIPE).stdout.decode().strip().encode()
        self.elevated(["chmod", "-Rf", "755", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
        self.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def gpu_accel_patches_11(self):
        igpu_vendor, igpu_device, igpu_acpi = DeviceProbe.pci_probe().gpu_probe("IGPU")
        dgpu_vendor, dgpu_device, dgpu_acpi = DeviceProbe.pci_probe().gpu_probe("GFX0")
        if dgpu_vendor:
            print(f"- Found GFX0: {dgpu_vendor}:{dgpu_device}")
            if dgpu_vendor == self.constants.pci_nvidia:
                if dgpu_device in PCIIDArray.nvidia_ids().tesla_ids or dgpu_device in PCIIDArray.nvidia_ids().fermi_ids:
                    print("- Merging legacy Nvidia Tesla and Fermi Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                    self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
                    self.added_kexts = True
                # TODO: Enable below code if macOS 12 drops support
                # elif dgpu_device in PCIIDArray.nvidia_ids().kepler_ids and self.constants.detected_os > self.constants.big_sur:
                #    print("- Merging legacy Nvidia Kepler Kexts and Bundles")
                #    self.add_new_binaries(ModelArray.AddNvidiaKeplerAccel11, self.constants.legacy_nvidia_kepler_path)
            elif dgpu_vendor == self.constants.pci_amd_ati:
                if dgpu_device in PCIIDArray.amd_ids().terascale_1_ids:
                    print("- Merging legacy AMD Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteAMDAccel11)
                    self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                    self.add_new_binaries(ModelArray.AddAMDAccel11, self.constants.legacy_amd_path)
                    self.added_kexts = True
                if self.model in ["MacBookPro8,2", "MacBookPro8,3"]:
                    # This is used for MacBookPro8,2/3 where dGPU is disabled via NVRAM and still requires AMD framebuffer
                    # For reference:
                    #- deMUX: Don't need the AMD patches
                    #- dGPUs enabled:  Don't install the AMD patches (Infinite login loop otherwise)
                    #- dGPUs disabled: Do need the AMD patches (Restores Brightness control)
                    dgpu_status: str = subprocess.run("nvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
                    if dgpu_status.startswith("FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs	%01"):
                        print("- Detected dGPU is disabled via NVRAM")
                        print("- Merging legacy AMD Kexts and Bundles")
                        self.delete_old_binaries(ModelArray.DeleteAMDAccel11)
                        self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                        self.add_new_binaries(ModelArray.AddAMDAccel11, self.constants.legacy_amd_path)
                        self.added_kexts = True
                    else:
                        print("- Cannot install Brightness Control, pleas ensure the dGPU is disabled via NVRAM")
        if igpu_vendor:
            print(f"- Found IGPU: {igpu_vendor}:{igpu_device}")
            if igpu_vendor == self.constants.pci_intel:
                if igpu_device in PCIIDArray.intel_ids().iron_ids:
                    print("- Merging legacy Intel 1st Gen Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                    self.add_new_binaries(ModelArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
                    self.added_kexts = True
                elif igpu_device in PCIIDArray.intel_ids().sandy_ids:
                    print("- Merging legacy Intel 2nd Gen Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                    self.add_new_binaries(ModelArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
                    self.added_kexts = True

                # TODO: Enable below code if macOS 12 drops support
                # elif igpu_device in PCIIDArray.intel_ids().ivy_ids:
                #    print("- Merging legacy Intel 3rd Gen Kexts and Bundles")
                #    self.add_new_binaries(ModelArray.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)
            elif igpu_vendor == self.constants.pci_nvidia:
                if not dgpu_vendor:
                    # Avoid patching twice, as Nvidia iGPUs will only have Nvidia dGPUs
                    print("- Merging legacy Nvidia Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddGeneralAccel, self.constants.legacy_general_path)
                    self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
                    self.added_kexts = True

        if self.added_kexts == True:
            # Frameworks
            print("- Merging legacy Frameworks")
            self.elevated(["ditto", self.constants.payload_apple_frameworks_path_accel, self.mount_frameworks], stdout=subprocess.PIPE).stdout.decode().strip().encode()

            if self.model in ModelArray.LegacyBrightness:
                self.add_brightness_patch()

            # LaunchDaemons
            if Path(self.mount_lauchd / Path("HiddHack.plist")).exists():
                print("- Removing legacy HiddHack")
                self.elevated(["rm", f"{self.mount_lauchd}/HiddHack.plist"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print("- Adding IOHID-Fixup.plist")
            self.elevated(["ditto", self.constants.payload_apple_lauchd_path_accel, self.mount_lauchd], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            self.elevated(["chmod", "755", f"{self.mount_lauchd}/IOHID-Fixup.plist"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            self.elevated(["chown", "root:wheel", f"{self.mount_lauchd}/IOHID-Fixup.plist"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

            # PrivateFrameworks
            print("- Merging legacy PrivateFrameworks")
            self.elevated(["ditto", self.constants.payload_apple_private_frameworks_path_accel, self.mount_private_frameworks], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            # Sets AppKit to Catalina Window Drawing codepath
            # Disabled upon ASentientBot request
            # print("- Enabling NSDefenestratorModeEnabled")
            # subprocess.run("defaults write -g NSDefenestratorModeEnabled -bool true".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        else:
            print("- No Acceleration Kexts were installed, skipping remaining acceleration patches")

    def patch_root_vol(self):
        print(f"- Detecting patches for {self.model}")
        rebuild_required = False
        # TODO: Create Backup of S*/L*/Extensions, Frameworks and PrivateFramework to easily revert changes
        # APFS snapshotting seems to ignore System Volume changes inconsistently, would like a backup to avoid total brick
        # Perhaps a basic py2 script to run in recovery to restore
        # Ensures no .DS_Stores got in
        print("- Preparing Files")
        self.elevated(["find", self.constants.payload_apple_root_path, "-name", "'.DS_Store'", "-delete"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

        if self.model in ModelArray.LegacyGPU or self.constants.assume_legacy is True:
            dgpu_vendor, dgpu_device, dgpu_acpi = DeviceProbe.pci_probe().gpu_probe("GFX0")
            if (
                dgpu_vendor
                and dgpu_vendor == self.constants.pci_amd_ati
                and (
                    dgpu_device in PCIIDArray.amd_ids().polaris_ids
                    or dgpu_device in PCIIDArray.amd_ids().vega_ids
                    or dgpu_device in PCIIDArray.amd_ids().navi_ids
                    or dgpu_device in PCIIDArray.amd_ids().legacy_gcn_ids
                )
            ):
                print("- Detected Metal-based AMD GPU, skipping legacy patches")
            elif dgpu_vendor and dgpu_vendor == self.constants.pci_nvidia and dgpu_device in PCIIDArray.nvidia_ids().kepler_ids:
                print("- Detected Metal-based Nvidia GPU, skipping legacy patches")
            else:
                print("- Detected legacy GPU, attempting legacy acceleration patches")
                self.gpu_accel_patches_11()
                rebuild_required = True

        if self.model in ["iMac7,1", "iMac8,1"]:
            print("- Fixing Volume Control Support")
            self.delete_old_binaries(ModelArray.DeleteVolumeControl)
            self.add_new_binaries(ModelArray.AddVolumeControl, self.constants.audio_path)
            rebuild_required = True

        if rebuild_required is True:
            self.rebuild_snapshot()

    def unpatch_root_vol(self):
        print("- Reverting to last signed APFS snapshot")
        self.elevated(["bless", "--mount", self.mount_location, "--bootefi", "--last-sealed-snapshot"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def rebuild_snapshot(self):
        if self.constants.gui_mode is False:
            input("Press [ENTER] to continue with cache rebuild")
        print("- Rebuilding Kernel Cache (This may take some time)")
        result = self.elevated(["kmutil", "install", "--volume-root", self.mount_location, "--update-all"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if result.returncode != 0:
            self.success_status = False
            print("- Unable to build new kernel cache")
            print("\nPlease report this to Github")
            print("Reason for Patch Failure:")
            print(result.stdout.decode())
            print("")
        else:
            self.success_status = True
            print("- Successfully built new kernel cache")
            if self.constants.gui_mode is False:
                input("Press [ENTER] to continue with snapshotting")
            print("- Creating new APFS snapshot")
            self.elevated(["bless", "--folder", f"{self.mount_location}/System/Library/CoreServices", "--bootefi", "--create-snapshot"], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        self.elevated(["diskutil", "unmount", self.root_mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def check_status(self):
        nvram_dump = plistlib.loads(subprocess.run("nvram -x -p".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        try:
            self.sip_status = nvram_dump["csr-active-config"]
        except KeyError:
            self.sip_status = b"\x00\x00\x00\x00"

        self.smb_model: str = subprocess.run("nvram 94B73556-2197-4702-82A8-3E1337DAFBFB:HardwareModel	".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if not self.smb_model.startswith("nvram: Error getting variable"):
            self.smb_model = [line.strip().split(":HardwareModel	", 1)[1] for line in self.smb_model.split("\n") if line.strip().startswith("94B73556-2197-4702-82A8-3E1337DAFBFB:")][0]
            if self.smb_model.startswith("j137"):
                self.smb_status = True
            else:
                self.smb_status = False
        else:
            self.smb_status = False
        self.fv_status = True
        if self.constants.recovery_status == False:
            self.fv_status: str = subprocess.run("fdesetup status".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
            if self.fv_status.startswith("FileVault is Off"):
                self.fv_status = False
        else:
            # Assume FileVault is off for Recovery purposes
            self.fv_status = False
        self.csr_decode(False)

    def check_files(self):
        if Path(self.constants.payload_apple_root_path).exists():
            print("- Found Apple Binaries")
            if self.constants.gui_mode is False:
                patch_input = input("Would you like to redownload?(y/n): ")
                if patch_input in {"y", "Y", "yes", "Yes"}:
                    shutil.rmtree(Path(self.constants.payload_apple_root_path))
                    self.download_files()
            else:
                self.download_files()
        else:
            print("- Apple binaries missing")
            self.download_files()

    def download_files(self):
        Utilities.cls()
        print("- Downloading Apple binaries")
        popen_oclp = subprocess.Popen(
            ["curl", "-S", "-L", f"{self.constants.url_apple_binaries}{self.constants.payload_version}.zip", "--output", self.constants.payload_apple_root_path_zip],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for stdout_line in iter(popen_oclp.stdout.readline, ""):
            print(stdout_line, end="")
        popen_oclp.stdout.close()
        if self.constants.payload_apple_root_path_zip.exists():
            print("- Download completed")
            print("- Unzipping download...")
            try:
                subprocess.run(["unzip", self.constants.payload_apple_root_path_zip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.constants.payload_path).stdout.decode()
                print("- Renaming folder")
                os.rename(self.constants.payload_apple_root_path_unzip, self.constants.payload_apple_root_path)
                print("- Binaries downloaded to:")
                print(self.constants.payload_path)
                if self.constants.gui_mode is False:
                    input("Press [ENTER] to continue")
            except zipfile.BadZipFile:
                print("- Couldn't unzip")
            os.remove(self.constants.payload_apple_root_path_zip)
        else:
            print("- Download failed, please verify the below link works:")
            print(f"{self.constants.url_apple_binaries}{self.constants.payload_version}")

    def start_patch(self):
        # Check SIP
        # self.check_files()
        if self.constants.custom_model is not None:
            print("Root Patching must be done on target machine!")
        elif self.model in ModelArray.NoRootPatch11 and self.constants.assume_legacy is False:
            print("Root Patching not required for this machine!")
        elif self.model not in ModelArray.SupportedSMBIOS11 and self.constants.assume_legacy is False:
            print("Cannot run on this machine, model is unsupported!")
        elif self.constants.detected_os != self.constants.big_sur:
            print("Cannot run on this OS, requires macOS 11!")
        else:
            self.check_status()
            Utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                if self.constants.gui_mode is False:
                    input("\nPress [ENTER] to continue")
                self.check_files()
                if self.constants.payload_apple_root_path.exists():
                    if not self.find_mount_root_vol(True):
                        return
                    self.unmount_drive()
                    print("- Patching complete")
                    if self.success_status is True:
                        print("\nPlease reboot the machine for patches to take effect")
                    else:
                        print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
            if self.sip_patch_status is True:
                print("SIP set incorrectly, cannot patch on this machine!")
                print("Please disable SIP and SecureBootModel in Patcher Settings")
                self.csr_decode(True)
                print("")
            if self.smb_status is True:
                print("SecureBootModel set incorrectly, unable to patch!")
                print("Please disable SecureBootModel in Patcher Settings")
                print("")
            if self.fv_status is True:
                print("FileVault enabled, unable to patch!")
                print("Please disable FileVault in System Preferences")
                print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to go exit.")

    def start_unpatch(self):
        if self.constants.custom_model is not None:
            print("Unpatching must be done on target machine!")
        elif self.constants.detected_os != self.constants.big_sur:
            print("Cannot run on this OS, requires macOS 11!")
        else:
            self.check_status()
            Utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                if self.constants.gui_mode is False:
                    input("\nPress [ENTER] to continue")
                if not self.find_mount_root_vol(False):
                    return
                self.unmount_drive()
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")
            if self.sip_patch_status is True:
                print("SIP set incorrectly, cannot unpatch on this machine!")
                print("Please disable SIP and SecureBootModel in Patcher Settings")
                self.csr_decode(True)
                print("")
            if self.smb_status is True:
                print("SecureBootModel set incorrectly, unable to unpatch!")
                print("Please disable SecureBootModel in Patcher Settings")
                print("")
            if self.fv_status is True:
                print("FileVault enabled, unable to unpatch!")
                print("Please disable FileVault in System Preferences")
                print("")
        if self.constants.gui_mode is False:
            input("Press [Enter] to go exit.")
