"""
non_metal_enforcement.py: Non-Metal Enforcement patches
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalEnforcement(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        Forces Metal kexts from High Sierra to run in the fallback non-Metal mode
        Verified functional with HD4000 and Iris Plus 655
        Only used for internal development purposes, not suitable for end users

        Note: Metal kexts in High Sierra rely on IOAccelerator, thus 'Non-Metal IOAccelerator Common'
        is needed for proper linking
        """
        if self._os_requires_patches() is False:
            return {}

        return {
            "Non-Metal Enforcement": {
                PatchType.EXECUTE: {
                    "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -boolean no": True,
                    "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useIOP -boolean no":   True,
                },
            },
        }