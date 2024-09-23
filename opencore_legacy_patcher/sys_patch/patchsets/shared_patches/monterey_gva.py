"""
monterey_gva.py: Monterey GVA patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class MontereyGVA(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value


    def patches(self) -> dict:
        """
        For GPUs last natively supported in Monterey
        Restores DRM support
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Monterey GVA": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "AppleGVA.framework":     "12.5",
                        "AppleGVACore.framework": "12.5",
                    },
                },
            },
        }


    def revert_patches(self) -> dict:
        """
        Revert if patches are no longer required/misapplied
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Revert Monterey GVA": {
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/AppleGVA.framework/Versions/A": [
                        "AppleGVA"
                    ],
                    "/System/Library/PrivateFrameworks/AppleGVACore.framework/Versions/A": [
                        "AppleGVACore"
                    ],
                }
            }
        }