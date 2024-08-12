"""
mkext.py: MKext cache management
"""

import logging
import subprocess

from ..base.cache import BaseKernelCache

from ....support import subprocess_wrapper


class MKext(BaseKernelCache):

    def __init__(self, mount_location: str) -> None:
        self.mount_location = mount_location


    def _mkext_arguments(self) -> list[str]:
        args = ["/usr/bin/touch", f"{self.mount_location}/System/Library/Extensions"]
        return args


    def rebuild(self) -> None:
        logging.info("- Rebuilding MKext cache")
        result = subprocess_wrapper.run_as_root(self._mkext_arguments(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if result.returncode != 0:
            subprocess_wrapper.log(result)
            return False

        return True