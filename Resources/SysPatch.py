# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
# Missing Features:
# - Full System/Library Snapshotting (need to research how Apple achieves this)
#   - Temorary Work-around: sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot
# - Work-around battery throttling on laptops with no battery (IOPlatformPluginFamily.kext/Contents/PlugIns/ACPI_SMC_PlatformPlugin.kext/Contents/Resources/)
# - Add kmutil error checking
from __future__ import print_function

import binascii
import plistlib
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path
from datetime import date

from Resources import Constants, ModelArray, utilities


class PatchSysVolume:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions

    def csr_decode(self, sip_raw, print_status):
        sip_int = int.from_bytes(sip_raw, byteorder='little')
        i = 0
        for current_sip_bit in self.constants.csr_values:
            if sip_int & (1 << i):
                temp = True
                # The below array are values that don't affect the ability to patch
                if current_sip_bit not in ["CSR_ALLOW_TASK_FOR_PID              ", "CSR_ALLOW_KERNEL_DEBUGGER           ", "CSR_ALLOW_APPLE_INTERNAL            ", "CSR_ALLOW_ANY_RECOVERY_OS           ",]:
                    self.sip_patch_status = False
            else:
                temp = False
            if print_status is True:
                print(f"- {current_sip_bit}\t {temp}")
            i = i + 1

    def find_mount_root_vol(self, patch):
        root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        self.root_mount_path = root_partition_info["DeviceIdentifier"]
        self.mount_location = "/System/Volumes/Update/mnt1"
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
        self.mount_frameworks = f"{self.mount_location}/System/Library/Frameworks"
        self.mount_lauchd = f"{self.mount_location}/System/Library/LaunchDaemons"
        self.mount_private_frameworks = f"{self.mount_location}/System/Library/PrivateFrameworks"

        if self.root_mount_path.startswith("disk"):
            self.root_mount_path = self.root_mount_path[:-2] if self.root_mount_path.endswith('s1') else self.root_mount_path
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                if patch is True:
                    self.patch_root_vol()
                else:
                    self.unpatch_root_vol()
            else:
                print("- Mounting drive as writable")
                subprocess.run(f"sudo mount -o nobrowse -t apfs /dev/{self.root_mount_path} {self.mount_location}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                if Path(self.mount_extensions).exists():
                    print("- Sucessfully mounted the Root Volume")
                    if patch is True:
                        self.patch_root_vol()
                    else:
                        self.unpatch_root_vol()
                else:
                    print("- Failed to mount the Root Volume")
        else:
            print("- Could not find root volume")

    def delete_old_binaries(self, vendor_patch):
        for delete_current_kext in vendor_patch:
            delete_path = Path(self.mount_extensions) / Path(delete_current_kext)
            if Path(delete_path).exists():
                print(f"- Deleting {delete_current_kext}")
                subprocess.run(f"sudo rm -R {delete_path}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            else:
                print(f"- Couldn't find {delete_current_kext}, skipping")

    def add_new_binaries(self, vendor_patch, vendor_location):
        for add_current_kext in vendor_patch:
            existing_path = Path(self.mount_extensions) / Path(add_current_kext)
            if Path(existing_path).exists():
                print(f"- Found conflicting kext, Deleting Root Volume's {add_current_kext}")
                subprocess.run(f"sudo rm -R {existing_path}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                print(f"- Adding {add_current_kext}")
                subprocess.run(f"sudo cp -R {vendor_location}/{add_current_kext} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            else:
                print(f"- Adding {add_current_kext}")
                subprocess.run(f"sudo cp -R {vendor_location}/{add_current_kext} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def gpu_accel_patches_11(self):
        # TODO: Add proper hardware checks
        # Due to MUX-based laptops and headless iGPUs, it's difficult to determine what GPU is present
        # Fix would be to parse IOReg for both IGPU and GFX0
        if self.model in ModelArray.LegacyGPUNvidia:
            print("- Merging legacy Nvidia Kexts and Bundles")
            self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
            self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
        elif self.model in ModelArray.LegacyGPUAMD:
            print("- Merging legacy AMD Kexts and Bundles")
            self.delete_old_binaries(ModelArray.DeleteAMDAccel11)
            self.add_new_binaries(ModelArray.AddAMDAccel11, self.constants.legacy_amd_path)
        if self.model in ModelArray.LegacyGPUIntelGen1:
            print("- Merging legacy Intel 1st Gen Kexts and Bundles")
            self.add_new_binaries(ModelArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
        elif self.model in ModelArray.LegacyGPUIntelGen2:
            print("- Merging legacy Intel 2nd Gen Kexts and Bundles")
            self.add_new_binaries(ModelArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
        # iMac10,1 came in both AMD and Nvidia GPU models, so we must do hardware detection
        if self.model == "iMac10,1":
            if self.constants.current_gpuv == "AMD (0x1002)":
                print("- Merging legacy AMD Kexts and Bundles")
                self.delete_old_binaries(ModelArray.DeleteAMDAccel11)
                self.add_new_binaries(ModelArray.AddAMDAccel11, self.constants.legacy_amd_path)
            else:
                print("- Merging legacy Nvidia Kexts and Bundles")
                self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)

        # Frameworks
        print("- Merging legacy Frameworks")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_frameworks_path} {self.mount_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # LaunchDaemons
        print("- Adding HiddHack.plist")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_lauchd_path} {self.mount_lauchd}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chmod 755 {self.mount_lauchd}/HiddHack.plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chown root:wheel {self.mount_lauchd}/HiddHack.plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # PrivateFrameworks
        print("- Merging legacy PrivateFrameworks")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_private_frameworks_path} {self.mount_private_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Sets AppKit to Catalina Window Drawing codepath
        print("- Disabling NSDefenestratorModeEnabled")
        subprocess.run("defaults write -g NSDefenestratorModeEnabled -bool false".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()


    def patch_root_vol(self):
        print(f"- Detecting patches for {self.model}")
        # TODO: Create Backup of S*/L*/Extensions, Frameworks and PrivateFramework to easily revert changes
        # APFS snapshotting seems to ignore System Volume changes inconcistently, would like a backup to avoid total brick
        # Perhaps a basic py2 script to run in recovery to restore
        print("- Creating backup snapshot of user data (This may take some time)")
        subprocess.run("tmutil snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        # Ensures no .DS_Stores got in
        print("- Preparing Files")
        subprocess.run(f"sudo find {self.constants.payload_apple_root_path} -name '.DS_Store' -delete".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        current_gpu: str = subprocess.run("system_profiler SPDisplaysDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        self.constants.current_gpuv = [line.strip().split(": ", 1)[1] for line in current_gpu.split("\n") if line.strip().startswith(("Vendor"))][0]
        self.constants.current_gpud = [line.strip().split(": ", 1)[1] for line in current_gpu.split("\n") if line.strip().startswith(("Device ID"))][0]

        # Start Patch engine
        if self.model in ModelArray.LegacyAudio:
            print("- Attempting AppleHDA Patch")
            subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleHDA.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(f"sudo cp -R {self.constants.applehda_path} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            rebuild_required = True

        if self.model in ModelArray.EthernetBroadcom:
            print("- Attempting AppleBCM5701Ethernet Patch")
            subprocess.run(f"sudo rm -R {self.mount_extensions}/IONetworkingFamily.kext/Contents/PlugIns/AppleBCM5701Ethernet.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            subprocess.run(f"sudo cp -R {self.constants.applebcm_path} {self.mount_extensions}/IONetworkingFamily.kext/Contents/PlugIns/".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            rebuild_required = True

        if (self.model in ModelArray.LegacyGPU) and (Path(self.constants.hiddhack_path).exists()):
            print(f"- Detected GPU: {self.constants.current_gpuv} {self.constants.current_gpud}")
            if (self.constants.current_gpuv == "AMD (0x1002)") & (self.constants.current_gpud in ModelArray.AMDMXMGPUs):
                print("- Detected Metal-based AMD GPU, skipping legacy patches")
            elif (self.constants.current_gpuv == "NVIDIA (0x10de)") & (self.constants.current_gpud in ModelArray.NVIDIAMXMGPUs):
                print("- Detected Metal-based Nvidia GPU, skipping legacy patches")
            else:
                print("- Detected legacy GPU, attempting legacy acceleration patches")
                self.gpu_accel_patches_11()
                rebuild_required = True

        if rebuild_required is True:
            self.rebuild_snapshot()

    def unpatch_root_vol(self):
        print("- Creating backup snapshot of user data (This may take some time)")
        subprocess.run("tmutil snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        print("- Reverting to last signed APFS snapshot")
        subprocess.run(f"sudo bless --mount {self.mount_location} --bootefi --last-sealed-snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def rebuild_snapshot(self):
        input("Press [ENTER] to continue with cache rebuild")
        print("- Rebuilding Kernel Cache (This may take some time)")
        subprocess.run(f"sudo kmutil install --volume-root {self.mount_location} --update-all".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        input("Press [ENTER] to continue with snapshotting")
        print("- Creating new APFS snapshot")
        subprocess.run(f"sudo bless --folder {self.mount_location}/System/Library/CoreServices --bootefi --create-snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        subprocess.run(f"sudo diskutil unmount {self.root_mount_path}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def check_status(self):
        nvram_dump = plistlib.loads(subprocess.run("nvram -x -p".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        try:
            self.sip_status = nvram_dump["csr-active-config"]
        except KeyError:
            self.sip_status = b'\x00\x00\x00\x00'

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
        self.fv_status: str = subprocess.run("fdesetup status".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if self.fv_status.startswith("FileVault is Off"):
            self.fv_status = False
        else:
            self.fv_status = True
        self.sip_patch_status = True
        self.csr_decode(self.sip_status, False)

    def start_patch(self):
        # Check SIP
        if self.constants.custom_model is not None:
            print("Root Patching must be done on target machine!")
        elif self.model in ModelArray.NoRootPatch11:
            print("Root Patching not required for this machine!")
        elif self.model not in ModelArray.SupportedSMBIOS:
            print("Cannot run on this machine, model is unsupported!")
        elif self.constants.detected_os < 20:
            print(f"Cannot run on this OS! Kernel detected: {self.constants.detected_os}")
        else:
            self.check_status()
            utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                input("\nPress [ENTER] to continue")
                self.find_mount_root_vol(True)
                self.unmount_drive()
                print("- Patching complete")
                print("\nPlease reboot the machine for patches to take effect")
            if self.sip_patch_status is True:
                print("SIP set incorrectly, cannot patch on this machine!")
                print("Please disable SIP and SecureBootModel in Patcher Settings")
                self.csr_decode(self.sip_status, True)
                print("")
            if self.smb_status is True:
                print("SecureBootModel set incorrectly, unable to patch!")
                print("Please disable SecureBootModel in Patcher Settings")
                print("")
            if self.fv_status is True:
                print("FileVault enabled, unable to patch!")
                print("Please disable FileVault in System Preferences")
                print("")
        input("Press [Enter] to go exit.")
    def start_unpatch(self):
        if self.constants.custom_model is not None:
            print("Unpatching must be done on target machine!")
        elif self.constants.detected_os < 20:
            print(f"Cannot run on this OS! Kernel detected: {self.constants.detected_os}")
        else:
            self.check_status()
            utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                input("\nPress [ENTER] to continue")
                self.find_mount_root_vol(False)
                self.unmount_drive()
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")
            if self.sip_patch_status is True:
                print("SIP set incorrectly, cannot unpatch on this machine!")
                print("Please disable SIP and SecureBootModel in Patcher Settings")
                self.csr_decode(self.sip_status, True)
                print("")
            if self.smb_status is True:
                print("SecureBootModel set incorrectly, unable to unpatch!")
                print("Please disable SecureBootModel in Patcher Settings")
                print("")
            if self.fv_status is True:
                print("FileVault enabled, unable to unpatch!")
                print("Please disable FileVault in System Preferences")
                print("")
        input("Press [Enter] to go exit.")

