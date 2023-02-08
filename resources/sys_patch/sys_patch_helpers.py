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
import logging

from resources import kdk_handler, bplist

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
            if Path(path).exists():
                with open(path, 'rb') as f:
                    data = f.read()
                    data = data.replace(board_to_patch_hex, reported_board_hex)
                    with open(path, 'wb') as f:
                        f.write(data)
            else:
                logging.info(f"- Error: Could not find {path}")
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

    def install_kdk(self):
        if not self.constants.kdk_download_path.exists():
            return

        logging.info(f"- Installing downloaded KDK (this may take a while)")
        with tempfile.TemporaryDirectory() as mount_point:
            utilities.process_status(subprocess.run(["hdiutil", "attach", self.constants.kdk_download_path, "-mountpoint", mount_point, "-nobrowse"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            # Due to a permissions bug in macOS, sometimes the OS will fail on a Read-only file system error
            # We don't actually need to write inside the KDK DMG, however macOS will do whatever it wants
            # Thus move the KDK to another location, and run the installer from there
            kdk_dst_path = Path(f"{self.constants.payload_path}/KernelDebugKit.pkg")
            if kdk_dst_path.exists():
                utilities.process_status(utilities.elevated(["rm", kdk_dst_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.process_status(subprocess.run(["cp", f"{mount_point}/KernelDebugKit.pkg", self.constants.payload_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            result = utilities.elevated(["installer", "-pkg", kdk_dst_path, "-target", "/"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.info("- Failed to install KDK:")
                logging.info(result.stdout.decode('utf-8'))
                if result.stderr:
                    logging.info(result.stderr.decode('utf-8'))
                utilities.elevated(["hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                raise Exception("Failed to install KDK")
            utilities.process_status(utilities.elevated(["rm", kdk_dst_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            utilities.elevated(["hdiutil", "detach", mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info("- Successfully installed KDK")



    def disable_window_server_caching(self):
        # On legacy GCN GPUs, the WindowServer cache generated creates
        # corrupted Opaque shaders.
        # To work-around this, we disable WindowServer caching
        # And force macOS into properly generating the Opaque shaders
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
        # On Ivy Bridge and Haswell iGPUs, RenderBox will crash the News Widgets in
        # Notification Centre. To ensure users can access Notifications normally,
        # we manually remove all News Widgets
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
            if "widgets" in data:
                if "instances" in data["widgets"]:
                    for widget in list(data["widgets"]["instances"]):
                        widget_data = bplist.BPListReader(widget).parse()
                        for entry in widget_data:
                            if not 'widget' in entry:
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
        # With macOS 13.2, Apple implemented the Rapid Security Response System
        # However Apple added a half baked snapshot reversion system if seal was broken,
        # which forgets to handle Preboot BootKC syncing

        # Thus this application will try to re-sync the BootKC with SysKC in the event of a panic
        # Reference: https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1019

        # This is a (hopefully) temporary work-around, however likely to stay.
        # RSRRepair has the added bonus of fixing desynced KCs from 'bless', so useful in Big Sur+
        # https://github.com/flagersgit/RSRRepair

        if self.constants.detected_os < os_data.os_data.big_sur:
            return

        logging.info("- Installing Kernel Collection syncing utility")
        result = utilities.elevated([self.constants.rsrrepair_userspace_path, "--install"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logging.info(f"  - Failed to install RSRRepair: {result.stdout.decode()}")