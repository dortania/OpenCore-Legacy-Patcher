"""
metal_31001.py: Metal 31001 patches
"""

import packaging.version

from .base import BaseSharedPatchSet

from ..base import PatchType, DynamicPatchset

from ....datasets.os_data import os_data


class LegacyMetal31001(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value


    def _patches_metal_31001_common(self) -> dict:
        """
        Intel Broadwell, Skylake, and AMD GCN are Metal 31001-based GPUs
        """
        if self._os_requires_patches() is False:
            return {}

        # Currently no common patches; here for future-proofing.
        return {}

    def _patches_metal_31001_metallibs(self) -> dict:
        """
        Metallib patches for Metal 31001 GPUs
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Metal 31001 Metallibs": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": {
                        **({ "default.metallib": f"RenderBox-{self._xnu_major}" }),
                    }
                },
            }
        }


    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        _base = {
            **self._patches_metal_31001_common(),
        }

        if self._is_gpu_architecture_present(
            [
                device_probe.Intel.Archs.Broadwell,
                device_probe.Intel.Archs.Skylake,
            ]
        ) is True:
            _base.update(self._patches_metal_31001_metallibs())

        return _base