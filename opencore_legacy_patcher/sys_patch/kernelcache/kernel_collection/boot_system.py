"""
boot_system.py: Boot and System Kernel Collection management
"""

import logging
import subprocess

from ..base.cache import BaseKernelCache
from ....support  import subprocess_wrapper
from ....datasets import os_data


class BootSystemKernelCollections(BaseKernelCache):

    def __init__(self, mount_location: str, detected_os: int, auxiliary_kc: bool) -> None:
        self.mount_location = mount_location
        self.detected_os  = detected_os
        self.auxiliary_kc = auxiliary_kc


    def _kmutil_arguments(self) -> list[str]:
        """
        Generate kmutil arguments for creating or updating
        the boot, system and auxiliary kernel collections
        """

        args = ["/usr/bin/kmutil"]

        if self.detected_os >= os_data.os_data.ventura:
            args.append("create")
            args.append("--allow-missing-kdk")
        else:
            args.append("install")

        args.append("--volume-root")
        args.append(self.mount_location)

        args.append("--update-all")

        args.append("--variant-suffix")
        args.append("release")

        if self.auxiliary_kc is True:
            # Following arguments are supposed to skip kext consent
            # prompts when creating auxiliary KCs with SIP disabled
            args.append("--no-authentication")
            args.append("--no-authorization")

        return args


    def rebuild(self) -> bool:
        logging.info(f"- Rebuilding {'Boot and System' if self.auxiliary_kc is False else 'Boot, System and Auxiliary'} Kernel Collections")
        if self.auxiliary_kc is True:
            logging.info("  (You will get a prompt by System Preferences, ignore for now)")

        result = subprocess_wrapper.run_as_root(self._kmutil_arguments(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            subprocess_wrapper.log(result)
            return False

        return True
