"""
cpu_missing_avx.py: Legacy CPUs (Lacking AVX) Detection

Note that this system is implemented only for macOS Ventura and
machines not using the legacy/modern wireless patches (AVX patch integrated into WiFi patches).

This commit implemented unconditional AVX usage, thus Safari 18.2 and later will crash:
https://github.com/WebKit/WebKit/commit/c15e741266db8ff9df309ce9971eda1cfd9021cc
"""

from ..base import BaseHardware, HardwareVariant

from ..networking.legacy_wireless import LegacyWireless
from ..networking.modern_wireless import ModernWireless

from ...base import PatchType

from .....constants  import Constants

from .....datasets.os_data import os_data


class CPUMissingAVX(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy CPUs (Lacking AVX)"


    def present(self) -> bool:
        """
        Targeting CPUs without AVX support
        """
        if self._constants.computer.rosetta_active is True:
            return False
        if "AVX1.0" in self._constants.computer.cpu.flags:
            return False

        return True


    def native_os(self) -> bool:
        """
        Only install this patch on macOS Ventura.
        This is because we integrated the patch into the WiFi patches which all Macs use in Sonoma+.
        """
        if self._xnu_major != os_data.ventura.value:
            return True

        if LegacyWireless(self._xnu_major, self._xnu_minor, self._os_build, self._constants).present() is True:
            return True
        if ModernWireless(self._xnu_major, self._xnu_minor, self._os_build, self._constants).present() is True:
            return True

        return False


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def patches(self) -> dict:
        """
        Patches for Legacy CPUs (Lacking AVX)
        """
        if self.native_os() is True:
            return {}

        return {
            "CPU Missing AVX": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "IO80211.framework": "13.7.2-22",
                    },
                }
            },
        }