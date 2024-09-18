"""
legacy_audio.py: Legacy Audio detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants
from .....support   import utilities

from .....datasets.os_data import os_data


class LegacyAudio(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy Audio"


    def present(self) -> bool:
        """
        Targeting Realtek Audio and machines without AppleALC
        """
        return self._computer.real_model in ["iMac7,1", "iMac8,1"] or (
        self._computer.real_model in ["MacBook5,1",
                                      "MacBook5,2",
                                      "MacBook6,1",
                                      "MacBook7,1",
                                      "MacBookAir2,1",
                                      "MacBookAir3,1",
                                      "MacBookAir3,2",
                                      "MacBookAir4,1",
                                      "MacBookAir4,2",
                                      "MacBookPro4,1",
                                      "MacBookPro5,1",
                                      "MacBookPro5,2",
                                      "MacBookPro5,3",
                                      "MacBookPro5,4",
                                      "MacBookPro5,5",
                                      "MacBookPro6,1",
                                      "MacBookPro6,2",
                                      "MacBookPro7,1",
                                      "MacBookPro8,1",
                                      "MacBookPro8,2",
                                      "MacBookPro8,3",
                                      "Macmini3,1",
                                      "Macmini4,1",
                                      "Macmini5,1",
                                      "Macmini5,2",
                                      "Macmini5,3",
                                      "iMac9,1",
                                      "iMac10,1",
                                      "iMac11,1",
                                      "iMac11,2",
                                      "iMac11,3",
                                      "iMac12,1",
                                      "iMac12,2",
                                      "MacPro3,1"
        ] and utilities.check_kext_loaded("as.vit9696.AppleALC") is False)


    def native_os(self) -> bool:
        """
        - iMac7,1 and iMac8,1 last supported in macOS 10.11, El Capitan
        - All other models pre-2012 models last supported in macOS 10.13, High Sierra
        """
        if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
            return self._xnu_major < os_data.sierra.value
        return self._xnu_major < os_data.mojave.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def _missing_gop_patches(self) -> dict:
        """
        Patches for graphics cards with missing GOP (ie. breaking AppleALC functionality)
        """
        return {
            "Legacy Non-GOP": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext": "10.13.6",
                    },
                },
            },
        }


    def _realtek_audio_patches(self) -> dict:
        """
        Patches for Realtek Audio
        """
        return {
            "Legacy Realtek": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext":      "10.11.6",
                        "IOAudioFamily.kext": "10.11.6",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AppleVirtIO.kext",
                        "AppleVirtualGraphics.kext",
                        "AppleVirtualPlatform.kext",
                        "ApplePVPanic.kext",
                        "AppleVirtIOStorage.kext",
                        "AvpFairPlayDriver.kext",
                    ],
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for legacy audio
        """
        if self.native_os() is True:
            return {}

        if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
            return self._realtek_audio_patches()
        return self._missing_gop_patches()