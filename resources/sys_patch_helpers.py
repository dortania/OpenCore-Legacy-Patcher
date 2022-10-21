# Additional support functions for sys_patch.py
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import subprocess
import tempfile
from data import os_data
from resources import generate_smbios, utilities
from pathlib import Path
from datetime import datetime
import plistlib
import os

from resources import constants

class sys_patch_helpers:

    def __init__(self, constants):
        self.constants = constants


    def snb_board_id_patch(self, source_files_path):
        # AppleIntelSNBGraphicsFB hard codes the supported Board IDs for Sandy Bridge iGPUs
        # Because of this, the kext errors out on unsupported systems
        # This function simply patches in a supported Board ID, using 'determine_best_board_id_for_sandy()'
        # to supplement the ideal Board ID
        source_files_path = str(source_files_path)
        if self.constants.computer.reported_board_id not in self.constants.sandy_board_id_stock:
            print(f"- Found unsupported Board ID {self.constants.computer.reported_board_id}, performing AppleIntelSNBGraphicsFB bin patching")
            board_to_patch = generate_smbios.determine_best_board_id_for_sandy(self.constants.computer.reported_board_id, self.constants.computer.gpus)
            print(f"- Replacing {board_to_patch} with {self.constants.computer.reported_board_id}")

            board_to_patch_hex = bytes.fromhex(board_to_patch.encode('utf-8').hex())
            reported_board_hex = bytes.fromhex(self.constants.computer.reported_board_id.encode('utf-8').hex())

            if len(board_to_patch_hex) > len(reported_board_hex):
                # Pad the reported Board ID with zeros to match the length of the board to patch
                reported_board_hex = reported_board_hex + bytes(len(board_to_patch_hex) - len(reported_board_hex))
            elif len(board_to_patch_hex) < len(reported_board_hex):
                print(f"- Error: Board ID {self.constants.computer.reported_board_id} is longer than {board_to_patch}")
                raise Exception("Host's Board ID is longer than the kext's Board ID, cannot patch!!!")

            path = source_files_path + "/10.13.6/System/Library/Extensions/AppleIntelSNBGraphicsFB.kext/Contents/MacOS/AppleIntelSNBGraphicsFB"
            if Path(path).exists():
                with open(path, 'rb') as f:
                    data = f.read()
                    data = data.replace(board_to_patch_hex, reported_board_hex)
                    with open(path, 'wb') as f:
                        f.write(data)
            else:
                print(f"- Error: Could not find {path}")
                raise Exception("Failed to find AppleIntelSNBGraphicsFB.kext, cannot patch!!!")


    def generate_patchset_plist(self, patchset, file_name, kdk_used):
        source_path = f"{self.constants.payload_path}"
        source_path_file = f"{source_path}/{file_name}"

        kdk_string = "Not applicable"
        if kdk_used:
            kdk_string = kdk_used

        data = {
            "OpenCore Legacy Patcher": f"v{self.constants.patcher_version}",
            "PatcherSupportPkg": f"v{self.constants.patcher_support_pkg_version}",
            "Time Patched": f"{datetime.now().strftime('%B %d, %Y @ %H:%M:%S')}",
            "Commit URL": f"{self.constants.commit_info[2]}",
            "Kernel Debug Kit Used": f"{kdk_string}",
        }
        data.update(patchset)
        if Path(source_path_file).exists():
            os.remove(source_path_file)
        # Need to write to a safe location
        plistlib.dump(data, Path(source_path_file).open("wb"), sort_keys=False)
        if Path(source_path_file).exists():
            return True
        return False

    def install_kdk(self):
        if not self.constants.kdk_download_path.exists():
            return

        print(f"- Installing downloaded KDK (this may take a while)")
        with tempfile.TemporaryDirectory() as mount_point:
            utilities.process_status(subprocess.run(["hdiutil", "attach", self.constants.kdk_download_path, "-mountpoint", mount_point, "-nobrowse"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            # Install the KDK
            utilities.process_status(utilities.elevated(["installer", "-pkg", f"{mount_point}/KernelDebugKit.pkg", "-target", "/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            subprocess.run(["hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # Do not really care if this fails
        print("- Successfully installed KDK")


    def determine_kdk_present(self, match_closest=False, override_build=None):
        # Check if KDK is present
        # If 'match_closest' is True, will provide the closest match to the reported KDK

        kdk_array = []

        search_build = self.constants.detected_os_build
        if override_build:
            search_build = override_build

        if not Path("/Library/Developer/KDKs").exists():
            return None


        for kdk_folder in Path("/Library/Developer/KDKs").iterdir():
            if not kdk_folder.name.endswith(".kdk"):
                continue

            # Ensure direct match
            if kdk_folder.name.endswith(f"{search_build}.kdk"):
                # Verify that the KDK is valid
                if (kdk_folder / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists():
                    return kdk_folder
            if match_closest is True:
                # ex: KDK_13.0_22A5266r.kdk -> 22A5266r.kdk -> 22A5266r
                try:
                    build = kdk_folder.name.split("_")[2].split(".")[0]
                    # Don't append if Darwin Major is different
                    if build.startswith(str(self.constants.detected_os)):
                        kdk_array.append(build)
                except IndexError:
                    pass

        if match_closest is True:
            result = os_data.os_conversion.find_largest_build(kdk_array)
            print(f"- Closest KDK match to {search_build}: {result}")
            for kdk_folder in Path("/Library/Developer/KDKs").iterdir():
                if kdk_folder.name.endswith(f"{result}.kdk"):
                    # Verify that the KDK is valid
                    if (kdk_folder / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists():
                        return kdk_folder
        return None


    def disable_window_server_caching(self):
        # On legacy GCN GPUs, the WindowServer cache generated creates
        # corrupted Opaque shaders.
        # To work-around this, we disable WindowServer caching
        # And force macOS into properly generating the Opaque shaders
        print("- Disabling WindowServer Caching")
        # Invoke via 'bash -c' to resolve pathing
        utilities.elevated(["bash", "-c", "rm -rf /private/var/folders/*/*/*/WindowServer/com.apple.WindowServer"])
        # Disable writing to WindowServer folder
        utilities.elevated(["bash", "-c", "chflags uchg /private/var/folders/*/*/*/WindowServer"])
