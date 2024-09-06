"""
support.py: Kernel Cache support functions
"""

import logging
import plistlib

from pathlib  import Path
from datetime import datetime

from ...patchsets import PatchType

from ....datasets import os_data
from ....support  import subprocess_wrapper


class KernelCacheSupport:

    def __init__(self, mount_location_data: str, detected_os: int, skip_root_kmutil_requirement: bool) -> None:
        self.mount_location_data = mount_location_data
        self.detected_os = detected_os
        self.skip_root_kmutil_requirement = skip_root_kmutil_requirement


    def check_kexts_needs_authentication(self, kext_name: str) -> bool:
        """
        Verify whether the user needs to authenticate in System Preferences
        Sets 'needs_to_open_preferences' to True if the kext is not in the AuxKC

        Logic:
            Under 'private/var/db/KernelManagement/AuxKC/CurrentAuxKC/com.apple.kcgen.instructions.plist'
                ["kextsToBuild"][i]:
                ["bundlePathMainOS"] = /Library/Extensions/Test.kext
                ["cdHash"] =           Bundle's CDHash (random on ad-hoc signed, static on dev signed)
                ["teamID"] =           Team ID (blank on ad-hoc signed)
            To grab the CDHash of a kext, run 'codesign -dvvv <kext_path>'
        """
        if not kext_name.endswith(".kext"):
            return False

        try:
            aux_cache_path = Path(self.mount_location_data) / Path("/private/var/db/KernelExtensionManagement/AuxKC/CurrentAuxKC/com.apple.kcgen.instructions.plist")
            if aux_cache_path.exists():
                aux_cache_data = plistlib.load((aux_cache_path).open("rb"))
                for kext in aux_cache_data["kextsToBuild"]:
                    if "bundlePathMainOS" in aux_cache_data["kextsToBuild"][kext]:
                        if aux_cache_data["kextsToBuild"][kext]["bundlePathMainOS"] == f"/Library/Extensions/{kext_name}":
                            return False
        except PermissionError:
            pass

        logging.info(f"  - {kext_name} requires authentication in System Preferences")

        return True


    def add_auxkc_support(self, install_file: str, source_folder_path: str, install_patch_directory: str, destination_folder_path: str) -> str:
        """
        Patch provided Kext to support Auxiliary Kernel Collection

        Logic:
            In macOS Ventura, KDKs are required to build new Boot and System KCs
            However for some patch sets, we're able to use the Auxiliary KCs with '/Library/Extensions'

            kernelmanagerd determines which kext is installed by their 'OSBundleRequired' entry
            If a kext is labeled as 'OSBundleRequired: Root' or 'OSBundleRequired: Safe Boot',
            kernelmanagerd will require the kext to be installed in the Boot/SysKC

            Additionally, kexts starting with 'com.apple.' are not natively allowed to be installed
            in the AuxKC. So we need to explicitly set our 'OSBundleRequired' to 'Auxiliary'

        Parameters:
            install_file            (str): Kext file name
            source_folder_path      (str): Source folder path
            install_patch_directory (str): Patch directory
            destination_folder_path (str): Destination folder path

        Returns:
            str: Updated destination folder path
        """

        if self.skip_root_kmutil_requirement is False:
            return destination_folder_path
        if not install_file.endswith(".kext"):
            return destination_folder_path
        if install_patch_directory != "/System/Library/Extensions":
            return destination_folder_path
        if self.detected_os < os_data.os_data.ventura:
            return destination_folder_path

        updated_install_location = str(self.mount_location_data) + "/Library/Extensions"

        logging.info(f"  - Adding AuxKC support to {install_file}")
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

        return updated_install_location


    def clean_auxiliary_kc(self) -> None:
        """
        Clean the Auxiliary Kernel Collection

        Logic:
            When reverting root volume patches, the AuxKC will still retain the UUID
            it was built against. Thus when Boot/SysKC are reverted, Aux will break
            To resolve this, delete all installed kexts in /L*/E* and rebuild the AuxKC
            We can verify our binaries based off the OpenCore-Legacy-Patcher.plist file
        """

        if self.detected_os < os_data.os_data.big_sur:
            return

        logging.info("- Cleaning Auxiliary Kernel Collection")
        oclp_path = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"
        if Path(oclp_path).exists():
            oclp_plist_data = plistlib.load(Path(oclp_path).open("rb"))
            for key in oclp_plist_data:
                if isinstance(oclp_plist_data[key], (bool, int)):
                    continue
                for install_type in [PatchType.OVERWRITE_SYSTEM_VOLUME, PatchType.OVERWRITE_DATA_VOLUME, PatchType.MERGE_SYSTEM_VOLUME, PatchType.MERGE_DATA_VOLUME]:
                    if install_type not in oclp_plist_data[key]:
                        continue
                    for location in oclp_plist_data[key][install_type]:
                        if not location.endswith("Extensions"):
                            continue
                        for file in oclp_plist_data[key][install_type][location]:
                            if not file.endswith(".kext"):
                                continue
                            if not Path(f"/Library/Extensions/{file}").exists():
                                continue
                            logging.info(f"  - Removing {file}")
                            subprocess_wrapper.run_as_root(["/bin/rm", "-Rf", f"/Library/Extensions/{file}"])

        # Handle situations where users migrated from older OSes with a lot of garbage in /L*/E*
        # ex. Nvidia Web Drivers, NetUSB, dosdude1's patches, etc.
        # Move if file's age is older than October 2021 (year before Ventura)
        if self.detected_os < os_data.os_data.ventura:
            return

        relocation_path = "/Library/Relocated Extensions"
        if not Path(relocation_path).exists():
            subprocess_wrapper.run_as_root(["/bin/mkdir", relocation_path])

        for file in Path("/Library/Extensions").glob("*.kext"):
            try:
                if datetime.fromtimestamp(file.stat().st_mtime) < datetime(2021, 10, 1):
                    logging.info(f"  - Relocating {file.name} kext to {relocation_path}")
                    if Path(relocation_path) / Path(file.name).exists():
                        subprocess_wrapper.run_as_root(["/bin/rm", "-Rf", relocation_path / Path(file.name)])
                    subprocess_wrapper.run_as_root(["/bin/mv", file, relocation_path])
            except:
                # Some users have the most cursed /L*/E* folders
                # ex. Symlinks pointing to symlinks pointing to dead files
                pass
