"""
nvidia_kepler.py: Nvidia Kepler detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.metal_3802      import LegacyMetal3802
from ...shared_patches.monterey_opencl import MontereyOpenCL

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
        if self._xnu_major == os_data.monterey.value:
            air_plugin = "12.0 Beta 6"
            # 12.5 moved the private fields accessed by the beta 6 driver
            metal_driver = "12.0 Beta 6-21" if self._xnu_float >= self.macOS_12_5 else "12.0 Beta 6"
        else:
            # fix the sequoia wallpaper
            air_plugin = "12.0 Beta 6-3802-24" if self._xnu_major == os_data.sequoia.value else "12.0 Beta 6-3802"
            metal_driver = {
                # fields moved again
                os_data.sequoia.value: "12.0 Beta 6-3802-24",
                os_data.tahoe.value: "12.0 Beta 6-3802-25",
            }.get(self._xnu_major, "12.0 Beta 6-3802")

        return {
            "Nvidia Kepler": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    **({
                        "/System/Library/Sandbox/Profiles": {
                            "nsattributedstringagent.sb": "26.0-25G229",
                        },
                    } if self._xnu_major >= os_data.sequoia.value else {}), # readd missing properties to fix nsattributedstringagent crashing
                    "/System/Library/Extensions": {
                        "GeForce.kext":            self._resolve_kepler_geforce_framebuffers(),
                        "NVDAGF100Hal.kext":       "12.0 Beta 6",
                        "NVDAGK100Hal.kext":       "12.0 Beta 6",
                        "NVDAResman.kext":         "12.0 Beta 6",
                        "NVDAStartup.kext":        "12.0 Beta 6",
                        "GeForceAIRPlugin.bundle": air_plugin,
                        "GeForceGLDriver.bundle":  "12.0 Beta 6",
                        "GeForceMTLDriver.bundle": metal_driver,
                        "GeForceVADriver.bundle":  "12.0 Beta 6",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    # restore removed opencl compiler files
                    "/System/Library/Frameworks/OpenCL.framework/Versions": {"A": "12.0 Beta 6"},
                    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions": {"A": "12.0 Beta 6"},
                },
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
            **self._model_specific_patches(),
        }
