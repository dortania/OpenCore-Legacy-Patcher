

"""
usb11.py: Legacy USB 1.1 Controller detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data
from .....datasets import smbios_data, cpu_data


class USB11Controller(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy USB 1.1"


    def present(self) -> bool:
        """
        Targeting UHCI/OHCI controllers
        """
        # If we're on a hackintosh, check for UHCI/OHCI controllers
        if self._constants.host_is_hackintosh is True:
            for controller in self._computer.usb_controllers:
                if (
                    isinstance(controller, device_probe.UHCIController) or
                    isinstance(controller, device_probe.OHCIController)
                ):
                    return True
            return False

        if self._computer.real_model not in smbios_data.smbios_dictionary:
            return False

        # If we're on a Mac, check for Penryn or older
        # This is due to Apple implementing an internal USB hub on post-Penryn (excluding MacPro4,1, MacPro5,1 and Xserve3,1)
        # Ref: https://techcommunity.microsoft.com/t5/microsoft-usb-blog/reasons-to-avoid-companion-controllers/ba-p/270710
        if (
            smbios_data.smbios_dictionary[self._computer.real_model]["CPU Generation"] <= cpu_data.CPUGen.penryn.value or \
            self._computer.real_model in ["MacPro4,1", "MacPro5,1", "Xserve3,1"]
        ):
            return True

        return False


    def native_os(self) -> bool:
        """
        Dropped support with macOS 13, Ventura
        """
        return self._xnu_major < os_data.ventura.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def _base_patches(self) -> dict:
        """
        Base patches for USB 1.1 Controller
        """
        return {
            "Legacy USB 1.1": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "IOUSBHostFamily.kext": "12.6.2" if self._xnu_float < self.macOS_14_4 else "12.6.2-23.4",
                    },
                },
            },
        }


    def _extended_patches(self) -> dict:
        """
        Extended patches for USB 1.1 Controller
        """
        if self._xnu_float < self.macOS_14_1:
            return {}

        return {
            # Injection of UHCI/OHCI causes a panic on 14.1+
            "Legacy USB 1.1 Extended": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions/IOUSBHostFamily.kext/Contents/PlugIns": {
                        "AppleUSBOHCI.kext":    "12.6.2-USB",
                        "AppleUSBOHCIPCI.kext": "12.6.2-USB",
                        "AppleUSBUHCI.kext":    "12.6.2-USB",
                        "AppleUSBUHCIPCI.kext": "12.6.2-USB",
                    },
                    "/System/Library/Extensions": {
                        **({ "AppleUSBAudio.kext": "14.5" } if self._xnu_major >= os_data.sequoia else {}),
                        **({ "AppleUSBCDC.kext":   "14.5" } if self._xnu_major >= os_data.sequoia else {}),
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for USB 1.1 Controller
        """
        if self.native_os() is True:
            return {}

        return {
            **self._base_patches(),
            **self._extended_patches(),
        }