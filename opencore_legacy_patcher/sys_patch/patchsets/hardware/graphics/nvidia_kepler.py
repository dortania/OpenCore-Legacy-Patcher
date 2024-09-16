"""
nvidia_kepler.py: Nvidia Kepler detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.metal_3802      import LegacyMetal3802
from ...shared_patches.monterey_opencl import MontereyOpenCL
from ...shared_patches.big_sur_opencl  import BigSurOpenCL
from ...shared_patches.monterey_webkit import MontereyWebKit

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class NvidiaKepler(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Nvidia Kepler"


    def present(self) -> bool:
        """
        Targeting Nvidia Kepler GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.NVIDIA.Archs.Kepler
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 12.0 Beta 7, Monterey
        """
        if self._xnu_major < os_data.monterey:
            return True

        if self._xnu_major == os_data.monterey:
            if self._xnu_minor <= 0:             # 12.0 Beta 8 increased XNU minor
                if self._os_build != "21A5522h": # 12.0 Beta 7
                    return True

        return False


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass
        """
        return HardwareVariantGraphicsSubclass.METAL_3802_GRAPHICS


    def requires_metallib_support_pkg(self) -> bool:
        """
        New compiler format introduced in macOS 15, Sequoia
        """
        return self._xnu_major >= os_data.sequoia.value


    def _resolve_kepler_geforce_framebuffers(self) -> str:
        """
        Resolve patchset directory for GeForce.kext
        """
        if self._xnu_major < os_data.sonoma:
            return "12.0 Beta 6"
        if self._xnu_float < self.macOS_14_4:
            return "12.0 Beta 6-23"
        return "12.0 Beta 6-23.4"


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Nvidia Kepler": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "GeForce.kext":            self._resolve_kepler_geforce_framebuffers(),
                        "NVDAGF100Hal.kext":       "12.0 Beta 6",
                        "NVDAGK100Hal.kext":       "12.0 Beta 6",
                        "NVDAResman.kext":         "12.0 Beta 6",
                        "NVDAStartup.kext":        "12.0 Beta 6",
                        "GeForceAIRPlugin.bundle": "11.0 Beta 3",
                        "GeForceGLDriver.bundle":  "11.0 Beta 3",
                        "GeForceMTLDriver.bundle": "11.0 Beta 3" if self._xnu_major <= os_data.monterey else f"11.0 Beta 3-22",
                        "GeForceVADriver.bundle":  "12.0 Beta 6",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        # XNU 21.6 (macOS 12.5)
                        **({ "Metal.framework": "12.5 Beta 2"} if (self._xnu_float >= self.macOS_12_5 and self._xnu_major < os_data.ventura) else {}),
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUCompiler.framework": "11.6",
                    },
                }
            },
        }


    def patches(self) -> dict:
        """
        Patches for Nvidia Kepler GPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **LegacyMetal3802(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **BigSurOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }
