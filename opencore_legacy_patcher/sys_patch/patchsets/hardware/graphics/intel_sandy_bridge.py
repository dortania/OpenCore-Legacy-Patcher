"""
intel_sandy_bridge.py: Intel Sandy Bridge detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.non_metal       import NonMetal
from ...shared_patches.monterey_webkit import MontereyWebKit
from ...shared_patches.high_sierra_gva import HighSierraGVA

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelSandyBridge(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Sandy Bridge"


    def present(self) -> bool:
        """
        Targeting Intel Sandy Bridge GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Sandy_Bridge
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major < os_data.mojave.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass
        """
        return HardwareVariantGraphicsSubclass.NON_METAL_GRAPHICS


    def requires_kernel_debug_kit(self) -> bool:
        """
        Requires replacing a number of kexts in the BootKC
        """
        if self._xnu_major >= os_data.ventura.value:
            return True
        return False


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Intel Sandy Bridge": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelHD3000Graphics.kext":           "10.13.6",
                        "AppleIntelHD3000GraphicsGA.plugin":       "10.13.6",
                        "AppleIntelHD3000GraphicsGLDriver.bundle": "10.13.6",
                        "AppleIntelHD3000GraphicsVADriver.bundle": "10.13.6",
                        "AppleIntelSNBGraphicsFB.kext":            "10.13.6",
                        "AppleIntelSNBVA.bundle":                  "10.13.6",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Sandy Bridge GPUs
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support and self._dortania_internal_check() is False:
            return {**self._model_specific_patches()}

        return {
            **NonMetal(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **HighSierraGVA(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }