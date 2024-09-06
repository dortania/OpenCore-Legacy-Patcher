"""
amd_opencl.py: AMD OpenCL patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class AMDOpenCL(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value


    def patches(self) -> dict:
        """
        In Ventura, Apple added AVX2.0 code to AMD's OpenCL/GL compilers
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "AMD OpenCL": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "OpenCL.framework": "12.5 non-AVX2.0",
                        "OpenGL.framework": "12.5 non-AVX2.0",
                    },
                },
            },
        }