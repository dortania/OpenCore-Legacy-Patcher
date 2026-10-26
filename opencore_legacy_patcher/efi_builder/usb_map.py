import copy
import logging
import plistlib
import shutil

from . import support

from .. import constants

from ..datasets import usb_map_data
from ..datasets.os_data import os_data


class BuildUSBMap:

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model = model
        self.constants = global_constants
        self.config = config

        self._build()


    def _build(self) -> None:
        if self.constants.allow_oc_everywhere is True and self.constants.allow_native_spoofs is False:
            return
        if self.model == "Dortania1,1":
            return

        source_path = self.constants.usb_maps_path / f"{self.model}.plist"
        if not source_path.is_file():
            return

        missing_since = next((release for release, models in usb_map_data.Missing_USB_Map.items() if self.model in models), None)
        spoofing = self.constants.serial_settings in ["Moderate", "Advanced"]
        if missing_since is None and spoofing is False:
            return

        logging.info(f"- Adding USB maps for {self.model}")
        with source_path.open("rb") as source_file:
            source = plistlib.load(source_file)
        template_path = self.constants.usb_map_template_path / "Contents/Info.plist"
        with template_path.open("rb") as template_file:
            usb_map = plistlib.load(template_file)

        usb_map["IOKitPersonalities_x86_64"] = source["IOKitPersonalities_x86_64"]
        for personality in usb_map["IOKitPersonalities_x86_64"].values():
            personality.pop("board-id", None)
            personality["model"] = self.model

        tahoe_map = copy.deepcopy(usb_map)
        for personality in tahoe_map["IOKitPersonalities_x86_64"].values():
            for port in personality.get("IOProviderMergeProperties", {}).get("ports", {}).values():
                if "UsbConnector" in port:
                    port["usb-port-type"] = port["UsbConnector"]
                if "port" in port:
                    port["usb-port-number"] = port["port"]

        minimum = 0 if spoofing else missing_since
        if minimum < os_data.tahoe.value:
            self._write_map("USB-Map.kext", usb_map, f"{minimum}.0.0" if minimum else "")
        self._write_map("USB-Map-Tahoe.kext", tahoe_map, f"{max(os_data.tahoe.value, minimum)}.0.0")


    def _write_map(self, bundle_name: str, usb_map: dict, min_kernel: str) -> None:
        destination = self.constants.kexts_path / bundle_name
        shutil.copytree(self.constants.usb_map_template_path, destination, dirs_exist_ok=True)
        with (destination / "Contents/Info.plist").open("wb") as plist_file:
            plistlib.dump(usb_map, plist_file, sort_keys=True)

        entry = support.BuildSupport(self.model, self.constants, self.config).get_kext_by_bundle_path(bundle_name)
        entry["Enabled"] = True
        entry["MinKernel"] = min_kernel
