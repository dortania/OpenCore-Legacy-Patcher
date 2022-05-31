# Additional support functions for sys_patch.py
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

from resources import generate_smbios
from pathlib import Path
from datetime import datetime
import plistlib
import os


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

            if len(board_to_patch_hex) != len(reported_board_hex):
                print(f"- Error: Board ID {self.constants.computer.reported_board_id} is not the same length as {board_to_patch}")
                raise Exception("Host's Board ID is not the same length as the kext's Board ID, cannot patch!!!")
            else:
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


    def generate_patchset_plist(self, patchset, file_name):
        source_path = f"{self.constants.payload_path}"
        source_path_file = f"{source_path}/{file_name}"

        data = {
            "OpenCore Legacy Patcher": f"v{self.constants.patcher_version}",
            "PatcherSupportPkg": f"v{self.constants.patcher_support_pkg_version}",
            "Time Patched": f"{datetime.now().strftime('%B %d, %Y @ %H:%M:%S')}",
        }
        data.update(patchset)
        if Path(source_path_file).exists():
            os.remove(source_path_file)
        # Need to write to a safe location
        plistlib.dump(data, Path(source_path_file).open("wb"), sort_keys=False)
        if Path(source_path_file).exists():
            return True
        return False