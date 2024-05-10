"""
reroute_payloads.py: Reroute binaries to tmp directory, and mount a disk image of the payloads
Implements a shadowfile to avoid direct writes to the dmg
"""

import atexit
import plistlib
import tempfile
import subprocess

import logging

from pathlib import Path

from . import subprocess_wrapper

from .. import constants


class RoutePayloadDiskImage:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        self._setup_tmp_disk_image()


    def _setup_tmp_disk_image(self) -> None:
        """
        Initialize temp directory and mount payloads.dmg
        Create overlay for patcher to write to

        Currently only applicable for GUI variant and not running from source
        """

        if self.constants.wxpython_variant is True and not self.constants.launcher_script:
            logging.info("Running in compiled binary, switching to tmp directory")
            self.temp_dir = tempfile.TemporaryDirectory()
            logging.info(f"New payloads location: {self.temp_dir.name}")
            logging.info("Creating payloads directory")
            Path(self.temp_dir.name / Path("payloads")).mkdir(parents=True, exist_ok=True)
            self._unmount_active_dmgs(unmount_all_active=False)
            output = subprocess.run(
                [
                    "/usr/bin/hdiutil", "attach", "-noverify", f"{self.constants.payload_path_dmg}",
                    "-mountpoint", Path(self.temp_dir.name / Path("payloads")),
                    "-nobrowse",
                    "-shadow", Path(self.temp_dir.name / Path("payloads_overlay")),
                    "-passphrase", "password"
                ],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if output.returncode == 0:
                logging.info("Mounted payloads.dmg")
                self.constants.current_path = Path(self.temp_dir.name)
                self.constants.payload_path = Path(self.temp_dir.name) / Path("payloads")
                atexit.register(self._unmount_active_dmgs, unmount_all_active=False)
            else:
                logging.info("Failed to mount payloads.dmg")
                subprocess_wrapper.log(output)


    def _unmount_active_dmgs(self, unmount_all_active: bool = True) -> None:
        """
        Unmounts disk images associated with OCLP

        Finds all DMGs that are mounted, and forcefully unmount them
        If our disk image was previously mounted, we need to unmount it to use again
        This can happen if we crash during a previous secession, however 'atexit' class should hopefully avoid this

        Parameters:
            unmount_all_active (bool): If True, unmount all active DMGs, otherwise only unmount our own DMG
        """

        dmg_info = subprocess.run(["/usr/bin/hdiutil", "info", "-plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        dmg_info = plistlib.loads(dmg_info.stdout)


        for variant in ["DortaniaInternalResources.dmg", "Universal-Binaries.dmg", "payloads.dmg"]:
            for image in dmg_info["images"]:
                if image["image-path"].endswith(variant):
                    if unmount_all_active is False:
                        # Check that only our personal payloads.dmg is unmounted
                        if "shadow-path" in image:
                            if self.temp_dir.name in image["shadow-path"]:
                                logging.info(f"Unmounting personal {variant}")
                                subprocess.run(
                                    ["/usr/bin/hdiutil", "detach", image["system-entities"][0]["dev-entry"], "-force"],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                                )
                    else:
                        logging.info(f"Unmounting {variant} at: {image['system-entities'][0]['dev-entry']}")
                        subprocess.run(
                            ["/usr/bin/hdiutil", "detach", image["system-entities"][0]["dev-entry"], "-force"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                        )