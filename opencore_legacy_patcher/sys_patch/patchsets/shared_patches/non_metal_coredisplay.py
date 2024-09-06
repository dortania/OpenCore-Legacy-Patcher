"""
non_metal_coredisplay.py: Non-Metal CoreDisplay patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalCoreDisplay(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        Nvidia Web Drivers require an older build of CoreDisplay
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Non-Metal CoreDisplay Common": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "CoreDisplay.framework": f"10.13.6-{self._xnu_major}",
                    },
                },
            },
        }