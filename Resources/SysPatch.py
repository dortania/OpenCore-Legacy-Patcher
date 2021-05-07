# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
# Missing Features:
# - Full System/Library Snapshotting (need to research how Apple achieves this)
#   - Temporary Work-around: sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot
# - Work-around battery throttling on laptops with no battery (IOPlatformPluginFamily.kext/Contents/PlugIns/ACPI_SMC_PlatformPlugin.kext/Contents/Resources/)
from __future__ import print_function

import binascii
import plistlib
import shutil
import signal
import subprocess
import sys
import uuid
import zipfile
import os
from pathlib import Path
from datetime import date

from Resources import Constants, ModelArray, Utilities, DeviceProbe


class PatchSysVolume:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions

    def hexswap(self, input_hex: str):
        hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
        hex_rev = hex_pairs[::-1]
        hex_str = "".join(["".join(x) for x in hex_rev])
        return hex_str.upper()

    def csr_decode(self, sip_raw, print_status):
        sip_int = int.from_bytes(sip_raw, byteorder='little')
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
        if ((self.constants.csr_values["CSR_ALLOW_UNTRUSTED_KEXTS           "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_UNRESTRICTED_FS           "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_UNRESTRICTED_DTRACE       "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_UNRESTRICTED_NVRAM        "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_DEVICE_CONFIGURATION      "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_UNAPPROVED_KEXTS          "] is True) \
        and (self.constants.csr_values["CSR_ALLOW_EXECUTABLE_POLICY_OVERRIDE"] is True) \
        and (self.constants.csr_values["CSR_ALLOW_UNAUTHENTICATED_ROOT      "] is True)):
            self.sip_patch_status = False
        else:
            self.sip_patch_status = True

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
                    print("- Successfully mounted the Root Volume")
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
                subprocess.run(f"sudo chmod -Rf 755 {self.mount_extensions}/{add_current_kext}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                subprocess.run(f"sudo chown -Rf root:wheel {self.mount_extensions}/{add_current_kext}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
            else:
                print(f"- Adding {add_current_kext}")
                subprocess.run(f"sudo cp -R {vendor_location}/{add_current_kext} {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                subprocess.run(f"sudo chmod -Rf 755 {self.mount_extensions}/{add_current_kext}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                subprocess.run(f"sudo chown -Rf root:wheel {self.mount_extensions}/{add_current_kext}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def add_brightness_patch(self):
        print("- Merging legacy Brightness Control Patches")
        self.delete_old_binaries(ModelArray.DeleteBrightness)
        self.add_new_binaries(ModelArray.AddBrightness, self.constants.legacy_brightness)
        subprocess.run(f"sudo ditto {self.constants.payload_apple_private_frameworks_path_brightness} {self.mount_private_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chmod -R 755 {self.mount_private_frameworks}/DisplayServices.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chown -R root:wheel {self.mount_private_frameworks}/DisplayServices.framework".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def gpu_accel_patches_11(self):
        igpu_vendor,igpu_device,igpu_acpi = DeviceProbe.pci_probe().gpu_probe("IGPU")
        dgpu_vendor,dgpu_device,dgpu_acpi = DeviceProbe.pci_probe().gpu_probe("GFX0")
        if dgpu_vendor:
            print(f"- Found GFX0: {dgpu_vendor}:{dgpu_device}")
            if dgpu_vendor == self.constants.pci_nvidia:
                #if self.nvidia_arch == self.constants.arch_kepler and self.constants.assume_legacy is True and self.constants.detected_os > self.constants.big_sur:
                #    print("- Merging legacy Nvidia Kepler Kexts and Bundles")
                #    self.add_new_binaries(ModelArray.AddNvidiaKeplerAccel11, self.constants.legacy_nvidia_kepler_path)
                #else:
                print("- Merging legacy Nvidia Tesla and Fermi Kexts and Bundles")
                self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
            elif dgpu_vendor == self.constants.pci_amd_ati:
                print("- Merging legacy AMD Kexts and Bundles")
                self.delete_old_binaries(ModelArray.DeleteAMDAccel11)
                self.add_new_binaries(ModelArray.AddAMDAccel11, self.constants.legacy_amd_path)
        if igpu_vendor:
            print(f"- Found IGPU: {igpu_vendor}:{igpu_device}")
            if igpu_vendor == self.constants.pci_intel:
                if igpu_device in ModelArray.IronLakepciid:
                    print("- Merging legacy Intel 1st Gen Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
                elif igpu_device in ModelArray.SandyBridgepiciid:
                    print("- Merging legacy Intel 2nd Gen Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
                    #if self.model in ModelArray.LegacyGPUAMDIntelGen2:
                        # Swap custom AppleIntelSNBGraphicsFB-AMD.kext, required to fix linking
                    #    subprocess.run(f"sudo rm -R {self.mount_extensions}/AppleIntelSNBGraphicsFB.kext".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
                    #    subprocess.run(f"sudo cp -R {self.constants.legacy_amd_path}/AMD-Link/AppleIntelSNBGraphicsFB.kext {self.mount_extensions}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

                # Code for when Ivy Bridge binares are presumably removed from macOS 12, code currently
                #elif igpu_device in ModelArray.IvyBridgepciid:
                #    print("- Merging legacy Intel 3rd Gen Kexts and Bundles")
                #    self.add_new_binaries(ModelArray.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)
            elif igpu_vendor == self.constants.pci_nvidia:
                if not dgpu_vendor:
                    # Avoid patching twice, as Nvidia iGPUs will only have Nvidia dGPUs
                    print("- Merging legacy Nvidia Kexts and Bundles")
                    self.delete_old_binaries(ModelArray.DeleteNvidiaAccel11)
                    self.add_new_binaries(ModelArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)

        # Frameworks
        print("- Merging legacy Frameworks")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_frameworks_path_accel} {self.mount_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        if self.model in ModelArray.LegacyBrightness:
            self.add_brightness_patch()

        # LaunchDaemons
        if Path(self.mount_lauchd / Path("HiddHack.plist")).exists():
            print("- Removing legacy HiddHack")
            subprocess.run(f"sudo rm {self.mount_lauchd}/HiddHack.plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        print("- Adding IOHID-Fixup.plist")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_lauchd_path_accel} {self.mount_lauchd}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chmod 755 {self.mount_lauchd}/IOHID-Fixup.plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()
        subprocess.run(f"sudo chown root:wheel {self.mount_lauchd}/IOHID-Fixup.plist".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # PrivateFrameworks
        print("- Merging legacy PrivateFrameworks")
        subprocess.run(f"sudo ditto {self.constants.payload_apple_private_frameworks_path_accel} {self.mount_private_frameworks}".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        # Sets AppKit to Catalina Window Drawing codepath
        # Disabled upon ASentientBot request
        print("- Enabling NSDefenestratorModeEnabled")
        subprocess.run("defaults write -g NSDefenestratorModeEnabled -bool true".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def patch_root_vol(self):
        print(f"- Detecting patches for {self.model}")
        rebuild_required = False
        # TODO: Create Backup of S*/L*/Extensions, Frameworks and PrivateFramework to easily revert changes
        # APFS snapshotting seems to ignore System Volume changes inconsistently, would like a backup to avoid total brick
        # Perhaps a basic py2 script to run in recovery to restore
        # Ensures no .DS_Stores got in
        print("- Preparing Files")
        subprocess.run(f"sudo find {self.constants.payload_apple_root_path} -name '.DS_Store' -delete".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

        if self.model in ModelArray.LegacyGPU or self.constants.assume_legacy is True:
            dgpu_vendor,dgpu_device,dgpu_acpi = DeviceProbe.pci_probe().gpu_probe("GFX0")
            if dgpu_vendor and dgpu_vendor == self.constants.pci_amd_ati and dgpu_device in ModelArray.AMDMXMGPUs:
                print("- Detected Metal-based AMD GPU, skipping legacy patches")
            elif dgpu_vendor and dgpu_vendor == self.constants.pci_nvidia and dgpu_device in ModelArray.NVIDIAMXMGPUs:
                print("- Detected Metal-based Nvidia GPU, skipping legacy patches")
            else:
                print("- Detected legacy GPU, attempting legacy acceleration patches")
                self.gpu_accel_patches_11()
                rebuild_required = True

        #if self.model == "iMac7,1":
        #    print("- Fixing Volume Control Support")
        #    self.add_new_binaries(ModelArray.AddVolumeControl, self.constants.audio_path)

        if rebuild_required is True:
            self.rebuild_snapshot()

    def unpatch_root_vol(self):
        print("- Reverting to last signed APFS snapshot")
        subprocess.run(f"sudo bless --mount {self.mount_location} --bootefi --last-sealed-snapshot".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def rebuild_snapshot(self):
        if self.constants.gui_mode is False:
            input("Press [ENTER] to continue with cache rebuild")
        print("- Rebuilding Kernel Cache (This may take some time)")
        result = subprocess.run(f"sudo kmutil install --volume-root {self.mount_location} --update-all".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if result.returncode != 0:
            self.sucess_status = False
            print("- Unable to build new kernel cache")
            print("\nPlease report this to Github")
            print("Reason for Patch Failure:")
            print(result.stdout.decode())
            print("")
        else:
            self.sucess_status = True
            print("- Successfully built new kernel cache")
            if self.constants.gui_mode is False:
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
        popen_oclp = subprocess.Popen(f"curl -S -L {self.constants.url_apple_binaries}{self.constants.payload_version}.zip --output {self.constants.payload_apple_root_path_zip}".split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for stdout_line in iter(popen_oclp.stdout.readline, ""):
            print(stdout_line, end="")
        popen_oclp.stdout.close()
        if self.constants.payload_apple_root_path_zip.exists():
            print("- Download completed")
            print("- Unzipping download...")
            try:
                subprocess.run(f"unzip {self.constants.payload_apple_root_path_zip}".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.constants.payload_path).stdout.decode()
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
        elif self.constants.detected_os < self.constants.big_sur:
            print(f"Cannot run on this OS, requires macOS 11!")
        else:
            self.check_status()
            Utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                if self.constants.gui_mode is False:
                    input("\nPress [ENTER] to continue")
                self.check_files()
                if self.constants.payload_apple_root_path.exists():
                    self.find_mount_root_vol(True)
                    self.unmount_drive()
                    print("- Patching complete")
                    if self.sucess_status is True:
                        print("\nPlease reboot the machine for patches to take effect")
                    else:
                        print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
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
        if self.constants.gui_mode is False:
            input("Press [Enter] to go exit.")

    def start_unpatch(self):
        if self.constants.custom_model is not None:
            print("Unpatching must be done on target machine!")
        elif self.constants.detected_os < self.constants.big_sur:
            print(f"Cannot run on this OS, requires macOS 11!")
        else:
            self.check_status()
            Utilities.cls()
            if (self.sip_patch_status is False) and (self.smb_status is False):
                print("- Detected SIP and SecureBootModel are disabled, continuing")
                if self.constants.gui_mode is False:
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
        if self.constants.gui_mode is False:
            input("Press [Enter] to go exit.")
