"""
keyboard_backlight.py: Legacy Keyboard Backlight detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class KeyboardBacklight(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy Keyboard Backlight"


    def present(self) -> bool:
        """
        Targeting Legacy Keyboard Backlight (ie. non-Metal Macs)
        """
        return self._computer.real_model.startswith("MacBook") and self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Iron_Lake,
                device_probe.Intel.Archs.Sandy_Bridge,
                device_probe.AMD.Archs.TeraScale_1,
                device_probe.AMD.Archs.TeraScale_2,
                device_probe.NVIDIA.Archs.Tesla,
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 11, Big Sur
        """
        return self._xnu_major < os_data.big_sur.value


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
        Patches for Legacy Keyboard Backlight
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support:
            return {}

        return {
            "Legacy Keyboard Backlight": {
                PatchType.EXECUTE: {
                    "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist Moraea_BacklightHack -bool true": True,
                }
            },
        }