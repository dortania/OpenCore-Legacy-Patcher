"""
non_metal_ioaccel.py: Non-Metal IOAccelerator patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalIOAccelerator(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        TeraScale 2 and Nvidia Web Drivers broke in Mojave due to mismatched structs in
        the IOAccelerator stack
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Non-Metal IOAccelerator Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "IOAcceleratorFamily2.kext":     "10.13.6",
                        "IOSurface.kext":                "10.14.6",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "IOSurface.framework": f"10.14.6-{self._xnu_major}",
                        "OpenCL.framework":     "10.13.6",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework":     "10.13.6",
                        "IOAccelerator.framework": f"10.13.6-{self._xnu_major}",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AppleCameraInterface.kext"
                    ],
                },
            },
        }