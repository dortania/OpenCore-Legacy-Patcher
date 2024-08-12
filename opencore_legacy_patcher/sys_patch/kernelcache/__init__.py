"""
kernelcache: Library for rebuilding macOS kernelcache files.

Usage:

>>> from kernelcache import RebuildKernelCache
>>> RebuildKernelCache(os_version, mount_location, auxiliary_cache, auxiliary_cache_only).rebuild()
"""

from .rebuild import RebuildKernelCache
from .kernel_collection.support import KernelCacheSupport