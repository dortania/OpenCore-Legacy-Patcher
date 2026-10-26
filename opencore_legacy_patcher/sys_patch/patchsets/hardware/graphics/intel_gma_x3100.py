from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.non_metal      import NonMetal
from ...shared_patches.non_metal_lion import NonMetalLion

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelGMAX3100(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        return f"{self.hardware_variant()}: Intel GMA X3100"


    def present(self) -> bool:
        return self._is_gpu_architecture_present([
            device_probe.Intel.Archs.GMA_X3100
        ])


    def native_os(self) -> bool:
        return self._xnu_major < os_data.mountain_lion.value


    def hardware_variant(self) -> HardwareVariant:
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        return HardwareVariantGraphicsSubclass.NON_METAL_GRAPHICS


    def requires_kernel_debug_kit(self) -> bool:
        return self._xnu_major >= os_data.ventura.value


    def _model_specific_patches(self) -> dict:
        return {
            "Intel GMA X3100": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelGMAX3100.kext":           "10.6.2-20",
                        "AppleIntelGMAX3100FB.kext":         "10.6.2-20",
                        "AppleIntelGMAX3100GLDriver.bundle": "10.7.5-20",
                    },
                },
            },
        }


    def patches(self) -> dict:
        if self.native_os() is True or self._xnu_major < os_data.big_sur.value:
            return {}

        return {
            **NonMetal(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **NonMetalLion(self._xnu_major, self._xnu_minor, self._os_build).patches(),
            **self._model_specific_patches(),
        }
