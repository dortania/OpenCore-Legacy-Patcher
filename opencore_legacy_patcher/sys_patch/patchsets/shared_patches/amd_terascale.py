"""
amd_terascale.py: AMD TeraScale patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class AMDTeraScale(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        Shared patches between TeraScale 1 and 2
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "AMD TeraScale Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMDFramebuffer.kext":           "10.13.6",
                        "AMDLegacyFramebuffer.kext":     "10.13.6" if self._xnu_float < self.macOS_13_3 else "10.13.6 TS2",
                        "AMDLegacySupport.kext":         "10.13.6",
                        "AMDShared.bundle":              "10.13.6",
                        "AMDSupport.kext":               "10.13.6",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AMD7000Controller.kext",
                        "AMD8000Controller.kext",
                        "AMD9000Controller.kext",
                        "AMD9500Controller.kext",
                        "AMD10000Controller.kext",
                    ],
                },
            },
        }