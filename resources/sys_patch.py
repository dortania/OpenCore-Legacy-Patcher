# Framework for mounting and patching macOS root volume
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

# System based off of Apple's Kernel Debug Kit (KDK)
# - https://developer.apple.com/download/all/

# The system relies on mounting the APFS volume as a live read/write volume
# We perform our required edits, then create a new snapshot for the system boot

# The manual process is as follows:
#  1. Find the Root Volume
#     'diskutil info / | grep "Device Node:"'
#  2. Convert Snapshot Device Node to Root Volume Device Node
#     /dev/disk3s1s1 -> /dev/disk3s1 (strip last 's1')
#  3. Mount the APFS volume as a read/write volume
#     'sudo mount -o nobrowse -t apfs  /dev/disk5s5 /System/Volumes/Update/mnt1'
#  4. Perform edits to the system (ie. create new KernelCollection)
#     'sudo kmutil install --volume-root /System/Volumes/Update/mnt1/ --update-all'
#  5. Create a new snapshot for the system boot
#     'sudo bless --folder /System/Volumes/Update/mnt1/System/Library/CoreServices --bootefi --create-snapshot'

# Additionally Apple's APFS snapshot system supports system rollbacks:
#   'sudo bless --mount /System/Volumes/Update/mnt1 --bootefi --last-sealed-snapshot'
# Note: root volume rollbacks are unstable in Big Sur due to quickly discarding the original snapshot
# - Generally within 2~ boots, the original snapshot is discarded
# - Monterey always preserves the original snapshot allowing for reliable rollbacks

# Alternative to mounting via 'mount', Apple's update system uses 'mount_apfs' directly
#   '/sbin/mount_apfs -R /dev/disk5s5 /System/Volumes/Update/mnt1'

# With macOS Ventura, you will also need to install the KDK onto root if you plan to use kmutil
# This is because Apple removed on-disk binaries (ref: https://github.com/dortania/OpenCore-Legacy-Patcher/issues/998)
#   'sudo ditto /Library/Developer/KDKs/<KDK Version>/System /System/Volumes/Update/mnt1/System'

import plistlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

from resources import constants, utilities, sys_patch_download, sys_patch_detect, sys_patch_auto, sys_patch_helpers, kdk_handler
from data import os_data


class PatchSysVolume:
    def __init__(self, model, versions, hardware_details=None):
        self.model = model
        self.constants: constants.Constants() = versions
        self.computer = self.constants.computer
        self.root_mount_path = None
        self.root_supports_snapshot = utilities.check_if_root_is_apfs_snapshot()
        self.constants.root_patcher_succeeded = False # Reset Variable each time we start
        self.constants.needs_to_open_preferences = False
        self.patch_set_dictionary = {}
        self.needs_kmutil_exemptions = False # For '/Library/Extensions' rebuilds
        self.kdk_path = None

        # GUI will detect hardware patches before starting PatchSysVolume()
        # However the TUI will not, so allow for data to be passed in manually avoiding multiple calls
        if hardware_details is None:
            hardware_details = sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).detect_patch_set()
        self.hardware_details = hardware_details
        self.init_pathing(custom_root_mount_path=None, custom_data_mount_path=None)

        self.skip_root_kmutil_requirement = self.hardware_details["Settings: Supports Auxiliary Cache"]

    def __del__(self):
        # Ensures that each time we're patching, we're using a clean repository
        if Path(self.constants.payload_local_binaries_root_path).exists():
            shutil.rmtree(self.constants.payload_local_binaries_root_path)

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


    def mount_root_vol(self):
        # Returns boolean if Root Volume is available
        self.root_mount_path = utilities.get_disk_path()
        if self.root_mount_path.startswith("disk"):
            print(f"- Found Root Volume at: {self.root_mount_path}")
            if Path(self.mount_extensions).exists():
                print("- Root Volume is already mounted")
                return True
            else:
                if self.root_supports_snapshot is True:
                    print("- Mounting APFS Snapshot as writable")
                    result = utilities.elevated(["mount", "-o", "nobrowse", "-t", "apfs", f"/dev/{self.root_mount_path}", self.mount_location], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    if result.returncode == 0:
                        print(f"- Mounted APFS Snapshot as writable at: {self.mount_location}")
                        if Path(self.mount_extensions).exists():
                            print("- Successfully mounted the Root Volume")
                            return True
                        else:
                            print("- Root Volume appears to have unmounted unexpectedly")
                    else:
                        print("- Unable to mount APFS Snapshot as writable")
                        print("Reason for mount failure:")
                        print(result.stdout.decode().strip())
        return False

    def merge_kdk_with_root(self):
        if self.skip_root_kmutil_requirement is True:
            return
        if self.constants.detected_os < os_data.os_data.ventura:
            return

        downloaded_kdk = None
        kdk_path = sys_patch_helpers.sys_patch_helpers(self.constants).determine_kdk_present(match_closest=False)
        if kdk_path is None:
            if not self.constants.kdk_download_path.exists():
                kdk_result, error_msg, downloaded_kdk = kdk_handler.kernel_debug_kit_handler(self.constants).download_kdk(self.constants.detected_os_version, self.constants.detected_os_build)
                if kdk_result is False:
                    raise Exception(f"Unable to download KDK: {error_msg}")
            sys_patch_helpers.sys_patch_helpers(self.constants).install_kdk()
            kdk_path = sys_patch_helpers.sys_patch_helpers(self.constants).determine_kdk_present(match_closest=True, override_build=downloaded_kdk)

        oclp_plist = Path("/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist")
        if (Path(self.mount_location) / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists() and oclp_plist.exists():
            # KDK was already merged, check if the KDK used is the same as the one we're using
            # If not, we'll rsync over with the new KDK
            try:
                oclp_plist_data = plistlib.load(open(oclp_plist, "rb"))
                if "Kernel Debug Kit Used" in oclp_plist_data:
                    if oclp_plist_data["Kernel Debug Kit Used"] == str(kdk_path):
                        print("- Matching KDK determined to already be merged, skipping")
                        return
            except:
                pass

        if kdk_path is None:
            print(f"- Unable to find Kernel Debug Kit: {downloaded_kdk}")
            raise Exception("Unable to find Kernel Debug Kit")
        self.kdk_path = kdk_path
        print(f"- Found KDK at: {kdk_path}")
        print("- Merging KDK with Root Volume")
        utilities.elevated(
            # Only merge '/System/Library/Extensions'
            # 'Kernels' and 'KernelSupport' is wasted space for root patching (we don't care above dev kernels)
            ["rsync", "-r", "-i", "-a", f"{kdk_path}/System/Library/Extensions/", f"{self.mount_location}/System/Library/Extensions"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        # During reversing, we found that kmutil uses this path to determine whether the KDK was successfully merged
        # Best to verify now before we cause any damage
        if not (Path(self.mount_location) / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists():
            print("- Failed to merge KDK with Root Volume")
            raise Exception("Failed to merge KDK with Root Volume")
        print("- Successfully merged KDK with Root Volume")

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
                self.delete_nonmetal_enforcement()
                self.clean_auxiliary_kc()
                self.constants.root_patcher_succeeded = True
                print("- Unpatching complete")
                print("\nPlease reboot the machine for patches to take effect")

    def rebuild_snapshot(self):
        if self.rebuild_kernel_collection() is True:
            self.update_preboot_kernel_cache()
            self.rebuild_dyld_shared_cache()
            if self.create_new_apfs_snapshot() is True:
                print("- Patching complete")
                print("\nPlease reboot the machine for patches to take effect")
                if self.needs_kmutil_exemptions is True:
                    print("Note: Apple will require you to open System Preferences -> Security to allow the new kernel extensions to be loaded")
                self.constants.root_patcher_succeeded = True
                if self.constants.gui_mode is False:
                    input("\nPress [ENTER] to continue")

    def rebuild_kernel_collection(self):
        print("- Rebuilding Kernel Cache (This may take some time)")
        if self.constants.detected_os > os_data.os_data.catalina:
            # Base Arguments
            args = ["kmutil", "install"]

            if self.skip_root_kmutil_requirement is True:
                # Only rebuild the Auxiliary Kernel Collection
                args.append("--new")
                args.append("aux")

                args.append("--boot-path")
                args.append(f"{self.mount_location}/System/Library/KernelCollections/BootKernelExtensions.kc")

                args.append("--system-path")
                args.append(f"{self.mount_location}/System/Library/KernelCollections/SystemKernelExtensions.kc")
            else:
                # Rebuild Boot, System and Auxiliary Kernel Collections
                args.append("--volume-root")
                args.append(self.mount_location)

                # Build Boot, Sys and Aux KC
                args.append("--update-all")

                # If multiple kernels found, only build release KCs
                args.append("--variant-suffix")
                args.append("release")

            if self.constants.detected_os >= os_data.os_data.ventura:
                # With Ventura, we're required to provide a KDK in some form
                # to rebuild the Kernel Cache
                #
                # However since we already merged the KDK onto root with 'ditto',
                # We can add '--allow-missing-kdk' to skip parsing the KDK
                #
                # This allows us to only delete/overwrite kexts inside of
                # /System/Library/Extensions and not the entire KDK
                args.append("--allow-missing-kdk")

                # 'install' and '--update-all' cannot be used together in Ventura.
                # kmutil will request the usage of 'create' instead:
                #     Warning: kmutil install's usage of --update-all is deprecated.
                #              Use kmutil create --update-install instead'
                args[1] = "create"

            if self.needs_kmutil_exemptions is True:
                # When installing to '/Library/Extensions', following args skip kext consent
                # prompt in System Preferences when SIP's disabled
                print("  (You will get a prompt by System Preferences, ignore for now)")
                args.append("--no-authentication")
                args.append("--no-authorization")
        else:
            args = ["kextcache", "-i", f"{self.mount_location}/"]

        result = utilities.elevated(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # kextcache notes:
        # - kextcache always returns 0, even if it fails
        # - Check the output for 'KernelCache ID' to see if the cache was successfully rebuilt
        # kmutil notes:
        # - will return 71 on failure to build KCs
        # - will return 31 on 'No binaries or codeless kexts were provided'
        # - will return -10 if the volume is missing (ie. unmounted by another process)
        if result.returncode != 0 or (self.constants.detected_os < os_data.os_data.catalina and "KernelCache ID" not in result.stdout.decode()):
            print("- Unable to build new kernel cache")
            print(f"\nReason for Patch Failure ({result.returncode}):")
            print(result.stdout.decode())
            print("")
            print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
            if self.constants.gui_mode is False:
                input("Press [ENTER] to continue")
            return False

        if self.skip_root_kmutil_requirement is True:
            # Force rebuild the Auxiliary KC
            result = utilities.elevated(["killall", "syspolicyd", "kernelmanagerd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                print("- Unable to remove kernel extension policy files")
                print(f"\nReason for Patch Failure ({result.returncode}):")
                print(result.stdout.decode())
                print("")
                print("\nPlease reboot the machine to avoid potential issues rerunning the patcher")
                if self.constants.gui_mode is False:
                    input("Press [ENTER] to continue")
                return False

            for file in ["KextPolicy", "KextPolicy-shm", "KextPolicy-wal"]:
                self.remove_file("/private/var/db/SystemPolicyConfiguration/", file)

        print("- Successfully built new kernel cache")
        return True

    def create_new_apfs_snapshot(self):
        if self.root_supports_snapshot is True:
            print("- Creating new APFS snapshot")
            bless = utilities.elevated(
                [
                    "bless",
                    "--folder", f"{self.mount_location}/System/Library/CoreServices",
                    "--bootefi", "--create-snapshot"
                ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if bless.returncode != 0:
                print("- Unable to create new snapshot")
                print("Reason for snapshot failure:")
                print(bless.stdout.decode())
                if "Can't use last-sealed-snapshot or create-snapshot on non system volume" in bless.stdout.decode():
                    print("- This is an APFS bug with Monterey and newer! Perform a clean installation to ensure your APFS volume is built correctly")
                return False
            self.unmount_drive()
        return True

    def unmount_drive(self):
        print("- Unmounting Root Volume (Don't worry if this fails)")
        utilities.elevated(["diskutil", "unmount", self.root_mount_path], stdout=subprocess.PIPE).stdout.decode().strip().encode()

    def rebuild_dyld_shared_cache(self):
        if self.constants.detected_os <= os_data.os_data.catalina:
            print("- Rebuilding dyld shared cache")
            utilities.process_status(utilities.elevated(["update_dyld_shared_cache", "-root", f"{self.mount_location}/"]))

    def update_preboot_kernel_cache(self):
        if self.constants.detected_os == os_data.os_data.catalina:
            print("- Rebuilding preboot kernel cache")
            utilities.process_status(utilities.elevated(["kcditto"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def clean_skylight_plugins(self):
        if (Path(self.mount_application_support) / Path("SkyLightPlugins/")).exists():
            print("- Found SkylightPlugins folder, removing old plugins")
            utilities.process_status(utilities.elevated(["rm", "-Rf", f"{self.mount_application_support}/SkyLightPlugins"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["mkdir", f"{self.mount_application_support}/SkyLightPlugins"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            print("- Creating SkylightPlugins folder")
            utilities.process_status(utilities.elevated(["mkdir", "-p", f"{self.mount_application_support}/SkyLightPlugins/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def delete_nonmetal_enforcement(self):
        for arg in ["useMetal", "useIOP"]:
            result = subprocess.run(["defaults", "read", "/Library/Preferences/com.apple.CoreDisplay", arg], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
            if result in ["0", "false", "1", "true"]:
                print(f"- Removing non-Metal Enforcement Preference: {arg}")
                utilities.elevated(["defaults", "delete", "/Library/Preferences/com.apple.CoreDisplay", arg])

    def clean_auxiliary_kc(self):
        # When reverting root volume patches, the AuxKC will still retain the UUID
        # it was built against. Thus when Boot/SysKC are reverted, Aux will break
        # To resolve this, delete all installed kexts in /L*/E* and rebuild the AuxKC
        # We can verify our binaries based off the OpenCore-Legacy-Patcher.plist file
        if self.constants.detected_os < os_data.os_data.big_sur:
            return

        oclp_path = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if not Path(oclp_path).exists():
            return

        print("- Cleaning Auxiliary Kernel Collection")
        oclp_plist_data = plistlib.load(Path(oclp_path).open("rb"))

        for key in oclp_plist_data:
            if "Install" not in oclp_plist_data[key]:
                continue
            for location in oclp_plist_data[key]["Install"]:
                if not location.endswith("Extensions"):
                    continue
                for file in oclp_plist_data[key]["Install"][location]:
                    if not file.endswith(".kext"):
                        continue
                    self.remove_file("/Library/Extensions", file)

        # Handle situations where users migrated from older OSes with a lot of garbage in /L*/E*
        # ex. Nvidia Web Drivers, NetUSB, dosdude1's patches, etc.
        # Move if file's age is older than October 2021 (year before Ventura)
        if self.constants.detected_os < os_data.os_data.ventura:
            return

        relocation_path = "/Library/Relocated Extensions"
        if not Path(relocation_path).exists():
            utilities.elevated(["mkdir", relocation_path])

        for file in Path("/Library/Extensions").glob("*.kext"):
            if datetime.fromtimestamp(file.stat().st_mtime) < datetime(2021, 10, 1):
                print(f"  - Relocating {file.name} kext to {relocation_path}")
                utilities.elevated(["mv", file, relocation_path])

    def write_patchset(self, patchset):
        destination_path = f"{self.mount_location}/System/Library/CoreServices"
        file_name = "OpenCore-Legacy-Patcher.plist"
        destination_path_file = f"{destination_path}/{file_name}"
        if sys_patch_helpers.sys_patch_helpers(self.constants).generate_patchset_plist(patchset, file_name, self.kdk_path):
            print("- Writing patchset information to Root Volume")
            if Path(destination_path_file).exists():
                utilities.process_status(utilities.elevated(["rm", destination_path_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(utilities.elevated(["cp", f"{self.constants.payload_path}/{file_name}", destination_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

    def add_auxkc_support(self, install_file, source_folder_path, install_patch_directory, destination_folder_path):
        # In macOS Ventura, KDKs are required to build new Boot and System KCs
        # However for some patch sets, we're able to use the Auxiliary KCs with '/Library/Extensions'

        # kernelmanagerd determines which kext is installed by their 'OSBundleRequired' entry
        # If a kext is labeled as 'OSBundleRequired: Root' or 'OSBundleRequired: Safe Boot',
        # kernelmanagerd will require the kext to be installed in the Boot/SysKC

        # Additionally, kexts starting with 'com.apple.' are not natively allowed to be installed
        # in the AuxKC. So we need to explicitly set our 'OSBundleRequired' to 'Auxiliary'

        if self.skip_root_kmutil_requirement is False:
            return destination_folder_path
        if not install_file.endswith(".kext"):
            return destination_folder_path
        if install_patch_directory != "/System/Library/Extensions":
            return destination_folder_path
        if self.constants.detected_os < os_data.os_data.ventura:
            return destination_folder_path

        updated_install_location = str(self.mount_location_data) + "/Library/Extensions"

        print(f"  - Adding AuxKC support to {install_file}")
        plist_path = Path(Path(source_folder_path) / Path(install_file) / Path("Contents/Info.plist"))
        plist_data = plistlib.load((plist_path).open("rb"))

        # Check if we need to update the 'OSBundleRequired' entry
        if not plist_data["CFBundleIdentifier"].startswith("com.apple."):
            return updated_install_location
        if "OSBundleRequired" in plist_data:
            if plist_data["OSBundleRequired"] == "Auxiliary":
                return updated_install_location

        plist_data["OSBundleRequired"] = "Auxiliary"
        plistlib.dump(plist_data, plist_path.open("wb"))

        self.check_kexts_needs_authentication(install_file)

        return updated_install_location

    def check_kexts_needs_authentication(self, kext_name):
        # Verify whether the user needs to authenticate in System Preferences
        # Specifically under 'private/var/db/KernelManagement/AuxKC/CurrentAuxKC/com.apple.kcgen.instructions.plist'
        #    ["kextsToBuild"][i]:
        #       ["bundlePathMainOS"] = /Library/Extensions/Test.kext
        #       ["cdHash"] =           Bundle's CDHash (random on ad-hoc signed, static on dev signed)
        #       ["teamID"] =           Team ID (blank on ad-hoc signed)
        # To grab the CDHash of a kext, run 'codesign -dvvv <kext_path>'
        try:
            aux_cache_path = Path(self.mount_location_data) / Path("/private/var/db/KernelExtensionManagement/AuxKC/CurrentAuxKC/com.apple.kcgen.instructions.plist")
            if aux_cache_path.exists():
                aux_cache_data = plistlib.load((aux_cache_path).open("rb"))
                for kext in aux_cache_data["kextsToBuild"]:
                    if "bundlePathMainOS" in aux_cache_data["kextsToBuild"][kext]:
                        if aux_cache_data["kextsToBuild"][kext]["bundlePathMainOS"] == f"/Library/Extensions/{kext_name}":
                            return
        except PermissionError:
            pass

        print(f"  - {kext_name} requires authentication in System Preferences")
        self.constants.needs_to_open_preferences = True # Notify in GUI to open System Preferences

    def patch_root_vol(self):
        print(f"- Running patches for {self.model}")
        if self.patch_set_dictionary != {}:
            self.execute_patchset(self.patch_set_dictionary)
        else:
            self.execute_patchset(sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).generate_patchset(self.hardware_details))

        if self.constants.wxpython_variant is True and self.constants.detected_os >= os_data.os_data.big_sur:
            sys_patch_auto.AutomaticSysPatch.install_auto_patcher_launch_agent(self.constants)

        self.rebuild_snapshot()

    def execute_patchset(self, required_patches):
        source_files_path = str(self.constants.payload_local_binaries_root_path)
        self.preflight_checks(required_patches, source_files_path)
        for patch in required_patches:
            print("- Installing Patchset: " + patch)
            if "Remove" in required_patches[patch]:
                for remove_patch_directory in required_patches[patch]["Remove"]:
                    print("- Remove Files at: " + remove_patch_directory)
                    for remove_patch_file in required_patches[patch]["Remove"][remove_patch_directory]:
                        destination_folder_path = str(self.mount_location) + remove_patch_directory
                        self.remove_file(destination_folder_path, remove_patch_file)


            for method_install in ["Install", "Install Non-Root"]:
                if method_install in required_patches[patch]:
                    for install_patch_directory in list(required_patches[patch][method_install]):
                        print(f"- Handling Installs in: {install_patch_directory}")
                        for install_file in list(required_patches[patch][method_install][install_patch_directory]):
                            source_folder_path = source_files_path + "/" + required_patches[patch][method_install][install_patch_directory][install_file] + install_patch_directory
                            if method_install == "Install":
                                destination_folder_path = str(self.mount_location) + install_patch_directory
                            else:
                                if install_patch_directory == "/Library/Extensions":
                                    self.needs_kmutil_exemptions = True
                                    self.check_kexts_needs_authentication(install_file)
                                destination_folder_path = str(self.mount_location_data) + install_patch_directory

                            updated_destination_folder_path = self.add_auxkc_support(install_file, source_folder_path, install_patch_directory, destination_folder_path)

                            if destination_folder_path != updated_destination_folder_path:
                                # Update required_patches to reflect the new destination folder path
                                if updated_destination_folder_path not in required_patches[patch][method_install]:
                                    required_patches[patch][method_install].update({updated_destination_folder_path: {}})
                                required_patches[patch][method_install][updated_destination_folder_path].update({install_file: required_patches[patch][method_install][install_patch_directory][install_file]})
                                required_patches[patch][method_install][install_patch_directory].pop(install_file)

                                destination_folder_path = updated_destination_folder_path

                            self.install_new_file(source_folder_path, destination_folder_path, install_file)

            if "Processes" in required_patches[patch]:
                for process in required_patches[patch]["Processes"]:
                    # Some processes need sudo, however we cannot directly call sudo in some scenarios
                    # Instead, call elevated funtion if string's boolean is True
                    if required_patches[patch]["Processes"][process] is True:
                        print(f"- Running Process as Root:\n{process}")
                        utilities.process_status(utilities.elevated(process.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
                    else:
                        print(f"- Running Process:\n{process}")
                        utilities.process_status(subprocess.run(process, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True))
        if "AMD Legacy GCN" in required_patches:
            sys_patch_helpers.sys_patch_helpers(self.constants).disable_window_server_caching()
        self.write_patchset(required_patches)

    def preflight_checks(self, required_patches, source_files_path):
        print("- Running Preflight Checks before patching")

        # Make sure old SkyLight plugins aren't being used
        self.clean_skylight_plugins()
        # Make sure non-Metal Enforcement preferences are not present
        self.delete_nonmetal_enforcement()
        # Make sure we clean old kexts in /L*/E* that are not in the patchset
        self.clean_auxiliary_kc()

        # Make sure SNB kexts are compatible with the host
        if "Intel Sandy Bridge" in required_patches:
            sys_patch_helpers.sys_patch_helpers(self.constants).snb_board_id_patch(source_files_path)

        for patch in required_patches:
            # Check if all files are present
            for method_type in ["Install", "Install Non-Root"]:
                if method_type in required_patches[patch]:
                    for install_patch_directory in required_patches[patch][method_type]:
                        for install_file in required_patches[patch][method_type][install_patch_directory]:
                            source_file = source_files_path + "/" + required_patches[patch][method_type][install_patch_directory][install_file] + install_patch_directory + "/" + install_file
                            if not Path(source_file).exists():
                                raise Exception(f"Failed to find {source_file}")

        # Ensure KDK is properly installed
        self.merge_kdk_with_root()

        print("- Finished Preflight, starting patching")

    def install_new_file(self, source_folder, destination_folder, file_name):
        # .frameworks are merged
        # .kexts and .apps are deleted and replaced
        file_name_str = str(file_name)

        if not Path(destination_folder).exists():
            print(f"  - Skipping {file_name}, cannot locate {source_folder}")
            return

        if file_name_str.endswith(".framework"):
            # merge with rsync
            print(f"  - Installing: {file_name}")
            utilities.elevated(["rsync", "-r", "-i", "-a", f"{source_folder}/{file_name}", f"{destination_folder}/"], stdout=subprocess.PIPE)
            self.fix_permissions(destination_folder + "/" + file_name)
        elif Path(source_folder + "/" + file_name_str).is_dir():
            # Applicable for .kext, .app, .plugin, .bundle, all of which are directories
            if Path(destination_folder + "/" + file_name).exists():
                print(f"  - Found existing {file_name}, overwriting...")
                utilities.process_status(utilities.elevated(["rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print(f"  - Installing: {file_name}")
            utilities.process_status(utilities.elevated(["cp", "-R", f"{source_folder}/{file_name}", destination_folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            self.fix_permissions(destination_folder + "/" + file_name)
        else:
            # Assume it's an individual file, replace as normal
            if Path(destination_folder + "/" + file_name).exists():
                print(f"  - Found existing {file_name}, overwriting...")
                utilities.process_status(utilities.elevated(["rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                print(f"  - Installing: {file_name}")
            utilities.process_status(utilities.elevated(["cp", f"{source_folder}/{file_name}", destination_folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            self.fix_permissions(destination_folder + "/" + file_name)

    def remove_file(self, destination_folder, file_name):
        if Path(destination_folder + "/" + file_name).exists():
            print(f"  - Removing: {file_name}")
            if Path(destination_folder + "/" + file_name).is_dir():
                utilities.process_status(utilities.elevated(["rm", "-R", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            else:
                utilities.process_status(utilities.elevated(["rm", f"{destination_folder}/{file_name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))


    def fix_permissions(self, destination_file):
        chmod_args = ["chmod", "-Rf", "755", destination_file]
        chown_args = ["chown", "-Rf", "root:wheel", destination_file]
        if not Path(destination_file).is_dir():
            # Strip recursive arguments
            chmod_args.pop(1)
            chown_args.pop(1)
        utilities.process_status(utilities.elevated(chmod_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        utilities.process_status(utilities.elevated(chown_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))


    def check_files(self):
        if Path(self.constants.payload_local_binaries_root_path).exists():
            print("- Found local Apple Binaries")
            if self.constants.gui_mode is False:
                patch_input = input("Would you like to redownload?(y/n): ")
                if patch_input in {"y", "Y", "yes", "Yes"}:
                    shutil.rmtree(Path(self.constants.payload_local_binaries_root_path))
                    output = self.download_files()
                else:
                    output = True
            else:
                output = self.download_files()
        else:
            output = self.download_files()
        return output

    def download_files(self):
        if self.constants.cli_mode is True:
            download_result, link = sys_patch_download.grab_patcher_support_pkg(self.constants).download_files()
        else:
            download_result = True
            link = sys_patch_download.grab_patcher_support_pkg(self.constants).generate_pkg_link()

        if download_result and self.constants.payload_local_binaries_root_path_zip.exists():
            print("- Unzipping binaries...")
            utilities.process_status(subprocess.run(["ditto", "-V", "-x", "-k", "--sequesterRsrc", "--rsrc", self.constants.payload_local_binaries_root_path_zip, self.constants.payload_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            print("- Binaries downloaded to:")
            print(self.constants.payload_path)
            return self.constants.payload_local_binaries_root_path
        else:
            if self.constants.gui_mode is True:
                print("- Download failed, please verify the below link work:")
                print(link)
                print("\nIf you continue to have issues, try using the Offline builds")
                print("located on Github next to the other builds")
            else:
                input("\nPress enter to continue")
        return None

    # Entry Function
    def start_patch(self):
        print("- Starting Patch Process")
        print(f"- Determining Required Patch set for Darwin {self.constants.detected_os}")
        self.patch_set_dictionary = sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).generate_patchset(self.hardware_details)

        if self.patch_set_dictionary == {}:
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
                    if self.mount_root_vol() is True:
                        self.patch_root_vol()
                        if self.constants.gui_mode is False:
                            input("\nPress [ENTER] to return to the main menu")
                    else:
                        print("- Recommend rebooting the machine and trying to patch again")
                        if self.constants.gui_mode is False:
                            input("- Press [ENTER] to exit: ")
            elif self.constants.gui_mode is False:
                input("\nPress [ENTER] to return to the main menu: ")

        else:
            print("- Returning to main menu")

    def start_unpatch(self):
        print("- Starting Unpatch Process")
        if sys_patch_detect.detect_root_patch(self.computer.real_model, self.constants).verify_patch_allowed(print_errors=True) is True:
            if self.mount_root_vol() is True:
                self.unpatch_root_vol()
                if self.constants.gui_mode is False:
                    input("\nPress [ENTER] to return to the main menu")
            else:
                print("- Recommend rebooting the machine and trying to patch again")
                if self.constants.gui_mode is False:
                    input("- Press [ENTER] to exit: ")
        elif self.constants.gui_mode is False:
            input("\nPress [ENTER] to return to the main menu")
