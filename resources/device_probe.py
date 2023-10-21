# Hardware probing
# Copyright (C) 2020-2022, Dhinak G, Mykola Grymalyuk

import binascii
import enum
import itertools
import subprocess
import plistlib
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional, Type, Union

from resources import utilities, ioreg
from data import pci_data, usb_data


def class_code_to_bytes(class_code: int) -> bytes:
    return class_code.to_bytes(4, byteorder="little")


@dataclass
class CPU:
    name: str
    flags: list[str]
    leafs: list[str]


@dataclass
class USBDevice:
    vendor_id:    int
    device_id:    int
    device_class: int
    device_speed: int
    product_name: str
    vendor_name:  Optional[str] = None

    @classmethod
    def from_ioregistry(cls, entry: ioreg.io_registry_entry_t):
        properties: dict = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperties(entry, None, ioreg.kCFAllocatorDefault, ioreg.kNilOptions)[1])

        vendor_id    = None
        device_id    = None
        device_class = None
        device_speed = None
        vendor_name  = None
        product_name = "N/A"

        if "idVendor" in properties:
            vendor_id = properties["idVendor"]
        if "idProduct" in properties:
            device_id = properties["idProduct"]
        if "bDeviceClass" in properties:
            device_class = properties["bDeviceClass"]
        if "kUSBProductString" in properties:
            product_name = properties["kUSBProductString"].strip()
        if "kUSBVendorString" in properties:
            vendor_name = properties["kUSBVendorString"].strip()
        if "USBSpeed" in properties:
            device_speed = properties["USBSpeed"]

        return cls(vendor_id, device_id, device_class, device_speed, product_name, vendor_name)


    def detect(self):
        self.detect_class()
        self.detect_speed()


    def detect_class(self) -> None:
        for device_class in self.ClassCode:
            if self.device_class == device_class.value:
                self.device_class = device_class


    def detect_speed(self) -> None:
        for speed in self.Speed:
            if self.device_speed == speed.value:
                self.device_speed = speed

    class Speed(enum.Enum):
        LOW_SPEED        = 0x01
        FULL_SPEED       = 0x02
        HIGH_SPEED       = 0x03
        SUPER_SPEED      = 0x04
        SUPER_SPEED_PLUS = 0x05


    class ClassCode(enum.Enum):
        # https://www.usb.org/defined-class-codes
        GENERIC           = 0x00
        AUDIO             = 0x01
        CDC_CONTROL       = 0x02
        HID               = 0x03
        PHYSICAL          = 0x05
        IMAGE             = 0x06
        PRINTER           = 0x07
        MASS_STORAGE      = 0x08
        HUB               = 0x09
        CDC_DATA          = 0x0A
        SMART_CARD        = 0x0B
        CONTENT_SEC       = 0x0D
        VIDEO             = 0x0E
        PERSONAL_HEALTH   = 0x0F
        AUDIO_VIDEO       = 0x10
        BILLBOARD         = 0x11
        USB_TYPE_C_BRIDGE = 0x12
        DISPLAY_BDP       = 0x13
        I3C               = 0x3C
        DIAGNOSTIC        = 0xDC
        WIRELESS          = 0xE0
        MISCELLANEOUS     = 0xEF
        APPLICATION       = 0xFE
        VENDOR_SPEC       = 0xFF


@dataclass
class PCIDevice:
    VENDOR_ID: ClassVar[int]  # Default vendor id, for subclasses.
    CLASS_CODES: ClassVar[list[int]]  # Default class codes, for subclasses.

    vendor_id:  int  # The vendor ID of this PCI device
    device_id:  int  # The device ID of this PCI device
    class_code: int  # The class code of this PCI device - https://pci-ids.ucw.cz/read/PD

    name:                Optional[str]  = None  # Name of IORegistryEntry
    model:               Optional[str]  = None  # model property
    acpi_path:           Optional[str]  = None  # ACPI Device Path
    pci_path:            Optional[str]  = None  # PCI Device Path
    disable_metal:       Optional[bool] = False # 'disable-metal' property
    force_compatible:    Optional[bool] = False # 'force-compat' property
    vendor_id_unspoofed: Optional[int]  = -1    # Unspoofed vendor ID of this PCI device
    device_id_unspoofed: Optional[int]  = -1    # Unspoofed device ID of this PCI device

    @classmethod
    def class_code_matching_dict(cls) -> dict:
        return {
            "IOProviderClass": "IOPCIDevice",
            "IOPropertyMatch": [{"class-code": class_code_to_bytes(class_code)} for class_code in cls.CLASS_CODES]
        }

    @classmethod
    def from_ioregistry(cls, entry: ioreg.io_registry_entry_t, anti_spoof=False):
        properties: dict = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperties(entry, None, ioreg.kCFAllocatorDefault, ioreg.kNilOptions)[1])  # type: ignore

        vendor_id = None
        device_id = None
        vendor_id_unspoofed = None
        device_id_unspoofed = None

        if "IOName" in properties:
            ioname = properties["IOName"]
            if type(ioname) is bytes:
                ioname = ioname.strip(b"\0").decode()

            if ioname.startswith("pci") and "," in ioname:
                vendor_id_unspoofed, device_id_unspoofed = (int(i, 16) for i in ioname[3:].split(","))
                if anti_spoof:
                    vendor_id = vendor_id_unspoofed
                    device_id = device_id_unspoofed

        if vendor_id is None and device_id is None:
            vendor_id, device_id = [int.from_bytes(properties[i][:4], byteorder="little") for i in ["vendor-id", "device-id"]]

        if vendor_id_unspoofed is None and device_id_unspoofed is None:
            vendor_id_unspoofed = vendor_id
            device_id_unspoofed = device_id

        device = cls(vendor_id, device_id, int.from_bytes(properties["class-code"][:6], byteorder="little"), name=ioreg.io_name_t_to_str(ioreg.IORegistryEntryGetName(entry, None)[1]))
        if "model" in properties:
            model = properties["model"]
            if isinstance(model, bytes):
                model = model.strip(b"\0").decode()
            device.model = model
        if "acpi-path" in properties:
            device.acpi_path = properties["acpi-path"]
        if "disable-metal" in properties:
            device.disable_metal = True
        if "force-compat" in properties:
            device.force_compatible = True

        device.vendor_id_unspoofed = vendor_id_unspoofed
        device.device_id_unspoofed = device_id_unspoofed
        device.populate_pci_path(entry)
        return device

    def vendor_detect(self, *, inherits: Optional[Type["PCIDevice"]] = None, classes: Optional[list] = None):
        for i in classes or itertools.chain.from_iterable([subclass.__subclasses__() for subclass in PCIDevice.__subclasses__()]):
            if issubclass(i, inherits or object) and i.detect(self):
                return i
        return None

    @classmethod
    def detect(cls, device):
        return device.vendor_id == cls.VENDOR_ID and ((device.class_code in cls.CLASS_CODES) if getattr(cls, "CLASS_CODES", None) else True) and ((device.class_code == cls.CLASS_CODE) if getattr(cls, "CLASS_CODE", None) else True)  # type: ignore  # pylint: disable=no-member

    def populate_pci_path(self, original_entry: ioreg.io_registry_entry_t):
        # Based off gfxutil logic, seems to work.
        paths = []
        entry = original_entry
        while entry:
            if ioreg.IOObjectConformsTo(entry, "IOPCIDevice".encode()):
                # Virtual PCI devices provide a botched IOService path (us.electronic.kext.vusb)
                # We only care about physical devices, so skip them
                try:
                    location = [hex(int(i, 16)) for i in ioreg.io_name_t_to_str(ioreg.IORegistryEntryGetLocationInPlane(entry, "IOService".encode(), None)[1]).split(",") + ["0"]]
                    paths.append(f"Pci({location[0]},{location[1]})")
                except ValueError:
                    break
            elif ioreg.IOObjectConformsTo(entry, "IOACPIPlatformDevice".encode()):
                paths.append(f"PciRoot({hex(int(ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(entry, '_UID', ioreg.kCFAllocatorDefault, ioreg.kNilOptions)) or 0))})")  # type: ignore
                break
            elif ioreg.IOObjectConformsTo(entry, "IOPCIBridge".encode()):
                pass
            else:
                # There's something in between that's not PCI! Abort
                paths = []
                break
            parent = ioreg.IORegistryEntryGetParentEntry(entry, "IOService".encode(), None)[1]
            if entry != original_entry:
                ioreg.IOObjectRelease(entry)
            entry = parent
        self.pci_path = "/".join(reversed(paths))


@dataclass
class GPU(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x030000, 0x038000]
    arch: enum.Enum = field(init=False)  # The architecture, see subclasses.

    def __post_init__(self):
        self.detect_arch()

    def detect_arch(self):
        raise NotImplementedError


@dataclass
class WirelessCard(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x028000]
    country_code: str = field(init=False)
    chipset: enum.Enum = field(init=False)

    def __post_init__(self):
        self.detect_chipset()

    @classmethod
    def from_ioregistry(cls, entry: ioreg.io_registry_entry_t, anti_spoof=True):
        device = super().from_ioregistry(entry, anti_spoof=anti_spoof)

        matching_dict = {
            "IOParentMatch": ioreg.corefoundation_to_native(ioreg.IORegistryEntryIDMatching(ioreg.IORegistryEntryGetRegistryEntryID(entry, None)[1])),
            "IOProviderClass": "IO80211Interface",
        }

        interface = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, matching_dict, None)[1]), None)
        if interface:
            device.country_code = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(interface, "IO80211CountryCode", ioreg.kCFAllocatorDefault, ioreg.kNilOptions))  # type: ignore # If not present, will be None anyways
        else:
            device.country_code = None  # type: ignore

        return device

    def detect_chipset(self):
        raise NotImplementedError


@dataclass
class NVMeController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [
        0x010802,
        # I don't know if this is a typo or what, but Apple controllers are 01:80:02, not 01:08:02
        0x018002
    ]

    aspm: Optional[int] = None
    # parent_aspm: Optional[int] = None

    @classmethod
    def from_ioregistry(cls, entry: ioreg.io_registry_entry_t, anti_spoof=True):
        device = super().from_ioregistry(entry, anti_spoof=anti_spoof)

        device.aspm: Union[int, bytes] = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(entry, "pci-aspm-default", ioreg.kCFAllocatorDefault, ioreg.kNilOptions)) or 0  # type: ignore
        if isinstance(device.aspm, bytes):
            device.aspm = int.from_bytes(device.aspm, byteorder="little")

        return device


@dataclass
class EthernetController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x020000]

    chipset: enum.Enum = field(init=False)

    def __post_init__(self):
        self.detect_chipset()

    def detect_chipset(self):
        raise NotImplementedError

@dataclass
class SATAController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x010601]

@dataclass
class SASController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x010400]

@dataclass
class XHCIController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x0c0330]

@dataclass
class EHCIController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x0c0320]

@dataclass
class OHCIController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x0c0310]

@dataclass
class UHCIController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x0c0300]

@dataclass
class SDXCController(PCIDevice):
    CLASS_CODES: ClassVar[list[int]] = [0x080501]

@dataclass
class NVIDIA(GPU):
    VENDOR_ID: ClassVar[int] = 0x10DE

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        Curie = "Curie"
        Fermi = "Fermi"
        Tesla = "Tesla"
        Kepler = "Kepler"
        Maxwell = "Maxwell"
        Pascal = "Pascal"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        # G80/G80GL
        if self.device_id in pci_data.nvidia_ids.curie_ids:
            self.arch = NVIDIA.Archs.Curie
        elif self.device_id in pci_data.nvidia_ids.tesla_ids:
            self.arch = NVIDIA.Archs.Tesla
        elif self.device_id in pci_data.nvidia_ids.fermi_ids:
            self.arch = NVIDIA.Archs.Fermi
        elif self.device_id in pci_data.nvidia_ids.kepler_ids:
            self.arch = NVIDIA.Archs.Kepler
        elif self.device_id in pci_data.nvidia_ids.maxwell_ids:
            self.arch = NVIDIA.Archs.Maxwell
        elif self.device_id in pci_data.nvidia_ids.pascal_ids:
            self.arch = NVIDIA.Archs.Pascal
        else:
            self.arch = NVIDIA.Archs.Unknown

@dataclass
class NVIDIAEthernet(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x10DE

    class Chipsets(enum.Enum):
        nForceEthernet = "nForceEthernet"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        # nForce driver matches against Vendor ID, thus making all nForce chipsets supported
        self.chipset = NVIDIAEthernet.Chipsets.nForceEthernet

@dataclass
class AMD(GPU):
    VENDOR_ID: ClassVar[int] = 0x1002

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        R500 = "R500"
        TeraScale_1 = "TeraScale 1"
        TeraScale_2 = "TeraScale 2"
        Legacy_GCN_7000 = "Legacy GCN v1"
        Legacy_GCN_8000 = "Legacy GCN v2"
        Legacy_GCN_9000 = "Legacy GCN v3"
        Polaris = "Polaris"
        Polaris_Spoof = "Polaris (Spoofed)"
        Vega = "Vega"
        Navi = "Navi"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        if self.device_id in pci_data.amd_ids.r500_ids:
            self.arch = AMD.Archs.R500
        elif self.device_id in pci_data.amd_ids.gcn_7000_ids:
            self.arch = AMD.Archs.Legacy_GCN_7000
        elif self.device_id in pci_data.amd_ids.gcn_8000_ids:
            self.arch = AMD.Archs.Legacy_GCN_8000
        elif self.device_id in pci_data.amd_ids.gcn_9000_ids:
            self.arch = AMD.Archs.Legacy_GCN_9000
        elif self.device_id in pci_data.amd_ids.terascale_1_ids:
            self.arch = AMD.Archs.TeraScale_1
        elif self.device_id in pci_data.amd_ids.terascale_2_ids:
            self.arch = AMD.Archs.TeraScale_2
        elif self.device_id in pci_data.amd_ids.polaris_ids:
            self.arch = AMD.Archs.Polaris
        elif self.device_id in pci_data.amd_ids.polaris_spoof_ids:
            self.arch = AMD.Archs.Polaris_Spoof
        elif self.device_id in pci_data.amd_ids.vega_ids:
            self.arch = AMD.Archs.Vega
        elif self.device_id in pci_data.amd_ids.navi_ids:
            self.arch = AMD.Archs.Navi
        else:
            self.arch = AMD.Archs.Unknown


@dataclass
class Intel(GPU):
    VENDOR_ID: ClassVar[int] = 0x8086

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        GMA_950 = "GMA 950"
        GMA_X3100 = "GMA X3100"
        Iron_Lake = "Iron Lake"
        Sandy_Bridge = "Sandy Bridge"
        Ivy_Bridge = "Ivy Bridge"
        Haswell = "Haswell"
        Broadwell = "Broadwell"
        Skylake = "Skylake"
        Kaby_Lake = "Kaby Lake"
        Coffee_Lake = "Coffee Lake"
        Comet_Lake = "Comet Lake"
        Ice_Lake = "Ice Lake"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        if self.device_id in pci_data.intel_ids.gma_950_ids:
            self.arch = Intel.Archs.GMA_950
        elif self.device_id in pci_data.intel_ids.gma_x3100_ids:
            self.arch = Intel.Archs.GMA_X3100
        elif self.device_id in pci_data.intel_ids.iron_ids:
            self.arch = Intel.Archs.Iron_Lake
        elif self.device_id in pci_data.intel_ids.sandy_ids:
            self.arch = Intel.Archs.Sandy_Bridge
        elif self.device_id in pci_data.intel_ids.ivy_ids:
            self.arch = Intel.Archs.Ivy_Bridge
        elif self.device_id in pci_data.intel_ids.haswell_ids:
            self.arch = Intel.Archs.Haswell
        elif self.device_id in pci_data.intel_ids.broadwell_ids:
            self.arch = Intel.Archs.Broadwell
        elif self.device_id in pci_data.intel_ids.skylake_ids:
            self.arch = Intel.Archs.Skylake
        elif self.device_id in pci_data.intel_ids.kaby_lake_ids:
            self.arch = Intel.Archs.Kaby_Lake
        elif self.device_id in pci_data.intel_ids.coffee_lake_ids:
            self.arch = Intel.Archs.Coffee_Lake
        elif self.device_id in pci_data.intel_ids.comet_lake_ids:
            self.arch = Intel.Archs.Comet_Lake
        elif self.device_id in pci_data.intel_ids.ice_lake_ids:
            self.arch = Intel.Archs.Ice_Lake
        else:
            self.arch = Intel.Archs.Unknown

@dataclass
class IntelEthernet(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x8086

    class Chipsets(enum.Enum):
        AppleIntel8254XEthernet = "AppleIntel8254XEthernet Supported"
        AppleIntelI210Ethernet = "AppleIntelI210Ethernet Supported"
        Intel82574L = "Intel82574L Supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.intel_ids.AppleIntel8254XEthernet:
            self.chipset = IntelEthernet.Chipsets.AppleIntel8254XEthernet
        elif self.device_id in pci_data.intel_ids.AppleIntelI210Ethernet:
            self.chipset = IntelEthernet.Chipsets.AppleIntelI210Ethernet
        elif self.device_id in pci_data.intel_ids.Intel82574L:
            self.chipset = IntelEthernet.Chipsets.Intel82574L
        else:
            self.chipset = IntelEthernet.Chipsets.Unknown

@dataclass
class Broadcom(WirelessCard):
    VENDOR_ID: ClassVar[int] = 0x14E4

    class Chipsets(enum.Enum):
        # pylint: disable=invalid-name
        AppleBCMWLANBusInterfacePCIe = "AppleBCMWLANBusInterfacePCIe supported"
        AirportBrcmNIC = "AirportBrcmNIC supported"
        AirPortBrcmNICThirdParty = "AirPortBrcmNICThirdParty supported"
        AirPortBrcm4360 = "AirPortBrcm4360 supported"
        AirPortBrcm4331 = "AirPortBrcm4331 supported"
        AirPortBrcm43224 = "AppleAirPortBrcm43224 supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.broadcom_ids.AppleBCMWLANBusInterfacePCIe:
            self.chipset = Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe
        elif self.device_id in pci_data.broadcom_ids.AirPortBrcmNIC:
            self.chipset = Broadcom.Chipsets.AirportBrcmNIC
        elif self.device_id in pci_data.broadcom_ids.AirPortBrcmNICThirdParty:
            self.chipset = Broadcom.Chipsets.AirPortBrcmNICThirdParty
        elif self.device_id in pci_data.broadcom_ids.AirPortBrcm4360:
            self.chipset = Broadcom.Chipsets.AirPortBrcm4360
        elif self.device_id in pci_data.broadcom_ids.AirPortBrcm4331:
            self.chipset = Broadcom.Chipsets.AirPortBrcm4331
        elif self.device_id in pci_data.broadcom_ids.AppleAirPortBrcm43224:
            self.chipset = Broadcom.Chipsets.AirPortBrcm43224
        else:
            self.chipset = Broadcom.Chipsets.Unknown

@dataclass
class BroadcomEthernet(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x14E4

    class Chipsets(enum.Enum):
        AppleBCM5701Ethernet = "AppleBCM5701Ethernet supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.broadcom_ids.AppleBCM5701Ethernet:
            self.chipset = BroadcomEthernet.Chipsets.AppleBCM5701Ethernet
        else:
            self.chipset = BroadcomEthernet.Chipsets.Unknown

@dataclass
class Atheros(WirelessCard):
    VENDOR_ID: ClassVar[int] = 0x168C

    class Chipsets(enum.Enum):
        # pylint: disable=invalid-name
        # Well there's only one model but
        AirPortAtheros40 = "AirPortAtheros40 supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.atheros_ids.AtherosWifi:
            self.chipset = Atheros.Chipsets.AirPortAtheros40
        else:
            self.chipset = Atheros.Chipsets.Unknown


@dataclass
class Aquantia(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x1D6A

    class Chipsets(enum.Enum):
        # pylint: disable=invalid-name
        AppleEthernetAquantiaAqtion = "AppleEthernetAquantiaAqtion supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.aquantia_ids.AppleEthernetAquantiaAqtion:
            self.chipset = Aquantia.Chipsets.AppleEthernetAquantiaAqtion
        else:
            self.chipset = Aquantia.Chipsets.Unknown

@dataclass
class Marvell(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x11AB

    class Chipsets(enum.Enum):
        MarvelYukonEthernet = "MarvelYukonEthernet supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.marvell_ids.MarvelYukonEthernet:
            self.chipset = Marvell.Chipsets.MarvelYukonEthernet
        else:
            self.chipset = Marvell.Chipsets.Unknown

@dataclass
class SysKonnect(EthernetController):
    VENDOR_ID: ClassVar[int] = 0x1148

    class Chipsets(enum.Enum):
        MarvelYukonEthernet = "MarvelYukonEthernet supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in pci_data.syskonnect_ids.MarvelYukonEthernet:
            self.chipset = SysKonnect.Chipsets.MarvelYukonEthernet
        else:
            self.chipset = SysKonnect.Chipsets.Unknown


@dataclass
class Computer:
    real_model: Optional[str] = None
    real_board_id: Optional[str] = None
    reported_model: Optional[str] = None
    reported_board_id: Optional[str] = None
    build_model: Optional[str] = None
    uuid_sha1: Optional[str] = None
    gpus: list[GPU] = field(default_factory=list)
    igpu: Optional[GPU] = None  # Shortcut for IGPU
    dgpu: Optional[GPU] = None  # Shortcut for GFX0
    storage: list[PCIDevice] = field(default_factory=list)
    usb_controllers: list[PCIDevice] = field(default_factory=list)
    sdxc_controller: list[PCIDevice] = field(default_factory=list)
    ethernet: list[EthernetController] = field(default_factory=list)
    wifi: Optional[WirelessCard] = None
    cpu: Optional[CPU] = None
    usb_devices: list[USBDevice] = field(default_factory=list)
    oclp_version: Optional[str] = None
    opencore_version: Optional[str] = None
    opencore_path: Optional[str] = None
    bluetooth_chipset: Optional[str] = None
    internal_keyboard_type: Optional[str] = None
    trackpad_type: Optional[str] = None
    ambient_light_sensor: Optional[bool] = False
    third_party_sata_ssd: Optional[bool] = False
    pcie_webcam: Optional[bool] = False
    t1_chip: Optional[bool] = False
    secure_boot_model: Optional[str] = None
    secure_boot_policy: Optional[int] = None
    oclp_sys_version: Optional[str] = None
    oclp_sys_date: Optional[str] = None
    oclp_sys_url: Optional[str] = None
    oclp_sys_signed: Optional[bool] = False
    firmware_vendor: Optional[str] = None
    rosetta_active: Optional[bool] = False

    @staticmethod
    def probe():
        computer = Computer()
        computer.gpu_probe()
        computer.dgpu_probe()
        computer.igpu_probe()
        computer.wifi_probe()
        computer.storage_probe()
        computer.usb_controller_probe()
        computer.sdxc_controller_probe()
        computer.ethernet_probe()
        computer.smbios_probe()
        computer.usb_device_probe()
        computer.cpu_probe()
        computer.bluetooth_probe()
        computer.topcase_probe()
        computer.t1_probe()
        computer.ambient_light_sensor_probe()
        computer.pcie_webcam_probe()
        computer.sata_disk_probe()
        computer.oclp_sys_patch_probe()
        computer.check_rosetta()
        return computer


    def usb_device_probe(self):
        devices = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault, {"IOProviderClass": "IOUSBDevice"}, None
            )[1]
        )
        for device in devices:
            properties = USBDevice.from_ioregistry(device)
            if properties:
                properties.detect()
                self.usb_devices.append(properties)
            ioreg.IOObjectRelease(device)


    def gpu_probe(self):
        # Chain together two iterators: one for class code 03:00:00, the other for class code 03:80:00
        devices = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault, GPU.class_code_matching_dict(), None
            )[1]
        )

        for device in devices:
            vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
            if vendor:
                self.gpus.append(vendor.from_ioregistry(device))  # type: ignore
            ioreg.IOObjectRelease(device)

    def dgpu_probe(self):
        device = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, ioreg.IOServiceNameMatching("GFX0".encode()), None)[1]), None)
        if not device:
            # No devices
            return

        vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
        if vendor:
            self.dgpu = vendor.from_ioregistry(device)  # type: ignore
        ioreg.IOObjectRelease(device)

    def igpu_probe(self):
        device = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, ioreg.IOServiceNameMatching("IGPU".encode()), None)[1]), None)
        if not device:
            # No devices
            return

        vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
        if vendor:
            self.igpu = vendor.from_ioregistry(device)  # type: ignore
        ioreg.IOObjectRelease(device)

    def wifi_probe(self):
        devices = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                WirelessCard.class_code_matching_dict(),
                None,
            )[1]
        )

        for device in devices:
            vendor: Type[WirelessCard] = PCIDevice.from_ioregistry(device, anti_spoof=True).vendor_detect(inherits=WirelessCard)  # type: ignore
            if vendor:
                self.wifi = vendor.from_ioregistry(device, anti_spoof=True)  # type: ignore
                break
            ioreg.IOObjectRelease(device)

    def ambient_light_sensor_probe(self):
        device = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, ioreg.IOServiceNameMatching("ALS0".encode()), None)[1]), None)
        if device:
            self.ambient_light_sensor = True
            ioreg.IOObjectRelease(device)

    def pcie_webcam_probe(self):
        # CMRA/14E4:1570
        device = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, ioreg.IOServiceNameMatching("CMRA".encode()), None)[1]), None)
        if device:
            self.pcie_webcam = True
            ioreg.IOObjectRelease(device)

    def sdxc_controller_probe(self):
        sdxc_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                SDXCController.class_code_matching_dict(),
                None,
            )[1]
        )

        for device in sdxc_controllers:
            self.sdxc_controller.append(SDXCController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)

    def usb_controller_probe(self):
        xhci_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                XHCIController.class_code_matching_dict(),
                None,
            )[1]
        )
        ehci_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                EHCIController.class_code_matching_dict(),
                None,
            )[1]
        )
        ohci_controllers  = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                OHCIController.class_code_matching_dict(),
                None,
            )[1]
        )

        uhci_controllers  = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                UHCIController.class_code_matching_dict(),
                None,
            )[1]
        )
        for device in xhci_controllers:
            self.usb_controllers.append(XHCIController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)
        for device in ehci_controllers:
            self.usb_controllers.append(EHCIController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)
        for device in ohci_controllers:
            self.usb_controllers.append(OHCIController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)
        for device in uhci_controllers:
            self.usb_controllers.append(UHCIController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)

    def ethernet_probe(self):
        ethernet_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                EthernetController.class_code_matching_dict(),
                None,
            )[1]
        )

        for device in ethernet_controllers:
            vendor: Type[EthernetController] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=EthernetController)  # type: ignore
            if vendor:
                self.ethernet.append(vendor.from_ioregistry(device))  # type: ignore
            ioreg.IOObjectRelease(device)

    def storage_probe(self):
        sata_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                SATAController.class_code_matching_dict(),
                None,
            )[1]
        )
        sas_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                SASController.class_code_matching_dict(),
                None,
            )[1]
        )

        nvme_controllers = ioreg.ioiterator_to_list(
            ioreg.IOServiceGetMatchingServices(
                ioreg.kIOMasterPortDefault,
                NVMeController.class_code_matching_dict(),
                None,
            )[1]
        )
        for device in sata_controllers:
            self.storage.append(SATAController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)

        for device in sas_controllers:
            self.storage.append(SASController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)

        for device in nvme_controllers:
            self.storage.append(NVMeController.from_ioregistry(device))
            ioreg.IOObjectRelease(device)

    def smbios_probe(self):
        # Reported model
        entry = next(ioreg.ioiterator_to_list(ioreg.IOServiceGetMatchingServices(ioreg.kIOMasterPortDefault, ioreg.IOServiceMatching("IOPlatformExpertDevice".encode()), None)[1]))
        self.reported_model = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(entry, "model", ioreg.kCFAllocatorDefault, ioreg.kNilOptions)).strip(b"\0").decode()  # type: ignore
        translated = subprocess.run("sysctl -in sysctl.proc_translated".split(), stdout=subprocess.PIPE).stdout.decode()
        if translated:
            board = "target-type"
        else:
            board = "board-id"
        self.reported_board_id = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(entry, board, ioreg.kCFAllocatorDefault, ioreg.kNilOptions)).strip(b"\0").decode()  # type: ignore
        self.uuid_sha1 = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(entry, "IOPlatformUUID", ioreg.kCFAllocatorDefault, ioreg.kNilOptions))  # type: ignore
        self.uuid_sha1 = hashlib.sha1(self.uuid_sha1.encode()).hexdigest()
        ioreg.IOObjectRelease(entry)

        # Real model
        self.real_model = utilities.get_nvram("oem-product", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True) or self.reported_model
        self.real_board_id = utilities.get_nvram("oem-board", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True) or self.reported_board_id
        self.build_model = utilities.get_nvram("OCLP-Model", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)

        # OCLP version
        self.oclp_version = utilities.get_nvram("OCLP-Version", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        self.opencore_version = utilities.get_nvram("opencore-version", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)
        self.opencore_path = utilities.get_nvram("boot-path", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)

        # SecureBoot Variables
        self.secure_boot_model = utilities.check_secure_boot_model()
        self.secure_boot_policy = utilities.check_ap_security_policy()

        # Firmware Vendor
        firmware_vendor = utilities.get_firmware_vendor(decode=False)
        if isinstance(firmware_vendor, bytes):
            firmware_vendor = str(firmware_vendor.replace(b"\x00", b"").decode("utf-8"))
        self.firmware_vendor = firmware_vendor

    def cpu_probe(self):
        self.cpu = CPU(
            subprocess.run("sysctl machdep.cpu.brand_string".split(), stdout=subprocess.PIPE).stdout.decode().partition(": ")[2].strip(),
            subprocess.run("sysctl machdep.cpu.features".split(), stdout=subprocess.PIPE).stdout.decode().partition(": ")[2].strip().split(" "),
            self.cpu_get_leafs(),
        )

    def cpu_get_leafs(self):
        leafs = []
        result = subprocess.run("sysctl machdep.cpu.leaf7_features".split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return result.stdout.decode().partition(": ")[2].strip().split(" ")
        return leafs

    def bluetooth_probe(self):
        if not self.usb_devices:
            return

        # Ensure we get the "best" bluetooth chipset (if multiple are present)
        if any("BRCM20702" in usb_device.product_name for usb_device in self.usb_devices):
            self.bluetooth_chipset = "BRCM20702 Hub"
        elif any("BCM20702A0" in usb_device.product_name or "BCM2045A0" in usb_device.product_name for usb_device in self.usb_devices):
            self.bluetooth_chipset = "3rd Party Bluetooth 4.0 Hub"
        elif any("BRCM2070 Hub" in usb_device.product_name for usb_device in self.usb_devices):
            self.bluetooth_chipset = "BRCM2070 Hub"
        elif any("BRCM2046 Hub" in usb_device.product_name for usb_device in self.usb_devices):
            self.bluetooth_chipset = "BRCM2046 Hub"
        elif any("Bluetooth" in usb_device.product_name for usb_device in self.usb_devices):
            self.bluetooth_chipset = "Generic"

    def topcase_probe(self):
        if not self.usb_devices:
            return

        for usb_device in self.usb_devices:
            if self.internal_keyboard_type and self.trackpad_type:
                break
            if usb_device.vendor_id != 0x5ac:
                continue

            if usb_device.device_id in usb_data.AppleIDs.Legacy_AppleUSBTCKeyboard:
                self.internal_keyboard_type = "Legacy"
            elif usb_device.device_id in usb_data.AppleIDs.Modern_AppleUSBTCKeyboard:
                self.internal_keyboard_type = "Modern"

            if usb_device.device_id in usb_data.AppleIDs.AppleUSBTrackpad:
                self.trackpad_type = "Legacy"
            elif usb_device.device_id in usb_data.AppleIDs.AppleUSBMultiTouch:
                self.trackpad_type = "Modern"

    def t1_probe(self):
        if not self.usb_devices:
            return

        for usb_device in self.usb_devices:
            if usb_device.vendor_id != 0x5ac:
                continue
            if usb_device.device_id != 0x8600:
                continue
            self.t1_chip = True
            break

    def sata_disk_probe(self):
        # Get all SATA Controllers/Disks from 'system_profiler SPSerialATADataType'
        # Determine whether SATA SSD is present and Apple-made
        sp_sata_data = plistlib.loads(subprocess.run(f"system_profiler SPSerialATADataType -xml".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
        for root in sp_sata_data:
            for ahci_controller in root["_items"]:
                # Each AHCI controller will have its own entry
                # Skip entries that are AHCI PCIe controllers
                # Apple's AHCI PCIe controller will report 'PCI' interconnect
                try:
                    if ahci_controller["spsata_physical_interconnect"] == "SATA":
                        for port in ahci_controller["_items"]:
                            if port["spsata_medium_type"] == "Solid State" and "apple" not in port["device_model"].lower():
                                self.third_party_sata_ssd = True
                                # Bail out of loop as we only need to know if there are any third-party SSDs present
                                break
                except KeyError:
                    # Notes:
                    # - SATA Optical Disk Drives don't report 'spsata_medium_type'
                    # - 'spsata_physical_interconnect' was not introduced till 10.9
                    continue

    def oclp_sys_patch_probe(self):
        path = Path("/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist")
        if not path.exists():
            self.oclp_sys_signed = True  # No plist, so assume root is valid
            return
        sys_plist = plistlib.load(path.open("rb"))
        if sys_plist:
            if "OpenCore Legacy Patcher" in sys_plist:
                self.oclp_sys_version = sys_plist["OpenCore Legacy Patcher"]
            if "Time Patched" in sys_plist:
                self.oclp_sys_date = sys_plist["Time Patched"]
            if "Commit URL" in sys_plist:
                self.oclp_sys_url = sys_plist["Commit URL"]
            if "Custom Signature" in sys_plist:
                self.oclp_sys_signed = sys_plist["Custom Signature"]

    def check_rosetta(self):
        result = subprocess.run("sysctl -in sysctl.proc_translated".split(), stdout=subprocess.PIPE).stdout.decode()
        if "1" in result:
            self.rosetta_active = True
        else:
            self.rosetta_active = False