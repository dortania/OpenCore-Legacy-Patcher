"""
big_sur_gva.py: Big Sur GVA patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class BigSurGVA(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.monterey.value


    def patches(self) -> dict:
        """
        For GPUs last natively supported in Catalina/Big Sur
        Restores DRM support for these GPUs
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Big Sur GVA": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "11.7.10",
                        "AppleGVACore.framework": "11.7.10",
                    },
                },
            },
        }