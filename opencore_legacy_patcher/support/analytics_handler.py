"""
analytics_handler.py: Analytics and Crash Reporting Handler
"""

import json
import datetime
import plistlib

from pathlib import Path

from .. import constants

from . import (
    network_handler,
    global_settings
)


DATE_FORMAT:      str = "%Y-%m-%d %H-%M-%S"
ANALYTICS_SERVER: str = ""
SITE_KEY:         str = ""
CRASH_URL:        str = ANALYTICS_SERVER + "/crash"

VALID_ANALYTICS_ENTRIES: dict = {
    'KEY':                 str,               # Prevent abuse (embedded at compile time)
    'UNIQUE_IDENTITY':     str,               # Host's UUID as SHA1 hash
    'APPLICATION_NAME':    str,               # ex. OpenCore Legacy Patcher
    'APPLICATION_VERSION': str,               # ex. 0.2.0
    'OS_VERSION':          str,               # ex. 10.15.7
    'MODEL':               str,               # ex. MacBookPro11,5
    'GPUS':                list,              # ex. ['Intel Iris Pro', 'AMD Radeon R9 M370X']
    'FIRMWARE':            str,               # ex. APPLE
    'LOCATION':            str,               # ex. 'US' (just broad region, don't need to be specific)
    'TIMESTAMP':           datetime.datetime, # ex. 2021-09-01-12-00-00
}

VALID_CRASH_ENTRIES: dict = {
    'KEY':                 str,               # Prevent abuse (embedded at compile time)
    'APPLICATION_VERSION': str,               # ex. 0.2.0
    'APPLICATION_COMMIT':  str,               # ex. 0.2.0 or {commit hash if not a release}
    'OS_VERSION':          str,               # ex. 10.15.7
    'MODEL':               str,               # ex. MacBookPro11,5
    'TIMESTAMP':           datetime.datetime, # ex. 2021-09-01-12-00-00
    'CRASH_LOG':           str,               # ex. "This is a crash log"
}


class Analytics:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants
        self.unique_identity = str(self.constants.computer.uuid_sha1)
        self.application =     str("OpenCore Legacy Patcher")
        self.version =         str(self.constants.patcher_version)
        self.os =              str(self.constants.detected_os_version)
        self.model =           str(self.constants.computer.real_model)
        self.date =            str(datetime.datetime.now().strftime(DATE_FORMAT))


    def send_analytics(self) -> None:
        if global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting") is True:
            return

        self._generate_base_data()
        self._post_analytics_data()


    def send_crash_report(self, log_file: Path) -> None:
        if ANALYTICS_SERVER == "":
            return
        if SITE_KEY == "":
            return
        if global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting") is True:
            return
        if not log_file.exists():
            return
        if self.constants.commit_info[0].startswith("refs/tags"):
            # Avoid being overloaded with crash reports
            return

        commit_info = self.constants.commit_info[0].split("/")[-1] + "_" + self.constants.commit_info[1].split("T")[0] + "_" + self.constants.commit_info[2].split("/")[-1]

        crash_data= {
            "KEY":                 SITE_KEY,
            "APPLICATION_VERSION": self.version,
            "APPLICATION_COMMIT":  commit_info,
            "OS_VERSION":          self.os,
            "MODEL":               self.model,
            "TIMESTAMP":           self.date,
            "CRASH_LOG":           log_file.read_text()
        }

        network_handler.NetworkUtilities().post(CRASH_URL, json = crash_data)


    def _get_country(self) -> str:
        # Get approximate country from .GlobalPreferences.plist
        path = "/Library/Preferences/.GlobalPreferences.plist"
        if not Path(path).exists():
            return "US"

        try:
            result = plistlib.load(Path(path).open("rb"))
        except:
            return "US"

        if "Country" not in result:
            return "US"

        return result["Country"]


    def _generate_base_data(self) -> None:
        self.gpus = []

        self.firmware = str(self.constants.computer.firmware_vendor)
        self.location = str(self._get_country())

        for gpu in self.constants.computer.gpus:
            self.gpus.append(str(gpu.arch))

        self.data = {
            'KEY':                 SITE_KEY,
            'UNIQUE_IDENTITY':     self.unique_identity,
            'APPLICATION_NAME':    self.application,
            'APPLICATION_VERSION': self.version,
            'OS_VERSION':          self.os,
            'MODEL':               self.model,
            'GPUS':                self.gpus,
            'FIRMWARE':            self.firmware,
            'LOCATION':            self.location,
            'TIMESTAMP':           self.date,
        }

        # convert to JSON:
        self.data = json.dumps(self.data)


    def _post_analytics_data(self) -> None:
        # Post data to analytics server
        if ANALYTICS_SERVER == "":
            return
        if SITE_KEY == "":
            return
        network_handler.NetworkUtilities().post(ANALYTICS_SERVER, json = self.data)



