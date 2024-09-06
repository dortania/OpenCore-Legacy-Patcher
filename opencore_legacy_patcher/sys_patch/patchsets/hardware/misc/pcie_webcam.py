"""
pci_webcam.py: PCIe FaceTime Camera detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants

from .....datasets.os_data import os_data


class PCIeFaceTimeCamera(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: PCIe FaceTime Camera"


    def present(self) -> bool:
        """
        Targeting PCIe FaceTime Cameras
        """
        return self._computer.pcie_webcam


    def native_os(self) -> bool:
        """
        Dropped support with macOS 14 Developer Beta 1 (23A5257q)
        """
        return self._xnu_major < os_data.sonoma.value or self._os_build == "23A5257q"


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def patches(self) -> dict:
        """
        Patches for PCIe FaceTime Camera
        """
        if self.native_os() is True:
            return {}

        return {
            "PCIe FaceTime Camera": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources": {
                        "AppleCamera.plugin":  "14.0 Beta 1"
                    },
                    "/System/Library/LaunchDaemons": {
                        "com.apple.cmio.AppleCameraAssistant.plist":  "14.0 Beta 1"
                    },
                },
            },
        }