"""
intel_broadwell.py: Intel Broadwell detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_gva    import MontereyGVA
from ...shared_patches.monterey_opencl import MontereyOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelBroadwell(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Broadwell"


    def present(self) -> bool:
        """
        Targeting Intel Broadwell GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Broadwell
            ]
        )

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


    def native_os(self) -> bool:
        """
        Dropped support with macOS 13, Ventura
        """
        return self._xnu_major < os_data.ventura.value


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Intel Broadwell": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelBDWGraphics.kext":            self._resolve_monterey_framebuffers(),
                        "AppleIntelBDWGraphicsFramebuffer.kext": self._resolve_monterey_framebuffers(),
                        "AppleIntelBDWGraphicsGLDriver.bundle":  "12.5",
                        "AppleIntelBDWGraphicsMTLDriver.bundle": "12.5-22" if self._xnu_major < os_data.sequoia else "12.5-24",
                        "AppleIntelBDWGraphicsVADriver.bundle":  "12.5",
                        "AppleIntelBDWGraphicsVAME.bundle":      "12.5",
                        "AppleIntelGraphicsShared.bundle":       "12.5",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Broadwell iGPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **MontereyGVA(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
        }
