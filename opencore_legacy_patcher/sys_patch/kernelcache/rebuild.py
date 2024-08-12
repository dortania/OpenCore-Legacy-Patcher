"""
rebuild.py: Manage kernel cache rebuilding regardless of macOS version
"""

from .base.cache import BaseKernelCache
from ...datasets import os_data


class RebuildKernelCache:
    """
    RebuildKernelCache: Rebuild the kernel cache

    Parameters:
    - os_version: macOS version
    - mount_location: Path to the mounted volume
    - auxiliary_cache: Whether to create auxiliary kernel cache (Big Sur and later)
    - auxiliary_cache_only: Whether to only create auxiliary kernel cache (Ventura and later)
    """
    def __init__(self, os_version: os_data.os_data, mount_location: str, auxiliary_cache: bool, auxiliary_cache_only: bool) -> None:
        self.os_version = os_version
        self.mount_location = mount_location
        self.auxiliary_cache = auxiliary_cache
        self.auxiliary_cache_only = auxiliary_cache_only


    def _rebuild_method(self) -> BaseKernelCache:
        """
        Determine the correct method to rebuild the kernel cache
        """
        if self.os_version >= os_data.os_data.big_sur:
            if self.os_version >= os_data.os_data.ventura:
                if self.auxiliary_cache_only:
                    from .kernel_collection.auxiliary import AuxiliaryKernelCollection
                    return AuxiliaryKernelCollection(self.mount_location)

            from .kernel_collection.boot_system import BootSystemKernelCollections
            return BootSystemKernelCollections(self.mount_location, self.os_version, self.auxiliary_cache)

        if os_data.os_data.catalina >= self.os_version >= os_data.os_data.lion:
            from .prelinked.prelinked import PrelinkedKernel
            return PrelinkedKernel(self.mount_location)

        from .mkext.mkext import MKext
        return MKext(self.mount_location)


    def rebuild(self) -> bool:
        """
        Rebuild the kernel cache
        """
        return self._rebuild_method().rebuild()