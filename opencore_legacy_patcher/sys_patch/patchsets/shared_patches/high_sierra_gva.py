"""
high_sierra_gva.py: High Sierra GVA patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class HighSierraGVA(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 11.0, Big Sur
        """
        return self._xnu_major >= os_data.big_sur.value


    def patches(self) -> dict:
        """
        For GPUs last natively supported in High Sierra/Catalina
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            # For GPUs last natively supported in High Sierra/Catalina
            # Restores DRM support
            "High Sierra GVA": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "10.13.6",
                        "AppleGVACore.framework": "10.15.7",
                    },
                },
            },
        }