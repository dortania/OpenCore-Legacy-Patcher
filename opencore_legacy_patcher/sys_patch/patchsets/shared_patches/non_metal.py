"""
non_metal.py: Non-Metal patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetal(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str, iosurface_version: str = "10.15.7") -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)
        self._iosurface_version = iosurface_version


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        General non-Metal GPU patches
        """
        if self._os_requires_patches() is False:
            return {}

        skylight_version = {
            os_data.mojave.value:   "10.14.6",
            os_data.catalina.value: "10.15.6",
            os_data.big_sur.value:  "11.7",
            os_data.monterey.value: "12.7",
            os_data.ventura.value:  "13.7",
            os_data.sonoma.value:   "14.8",
            os_data.sequoia.value:  "15.8",
            os_data.tahoe.value:    "26.7",
        }.get(self._xnu_major, "26.7")

        return {
            "Non-Metal Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "IOSurface.kext": self._iosurface_version,
                    },
                    "/System/Applications": {
                        **({ "Photo Booth.app": "11.7.9"} if self._xnu_major >= os_data.monterey else {}),
                    },
                    "/System/Library/CoreServices": {
                        **({ "iconservicesagent": "26.0" } if self._xnu_major >= os_data.tahoe else {}),
                    },
                    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A": {
                        "SkyLight":         f"{skylight_version}-{self._xnu_major}",
                        "SkyLightOriginal": f"{skylight_version}-{self._xnu_major}",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AMDRadeonX4000.kext",
                        "AMDRadeonX4000HWServices.kext",
                        "AMDRadeonX5000.kext",
                        "AMDRadeonX5000HWServices.kext",
                        "AMDRadeonX6000.kext",
                        "AMDRadeonX6000Framebuffer.kext",
                        "AMDRadeonX6000HWServices.kext",
                        "AppleIntelBDWGraphics.kext",
                        "AppleIntelBDWGraphicsFramebuffer.kext",
                        "AppleIntelCFLGraphicsFramebuffer.kext",
                        "AppleIntelHD4000Graphics.kext",
                        "AppleIntelHD5000Graphics.kext",
                        "AppleIntelICLGraphics.kext",
                        "AppleIntelICLLPGraphicsFramebuffer.kext",
                        "AppleIntelKBLGraphics.kext",
                        "AppleIntelKBLGraphicsFramebuffer.kext",
                        "AppleIntelSKLGraphics.kext",
                        "AppleIntelSKLGraphicsFramebuffer.kext",
                        "AppleIntelFramebufferAzul.kext",
                        "AppleIntelFramebufferCapri.kext",
                        "AppleParavirtGPU.kext",
                        "GeForce.kext",
                        "IOAcceleratorFamily2.kext",
                        "IOGPUFamily.kext",
                        "AppleAfterburner.kext",
                    ],
                    "/System/Library/ExtensionKit/Extensions/": [
                        "WallpaperMacintoshExtension.appex"
                    ],
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "OpenGL.framework":       "10.14.3",
                        "CoreDisplay.framework": f"10.14.4-{self._xnu_major}",
                        "IOSurface.framework":   f"{self._iosurface_version}-{self._xnu_major}",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework": "10.14.3",
                        **({"FaceCore.framework":  f"13.5"} if self._xnu_major >= os_data.sonoma else {}),
                    },
                },
            },
        }
