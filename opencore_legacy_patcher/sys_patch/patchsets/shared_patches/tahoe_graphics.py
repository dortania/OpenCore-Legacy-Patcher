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


    def camera_patches(self) -> dict:
        if self._os_requires_patches() is False:
            return {}

        return {
            "Tahoe Camera": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/LaunchDaemons": {
                        "com.apple.cmio.AppleCameraAssistant.plist": "14.0 Beta 1",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "CoreMediaIO.framework": "14.0 Beta 1",
                    },
                },
            },
        }
