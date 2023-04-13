import datetime
import plistlib
from pathlib import Path
import json

from resources import network_handler, constants, global_settings


DATE_FORMAT:      str = "%Y-%m-%d %H-%M-%S"
ANALYTICS_SERVER: str = ""
SITE_KEY:         str = ""

VALID_ENTRIES: dict = {
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


class Analytics:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants

        if global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting") is True:
            return

        self._generate_base_data()
        self._post_data()


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

        self.unique_identity = str(self.constants.computer.uuid_sha1)
        self.application = str("OpenCore Legacy Patcher")
        self.version = str(self.constants.patcher_version)
        self.os = str( self.constants.detected_os_version)
        self.model = str(self.constants.computer.real_model)
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
            'TIMESTAMP':           str(datetime.datetime.now().strftime(DATE_FORMAT)),
        }

        # convert to JSON:
        self.data = json.dumps(self.data)


    def _post_data(self) -> None:
        # Post data to analytics server
        if ANALYTICS_SERVER == "":
            return
        if SITE_KEY == "":
            return
        network_handler.NetworkUtilities().post(ANALYTICS_SERVER, json = self.data)



