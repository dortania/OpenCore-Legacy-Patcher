"""
intel_skylake.py: Intel Skylake detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_opencl import MontereyOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelSkylake(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Skylake"


    def present(self) -> bool:
        """
        Targeting Intel Skylake GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Skylake
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 13, Ventura
        """
        return self._xnu_major < os_data.ventura.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass
        """
        return HardwareVariantGraphicsSubclass.METAL_31001_GRAPHICS


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Intel Skylake": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelSKLGraphics.kext":            self._resolve_monterey_framebuffers(),
                        "AppleIntelSKLGraphicsFramebuffer.kext": self._resolve_monterey_framebuffers(),
                        "AppleIntelSKLGraphicsGLDriver.bundle":  "12.5",
                        "AppleIntelSKLGraphicsMTLDriver.bundle": "12.5" if self._xnu_major < os_data.sequoia else "12.5-24",
                        "AppleIntelSKLGraphicsVADriver.bundle":  "12.5",
                        "AppleIntelSKLGraphicsVAME.bundle":      "12.5",
                        "AppleIntelGraphicsShared.bundle":       "12.5",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Skylake iGPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
        }