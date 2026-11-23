from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class TahoeGraphics(BaseSharedPatchSet):

    def _os_requires_patches(self) -> bool:
        return self._xnu_major >= os_data.tahoe.value


    def patches(self) -> dict:
        if self._os_requires_patches() is False:
            return {}

        return {
            "Tahoe Graphics": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": {
                        "default.metallib": "26.0-3802",
                    },
                },
            },
        }