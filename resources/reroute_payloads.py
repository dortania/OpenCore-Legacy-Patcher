# Reroute binaries to tmp directory, and mount a disk image of the payloads
# Implements a shadowfile to avoid direct writes to the dmg
# Copyright (C) 2022, Mykola Grymalyuk

import plistlib
from pathlib import Path
import subprocess
import tempfile
import atexit

class reroute_payloads:
    def __init__(self, constants):
        self.constants = constants

    def setup_tmp_disk_image(self):
        # Create a temp directory to mount the payloads.dmg
        # Then reroute r/w to this new temp directory
        # Currently only applicable for GUI variant
        if self.constants.wxpython_variant is True and not self.constants.launcher_script:
            print("- Running in Binary GUI mode, switching to tmp directory")
            self.temp_dir = tempfile.TemporaryDirectory()
            print(f"- New payloads location: {self.temp_dir.name}")
            print("- Creating payloads directory")
            Path(self.temp_dir.name / Path("payloads")).mkdir(parents=True, exist_ok=True)
            self.unmount_active_dmgs(unmount_all_active=False)
            output = subprocess.run(
                [
                    "hdiutil", "attach", "-noverify", f"{self.constants.payload_path}.dmg",
                    "-mountpoint", Path(self.temp_dir.name / Path("payloads")),
                    "-nobrowse",
                    "-shadow", Path(self.temp_dir.name / Path("payloads_overlay")),
                    "-passphrase", "password"
                ],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if output.returncode == 0:
                print("- Mounted payloads.dmg")
                self.constants.current_path = Path(self.temp_dir.name)
                self.constants.payload_path = Path(self.temp_dir.name) / Path("payloads")
                atexit.register(self.unmount_active_dmgs, unmount_all_active=False)
            else:
                print("- Failed to mount payloads.dmg")
                print(f"Output: {output.stdout.decode()}")
                print(f"Return Code: {output.returncode}")

    def unmount_active_dmgs(self, unmount_all_active=True):
        # Find all DMGs that are mounted, and forcefully unmount them
        # If our disk image was previously mounted, we need to unmount it to use again
        # This can happen if we crash during a previous secession, however 'atexit' class should hopefully avoid this
        dmg_info = subprocess.run(["hdiutil", "info", "-plist"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        dmg_info = plistlib.loads(dmg_info.stdout)

        for image in dmg_info["images"]:
            if image["image-path"].endswith("payloads.dmg"):
                if unmount_all_active is False:
                    # Check that only our personal payloads.dmg is unmounted
                    if "shadow-path" in image:
                        if self.temp_dir.name in image["shadow-path"]:
                            print("- Unmounting personal payloads.dmg")
                            subprocess.run(
                                ["hdiutil", "detach", image["system-entities"][0]["dev-entry"], "-force"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                            )
                else:
                    print(f"- Unmounting payloads.dmg at: {image['system-entities'][0]['dev-entry']}")
                    subprocess.run(
                        ["hdiutil", "detach", image["system-entities"][0]["dev-entry"], "-force"],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    )