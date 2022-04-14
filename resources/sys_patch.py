# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk
# Missing Features:
# - Full System/Library Snapshotting (need to research how Apple achieves this)
#   - Temporary Work-around: sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot
# - Work-around battery throttling on laptops with no battery (IOPlatformPluginFamily.kext/Contents/PlugIns/ACPI_SMC_PlatformPlugin.kext/Contents/Resources/)

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from resources import constants, utilities, generate_smbios, sys_patch_download, sys_patch_detect
from data import sip_data, sys_patch_data, os_data


class PatchSysVolume:
    def __init__(self, model, versions, hardware_details=None):
        self.model = model
        self.constants: constants.Constants() = versions
        self.computer = self.constants.computer
        self.root_mount_path = None
        self.validate = False
        self.added_legacy_kexts = False
        self.root_supports_snapshot = utilities.check_if_root_is_apfs_snapshot()

        # GUI will detect hardware patches betfore starting PatchSysVolume()
        # However the TUI will not, so allow for data to be passed in manually avoiding multiple calls
        if hardware_details is None:
            hardware_details = sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).detect_patch_set()
        self.init_hardware_patches(hardware_details)
        self.init_pathing(custom_root_mount_path=None, custom_data_mount_path=None)

    def init_hardware_patches(self, hardware_details):
        
        self.amfi_must_disable = hardware_details["Settings: Requires AMFI exemption"]
        self.check_board_id = hardware_details["Settings: Requires Board ID validation"]
        self.sip_enabled = hardware_details["Validation: SIP is enabled"]
        self.sbm_enabled = hardware_details["Validation: SBM is enabled"]
        self.amfi_enabled = hardware_details["Validation: AMFI is enabled"]
        self.fv_enabled = hardware_details["Validation: FileVault is enabled"]
        self.dosdude_patched = hardware_details["Validation: System is dosdude1 patched"]
        self.bad_board_id = hardware_details[f"Validation: Board ID is unsupported \n({self.computer.reported_board_id})"]

        self.nvidia_legacy = hardware_details["Graphics: Nvidia Tesla"]
        self.kepler_gpu = hardware_details["Graphics: Nvidia Kepler"]
        self.amd_ts1 = hardware_details["Graphics: AMD TeraScale 1"]
        self.amd_ts2 = hardware_details["Graphics: AMD TeraScale 2"]
        self.iron_gpu = hardware_details["Graphics: Intel Ironlake"]
        self.sandy_gpu = hardware_details["Graphics: Intel Sandy Bridge"]
        self.ivy_gpu = hardware_details["Graphics: Intel Ivy Bridge"]
        self.brightness_legacy = hardware_details["Brightness: Legacy Backlight Control"]
        self.legacy_audio = hardware_details["Audio: Legacy Realtek"]
        self.legacy_wifi = hardware_details["Networking: Legacy Wireless"]
        self.legacy_gmux = hardware_details["Miscellaneous: Legacy GMUX"]
        self.legacy_keyboard_backlight = hardware_details["Miscellaneous: Legacy Keyboard Backlight"]

    def init_pathing(self, custom_root_mount_path=None, custom_data_mount_path=None):
        if custom_root_mount_path and custom_data_mount_path:
            self.mount_location = custom_root_mount_path
            self.data_mount_location = custom_data_mount_path
        elif self.root_supports_snapshot is True:
            # Big Sur and newer use APFS snapshots
            self.mount_location = "/System/Volumes/Update/mnt1"
            self.mount_location_data = ""
        else:
            self.mount_location = ""
            self.mount_location_data = ""
        self.mount_coreservices = f"{self.mount_location}/System/Library/CoreServices"
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
        self.mount_frameworks = f"{self.mount_location}/System/Library/Frameworks"
        self.mount_lauchd = f"{self.mount_location}/System/Library/LaunchDaemons"
        self.mount_private_frameworks = f"{self.mount_location}/System/Library/PrivateFrameworks"
        self.mount_libexec = f"{self.mount_location}/usr/libexec"
        self.mount_extensions_mux = f"{self.mount_location}/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns/"
        self.mount_private_etc = f"{self.mount_location_data}/private/etc"
        self.mount_application_support = f"{self.mount_location_data}/Library/Application Support"

    def find_mount_root_vol(self, patch):
        self.root_mount_path = utilities.get_disk_path()
        if self.root_mount_path.startswith("disk"):
            if (
                self.constants.detected_os == os_data.os_data.catalina or 
                (self.constants.detected_os > os_data.os_data.catalina and self.root_supports_snapshot is False)
            ):
                print("- Mounting Dedicated Root Volume as writable")
                utilities.elevated(["mount", "-uw", f"{self.mount_location}/"], stdout=subprocess.PIPE).stdout.decode().strip().encode()
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                if patch is True:
                    # Root Volume unpatching is unreliable due to being a live volume
                    # Only worth while on Big Sur as '--last-sealed-snapshot' is hit or miss
                    if self.constants.detected_os == os_data.os_data.big_sur and self.root_supports_snapshot is True and utilities.check_seal() is True:
                        self.backup_volume()
                    self.patch_root_vol()
                    return True
                else:
                    self.unpatch_root_vol()
                    return True
            else:
                if self.constants.detected_os > os_data.os_data.catalina and self.root_supports_snapshot is True:
                    print("- Mounting APFS Snapshot as writable")
                    result = utilities.elevated(["mount", "-o", "nobrowse", "-t", "apfs", f"/dev/{self.root_mount_path}", self.mount_location], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    if result.returncode == 0:
                        print(f"- Mounted APFS Snapshot as writable at: {self.mount_location}")
                if Path(self.mount_extensions).exists():
                    print("- Successfully mounted the Root Volume")
                    if patch is True:
                        # Root Volume unpatching is unreliable due to being a live volume
                        # Only worth while on Big Sur as '--last-sealed-snapshot' is hit or miss
                        if self.constants.detected_os == os_data.os_data.big_sur and self.root_supports_snapshot is True and utilities.check_seal() is True:
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
        for location in sys_patch_data.BackupLocations:
            utilities.cls()
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
                utilities.process_status(
                    utilities.elevated(
                        ["cp", "-r", f"{self.mount_location}/{location}", f"{self.mount_location}/{location}-Backup"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )
                print("- Zipping Backup folder")
                utilities.process_status(
                    utilities.elevated(
                        ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", f"{self.mount_location}/{location}-Backup", f"{self.mount_location}/{location_zip}"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )

                print("- Removing Backup folder")
                utilities.process_status(
                    utilities.elevated(
                        ["rm", "-r", f"{self.mount_location}/{location}-Backup"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                )

    def manual_root_patch_revert(self):
        print("- Attempting to revert patches")
        if (Path(self.mount_location) / Path("/System/Library/Extensions-Backup.zip")).exists():
            print("- Verified manual unpatching is available")

            for location in sys_patch_data.BackupLocations:
                utilities.cls()
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
                    utilities.process_status(utilities.elevated(["unzip", location_zip_path, "-d", copy_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    if location_old_path.exists():
                        print(f"- Renaming {location}")
                        utilities.process_status(utilities.elevated(["mv", location_old_path, f"{location_old_path}-Patched"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    print(f"- Renaming {location}-Backup")
                    utilities.process_status(utilities.elevated(["mv", f"{location_old_path}-Backup", location_old_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    print(f"- Removing {location_old_path}-Patched")
                    utilities.process_status(utilities.elevated(["rm", "-r", f"{location_old_path}-Patched"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                    # ditto will create a '__MACOSX' folder
                    # print("- Removing __MACOSX folder")
                    # utilities.process_status(utilities.elevated(["rm", "-r", f"{copy_path}/__MACOSX"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                else:
                    print(f"- Failed to find {location_zip}, unable to unpatch")
            if self.validate is False:
                self.rebuild_snapshot()
        else:
            print("- Could not find Extensions.zip, cannot manually unpatch root volume")

    def unpatch_root_vol(self):
        if self.constants.detected_os > os_data.os_data.catalina and self.root_supports_snapshot is True:
            print("- Reverting to last signed APFS snapshot")
            result = utilities.elevated(["bless", "--mount", self.mount_location, "--bootefi", "--last-sealed-snapshot"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("- Unable to revert root volume patches")
                print("Reason for unpatch Failure:")
                print(result.stdout.decode())
                print("- Failed to revert snapshot via bless, falling back on manual restoration")
                self.manual_root_patch_revert()
            else:
                self.clean_skylight_plugins()
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")
        else:
            self.manual_root_patch_revert()

    def rebuild_snapshot(self):
        print("- Rebuilding Kernel Cache (This may take some time)")
        if self.constants.detected_os > os_data.os_data.catalina:
            result = utilities.elevated(["kmutil", "install", "--volume-root", self.mount_location, "--update-all"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            result = utilities.elevated(["kextcache", "-i", f"{self.mount_location}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # kextcache notes:
        # - kextcache always returns 0, even if it fails
        # - Check the output for 'KernelCache ID' to see if the cache was successfully rebuilt
        # kmutil notes:
        # - kmutil will return 71 on failure to build KCs
        # - kmutil will sometimes have a stroke and return a negative value even if it succeeds
        if result.returncode > 0 or (self.constants.detected_os < os_data.os_data.catalina and "KernelCache ID" not in result.stdout.decode()):
            self.success_status = False
            print("- Unable to build new kernel cache")
            print(f"\nReason for Patch Failure({result.returncode}):")
            print(result.stdout.decode())
            print("")
            print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
            if self.constants.gui_mode is False:
                input("Press [ENTER] to continue")
        else:
            self.success_status = True
            print(f"- Successfully built new kernel cache({result.returncode})")
            if self.root_supports_snapshot is True:
                print("- Creating new APFS snapshot")
                bless = utilities.elevated(
                    ["bless", "--folder", f"{self.mount_location}/System/Library/CoreServices", "--bootefi", "--create-snapshot"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                if bless.returncode != 0:
                    print("- Unable to create new snapshot")
                    print("Reason for snapshot failure:")
                    print(bless.stdout.decode())
                    if "Can't use last-sealed-snapshot or create-snapshot on non system volume" in bless.stdout.decode():
                        print("- This is an APFS bug with Monterey! Perform a clean installation to ensure your APFS volume is built correctly")
                    return
                else:
                    self.unmount_drive()
            else:
                if self.constants.detected_os == os_data.os_data.catalina:
                    print("- Merging kernel cache")
                    utilities.process_status(utilities.elevated(["kcditto"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
                if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
                    print("- Merging dyld cache")
                    utilities.process_status(utilities.elevated(["update_dyld_shared_cache", "-root", f"{self.mount_location}/"]))
            print("- Patching complete")
            print("\nPlease reboot the machine for patches to take effect")
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to continue")

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        utilities.elevated(["diskutil", "unmount", self.root_mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def delete_old_binaries(self, vendor_patch):
        for delete_current_kext in vendor_patch:
            delete_path = Path(self.mount_extensions) / Path(delete_current_kext)
            if Path(delete_path).exists():
                print(f"- Deleting {delete_current_kext}")
                utilities.process_status(utilities.elevated(["rm", "-R", delete_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print(f"- Couldn't find {delete_current_kext}, skipping")

    def add_new_binaries(self, vendor_patch, vendor_location):
        for add_current_kext in vendor_patch:
            existing_path = Path(self.mount_extensions) / Path(add_current_kext)
            if Path(existing_path).exists():
                print(f"- Found conflicting kext, Deleting Root Volume's {add_current_kext}")
                utilities.process_status(utilities.elevated(["rm", "-R", existing_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            print(f"- Adding {add_current_kext}")
            utilities.process_status(utilities.elevated(["cp", "-R", f"{vendor_location}/{add_current_kext}", self.mount_extensions], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chmod", "-Rf", "755", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_extensions}/{add_current_kext}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        
    def install_auto_patcher_launch_agent(self):
        # Installs the following:
        #   - OpenCore-Patcher.app in /Library/Application Support/Dortania/
        #   - com.dortania.opencore-legacy-patcher.auto-patch.plist in /Library/LaunchAgents/
        if self.constants.launcher_script is None:
            # Verify our binary isn't located in '/Library/Application Support/Dortania/'
            # As we'd simply be duplicating ourselves
            if not self.constants.launcher_binary.startswith("/Library/Application Support/Dortania/"):
                print("- Installing Auto Patcher Launch Agent")
            
                if not Path("Library/Application Support/Dortania").exists():
                    print("- Creating /Library/Application Support/Dortania/")
                    utilities.process_status(utilities.elevated(["mkdir", "-p", "/Library/Application Support/Dortania"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                print("- Copying OpenCore Patcher to /Library/Application Support/Dortania/")
                if Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
                    print("- Deleting existing OpenCore-Patcher")
                    utilities.process_status(utilities.elevated(["rm", "-R", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                # Strip everything after OpenCore-Patcher.app
                path = str(self.constants.launcher_binary).split("/Contents/MacOS/OpenCore-Patcher")[0]
                print(f"- Copying {path} to /Library/Application Support/Dortania/")
                utilities.process_status(utilities.elevated(["cp", "-R", path, "/Library/Application Support/Dortania/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

                if not Path("/Library/Application Support/Dortania/OpenCore-Patcher.app").exists():
                    # Sometimes the binary the user launches maye have a suffix (ie. OpenCore-Patcher 3.app)
                    # We'll want to rename it to OpenCore-Patcher.app
                    path = path.split("/")[-1]
                    print(f"- Renaming {path} to OpenCore-Patcher.app")
                    utilities.process_status(utilities.elevated(["mv", f"/Library/Application Support/Dortania/{path}", "/Library/Application Support/Dortania/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Copy over our launch agent
            print("- Copying auto-patch.plist Launch Agent to /Library/LaunchAgents/")
            if Path("/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist").exists():
                print("- Deleting existing auto-patch.plist")
                utilities.process_status(utilities.elevated(["rm", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["cp", self.constants.auto_patch_launch_agent_path, "/Library/LaunchAgents/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Set the permissions on the com.dortania.opencore-legacy-patcher.auto-patch.plist
            print("- Setting permissions on auto-patch.plist")
            utilities.process_status(utilities.elevated(["chmod", "644", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "root:wheel", "/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            # Making app alias
            # Simply an easy way for users to notice the app
            # If there's already an alias or exiting app, skip
            if not Path("/Applications/OpenCore-Patcher.app").exists():
                print("- Making app alias")
                utilities.process_status(utilities.elevated(["ln", "-s", "/Library/Application Support/Dortania/OpenCore-Patcher.app", "/Applications/OpenCore-Patcher.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            print("- Skipping Auto Patcher Launch Agent, not supported when running from source")

    def clean_skylight_plugins(self):
        if (Path(self.mount_application_support) / Path("SkyLightPlugins/")).exists():
            print("- Found SkylightPlugins folder, removing")
            utilities.process_status(utilities.elevated(["rm", "-rf", f"{self.mount_application_support}/SkyLightPlugins"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def add_brightness_patch(self):
        self.delete_old_binaries(sys_patch_data.DeleteBrightness)
        self.add_new_binaries(sys_patch_data.AddBrightness, self.constants.legacy_brightness)
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_brightness}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        utilities.process_status(utilities.elevated(["chmod", "-Rf", "755", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        utilities.process_status(utilities.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_private_frameworks}/DisplayServices.framework"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def add_audio_patch(self):
        if self.model in ["iMac7,1", "iMac8,1"]:
            self.delete_old_binaries(sys_patch_data.DeleteVolumeControl)
            self.add_new_binaries(sys_patch_data.AddVolumeControl, self.constants.audio_path)
        else:
            self.add_new_binaries(sys_patch_data.AddVolumeControlv2, self.constants.audio_v2_path)

    def add_wifi_patch(self):
        print("- Merging Wireless CoreSerices patches")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_wifi_coreservices}/", self.mount_coreservices], stdout=subprocess.PIPE)
        utilities.process_status(utilities.elevated(["chmod", "-Rf", "755", f"{self.mount_coreservices}/WiFiAgent.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        utilities.process_status(utilities.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_coreservices}/WiFiAgent.app"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        print("- Merging Wireless usr/libexec patches")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_wifi_libexec}/", self.mount_libexec], stdout=subprocess.PIPE)
        utilities.process_status(utilities.elevated(["chmod", "755", f"{self.mount_libexec}/airportd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        utilities.process_status(utilities.elevated(["chown", "root:wheel", f"{self.mount_libexec}/airportd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        # dylib patch to resolve password crash prompt
        # Note requires ASentientBot's SkyLight to function
        # Thus Metal machines do not benefit from this patch, however install anyways as harmless 
        print("- Merging Wireless SkyLightPlugins")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_wifi_support}/", self.mount_application_support], stdout=subprocess.PIPE)

    def add_legacy_mux_patch(self):
        self.delete_old_binaries(sys_patch_data.DeleteDemux)
        print("- Merging Legacy Mux Kext patches")
        utilities.process_status(
            utilities.elevated(["cp", "-R", f"{self.constants.legacy_mux_path}/AppleMuxControl.kext", self.mount_extensions_mux], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        )
    
    def add_legacy_keyboard_backlight_patch(self):
        print("- Enabling Keyboard Backlight delay")
        utilities.process_status(
            utilities.elevated(["defaults", "write", "/Library/Preferences/.GlobalPreferences.plist", "NonMetal_BacklightHack", "-bool", "true"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        )
    
    def add_legacy_dropbox_patch(self):
        print("- Merging DropboxHack SkyLightPlugins")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.legacy_dropbox_support}/", self.mount_application_support], stdout=subprocess.PIPE)

    def gpu_accel_legacy(self):
        if self.constants.detected_os == os_data.os_data.mojave:
            print("- Installing General Acceleration Kext patches for Mojave")
            self.add_new_binaries(sys_patch_data.AddGeneralAccelMojave, self.constants.legacy_general_path)
        elif self.constants.detected_os == os_data.os_data.catalina:
            print("- Installing General Acceleration Kext patches for Catalina")
            self.add_new_binaries(sys_patch_data.AddGeneralAccelCatalina, self.constants.legacy_general_path)
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
            print("- Installing General Acceleration Kext patches for Big Sur/Monterey")
            self.add_new_binaries(sys_patch_data.AddGeneralAccel, self.constants.legacy_general_path)

    # Nvidia
    def gpu_accel_legacy_nvidia_master(self):
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
            print("- Installing Nvidia Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddNvidiaAccelLegacy, self.constants.legacy_nvidia_path)
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
            print("- Installing Nvidia Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(sys_patch_data.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddNvidiaAccel11, self.constants.legacy_nvidia_path)
            if self.constants.detected_os == os_data.os_data.monterey and self.constants.detected_os_minor > 0:
                # Beta 7+ removes NVDAStartup
                self.add_new_binaries(sys_patch_data.AddNvidiaTeslaAccel12, self.constants.legacy_nvidia_kepler_path)
        else:
            print("- Installing basic Nvidia Framebuffer Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddNvidiaBrightness, self.constants.legacy_nvidia_path)

    # AMD/ATI
    def gpu_accel_legacy_ts1_master(self):
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
            print("- Installing TeraScale 1 Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddAMDAccelLegacy, self.constants.legacy_amd_path)
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
            print("- Installing TeraScale 1 Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(sys_patch_data.DeleteAMDAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddAMDAccel11, self.constants.legacy_amd_path)
        else:
            print("- Installing basic TeraScale 1 Framebuffer Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddAMDBrightness, self.constants.legacy_amd_path)

    def gpu_accel_legacy_ts2_master(self):
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina] and self.constants.allow_ts2_accel is True:
            print("- Installing TeraScale 2 Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddAMDAccelLegacy, self.constants.legacy_amd_path)
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey] and self.constants.allow_ts2_accel is True:
            print("- Installing TeraScale 2 Acceleration Kext patches for Big Sur")
            self.delete_old_binaries(sys_patch_data.DeleteAMDAccel11)
            self.delete_old_binaries(sys_patch_data.DeleteAMDAccel11TS2)
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddAMDAccel11, self.constants.legacy_amd_path)
        else:
            print("- Installing basic TeraScale 2 Framebuffer Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddAMDBrightness, self.constants.legacy_amd_path)

    # Intel
    def gpu_accel_legacy_ironlake_master(self):
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
            print("- Installing Ironlake Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
            print("- Installing Ironlake Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(sys_patch_data.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)
        else:
            print("- Installing basic Ironlake Framebuffer Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddIntelGen1Accel, self.constants.legacy_intel_gen1_path)

    def gpu_accel_legacy_sandybridge_master(self):
        if self.constants.detected_os in [os_data.os_data.mojave, os_data.os_data.catalina]:
            print("- Installing Sandy Bridge Acceleration Kext patches for Mojave/Catalina")
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
            self.gpu_accel_legacy_sandybridge_board_id()
        elif self.constants.detected_os in [os_data.os_data.big_sur, os_data.os_data.monterey]:
            print("- Installing Sandy Bridge Acceleration Kext patches for Big Sur/Monterey")
            self.delete_old_binaries(sys_patch_data.DeleteNvidiaAccel11)
            self.gpu_accel_legacy()
            self.add_new_binaries(sys_patch_data.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
            self.gpu_accel_legacy_sandybridge_board_id()
            self.gpu_accel_legacy_gva()
        else:
            print("- Installing basic Sandy Bridge Framebuffer Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddIntelGen2Accel, self.constants.legacy_intel_gen2_path)
            self.gpu_accel_legacy_sandybridge_board_id()

    def gpu_accel_legacy_sandybridge_board_id(self):
        if self.constants.computer.reported_board_id in self.constants.sandy_board_id_stock:
            print("- Using stock AppleIntelSNBGraphicsFB")
            # TODO: Clean this function up
            # add_new_binaries() and delete_old_binaries() have a bug when the passed array has a single element
            #   'TypeError: expected str, bytes or os.PathLike object, not list'
            # This is a temporary workaround to fix that
            utilities.elevated(["rm", "-r", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB-Clean.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            utilities.elevated(["rm", "-r", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Add kext
            print("- Adding AppleIntelSNBGraphicsFB.kext")
            utilities.elevated(
                ["cp", "-r", f"{self.constants.legacy_intel_gen2_path}/AppleIntelSNBGraphicsFB-Clean.kext", f"{self.mount_extensions}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # Rename kext
            utilities.elevated(
                ["mv", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB-Clean.kext", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # Fix permissions
            utilities.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            utilities.elevated(["chmod", "-Rf", "755", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        else:
            # Adjust board ID for spoofs
            print("- Using Board ID patched AppleIntelSNBGraphicsFB")
            utilities.elevated(["rm", "-r", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB-Clean.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            utilities.elevated(["rm", "-r", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Add kext
            print("- Adding AppleIntelSNBGraphicsFB.kext")
            utilities.elevated(["cp", "-r", f"{self.constants.legacy_intel_gen2_path}/AppleIntelSNBGraphicsFB.kext", f"{self.mount_extensions}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Fix permissions
            utilities.elevated(["chown", "-Rf", "root:wheel", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            utilities.elevated(["chmod", "-Rf", "755", f"{self.mount_extensions}/AppleIntelSNBGraphicsFB.kext"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def gpu_framebuffer_ivybridge_master(self):
        if self.constants.detected_os == os_data.os_data.monterey:
            print("- Installing IvyBridge Acceleration Kext patches for Monterey")
            self.add_new_binaries(sys_patch_data.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)
            if self.validate is False:
                print("- Fixing Acceleration in CoreMedia")
                utilities.process_status(subprocess.run(["defaults", "write", "com.apple.coremedia", "hardwareVideoDecoder", "-string", "enable"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            print("- Merging Ivy Bridge Frameworks")
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ivy}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print("- Merging Ivy Bridge PrivateFrameworks")
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel_ivy}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        else:
            print("- Installing basic Ivy Bridge Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddIntelGen3Accel, self.constants.legacy_intel_gen3_path)

    def gpu_framebuffer_kepler_master(self):
        if self.constants.detected_os == os_data.os_data.monterey:
            print("- Installing Kepler Acceleration Kext patches for Monterey")
            self.add_new_binaries(sys_patch_data.AddNvidiaKeplerAccel11, self.constants.legacy_nvidia_kepler_path)
            print("- Merging Kepler Frameworks")
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_kepler}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            print("- Installing Kepler Kext patches for generic OS")
            self.add_new_binaries(sys_patch_data.AddNvidiaKeplerAccel11, self.constants.legacy_nvidia_kepler_path)

    def gpu_accel_legacy_gva(self):
        print("- Merging AppleGVA Hardware Accel patches for non-Metal")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_legacy_drm}/", self.mount_private_frameworks], stdout=subprocess.PIPE)

    def gpu_accel_legacy_extended(self):
        if self.constants.detected_os == os_data.os_data.monterey:
            self.add_legacy_dropbox_patch()

        if self.legacy_keyboard_backlight is True:
            self.add_legacy_keyboard_backlight_patch()
        
        print("- Merging general legacy Frameworks")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if self.constants.detected_os > os_data.os_data.big_sur:
            print("- Merging Monterey WebKit patch")
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ivy}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print("- Merging general legacy PrivateFrameworks")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        if self.constants.detected_os > os_data.os_data.catalina:
            # With PatcherSupportPkg v0.2.0, IOHID-Fixup.plist is deprecated and integrated into SkyLight patch set
            if (Path(self.mount_lauchd) / Path("IOHID-Fixup.plist")).exists():
                print("- Stripping legacy IOHID-Fixup.plist")
                utilities.process_status(
                    utilities.elevated(["rm", "-f", f"{self.mount_lauchd}/IOHID-Fixup.plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                )
        else:
            print("- Disabling Library Validation")
            utilities.process_status(
                utilities.elevated(
                    ["defaults", "write", "/Library/Preferences/com.apple.security.libraryvalidation.plist", "DisableLibraryValidation", "-bool", "true"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            )

    def gpu_accel_legacy_extended_ts2(self):
        print("- Merging TeraScale 2 legacy Frameworks")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_frameworks_path_accel_ts2}/", self.mount_frameworks], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print("- Merging TeraScale 2 PrivateFrameworks")
        utilities.elevated(["rsync", "-r", "-i", "-a", f"{self.constants.payload_apple_private_frameworks_path_accel_ts2}/", self.mount_private_frameworks], stdout=subprocess.PIPE)
        if self.validate is False:
            print("- Fixing Acceleration in CMIO")
            utilities.process_status(subprocess.run(["defaults", "write", "com.apple.cmio", "CMIO_Unit_Input_ASC.DoNotUseOpenCL", "-bool", "true"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def patch_root_vol(self):
        print(f"- Running patches for {self.model}")
        
        # Before starting, clean out old plugins
        self.clean_skylight_plugins()
        
        # Graphics patches
        if self.nvidia_legacy is True:
            print("- Installing legacy Nvidia Patches")
            if self.constants.detected_os in self.constants.legacy_accel_support:
                print("- Detected supported OS, installing Acceleration Patches")
                self.added_legacy_kexts = True
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_accel_legacy_nvidia_master()

        elif self.kepler_gpu is True:
            print("- Installing Kepler Patches")
            if self.constants.detected_os == os_data.os_data.monterey:
                print("- Detected supported OS, installing Acceleration Patches")
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_framebuffer_kepler_master()

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
            if self.constants.detected_os == os_data.os_data.monterey:
                print("- Detected supported OS, installing Acceleration Patches")
            else:
                print("- Detected unsupported OS, installing Basic Framebuffer")
            self.gpu_framebuffer_ivybridge_master()

        if self.amd_ts2 is True and self.constants.detected_os in self.constants.legacy_accel_support and self.constants.allow_ts2_accel is True:
            # TeraScale 2 patches must be installed after Intel HD3000
            self.add_new_binaries(sys_patch_data.AddAMDAccel11TS2, self.constants.legacy_amd_path_ts2)

        if self.added_legacy_kexts is True and self.constants.detected_os in self.constants.legacy_accel_support:
            self.gpu_accel_legacy_extended()
            if self.amd_ts2 is True and self.constants.allow_ts2_accel is True:
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

        if self.legacy_gmux is True:
            print("- Installing Legacy Mux Brightness support")
            self.add_legacy_mux_patch()

        if self.constants.wxpython_variant is True and self.constants.detected_os >= os_data.os_data.big_sur: 
            self.install_auto_patcher_launch_agent()

        if self.validate is False:
            self.rebuild_snapshot()

    def check_files(self):
        if Path(self.constants.payload_apple_root_path).exists():
            print("- Found local Apple Binaries")
            if self.constants.gui_mode is False:
                patch_input = input("Would you like to redownload?(y/n): ")
                if patch_input in {"y", "Y", "yes", "Yes"}:
                    shutil.rmtree(Path(self.constants.payload_apple_root_path))
                    output = self.download_files()
            else:
                output = self.download_files()
        else:
            output = self.download_files()
        return output

    def download_files(self):
        if self.constants.gui_mode is False or "Library/InstallerSandboxes/" in str(self.constants.payload_path):
            download_result, os_ver, link = sys_patch_download.grab_patcher_support_pkg(self.constants).download_files()
        else:
            download_result = True
            os_ver, link = sys_patch_download.grab_patcher_support_pkg(self.constants).generate_pkg_link()

        if download_result and self.constants.payload_apple_root_path_zip.exists():
            print("- Download completed")
            print("- Unzipping download...")
            try:
                utilities.process_status(subprocess.run(["unzip", self.constants.payload_apple_root_path_zip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.constants.payload_path))
                print("- Renaming folder")
                os.rename(self.constants.payload_path / Path(os_ver), self.constants.payload_apple_root_path)
                Path(self.constants.payload_apple_root_path_zip).unlink()
                print("- Binaries downloaded to:")
                print(self.constants.payload_path)
                return self.constants.payload_apple_root_path
            except zipfile.BadZipFile:
                print("- Couldn't unzip")
                return None
        else:
            if self.constants.gui_mode is True:
                print("- Download failed, please verify the below link works:")
                print(link)
                print("\nIf you continue to have issues, try using the Offline builds")
                print("located on Github next to the other builds")
            else:
                input("\nPress enter to continue")
        return None


    def detect_patch_set(self):
        utilities.cls()
        print("The following patches will be applied:")
        if self.nvidia_legacy is True:
            print("- Add Legacy Nvidia Tesla Graphics Patch")
        elif self.kepler_gpu is True:
            print("- Add Legacy Nvidia Kepler Graphics Patch")
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
        if self.legacy_gmux is True:
            print("- Add Legacy Mux Brightness Control")
        if self.legacy_keyboard_backlight is True:
            print("- Add Legacy Keyboard Backlight Control")

        self.no_patch = not any(
            [
                self.nvidia_legacy,
                self.kepler_gpu,
                self.amd_ts1,
                self.amd_ts2,
                self.iron_gpu,
                self.sandy_gpu,
                self.ivy_gpu,
                self.brightness_legacy,
                self.legacy_audio,
                self.legacy_wifi,
                self.legacy_gmux,
            ]
        )

    def verify_patch_allowed(self):
        sip = sip_data.system_integrity_protection.root_patch_sip_big_sur if self.constants.detected_os > os_data.os_data.catalina else sip_data.system_integrity_protection.root_patch_sip_mojave
        if sip == sip_data.system_integrity_protection.root_patch_sip_mojave:
            sip_value = "For Hackintoshes, please set csr-active-config to '03060000' (0x603)\nFor non-OpenCore Macs, please run 'csrutil disable' in RecoveryOS"
        else:
            sip_value = (
                "For Hackintoshes, please set csr-active-config to '02080000' (0x802)\nFor non-OpenCore Macs, please run 'csrutil disable' and \n'csrutil authenticated-root disable' in RecoveryOS"
            )
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
            print("For OCLP Macs, please rebuild your config with 0.2.5 or newer")
            print("For others, Go to System Preferences -> Security and disable FileVault")

        if self.amfi_enabled is True and self.amfi_must_disable is True:
            print("\nCannot patch! Please disable AMFI.")
            print("For Hackintoshes, please add amfi_get_out_of_my_way=1 to boot-args")

        if self.check_board_id is True and (self.computer.reported_board_id not in self.constants.sandy_board_id and self.computer.reported_board_id not in self.constants.sandy_board_id_stock):
            print("\nCannot patch! Board ID not supported by AppleIntelSNBGraphicsFB")
            print(f"Detected Board ID: {self.computer.reported_board_id}")
            print("Please ensure your Board ID is listed below:")
            for board in self.constants.sandy_board_id:
                print(f"- {board} ({generate_smbios.find_model_off_board(board)})")
            for board in self.constants.sandy_board_id_stock:
                print(f"- {board} ({generate_smbios.find_model_off_board(board)})")

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
        print(f"- Determining Required Patch set for Darwin {self.constants.detected_os}")
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
            print("- Continuing root patching")
        if change_menu in ["y", "Y"]:
            print("- Continuing with Patching")
            print("- Verifying whether Root Patching possible")
            if self.verify_patch_allowed() is True:
                print("- Patcher is capable of patching")
                if self.check_files():
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
        elif self.constants.gui_mode is False:
            input("\nPress [ENTER] to return to the main menu")
