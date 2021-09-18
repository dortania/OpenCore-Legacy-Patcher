# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2021, Dhinak G, Mykola Grymalyuk
# Missing Features:
# - Full System/Library Snapshotting (need to research how Apple achieves this)
#   - Temporary Work-around: sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot
# - Work-around battery throttling on laptops with no battery (IOPlatformPluginFamily.kext/Contents/PlugIns/ACPI_SMC_PlatformPlugin.kext/Contents/Resources/)

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from Resources import Constants, device_probe, ModelArray, SysPatchArray, Utilities


class PatchSysVolume:
    def __init__(self, model, versions):
        self.model = model
        self.constants: Constants.Constants = versions
        self.computer = self.constants.computer
        self.root_mount_path = None
        self.sip_enabled = True
        self.sbm_enabled = True
        self.amfi_enabled = True
        self.fv_enabled = True
        self.dosdude_patched = True
        self.nvidia_legacy = False
        self.amd_ts1 = False
        self.amd_ts2 = False
        self.iron_gpu = False
        self.sandy_gpu = False
        self.ivy_gpu = False
        self.brightness_legacy = False
        self.legacy_audio = False
        self.legacy_wifi = False
        self.added_legacy_kexts = False
        self.amfi_must_disable = False
        self.check_board_id = False
        self.bad_board_id = False
        self.no_patch = True
        self.validate = False

        # if (Path.home() / "Desktop/OCLP-Test/").exists:
        #    self.mount_location = Path.home() / "Desktop/OCLP-Test"
        #    self.validate = True
        if self.constants.detected_os > self.constants.catalina:
            # Big Sur and newer use APFS snapshots
            self.mount_location = "/System/Volumes/Update/mnt1"
        else:
            self.mount_location = ""
        self.mount_coreservices = f"{self.mount_location}/System/Library/CoreServices"
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
        self.mount_frameworks = f"{self.mount_location}/System/Library/Frameworks"
        self.mount_lauchd = f"{self.mount_location}/System/Library/LaunchDaemons"
        self.mount_private_frameworks = f"{self.mount_location}/System/Library/PrivateFrameworks"
        self.mount_libexec = f"{self.mount_location}/usr/libexec"

    def elevated(self, *args, **kwargs) -> subprocess.CompletedProcess:
        if os.getuid() == 0 or self.constants.gui_mode is True:
            return subprocess.run(*args, **kwargs)
        else:
            return subprocess.run(["sudo"] + [args[0][0]] + args[0][1:], **kwargs)

    def find_mount_root_vol(self, patch):
        self.root_mount_path = Utilities.get_disk_path()
        if self.root_mount_path.startswith("disk"):
            if self.constants.detected_os == self.constants.catalina and self.validate is False:
                print("- Mounting Catalina Root Volume as writable")
                self.elevated(["mount", "-uw", f"{self.mount_location}/"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                if patch is True:
                    if self.constants.detected_os < self.constants.big_sur or (self.constants.detected_os == self.constants.big_sur and Utilities.check_seal() is True):
                        self.backup_volume()
                    self.patch_root_vol()
                    return True
                else:
                    self.unpatch_root_vol()
                    return True
            else:
                if self.constants.detected_os > self.constants.catalina:
                    print("- Mounting APFS Snapshot as writable")
                    self.elevated(["mount", "-o", "nobrowse", "-t", "apfs", f"/dev/{self.root_mount_path}", self.mount_location], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                if Path(self.mount_extensions).exists():
                    print("- Successfully mounted the Root Volume")
                    if patch is True:
                        if self.constants.detected_os < self.constants.big_sur or (self.constants.detected_os == self.constants.big_sur and Utilities.check_seal() is True):
                            self.backup_volume()
                        self.patch_root_vol()
                        return True
                    else:
                        self.unpatch_root_vol()
                        return True
                else:
                    print("- Failed to mount the Root Volume")
                    print("- Recommend rebooting the machine and trying to patch again")
                    if self.constants.gui_mode is False:
                        input("- Press [ENTER] to exit: ")
        else:
            print("- Could not find root volume")
            if self.constants.gui_mode is False:
                input("- Press [ENTER] to exit: ")

    def backup_volume(self):
        for location in SysPatchArray.BackupLocations:
            Utilities.cls()
            print("Backing up root volume before patching (This may take some time)")
            print(f"- Attempting to backup {location}")
            location_zip = f"{location}-Backup.zip"
            location_zip_path = Path(self.mount_location) / Path(location_zip)

            if location_zip_path.exists():
                print(f"- Found existing {location_zip}, skipping")
            else:
                print(f"- Backing up {location}")
                # cp -r ./Extensions ./Extensions-Backup
                # ditto -c -k --sequesterRsrc --keepParent ./Extensions-Backup ./Extensions-Backup.zip
                # rm -r ./Extensions-Backup

                print("- Creating Backup folder")
                Utilities.process_status(
                    self.elevated(
                        ["cp", "-r", f"{self.mount_location}/{location}", f"{self.mount_location}/{location}-Backup"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )
                print("- Zipping Backup folder")
                Utilities.process_status(
                    self.elevated(
                        ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", f"{self.mount_location}/{location}-Backup", f"{self.mount_location}/{location_zip}"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )

                print("- Removing Backup folder")
                Utilities.process_status(
                    self.elevated(
                        ["rm", "-r", f"{self.mount_location}/{location}-Backup"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )

    def manual_root_patch_revert(self):
        print("- Attempting to revert patches")
        if (Path(self.mount_location) / Path("/System/Library/Extensions-Backup.zip")).exists():
            print("- Verified manual unpatching is available")

            for location in SysPatchArray.BackupLocations:
                Utilities.cls()
                print("Reverting root volume patches (This may take some time)")

                print(f"- Attempting to unpatch {location}")
                location_zip = f"/{location}-Backup.zip"
                location_zip_path = Path(self.mount_location) / Path(location_zip)
                location_old_path = Path(self.mount_location) / Path(location)

                if "PrivateFrameworks" in location:
                    copy_path = Path(self.mount_location) / Path("/System/Library/PrivateFrameworks")
                elif "Frameworks" in location:
                    copy_path = Path(self.mount_location) / Path("/System/Library/Frameworks")
                else:
                    copy_path = Path(self.mount_location) / Path("/System/Library")

                if location_zip_path.exists():
                    print(f"- Found {location_zip}")

                    print(f"- Unzipping {location_zip}")
                    Utilities.process_status(self.elevated(["unzip", location_zip_path, "-d", copy_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    if location_old_path.exists():
                        print(f"- Renaming {location}")
                        Utilities.process_status(self.elevated(["mv", location_old_path, f"{location_old_path}-Patched"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    print(f"- Renaming {location}-Backup")
                    Utilities.process_status(self.elevated(["mv", f"{location_old_path}-Backup", location_old_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    print(f"- Removing {location_old_path}-Patched")
                    Utilities.process_status(self.elevated(["rm", "-r", f"{location_old_path}-Patched"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    # ditto will create a '__MACOSX' folder
                    # print("- Removing __MACOSX folder")
                    # Utilities.process_status(self.elevated(["rm", "-r", f"{copy_path}/__MACOSX"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                else:
                    print(f"- Failed to find {location_zip}, unable to unpatch")
            if self.validate is False:
                self.rebuild_snapshot()
        else:
            print("- Could not find Extensions.zip, cannot manually unpatch root volume")

    def unpatch_root_vol(self):
        if self.constants.detected_os > self.constants.catalina:
            print("- Reverting to last signed APFS snapshot")
            result = self.elevated(["bless", "--mount", self.mount_location, "--bootefi", "--last-sealed-snapshot"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("- Unable to revert root volume patches")
                print("Reason for unpatch Failure:")
                print(result.stdout.decode())
                print("- Failed to revert snapshot via bless, falling back on manual restoration")
                self.manual_root_patch_revert()
            else:
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")
        else:
            self.manual_root_patch_revert()

    def rebuild_snapshot(self):
        if self.constants.gui_mode is False:
            input("Press [ENTER] to continue with cache rebuild: ")
        print("- Rebuilding Kernel Cache (This may take some time)")
        if self.constants.detected_os > self.constants.catalina:
            result = self.elevated(["kmutil", "install", "--volume-root", self.mount_location, "--update-all"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            result = self.elevated(["kextcache", "-i", f"{self.mount_location}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # kextcache always returns 0, even if it fails
        # Check the output for 'KernelCache ID' to see if the cache was successfully rebuilt
        if result.returncode != 0 or (self.constants.detected_os < self.constants.catalina and "KernelCache ID" not in result.stdout.decode()):
            self.success_status = False
            print("- Unable to build new kernel cache")
            print("\nPlease report this to Github")
            print("Reason for Patch Failure:")
            print(result.stdout.decode())
            print("")
            print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
            if self.constants.gui_mode is False:
                input("Press [ENTER] to continue")
        else:
            self.success_status = True
            print("- Successfully built new kernel cache")
            if self.constants.gui_mode is False:
                if self.constants.detected_os > self.constants.catalina:
                    input("Press [ENTER] to continue with snapshotting")
                else:
                    input("Press [ENTER] to continue with kernel and dyld cache merging")
            if self.constants.detected_os > self.constants.catalina:
                print("- Creating new APFS snapshot")
                self.elevated(["bless", "--folder", f"{self.mount_location}/System/Library/CoreServices", "--bootefi", "--create-snapshot"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
                self.unmount_drive()
            else:
                if self.constants.detected_os == self.constants.catalina:
                    print("- Merging kernel cache")
                    Utilities.process_status(self.elevated(["kcditto"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
                print("- Merging dyld cache")
                Utilities.process_status(self.elevated(["update_dyld_shared_cache", "-root", f"{self.mount_location}/"]))
            print("- Patching complete")
            print("\nPlease reboot the machine for patches to take effect")
            if self.amd_ts2 is True and self.constants.allow_ts2_accel is True:
                print(
                    """\nPlease note that with ATI TeraScale 2 GPUs, you may experience colour strobing
on reboot. Please use SwitchResX or ResXtreme to force 1 million colours on your
monitor to fix this. If you are epileptic, please ask for someone to aid you or
set million colour before rebooting"""
                )
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to continue")

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        self.elevated(["diskutil", "unmount", self.root_mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def delete_old_binaries(self, vendor_patch):
        for delete_current_kext in vendor_patch:
            delete_path = Path(self.mount_extensions) / Path(delete_current_kext)
            if Path(delete_path).exists():
                print(f"- Deleting {delete_current_kext}")
                Utilities.process_status(self.elevated(["rm", "-R", delete_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print(f"- Couldn't find {delete_current_kext}, skipping")

    def add_new_binaries(self, vendor_patch, vendor_location):
        for add_current_kext in vendor_patch:
            existing_path = Path(self.mount_extensions) / Path(add_current_kext)
            if Path(existing_path).exists():
                print(f"- Found conflicting kext, Deleting Root Volume's {add_current_kext}")
                Utilities.process_status(self.elevated(["rm", "-R", existing_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            print(f"- Adding {add_current_kext}")
            Utilities.process_status(self.elevated(["cp", "-R", f"{vendor_location}/{add_current_kext}", self.mount_extensions], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            Utilities.process_status(self.elevated(["chmod", "-Rf", "755", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            Utilities.process_status(self.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def add_brightness_patch(self):
        self.delete_old_binaries(SysPatchArray.DeleteBrightness)
        self.add_new_binaries(SysPatchArray.AddBrightness, self.constants.legacy_brightness)
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_brightness}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        Utilities.process_status(self.elevated(["chmod", "-Rf", "755", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        Utilities.process_status(self.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def add_audio_patch(self):
        self.delete_old_binaries(SysPatchArray.DeleteVolumeControl)
        self.add_new_binaries(SysPatchArray.AddVolumeControl, self.constants.audio_path)
    
    def add_wifi_patch(self):
        print("- Merging Wireless CoreSerices patches")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_wifi_coreservices}/", self.mount_coreservices], stdout=subprocess.PIPE)
        print("- Merging Wireless usr/libexec patches")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_wifi_libexec}/", self.mount_libexec], stdout=subprocess.PIPE)
        

    def gpu_accel_legacy(self):
        if self.constants.detected_os == self.constants.mojave:
            print("- Installing General Acceleration Kext patches for Mojave")
            self.add_new_binaries(SysPatchArray.AddGeneralAccelMojave, self.constants.legacy_general_path)
        elif self.constants.detected_os == self.constants.catalina:
            print("- Installing General Acceleration Kext patches for Catalina")
            self.add_new_binaries(SysPatchArray.AddGeneralAccelCatalina, self.constants.legacy_general_path)
        elif self.constants.detected_os in [self.constants.big_sur, self.constants.monterey]:
            print("- Installing General Acceleration Kext patches for Big Sur/Monterey")
            self.add_new_binaries(SysPatchArray.AddGeneralAccel, self.constants.legacy_general_path)

    # Nvidia
    def gpu_accel_legacy_nvidia_master(self):
        if self.constants.detected_os in [self.constants.mojave, self.constants.catalina]:
            print("- Installing Nvidia Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddNvidiaAccelLegacy, self.constants.legacy_nvidia_path)
        elif self.constants.detected_os in [self.constants.big_sur, self.constants.monterey]:
            print("- Installing Nvidia Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(SysPatchArray.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
        else:
            print("- Installing basic Nvidia Framebuffer Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddNvidiaBrightness, self.constants.legacy_nvidia_path)

    # AMD/ATI
    def gpu_accel_legacy_ts1_master(self):
        if self.constants.detected_os in [self.constants.mojave, self.constants.catalina]:
            print("- Installing TeraScale 1 Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddAMDAccelLegacy, self.constants.legacy_amd_path)
        elif self.constants.detected_os in [self.constants.big_sur, self.constants.monterey]:
            print("- Installing TeraScale 1 Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(SysPatchArray.DeleteAMDAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddAMDAccel11, self.constants.legacy_amd_path)
        else:
            print("- Installing basic TeraScale 1 Framebuffer Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddAMDBrightness, self.constants.legacy_amd_path)

    def gpu_accel_legacy_ts2_master(self):
        if self.constants.detected_os in [self.constants.mojave, self.constants.catalina] and self.constants.allow_ts2_accel is True:
            print("- Installing TeraScale 2 Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddAMDAccelLegacy, self.constants.legacy_amd_path)
        elif self.constants.detected_os == self.constants.big_sur and self.constants.allow_ts2_accel is True:
            # TODO: Enable for Monterey when acceleration patches proress
            print("- Installing TeraScale 2 Acceleration Kext patches for Big Sur")
            self.delete_old_binaries(SysPatchArray.DeleteAMDAccel11)
            self.delete_old_binaries(SysPatchArray.DeleteAMDAccel11TS2)
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddAMDAccel11, self.constants.legacy_amd_path)
        else:
            print("- Installing basic TeraScale 2 Framebuffer Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddAMDBrightness, self.constants.legacy_amd_path)

    # Intel
    def gpu_accel_legacy_ironlake_master(self):
        if self.constants.detected_os in [self.constants.mojave, self.constants.catalina]:
            print("- Installing Ironlake Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
        elif self.constants.detected_os in [self.constants.big_sur, self.constants.monterey]:
            print("- Installing Ironlake Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(SysPatchArray.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
        else:
            print("- Installing basic Ironlake Framebuffer Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)

    def gpu_accel_legacy_sandybridge_master(self):
        if self.constants.detected_os in [self.constants.mojave, self.constants.catalina]:
            print("- Installing Sandy Bridge Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
        elif self.constants.detected_os in [self.constants.big_sur, self.constants.monterey]:
            print("- Installing Sandy Bridge Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(SysPatchArray.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(SysPatchArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
        else:
            print("- Installing basic Sandy Bridge Framebuffer Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)

    def gpu_framebuffer_ivybridge_master(self):
        if self.constants.detected_os == self.constants.monterey:
            print("- Installing IvyBridge Acceleration Kext patches for Monterey")
            self.add_new_binaries(SysPatchArray.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)
            if self.validate is False:
                print("- Fixing Acceleration in CoreMedia")
                Utilities.process_status(subprocess.run(["defaults", "write", "com.apple.coremedia", "hardwareVideoDecoder", "-string", "enable"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            print("- Merging Ivy Bridge Frameworks")
            self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ivy}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print("- Merging Ivy Bridge PrivateFrameworks")
            self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel_ivy}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        else:
            print("- Installing basic Ivy Bridge Kext patches for generic OS")
            self.add_new_binaries(SysPatchArray.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)

    def gpu_accel_legacy_extended(self):
        print("- Merging general legacy Frameworks")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if self.constants.detected_os > self.constants.big_sur:
            print("- Merging Monterey WebKit patch")
            self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ivy}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print("- Merging general legacy PrivateFrameworks")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        if self.constants.detected_os > self.constants.catalina:
            print("- Adding IOHID-Fixup.plist")
            Utilities.process_status(
                self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_lauchd_path_accel}/", self.mount_lauchd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            )
            Utilities.process_status(self.elevated(["chmod", "755", f"{self.mount_lauchd}/IOHID-Fixup.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            Utilities.process_status(self.elevated(["chown", "root:wheel", f"{self.mount_lauchd}/IOHID-Fixup.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            print("- Disabling Library Validation")
            Utilities.process_status(
                self.elevated(["defaults", "write", "/Library/Preferences/com.apple.security.libraryvalidation.plist", "-bool", "true"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            )

    def gpu_accel_legacy_extended_ts2(self):
        print("- Merging TeraScale 2 legacy Frameworks")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ts2}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print("- Merging TeraScale 2 PrivateFrameworks")
        self.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel_ts2}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        if self.validate is False:
            print("- Fixing Acceleration in CMIO")
            Utilities.process_status(subprocess.run(["defaults", "write", "com.apple.cmio", "CMIO_Unit_Input_ASC.DoNotUseOpenCL", "-bool", "true"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def patch_root_vol(self):
        print(f"- Running patches for {self.model}")
        # Graphics patches
        if self.nvidia_legacy is True:
            print("- Installing legacy Nvidia Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_nvidia_master()

        elif self.amd_ts1 is True:
            print("- Installing legacy TeraScale 1 Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_ts1_master()

        elif self.amd_ts2 is True:
            print("- Installing legacy TeraScale 2 Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_ts2_master()

        if self.iron_gpu is True:
            print("- Installing legacy Ironlake Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_ironlake_master()

        elif self.sandy_gpu is True:
            print("- Installing legacy Sandy Bridge Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_sandybridge_master()

        elif self.ivy_gpu is True:
            print("- Installing Ivy Bridge Patches")
            if self.constants.detected_os == self.constants.monterey:
                print("- Detected supported OS, installing Acceleration Patches")
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_framebuffer_ivybridge_master()

        if (
            self.amd_ts2 is True
            and self.constants.detected_os in self.constants.legacy_accel_support
            and self.constants.allow_ts2_accel is True
            and self.constants.detected_os != self.constants.monterey
        ):
            # TeraScale 2 patches must be installed after Intel HD3000
            self.add_new_binaries(SysPatchArray.AddAMDAccel11TS2, self.constants.legacy_amd_path_ts2)

        if self.added_legacy_kexts is True and self.constants.detected_os in self.constants.legacy_accel_support:
            self.gpu_accel_legacy_extended()
            if self.amd_ts2 is True and self.constants.allow_ts2_accel is True and self.constants.detected_os != self.constants.monterey:
                self.gpu_accel_legacy_extended_ts2()

        # Misc patches
        if self.brightness_legacy is True:
            print("- Installing legacy Brightness Control")
            self.add_brightness_patch()

        if self.legacy_audio is True:
            print("- Fixing Volume Control Support")
            self.add_audio_patch()
        
        if self.legacy_wifi is True:
            print("- Installing legacy Wireless support")
            self.add_wifi_patch()

        if self.validate is False:
            self.rebuild_snapshot()

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
        if self.constants.detected_os == self.constants.monterey:
            os_ver = "12-Monterey"
        elif self.constants.detected_os == self.constants.big_sur:
            os_ver = "11-Big-Sur"
        elif self.constants.detected_os == self.constants.catalina:
            os_ver = "10.15-Catalina"
        elif self.constants.detected_os == self.constants.mojave:
            os_ver = "10.14-Mojave"
        else:
            raise Exception(f"Unsupported OS: {self.constants.detected_os}")
        link = f"{self.constants.url_patcher_support_pkg}{self.constants.patcher_support_pkg_version}/{os_ver}.zip"

        if Path(self.constants.payload_apple_root_path).exists():
            print("- Removing old Apple Binaries folder")
            Path(self.constants.payload_apple_root_path).unlink()
        if Path(self.constants.payload_apple_root_path_zip).exists():
            print("- Removing old Apple Binaries zip")
            Path(self.constants.payload_apple_root_path_zip).unlink()

        local_zip = Path(self.constants.payload_path) / f"{os_ver}.zip"
        if Path(local_zip).exists():
            print(f"- Found local {os_ver} zip, skipping download")
            print(f"- Duplicating into Apple.zip")
            shutil.copy(local_zip, self.constants.payload_apple_root_path_zip)
        else:
            Utilities.download_file(link, self.constants.payload_apple_root_path_zip)

        if self.constants.payload_apple_root_path_zip.exists():
            print("- Download completed")
            print("- Unzipping download...")
            try:
                Utilities.process_status(subprocess.run(["unzip", self.constants.payload_apple_root_path_zip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.constants.payload_path))
                print("- Renaming folder")
                os.rename(self.constants.payload_path / Path(os_ver), self.constants.payload_apple_root_path)
                Path(self.constants.payload_apple_root_path_zip).unlink()
                print("- Binaries downloaded to:")
                print(self.constants.payload_path)
                if self.constants.gui_mode is False:
                    input("Press [ENTER] to continue")
            except zipfile.BadZipFile:
                print("- Couldn't unzip")
                return
        else:
            print("- Download failed, please verify the below link works:")
            print(link)
            input("Press [ENTER] to continue")

    def detect_gpus(self):
        dgpu = self.constants.computer.dgpu
        igpu = self.constants.computer.igpu
        if self.constants.moj_cat_accel is True:
            non_metal_os = self.constants.high_sierra
        else:
            non_metal_os = self.constants.catalina
        if dgpu:
            print(f"- Found GFX0: {Utilities.friendly_hex(dgpu.vendor_id)}:{Utilities.friendly_hex(dgpu.device_id)}")
            if dgpu.arch in [device_probe.NVIDIA.Archs.Tesla, device_probe.NVIDIA.Archs.Fermi]:
                if self.constants.detected_os > non_metal_os:
                    self.nvidia_legacy = True
                    self.amfi_must_disable = True
            elif dgpu.arch == device_probe.AMD.Archs.TeraScale_1:
                if self.constants.detected_os > non_metal_os:
                    self.amd_ts1 = True
                    self.amfi_must_disable = True
            elif dgpu.arch == device_probe.AMD.Archs.TeraScale_2:
                if self.constants.detected_os > non_metal_os:
                    self.amd_ts2 = True
                    self.amfi_must_disable = True
        if igpu and igpu.class_code != 0xFFFFFF:
            print(f"- Found IGPU: {Utilities.friendly_hex(igpu.vendor_id)}:{Utilities.friendly_hex(igpu.device_id)}")
            if igpu.arch == device_probe.Intel.Archs.Iron_Lake:
                if self.constants.detected_os > non_metal_os:
                    self.iron_gpu = True
                    self.amfi_must_disable = True
            elif igpu.arch == device_probe.Intel.Archs.Sandy_Bridge:
                if self.constants.detected_os > non_metal_os:
                    self.sandy_gpu = True
                    self.amfi_must_disable = True
                    self.check_board_id = True
            elif igpu.arch == device_probe.Intel.Archs.Ivy_Bridge:
                if self.constants.detected_os > self.constants.big_sur:
                    self.ivy_gpu = True
            elif isinstance(igpu, device_probe.NVIDIA):
                if self.constants.detected_os > non_metal_os:
                    self.nvidia_legacy = True
                    self.amfi_must_disable = True

    def detect_patch_set(self):
        self.detect_gpus()
        if self.model in ModelArray.LegacyBrightness:
            if self.constants.detected_os > self.constants.catalina:
                self.brightness_legacy = True

        if self.model in ["iMac7,1", "iMac8,1"]:
            if self.constants.detected_os > self.constants.catalina:
                self.legacy_audio = True

        if (
            isinstance(self.constants.computer.wifi, device_probe.Broadcom)
            and self.computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ) or (isinstance(self.computer.wifi, device_probe.Atheros) and self.computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40):
            if self.constants.detected_os > self.constants.big_sur:
                self.legacy_wifi = True

        Utilities.cls()
        print("The following patches will be applied:")
        if self.nvidia_legacy is True:
            print("- Add Legacy Nvidia Tesla Graphics Patch")
        elif self.amd_ts1 is True:
            print("- Add Legacy ATI TeraScale 1 Graphics Patch")
        elif self.amd_ts2 is True:
            print("- Add Legacy ATI TeraScale 2 Graphics Patch")
        if self.iron_gpu is True:
            print("- Add Legacy Intel IronLake Graphics Patch")
        elif self.sandy_gpu is True:
            print("- Add Legacy Intel Sandy Bridge Graphics Patch")
        elif self.ivy_gpu is True:
            print("- Add Legacy Intel Ivy Bridge Graphics Patch")
        if self.brightness_legacy is True:
            print("- Add Legacy Brightness Control")
        if self.legacy_audio is True:
            print("- Add legacy Audio Control")
        if self.legacy_wifi is True:
            print("- Add legacy WiFi Control")

        self.no_patch = not any(
            [
                self.nvidia_legacy,
                self.amd_ts1,
                self.amd_ts2,
                self.iron_gpu,
                self.sandy_gpu,
                self.ivy_gpu,
                self.brightness_legacy,
                self.legacy_audio,
                self.legacy_wifi,
            ]
        )

    def verify_patch_allowed(self):
        sip = self.constants.root_patch_sip_big_sur if self.constants.detected_os > self.constants.catalina else self.constants.root_patch_sip_mojave
        if sip == self.constants.root_patch_sip_mojave:
            sip_value = "For Hackintoshes, please set csr-active-config to '03060000' (0x603)\nFor non-OpenCore Macs, please run 'csrutil disable' in RecoveryOS"
        else:
            sip_value = (
                "For Hackintoshes, please set csr-active-config to '030E0000' (0xE03)\nFor non-OpenCore Macs, please run 'csrutil disable' and \n'csrutil authenticated-root disable' in RecoveryOS"
            )
        self.sip_enabled, self.sbm_enabled, self.amfi_enabled, self.fv_enabled, self.dosdude_patched = Utilities.patching_status(sip, self.constants.detected_os)
        if self.sip_enabled is True:
            print("\nCannot patch! Please disable System Integrity Protection (SIP).")
            print("Disable SIP in Patcher Settings and Rebuild OpenCore\n")
            print("Ensure the following bits are set for csr-active-config:")
            print("\n".join(sip))
            print(sip_value)

        if self.sbm_enabled is True:
            print("\nCannot patch! Please disable Apple Secure Boot.")
            print("Disable SecureBootModel in Patcher Settings and Rebuild OpenCore")
            print("For Hackintoshes, set SecureBootModel to Disabled")

        if self.fv_enabled is True:
            print("\nCannot patch! Please disable FileVault.")
            print("Go to System Preferences -> Security and disable FileVault")

        if self.amfi_enabled is True and self.amfi_must_disable is True:
            print("\nCannot patch! Please disable AMFI.")
            print("For Hackintoshes, please add amfi_get_out_of_my_way=1 to boot-args")

        if self.check_board_id is True and self.computer.reported_board_id not in self.constants.sandy_board_id:
            print("\nCannot patch! Board ID not supported by AppleIntelSNBGraphicsFB")
            print(f"Detected Board ID: {self.computer.reported_board_id}")
            print("Please ensure your Board ID is listed below:")
            print("\n".join(self.constants.sandy_board_id))
            self.bad_board_id = True

        if self.dosdude_patched is True:
            print("\nCannot patch! Detected machine has already been patched by another patcher")
            print("Please ensure your install is either clean or patched with OpenCore Legacy Patcher")

        if any(
            [self.sip_enabled, self.sbm_enabled, self.fv_enabled, self.dosdude_patched, self.amfi_enabled if self.amfi_must_disable else False, self.bad_board_id if self.check_board_id else False]
        ):
            return False
        else:
            return True

    # Entry Function
    def start_patch(self):
        print("- Starting Patch Process")
        print(f"- Determinging Required Patch set for Darwin {self.constants.detected_os}")
        self.detect_patch_set()
        if self.no_patch is True:
            change_menu = None
            print("- No Root Patches required for your machine!")
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu: ")
        elif self.constants.gui_mode is False:
            change_menu = input("Would you like to continue with Root Volume Patching?(y/n): ")
        else:
            change_menu = "y"
            print("Continuing root patching")
        if change_menu in ["y", "Y"]:
            print("- Continuing with Patching")
            print("- Verifying whether Root Patching possible")
            if self.verify_patch_allowed() is True:
                print("- Patcher is capable of patching")
                self.check_files()
                self.find_mount_root_vol(True)
            elif self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu: ")

        else:
            print("- Returning to main menu")

    def start_unpatch(self):
        print("- Starting Unpatch Process")
        if self.verify_patch_allowed() is True:
            self.find_mount_root_vol(False)
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu")
