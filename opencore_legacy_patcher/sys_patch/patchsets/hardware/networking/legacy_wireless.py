"""
legacy_wireless.py: Legacy Wireless detection
"""

import packaging.version

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class LegacyWireless(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy Wireless"


    def present(self) -> bool:
        """
        Targeting Legacy Wireless
        """
        if (
            isinstance(self._computer.wifi, device_probe.Broadcom)
            and self._computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ):
            return True

        if (
            isinstance(self._computer.wifi, device_probe.Atheros)
            and self._computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40
        ):
            return True

        return False


    def native_os(self) -> bool:
        """
        Dropped support with macOS 12, Monterey
        """
        return self._xnu_major < os_data.monterey.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.NETWORKING


    def _affected_by_cve_2024_23227(self) -> bool:
        """
        CVE-2024-23227 broke our airportd patches for 12.7.4, 13.6.5 and 14.4

        Note that since the XNU version's security patch level is not increment
        """

        if self._xnu_major > os_data.sonoma:
            return True

        marketing_version = self._constants.detected_os_version
        parsed_version = packaging.version.parse(marketing_version)

        if marketing_version.startswith("12"):
            return parsed_version >= packaging.version.parse("12.7.4")
        if marketing_version.startswith("13"):
            return parsed_version >= packaging.version.parse("13.6.5")
        if marketing_version.startswith("14"):
            return parsed_version >= packaging.version.parse("14.4")

        return False


    def _base_patch(self) -> dict:
        """
        Base patches for Legacy Wireless
        """
        return {
            "Legacy Wireless": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/usr/libexec": {
                        "airportd": "11.7.10" if self._affected_by_cve_2024_23227 is False else "11.7.10-Sandbox",
                    },
                    "/System/Library/CoreServices": {
                        "WiFiAgent.app": "11.7.10",
                    },
                },
                PatchType.OVERWRITE_DATA_VOLUME: {
                    "/Library/Application Support/SkyLightPlugins": {
                        **({ "CoreWLAN.dylib": "SkyLightPlugins" } if self._xnu_major == os_data.monterey else {}),
                        **({ "CoreWLAN.txt": "SkyLightPlugins" } if self._xnu_major == os_data.monterey else {}),
                    },
                },
            },
        }


    def _extended_patch(self) -> dict:
        """
        Extended patches for Legacy Wireless
        """
        if self._xnu_major < os_data.ventura:
            return {}

        return {
            "Legacy Wireless Extended": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/usr/libexec": {
                        "wps":      "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                        "wifip2pd": "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "CoreWLAN.framework": "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "CoreWiFi.framework":       "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                        "IO80211.framework":        "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                        "WiFiPeerToPeer.framework": "12.7.2" if self._xnu_major < os_data.sequoia else f"12.7.2-{self._xnu_major}",
                    },
                }
            },
        }


    def patches(self) -> dict:
        """
        Patches for Legacy Wireless
        """
        if self.native_os() is True:
            return {}

        return {
            **self._base_patch(),
            **self._extended_patch(),
        }