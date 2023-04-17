# Additional support functions for sys_patch.py
# Copyright (C) 2020-2023, Dhinak G, Mykola Grymalyuk

import plistlib
import os
import logging
import subprocess

from typing import Union
from pathlib import Path
from datetime import datetime

from data import os_data
from resources import bplist, constants, generate_smbios, utilities


class SysPatchHelpers:
    """
    Library of helper functions for sys_patch.py and related libraries
    """

    def __init__(self, global_constants: constants.Constants):
        self.constants: constants.Constants = global_constants


    def snb_board_id_patch(self, source_files_path: str):
        """
        Patch AppleIntelSNBGraphicsFB.kext to support unsupported Board IDs

        AppleIntelSNBGraphicsFB hard codes the supported Board IDs for Sandy Bridge iGPUs
        Because of this, the kext errors out on unsupported systems
        This function simply patches in a supported Board ID, using 'determine_best_board_id_for_sandy()'
        to supplement the ideal Board ID

        Parameters:
            source_files_path (str): Path to the source files

        """

        source_files_path = str(source_files_path)

        if self.constants.computer.reported_board_id in self.constants.sandy_board_id_stock:
            return

        logging.info(f"- Found unsupported Board ID {self.constants.computer.reported_board_id}, performing AppleIntelSNBGraphicsFB bin patching")

        board_to_patch = generate_smbios.determine_best_board_id_for_sandy(self.constants.computer.reported_board_id, self.constants.computer.gpus)
        logging.info(f"- Replacing {board_to_patch} with {self.constants.computer.reported_board_id}")

        board_to_patch_hex = bytes.fromhex(board_to_patch.encode('utf-8').hex())
        reported_board_hex = bytes.fromhex(self.constants.computer.reported_board_id.encode('utf-8').hex())

        if len(board_to_patch_hex) > len(reported_board_hex):
            # Pad the reported Board ID with zeros to match the length of the board to patch
            reported_board_hex = reported_board_hex + bytes(len(board_to_patch_hex) - len(reported_board_hex))
        elif len(board_to_patch_hex) < len(reported_board_hex):
            logging.info(f"- Error: Board ID {self.constants.computer.reported_board_id} is longer than {board_to_patch}")
            raise Exception("Host's Board ID is longer than the kext's Board ID, cannot patch!!!")

        path = source_files_path + "/10.13.6/System/Library/Extensions/AppleIntelSNBGraphicsFB.kext/Contents/MacOS/AppleIntelSNBGraphicsFB"
        if not Path(path).exists():
            logging.info(f"- Error: Could not find {path}")
            raise Exception("Failed to find AppleIntelSNBGraphicsFB.kext, cannot patch!!!")

        with open(path, 'rb') as f:
            data = f.read()
            data = data.replace(board_to_patch_hex, reported_board_hex)
            with open(path, 'wb') as f:
                f.write(data)


    def generate_patchset_plist(self, patchset: dict, file_name: str, kdk_used: Path):
        """
        Generate patchset file for user reference

        Parameters:
            patchset (dict): Dictionary of patchset, see sys_patch_detect.py and sys_patch_dict.py
            file_name (str): Name of the file to write to
            kdk_used (Path): Path to the KDK used, if any

        Returns:
            bool: True if successful, False if not

        """

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
            "OS Version": f"{self.constants.detected_os}.{self.constants.detected_os_minor} ({self.constants.detected_os_build})",
        }

        data.update(patchset)

        if Path(source_path_file).exists():
            os.remove(source_path_file)

        # Need to write to a safe location
        plistlib.dump(data, Path(source_path_file).open("wb"), sort_keys=False)

        if Path(source_path_file).exists():
            return True

        return False


    def disable_window_server_caching(self):
        """
        Disable WindowServer's asset caching

        On legacy GCN GPUs, the WindowServer cache generated creates
        corrupted Opaque shaders.

        To work-around this, we disable WindowServer caching
        And force macOS into properly generating the Opaque shaders
        """

        if self.constants.detected_os < os_data.os_data.ventura:
             return

        logging.info("- Disabling WindowServer Caching")
        # Invoke via 'bash -c' to resolve pathing
        utilities.elevated(["bash", "-c", "rm -rf /private/var/folders/*/*/*/WindowServer/com.apple.WindowServer"])
        # Disable writing to WindowServer folder
        utilities.elevated(["bash", "-c", "chflags uchg /private/var/folders/*/*/*/WindowServer"])
        # Reference:
        #   To reverse write lock:
        #   'chflags nouchg /private/var/folders/*/*/*/WindowServer'


    def remove_news_widgets(self):
        """
        Remove News Widgets from Notification Centre

        On Ivy Bridge and Haswell iGPUs, RenderBox will crash the News Widgets in
        Notification Centre. To ensure users can access Notifications normally,
        we manually remove all News Widgets
        """

        if self.constants.detected_os < os_data.os_data.ventura:
            return

        logging.info("- Parsing Notification Centre Widgets")
        file_path = "~/Library/Containers/com.apple.notificationcenterui/Data/Library/Preferences/com.apple.notificationcenterui.plist"
        file_path = Path(file_path).expanduser()

        if not file_path.exists():
            logging.info("  - Defaults file not found, skipping")
            return

        did_find = False
        with open(file_path, "rb") as f:
            data = plistlib.load(f)
            if "widgets" not in data:
                return

            if "instances" not in data["widgets"]:
                return

            for widget in list(data["widgets"]["instances"]):
                widget_data = bplist.BPListReader(widget).parse()
                for entry in widget_data:
                    if 'widget' not in entry:
                        continue
                    sub_data = bplist.BPListReader(widget_data[entry]).parse()
                    for sub_entry in sub_data:
                        if not '$object' in sub_entry:
                            continue
                        if not b'com.apple.news' in sub_data[sub_entry][2]:
                            continue
                        logging.info(f"  - Found News Widget to remove: {sub_data[sub_entry][2].decode('ascii')}")
                        data["widgets"]["instances"].remove(widget)
                        did_find = True

        if did_find:
            with open(file_path, "wb") as f:
                plistlib.dump(data, f, sort_keys=False)
            subprocess.run(["killall", "NotificationCenter"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def install_rsr_repair_binary(self):
        """
        Installs RSRRepair

        RSRRepair is a utility that will sync the SysKC and BootKC in the event of a panic

        With macOS 13.2, Apple implemented the Rapid Security Response System
        However Apple added a half baked snapshot reversion system if seal was broken,
        which forgets to handle Preboot BootKC syncing.

        Thus this application will try to re-sync the BootKC with SysKC in the event of a panic
            Reference: https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1019

        This is a (hopefully) temporary work-around, however likely to stay.
        RSRRepair has the added bonus of fixing desynced KCs from 'bless', so useful in Big Sur+
            Source: https://github.com/flagersgit/RSRRepair

        """

        if self.constants.detected_os < os_data.os_data.big_sur:
            return

        logging.info("- Installing Kernel Collection syncing utility")
        result = utilities.elevated([self.constants.rsrrepair_userspace_path, "--install"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.info(f"  - Failed to install RSRRepair: {result.stdout.decode()}")


    def patch_gpu_compiler_libraries(self, mount_point: Union[str, Path]):
        """
        Fix GPUCompiler.framework's libraries to resolve linking issues

        On 13.3 with 3802 GPUs, OCLP will downgrade GPUCompiler to resolve
        graphics support. However the binary hardcodes the library names,
        and thus we need to adjust the libraries to match (31001.669)

        Important portions of the library will be downgraded to 31001.669,
        and the remaining bins will be copied over (via CoW to reduce waste)

        Primary folders to merge:
        - 31001.XXX: (current OS version)
            - include:
                - module.modulemap
                - opencl-c.h
            - lib (entire directory)

        Parameters:
            mount_point: The mount point of the target volume
        """

        if self.constants.detected_os < os_data.os_data.ventura:
            return
        if self.constants.detected_os == os_data.os_data.ventura:
            if self.constants.detected_os_minor < 4:
                return

        LIBRARY_DIR = f"{mount_point}/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/31001/Libraries/lib/clang"
        GPU_VERSION = "31001.669"

        DEST_DIR = f"{LIBRARY_DIR}/{GPU_VERSION}"

        if not Path(DEST_DIR).exists():
            return

        for file in Path(LIBRARY_DIR).iterdir():
            if file.is_file():
                continue
            if file.name == GPU_VERSION:
                continue

            # Partial match as each OS can increment the version
            if not file.name.startswith("31001."):
                continue

            logging.info(f"- Merging GPUCompiler.framework libraries to match binary")

            src_dir = f"{LIBRARY_DIR}/{file.name}"
            if not Path(f"{DEST_DIR}/lib").exists():
                utilities.process_status(utilities.elevated(["cp", "-cR", f"{src_dir}/lib", f"{DEST_DIR}/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))

            break