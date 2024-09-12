"""
gmux.py: Legacy GMUX detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants
from .....support   import utilities

from .....datasets.os_data import os_data


class GraphicsMultiplexer(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy GMUX"


    def _check_dgpu_status(self) -> bool:
        """
        Query whether system has an active dGPU
        """
        dgpu = self._computer.dgpu
        if dgpu:
            if dgpu.class_code and dgpu.class_code == 0xFFFFFFFF:
                # If dGPU is disabled via class-codes, assume demuxed
                return False
            return True
        return False


    def _detect_demux(self) -> bool:
        """
        Query whether system has been demuxed (ex. MacBookPro8,2, disabled dGPU)
        """
        # If GFX0 is missing, assume machine was demuxed
        # -wegnoegpu would also trigger this, so ensure arg is not present
        if not "-wegnoegpu" in (utilities.get_nvram("boot-args", decode=True) or ""):
            igpu = self._constants.computer.igpu
            dgpu = self._check_dgpu_status()
            if igpu and not dgpu:
                return True
        return False


    def present(self) -> bool:
        """
        Targeting Legacy GMUX Controllers
        Ref: https://doslabelectronics.com/Demux.html

        Sierra uses a legacy GMUX control method needed for dGPU switching on MacBookPro5,x
        Same method is also used for demuxed machines
        Note that MacBookPro5,x machines are extremely unstable with this patch set, so disabled until investigated further
        Ref: https://github.com/dortania/OpenCore-Legacy-Patcher/files/7360909/KP-b10-030.txt
        """
        return self._computer.real_model in ["MacBookPro8,2", "MacBookPro8,3"] and self._detect_demux()


    def native_os(self) -> bool:
        """
        Dropped support with macOS 10.13, High Sierra
        """
        return self._xnu_major < os_data.sierra.value


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
        Patches for Legacy GMUX Controllers
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support:
            return {}

        return {
            "Legacy GMUX": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": {
                        "AppleMuxControl.kext": "10.12.6",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AppleBacklight.kext",
                    ],
                    "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                        "AGDCBacklightControl.kext",
                        "AppleMuxControl.kext",
                    ],
                },
            },
        }