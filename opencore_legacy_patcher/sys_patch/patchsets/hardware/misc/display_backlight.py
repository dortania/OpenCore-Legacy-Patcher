"""
display_backlight.py: Legacy Backlight Control detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants  import Constants

from .....datasets.os_data import os_data


class DisplayBacklight(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy Backlight Control"


    def present(self) -> bool:
        """
        Targeting Legacy Backlight Controllers
        """
        return self._computer.real_model in [
            "MacBook5,2",
            "iMac7,1",
            "iMac8,1",
            "iMac9,1",
        ]


    def native_os(self) -> bool:
        """
        Dropped support with macOS 10.13, High Sierra
        """
        return self._xnu_major < os_data.high_sierra.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def requires_kernel_debug_kit(self) -> bool:
        """
        Apple no longer provides standalone kexts in the base OS
        """
        return self._xnu_major >= os_data.ventura.value


    def patches(self) -> dict:
        """
        Patches for Legacy Backlight Control
        """
        if self.native_os() is True:
            return {}

        return {
            "Legacy Backlight Control": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleBacklight.kext":       "10.12.6",
                        "AppleBacklightExpert.kext": "10.12.6",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "DisplayServices.framework": "10.12.6",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                        "AGDCBacklightControl.kext",
                    ],
                },
            },
        }