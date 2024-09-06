"""
monterey_opencl.py: Monterey OpenCL patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class MontereyWebKit(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major == os_data.monterey.value


    def patches(self) -> dict:
        """
        Monterey has a WebKit sandboxing issue where many UI elements fail to render
        This patch simple replaces the sandbox profile with one supporting our GPUs
        Note: Neither Big Sur nor Ventura have this issue
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "WebKit Monterey Common": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "WebKit.framework":  "11.6"
                    },
                },
                PatchType.MERGE_DATA_VOLUME: {
                    "/Library/Apple/System/Library/StagedFrameworks/Safari": {
                        "WebKit.framework":  "11.6"
                    },
                },
            },
        }