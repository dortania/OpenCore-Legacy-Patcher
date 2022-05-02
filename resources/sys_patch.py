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

from resources import constants, generate_smbios, utilities, sys_patch_download, sys_patch_detect
from data import os_data, sys_patch_dict


class PatchSysVolume:
    def __init__(self, model, versions, hardware_details=None):
        self.model = model
        self.constants: constants.Constants() = versions
        self.computer = self.constants.computer
        self.root_mount_path = None
        self.validate = False
        self.added_legacy_kexts = False
        self.root_supports_snapshot = utilities.check_if_root_is_apfs_snapshot()
        self.constants.root_patcher_succeded = False # Reset Variable each time we start

        # GUI will detect hardware patches before starting PatchSysVolume()
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
        self.mount_extensions = f"{self.mount_location}/System/Library/Extensions"
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

    def unpatch_root_vol(self):
        if self.constants.detected_os > os_data.os_data.catalina and self.root_supports_snapshot is True:
            print("- Reverting to last signed APFS snapshot")
            result = utilities.elevated(["bless", "--mount", self.mount_location, "--bootefi", "--last-sealed-snapshot"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("- Unable to revert root volume patches")
                print("Reason for unpatch Failure:")
                print(result.stdout.decode())
                print("- Failed to revert snapshot via Apple's 'bless' command")
            else:
                self.clean_skylight_plugins()
                self.constants.root_patcher_succeded = True
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")

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
        # - will return 71 on failure to build KCs
        # - will return 31 on 'No binaries or codeless kexts were provided'
        # - will return -10 if the volume is missing (ie. unmounted by another process)
        if result.returncode != 0 or (self.constants.detected_os < os_data.os_data.catalina and "KernelCache ID" not in result.stdout.decode()):
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
            print("- Successfully built new kernel cache")
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
            self.constants.root_patcher_succeded = True
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to continue")

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        utilities.elevated(["diskutil", "unmount", self.root_mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()


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
            print("- Found SkylightPlugins folder, removing old plugins")
            utilities.process_status(utilities.elevated(["rm", "-Rf", f"{self.mount_application_support}/SkyLightPlugins"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["mkdir", f"{self.mount_application_support}/SkyLightPlugins"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            print("- Creating SkylightPlugins folder")
            utilities.process_status(utilities.elevated(["mkdir", f"{self.mount_application_support}/SkyLightPlugins/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

 
    def patch_root_vol(self):
        print(f"- Running patches for {self.model}")
                
        self.execute_patchset(self.generate_patchset())

        if self.constants.wxpython_variant is True and self.constants.detected_os >= os_data.os_data.big_sur: 
            self.install_auto_patcher_launch_agent()

        self.rebuild_snapshot()
    
    def generate_patchset(self):
        all_hardware_patchset = sys_patch_dict.SystemPatchDictionary(self.constants.detected_os)
        required_patches = {}
        
        print("- Creating Patch Set for Booted Hardware:")
        if self.iron_gpu is True:
            print("  - Adding Intel Ironlake Graphics Patchset")
            required_patches.update({"Non-Metal Common": all_hardware_patchset["Graphics"]["Non-Metal Common"]})
            required_patches.update({"Intel Ironlake": all_hardware_patchset["Graphics"]["Intel Ironlake"]})
        if self.sandy_gpu is True:
            print("  - Adding Intel Sandy Bridge Graphics Patchset")
            required_patches.update({"Non-Metal Common": all_hardware_patchset["Graphics"]["Non-Metal Common"]})
            required_patches.update({"Legacy GVA": all_hardware_patchset["Graphics"]["Legacy GVA"]})
            required_patches.update({"Intel Sandy Bridge": all_hardware_patchset["Graphics"]["Intel Sandy Bridge"]})
        if self.ivy_gpu is True:
            print("  - Adding Intel Ivy Bridge Graphics Patchset")
            required_patches.update({"Metal Common": all_hardware_patchset["Graphics"]["Metal Common"]})
            required_patches.update({"Intel Ivy Bridge": all_hardware_patchset["Graphics"]["Intel Ivy Bridge"]})
        if self.nvidia_legacy is True:
            print("  - Adding Nvidia Tesla Graphics Patchset")
            required_patches.update({"Non-Metal Common": all_hardware_patchset["Graphics"]["Non-Metal Common"]})
            required_patches.update({"Nvidia Tesla": all_hardware_patchset["Graphics"]["Nvidia Tesla"]})
        if self.kepler_gpu is True:
            print("  - Adding Nvidia Kepler Graphics Patchset")
            required_patches.update({"Metal Common": all_hardware_patchset["Graphics"]["Metal Common"]})
            required_patches.update({"Nvidia Kepler": all_hardware_patchset["Graphics"]["Nvidia Kepler"]})
        if self.amd_ts1 is True:
            print("  - Adding AMD TeraScale 1 Graphics Patchset")
            required_patches.update({"Non-Metal Common": all_hardware_patchset["Graphics"]["Non-Metal Common"]})
            required_patches.update({"AMD TeraScale 1": all_hardware_patchset["Graphics"]["AMD TeraScale 1"]})
        if self.amd_ts2 is True:
            print("  - Adding AMD TeraScale 2 Graphics Patchset")
            required_patches.update({"Non-Metal Common": all_hardware_patchset["Graphics"]["Non-Metal Common"]})
            required_patches.update({"AMD TeraScale 2": all_hardware_patchset["Graphics"]["AMD TeraScale 2"]})
        if self.brightness_legacy is True:
            print("  - Adding Legacy Brightness Patchset")
            required_patches.update({"Legacy Brightness": all_hardware_patchset["Brightness"]["Legacy Brightness"]})
        if self.legacy_audio is True:
            print("  - Adding Legacy Audio Patchset")
            if self.model in ["iMac7,1", "iMac8,1"]:
                required_patches.update({"Legacy Realtek": all_hardware_patchset["Audio"]["Legacy Realtek"]})
            else:
                required_patches.update({"Legacy Non-GOP": all_hardware_patchset["Audio"]["Legacy Non-GOP"]})
        if self.legacy_wifi is True:
            print("  - Adding Legacy WiFi Patchset")
            required_patches.update({"Legacy WiFi": all_hardware_patchset["Networking"]["Legacy WiFi"]})
        if self.legacy_gmux is True:
            print("  - Adding Legacy GMUX Patchset")
            required_patches.update({"Legacy GMUX": all_hardware_patchset["Miscellaneous"]["Legacy GMUX"]})
        if self.legacy_keyboard_backlight:
            print("  - Adding Legacy Keyboard Backlight Patchset")
            required_patches.update({"Legacy Keyboard Backlight": all_hardware_patchset["Miscellaneous"]["Legacy Keyboard Backlight"]})
        
        return required_patches
    
    
    def execute_patchset(self, required_patches):
        source_files_path = str(self.constants.payload_local_binaries_root_path)
        print("- Running Preflight Checks before patching")
        # Make sure old SkyLight plugins aren't being used
        self.clean_skylight_plugins()
        # Make sure SNB kexts are compatible with the host
        if "Intel Sandy Bridge" in required_patches:
            if self.computer.reported_board_id not in self.constants.sandy_board_id_stock:
                print(f"- Found unspported Board ID {self.computer.reported_board_id}, performing AppleIntelSNBGraphicsFB bin patching")
                board_to_patch = generate_smbios.determine_best_board_id_for_sandy(self.computer.reported_board_id, self.computer.gpus)
                print(f"- Replacing {board_to_patch} with {self.computer.reported_board_id}")

                board_to_patch_hex = bytes.fromhex(board_to_patch.encode('utf-8').hex())
                reported_board_hex = bytes.fromhex(self.computer.reported_board_id.encode('utf-8').hex())

                if len(board_to_patch_hex) != len(reported_board_hex):
                    print(f"- Error: Board ID {self.computer.reported_board_id} is not the same length as {board_to_patch}")
                    raise Exception("Host's Board ID is not the same length as the kext's Board ID, cannot patch!!!")
                else:
                    path = source_files_path + "10.13.6/System/Library/Extensions/AppleIntelSNBGraphicsFB.kext/Contents/MacOS/AppleIntelSNBGraphicsFB"
                    if Path(path).exists:
                        with open(path, 'rb') as f:
                            data = f.read()
                            data = data.replace(board_to_patch_hex, reported_board_hex)
                            with open(path, 'wb') as f:
                                f.write(data)
                    else:
                        raise Exception("Failed to find AppleIntelSNBGraphicsFB.kext, cannot patch!!!")

        print("- Finished Preflight, starting patching")
        for patch in required_patches:
            print("- Installing Patchset: " + patch)
            if "Remove" in required_patches[patch]:
                for remove_patch_directory in required_patches[patch]["Remove"]:
                    print("- Remove Files at: " + remove_patch_directory)
                    for remove_patch_file in required_patches[patch]["Remove"][remove_patch_directory]:
                        destination_folder_path = str(self.mount_location) + remove_patch_directory
                        self.remove_file(destination_folder_path, remove_patch_file)
            
            if "Install" in required_patches[patch]:
                for install_patch_directory in required_patches[patch]["Install"]:
                    print(f"- Handling Installs in: {install_patch_directory}")
                    for install_file in required_patches[patch]["Install"][install_patch_directory]:
                        source_folder_path = source_files_path + "/" + required_patches[patch]['Install'][install_patch_directory][install_file] + install_patch_directory
                        destination_folder_path = str(self.mount_location) + install_patch_directory
                        self.install_new_file(source_folder_path, destination_folder_path, install_file)
            
            if "Install Non-Root" in required_patches[patch]:
                for install_patch_directory in required_patches[patch]["Install Non-Root"]:
                    print(f"- Handling Non-Root Installs in: {install_patch_directory}")
                    for install_file in required_patches[patch]["Install Non-Root"][install_patch_directory]:
                        source_folder_path = source_files_path + "/" + required_patches[patch]['Install Non-Root'][install_patch_directory][install_file] + install_patch_directory
                        destination_folder_path = str(self.mount_location_data) + install_patch_directory
                        self.install_new_file(source_folder_path, destination_folder_path, install_file)

            if "Processes" in required_patches[patch]:
                for process in required_patches[patch]["Processes"]:
                    # Some processes need sudo, however we cannot directly call sudo in some scenarios
                    # Instead, call elevated funtion and strip sudo from argument
                    process_array = process.split(" ")
                    if required_patches[patch]["Processes"][process] is True:
                        utilities.process_status(utilities.elevated(process_array, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
                    else:
                        utilities.process_status(subprocess.run(process_array, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def install_new_file(self, source_folder, destination_folder, file_name):
        # .frameworks are merged
        # .kexts and .apps are deleted and replaced
        file_name_str = str(file_name)
        if file_name_str.endswith(".kext") or file_name_str.endswith(".app") or file_name_str.endswith(".bundle") or file_name_str.endswith(".plugin"):
            if Path(destination_folder + "/" + file_name).exists():
                print(f"  - Found existing {file_name}, overwritting...")
                utilities.process_status(utilities.elevated(["rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print("  - Installing: " + file_name)
            utilities.process_status(utilities.elevated(["cp", "-R", f"{source_folder}/{file_name}", destination_folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chmod", "-Rf", "755", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "-Rf", "root:wheel", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

        elif file_name_str.endswith(".framework"):
            # merge with rsync
            print("  - Installing: " + file_name)
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{source_folder}/{file_name}", f"{destination_folder}/"], stdout=subprocess.PIPE)
            utilities.process_status(utilities.elevated(["chmod", "-Rf", "755", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "-Rf", "root:wheel", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            # Assume it's an individual file, replace as normal
            if Path(destination_folder + "/" + file_name).exists():
                print(f"  - Found existing {file_name}, overwritting...")
                utilities.process_status(utilities.elevated(["rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print("  - Installing: " + file_name)
            utilities.process_status(utilities.elevated(["cp", f"{source_folder}/{file_name}", destination_folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chmod", "755", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["chown", "root:wheel", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def remove_file(self, destination_folder, file_name):
        if Path(destination_folder + "/" + file_name).exists():
            print("  - Removing: " + file_name)
            if Path(destination_folder + "/" + file_name).is_dir():
                utilities.process_status(utilities.elevated(["rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                utilities.process_status(utilities.elevated(["rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))


    def check_files(self):
        if Path(self.constants.payload_local_binaries_root_path).exists():
            print("- Found local Apple Binaries")
            if self.constants.gui_mode is False:
                patch_input = input("Would you like to redownload?(y/n): ")
                if patch_input in {"y", "Y", "yes", "Yes"}:
                    shutil.rmtree(Path(self.constants.payload_local_binaries_root_path))
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

        if download_result and self.constants.payload_local_binaries_root_path_zip.exists():
            print("- Unzipping binaries...")
            try:
                utilities.process_status(subprocess.run(["ditto", "-V", "-x", "-k", "--sequesterRsrc", "--rsrc", self.constants.payload_local_binaries_root_path_zip, self.constants.payload_path]))
                print("- Renaming folder")
                print("- Binaries downloaded to:")
                print(self.constants.payload_path)
                return self.constants.payload_local_binaries_root_path
            except zipfile.BadZipFile:
                print("- Couldn't unzip")
                return None
        else:
            if self.constants.gui_mode is True:
                print("- Download failed, please verify the below link work:")
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
            print("- Verifying whether Root Patching possible")
            if sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).verify_patch_allowed(print_errors=not self.constants.wxpython_variant) is True:
                print("- Patcher is capable of patching")
                if self.check_files():
                    self.find_mount_root_vol(True)
            elif self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu: ")

        else:
            print("- Returning to main menu")

    def start_unpatch(self):
        print("- Starting Unpatch Process")
        if sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).verify_patch_allowed(print_errors=not self.constants.wxpython_variant) is True:
            self.find_mount_root_vol(False)
            if self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu")
        elif self.constants.gui_mode is False:
            input("\nPress [ENTER] to return to the main menu")
