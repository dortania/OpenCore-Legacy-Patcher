"""
products.py: Parse products from Software Update Catalog
"""

import re
import plistlib

import packaging.version
import xml.etree.ElementTree as ET

from pathlib   import Path
from functools import cached_property

from .url       import CatalogURL
from .constants import CatalogVersion, SeedType

from ..support import network_handler


class CatalogProducts:
    """
    Args:
        catalog                       (dict): Software Update Catalog (contents of CatalogURL's URL)
        install_assistants_only       (bool): Only list InstallAssistant products
        only_vmm_install_assistants   (bool): Only list VMM-x86_64-compatible InstallAssistant products
        max_install_assistant_version (CatalogVersion): Maximum InstallAssistant version to list
    """
    def __init__(self,
                 catalog: dict,
                 install_assistants_only: bool = True,
                 only_vmm_install_assistants: bool = True,
                 max_install_assistant_version: CatalogVersion = CatalogVersion.TAHOE
                ) -> None:
        self.catalog:             dict = catalog
        self.ia_only:             bool = install_assistants_only
        self.vmm_only:            bool = only_vmm_install_assistants
        self.max_ia_version: packaging = packaging.version.parse(f"{max_install_assistant_version.value}.99.99")
        self.max_ia_catalog: CatalogVersion = max_install_assistant_version


    def _legacy_parse_info_plist(self, data: dict) -> dict:
        """
        Legacy version of parsing for installer details through Info.plist
        """

        if "MobileAssetProperties" not in data:
            return {}
        if "SupportedDeviceModels" not in data["MobileAssetProperties"]:
            return {}
        if "OSVersion" not in data["MobileAssetProperties"]:
            return {}
        if "Build" not in data["MobileAssetProperties"]:
            return {}

        # Ensure Apple Silicon specific Installers are not listed
        if "VMM-x86_64" not in data["MobileAssetProperties"]["SupportedDeviceModels"]:
            if self.vmm_only:
                return {"Missing VMM Support": True}

        version = data["MobileAssetProperties"]["OSVersion"]
        build   = data["MobileAssetProperties"]["Build"]

        catalog = ""
        try:
            catalog = data["MobileAssetProperties"]["BridgeVersionInfo"]["CatalogURL"]
        except KeyError:
            pass

        if any([version, build]) is None:
            return {}

        return {
            "Version": version,
            "Build":   build,
            "Catalog": CatalogURL().catalog_url_to_seed(catalog),
        }


    def _parse_mobile_asset_plist(self, data: dict) -> dict:
        """
        Parses the MobileAsset plist for installer details

        With macOS Sequoia, the Info.plist is no longer present in the InstallAssistant's assets
        """
        _does_support_vmm = False
        for entry in data["Assets"]:
            if "SupportedDeviceModels" not in entry:
                continue
            if "OSVersion" not in entry:
                continue
            if "Build" not in entry:
                continue
            if "VMM-x86_64" not in entry["SupportedDeviceModels"]:
                if self.vmm_only:
                    continue

            _does_support_vmm = True

            build   = entry["Build"]
            version = entry["OSVersion"]

            catalog_url = ""
            try:
                catalog_url = entry["BridgeVersionInfo"]["CatalogURL"]
            except KeyError:
                pass

            return {
                "Version": version,
                "Build":   build,
                "Catalog": CatalogURL().catalog_url_to_seed(catalog_url),
            }

        if _does_support_vmm is False:
            if self.vmm_only:
                return {"Missing VMM Support": True}

        return {}


    def _parse_english_distributions(self, data: bytes) -> dict:
        """
        Resolve Title, Build and Version from the English distribution file
        """
        try:
            plist_contents = plistlib.loads(data)
        except plistlib.InvalidFileException:
            plist_contents = None

        try:
            xml_contents = ET.fromstring(data)
        except ET.ParseError:
            xml_contents = None

        _product_map = {
            "Title":   None,
            "Build":   None,
            "Version": None,
        }

        if plist_contents:
            if "macOSProductBuildVersion" in plist_contents:
                _product_map["Build"] = plist_contents["macOSProductBuildVersion"]
            if "macOSProductVersion" in plist_contents:
                _product_map["Version"] = plist_contents["macOSProductVersion"]
            if "BUILD" in plist_contents:
                _product_map["Build"] = plist_contents["BUILD"]
            if "VERSION" in plist_contents:
                _product_map["Version"] = plist_contents["VERSION"]

        if xml_contents:
            # Fetch item title
            item_title = xml_contents.find(".//title").text
            if item_title in ["SU_TITLE", "MANUAL_TITLE", "MAN_TITLE"]:
                # regex search the contents for the title
                title_search = re.search(r'"SU_TITLE"\s*=\s*"(.*)";', data.decode("utf-8"))
                if title_search:
                    item_title = title_search.group(1)

            _product_map["Title"] = item_title

        return _product_map


    def _build_installer_name(self, version: str, catalog: SeedType) -> str:
        """
        Builds the installer name based on the version and catalog
        """
        try:
            marketing_name = CatalogVersion(version.split(".")[0]).name
        except ValueError:
            marketing_name = "Unknown"

        # Replace _ with space
        marketing_name = marketing_name.replace("_", " ")

        # Convert to upper for each word
        marketing_name = "macOS " + " ".join([word.capitalize() for word in marketing_name.split()])

        # Append Beta if needed
        if catalog in [SeedType.DeveloperSeed, SeedType.PublicSeed, SeedType.CustomerSeed]:
            marketing_name += " Beta"

        return marketing_name


    def _list_latest_installers_only(self, products: list) -> list:
        """
        List only the latest installers per macOS version

        macOS versions capped at n-3 (n being the latest macOS version)
        """

        supported_versions = []

        # Build list of supported versions (n to n-3, where n is the latest macOS version set)
        did_find_latest = False
        for version in CatalogVersion:
            if did_find_latest is False:
                if version != self.max_ia_catalog:
                    continue
                did_find_latest = True

            supported_versions.append(version)

            if len(supported_versions) == 4:
                break

        # Invert the list
        supported_versions = supported_versions[::-1]

        # Create duplicate product list
        products_copy = products.copy()

        # Remove all but the newest version
        for version in supported_versions:
            _newest_version = packaging.version.parse("0.0.0")

            # First, determine largest version
            for installer in products:
                if installer["Version"] is None:
                    continue
                if not installer["Version"].startswith(version.value):
                    continue
                if installer["Catalog"] in [SeedType.CustomerSeed, SeedType.DeveloperSeed, SeedType.PublicSeed]:
                    continue
                try:
                    if packaging.version.parse(installer["Version"]) > _newest_version:
                        _newest_version = packaging.version.parse(installer["Version"])
                except packaging.version.InvalidVersion:
                    pass

            # Next, remove all installers that are not the newest version
            for installer in products:
                if installer["Version"] is None:
                    continue
                if not installer["Version"].startswith(version.value):
                    continue
                try:
                    if packaging.version.parse(installer["Version"]) < _newest_version:
                        if installer in products_copy:
                            products_copy.pop(products_copy.index(installer))
                except packaging.version.InvalidVersion:
                    pass

                # Remove beta versions if a public release is available
                if _newest_version != packaging.version.parse("0.0.0"):
                    if installer["Catalog"] in [SeedType.CustomerSeed, SeedType.DeveloperSeed, SeedType.PublicSeed]:
                        if installer in products_copy:
                            products_copy.pop(products_copy.index(installer))


        # Remove EOL versions (older than n-3)
        for installer in products:
            if installer["Version"].split(".")[0] < supported_versions[-4].value:
                if installer in products_copy:
                    products_copy.pop(products_copy.index(installer))

        return products_copy


    @cached_property
    def products(self) -> None:
        """
        Returns a list of products from the sucatalog
        """

        catalog = self.catalog

        _products = []

        for product in catalog["Products"]:

            # InstallAssistants.pkgs (macOS Installers) will have the following keys:
            if self.ia_only:
                if "ExtendedMetaInfo" not in catalog["Products"][product]:
                    continue
                if "InstallAssistantPackageIdentifiers" not in catalog["Products"][product]["ExtendedMetaInfo"]:
                    continue
                if "SharedSupport" not in catalog["Products"][product]["ExtendedMetaInfo"]["InstallAssistantPackageIdentifiers"]:
                    continue

            _product_map = {
                "ProductID": product,
                "PostDate":  catalog["Products"][product]["PostDate"],
                "Title":     None,
                "Build":     None,
                "Version":   None,
                "Catalog":   None,

                # Optional keys if not InstallAssistant only:
                # "Packages": None,

                # Optional keys if InstallAssistant found:
                # "InstallAssistant": {
                #     "URL":       None,
                #     "Size":      None,
                #     "XNUMajor":  None,
                #     "IntegrityDataURL":  None,
                #     "IntegrityDataSize": None
                # },
            }

            # InstallAssistant logic
            if "Packages" in catalog["Products"][product]:
                # Add packages to product map if not InstallAssistant only
                if self.ia_only is False:
                    _product_map["Packages"] = catalog["Products"][product]["Packages"]
                for package in catalog["Products"][product]["Packages"]:
                    if "URL" in package:
                        if Path(package["URL"]).name == "InstallAssistant.pkg":
                            _product_map["InstallAssistant"] = {
                                "URL":               package["URL"],
                                "Size":              package["Size"],
                                "IntegrityDataURL":  package["IntegrityDataURL"],
                                "IntegrityDataSize": package["IntegrityDataSize"]
                            }

                        if Path(package["URL"]).name not in ["Info.plist", "com_apple_MobileAsset_MacSoftwareUpdate.plist"]:
                            continue

                        net_obj = network_handler.NetworkUtilities().get(package["URL"])
                        if net_obj is None:
                            continue

                        contents = net_obj.content
                        try:
                            plist_contents = plistlib.loads(contents)
                        except plistlib.InvalidFileException:
                            continue

                        if plist_contents:
                            if Path(package["URL"]).name == "Info.plist":
                                result = self._legacy_parse_info_plist(plist_contents)
                            else:
                                result = self._parse_mobile_asset_plist(plist_contents)

                            if result == {"Missing VMM Support": True}:
                                _product_map = {}
                                break

                            _product_map.update(result)

            if _product_map == {}:
                continue

            if _product_map["Version"] is not None:
                _product_map["Title"] = self._build_installer_name(_product_map["Version"], _product_map["Catalog"])

            # Fall back to English distribution if no version is found
            if _product_map["Version"] is None:
                url = None
                if "Distributions" in catalog["Products"][product]:
                    if "English" in catalog["Products"][product]["Distributions"]:
                        url = catalog["Products"][product]["Distributions"]["English"]
                    elif "en" in catalog["Products"][product]["Distributions"]:
                        url = catalog["Products"][product]["Distributions"]["en"]

                if url is None:
                    continue

                net_obj = network_handler.NetworkUtilities().get(url)
                if net_obj is None:
                    continue

                contents = net_obj.content

                _product_map.update(self._parse_english_distributions(contents))

                if _product_map["Version"] is None:
                    if "ServerMetadataURL" in catalog["Products"][product]:
                        server_metadata_url = catalog["Products"][product]["ServerMetadataURL"]

                        net_obj = network_handler.NetworkUtilities().get(server_metadata_url)
                        if net_obj is None:
                            continue

                        server_metadata_contents = net_obj.content

                        try:
                            server_metadata_plist = plistlib.loads(server_metadata_contents)
                        except plistlib.InvalidFileException:
                            pass

                        if "CFBundleShortVersionString" in server_metadata_plist:
                            _product_map["Version"] = server_metadata_plist["CFBundleShortVersionString"]


            if _product_map["Version"] is not None:
                # Check if version is newer than the max version
                if self.ia_only:
                    try:
                        if packaging.version.parse(_product_map["Version"]) > self.max_ia_version:
                            continue
                    except packaging.version.InvalidVersion:
                        pass

            if _product_map["Build"] is not None:
                if "InstallAssistant" in _product_map:
                    try:
                        # Grab first 2 characters of build
                        _product_map["InstallAssistant"]["XNUMajor"] = int(_product_map["Build"][:2])
                    except ValueError:
                        pass

            # If version is still None, set to 0.0.0
            if _product_map["Version"] is None:
                _product_map["Version"] = "0.0.0"

            _products.append(_product_map)

        _products = sorted(_products, key=lambda x: x["Version"])

        return _products


    @cached_property
    def latest_products(self) -> list:
        """
        Returns a list of the latest products from the sucatalog
        """
        return self._list_latest_installers_only(self.products)