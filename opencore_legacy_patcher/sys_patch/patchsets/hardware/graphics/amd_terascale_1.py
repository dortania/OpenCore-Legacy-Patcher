"""
amd_terascale_1.py: AMD TeraScale 1 detection
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.non_metal       import NonMetal
from ...shared_patches.monterey_webkit import MontereyWebKit
from ...shared_patches.amd_terascale   import AMDTeraScale

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class AMDTeraScale1(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: AMD TeraScale 1"


    def present(self) -> bool:
        """
        Targeting AMD TeraScale GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.AMD.Archs.TeraScale_1
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
        Apple no longer provides standalone kexts in the base OS
        """
        return self._xnu_major >= os_data.ventura.value


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "AMD TeraScale 1": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AMD2400Controller.kext":        "10.13.6",
                        "AMD2600Controller.kext":        "10.13.6",
                        "AMD3800Controller.kext":        "10.13.6",
                        "AMD4600Controller.kext":        "10.13.6",
                        "AMD4800Controller.kext":        "10.13.6",
                        "ATIRadeonX2000.kext":           "10.13.6" if self._xnu_major < os_data.ventura else "10.13.6 TS1",
                        "ATIRadeonX2000GA.plugin":       "10.13.6",
                        "ATIRadeonX2000GLDriver.bundle": "10.13.6",
                        "ATIRadeonX2000VADriver.bundle": "10.13.6",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for AMD TeraScale 1 GPUs
        """
        if self.native_os() is True:
            return {}

        if self._xnu_major not in self._constants.legacy_accel_support and self._dortania_internal_check() is False:
            return {
                **AMDTeraScale(self._xnu_major, self._xnu_minor, self._os_build).patches(),
                **self._model_specific_patches()
            }

        return {
            **NonMetal(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **MontereyWebKit(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **AMDTeraScale(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }