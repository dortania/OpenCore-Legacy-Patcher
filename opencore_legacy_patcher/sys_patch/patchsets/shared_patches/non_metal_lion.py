from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalLion(BaseSharedPatchSet):

    def _os_requires_patches(self) -> bool:
        return self._xnu_major >= os_data.big_sur.value


    def patches(self) -> dict:
        if self._os_requires_patches() is False:
            return {}

        return {
            "Non-Metal Lion Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/LaunchAgents": {
                        "org.legacygl.cvmsCAgent_i386.plist":   "LegacyGL",
                        "org.legacygl.cvmsCAgent_x86_64.plist": "LegacyGL",
                    },
                    "/System/Library/LaunchDaemons": {
                        "org.legacygl.cvmsd.plist": "LegacyGL",
                    },
                    "/usr/share/sandbox": {
                        "cvmsLegacy.sb": "LegacyGL",
                    },
                    "/System/Library/Frameworks/OpenGL.framework/Versions/A/Resources": {
                        "cvmsLegacy.plist": "LegacyGL",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "OpenGL.framework": "10.7.5-20",
                    },
                },
            },
        }
