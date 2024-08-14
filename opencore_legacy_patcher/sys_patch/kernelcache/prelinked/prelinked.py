"""
prelinked.py: Prelinked Kernel cache management
"""

import logging
import subprocess

from pathlib import Path

from ..base.cache import BaseKernelCache
from ....support import subprocess_wrapper


class PrelinkedKernel(BaseKernelCache):

    def __init__(self, mount_location: str) -> None:
        self.mount_location = mount_location


    def _kextcache_arguments(self) -> list[str]:
        args = ["/usr/sbin/kextcache", "-invalidate", f"{self.mount_location}/"]
        return args

    def _update_preboot_kernel_cache(self) -> bool:
        """
        Ensure Preboot volume's kernel cache is updated
        """
        if not Path("/usr/sbin/kcditto").exists():
            return

        logging.info("- Syncing Kernel Cache to Preboot")
        subprocess_wrapper.run_as_root_and_verify(["/usr/sbin/kcditto"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def rebuild(self) -> None:
        logging.info("- Rebuilding Prelinked Kernel")
        result = subprocess_wrapper.run_as_root(self._kextcache_arguments(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # kextcache notes:
        # - kextcache always returns 0, even if it fails
        # - Check the output for 'KernelCache ID' to see if the cache was successfully rebuilt
        if "KernelCache ID" not in result.stdout.decode():
            subprocess_wrapper.log(result)
            return False

        self._update_preboot_kernel_cache()

        return True