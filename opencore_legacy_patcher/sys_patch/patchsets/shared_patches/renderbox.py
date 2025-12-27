"""
renderbox.py: RenderBox metallib patch set
"""

import packaging.version

from .base import BaseSharedPatchSet

from ..base import PatchType, DynamicPatchset

from ....datasets.os_data import os_data


class RenderBox(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value


    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "RenderBox Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": {
                        **({ "default.metallib": f"RenderBox-{self._xnu_major}" }),
                    },
                },
            }
        }