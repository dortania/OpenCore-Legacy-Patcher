import binascii
import enum
import itertools
import subprocess
from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional, Type

from Resources import PCIIDArray, Utilities, ioreg


@dataclass
class PCIDevice:
    VENDOR_ID: ClassVar[int]  # Default vendor id, for subclasses.

    vendor_id: int  # The vendor ID of this PCI device
    device_id: int  # The device ID of this PCI device
    class_code: int  # The class code of this PCI device

    # ioregistryentry: Optional[ioreg.IORegistryEntry] = None
    name: Optional[str] = None  # Name of IORegistryEntry
    model: Optional[str] = None  # model property
    pci_path: Optional[str] = None

    # def __getstate__(self):
    #     state = self.__dict__.copy()
    #     state.pop("ioregistryentry")
    #     return state

    @classmethod
    def from_ioregistry(cls, entry: ioreg.IORegistryEntry, anti_spoof=False):
        if anti_spoof and "IOName" in entry.properties:
            vendor_id, device_id = (int(i, 16) for i in entry.properties["IOName"][3:].split(","))
        else:
            vendor_id, device_id = [int.from_bytes(entry.properties[i][:4], byteorder="little") for i in ["vendor-id", "device-id"]]

        device = cls(vendor_id, device_id, int.from_bytes(entry.properties["class-code"][:6], byteorder="little"), name=entry.name)
        if "model" in entry.properties:
            device.model = entry.properties["model"].strip(b"\0").decode()
        device.populate_pci_path(entry)
        return device

    # @staticmethod
    # def vendor_detect_old(device):
    #     for i in [NVIDIA, AMD]:
    #         if i.detect(device):
    #             return i
    #     return None

    def vendor_detect(self, *, inherits: ClassVar[Any] = None, classes: list = None):
        for i in classes or itertools.chain.from_iterable([subclass.__subclasses__() for subclass in PCIDevice.__subclasses__()]):
            if issubclass(i, inherits or object) and i.detect(self):
                return i
        return None

    @classmethod
    def detect(cls, device):
        return device.vendor_id == cls.VENDOR_ID and ((device.class_code == cls.CLASS_CODE) if getattr(cls, "CLASS_CODE", None) else True)  # type: ignore  # pylint: disable=no-member

    # def acpi_path(self):
    #     # Eventually
    #     raise NotImplementedError

    def populate_pci_path(self, entry: ioreg.IORegistryEntry):
        # Based off gfxutil logic, seems to work.
        paths = []
        while entry:
            if entry.entry_class == "IOPCIDevice":
                location = [hex(int(i, 16)) for i in entry.location.split(",") + ["0"]]
                paths.append(f"Pci({location[0]},{location[1]})")
            elif entry.entry_class == "IOACPIPlatformDevice":
                paths.append(f"PciRoot({hex(int(entry.properties.get('_UID', 0)))})")
                break
            entry = entry.parent
        self.pci_path = "/".join(reversed(paths))


@dataclass
class GPU(PCIDevice):
    arch: enum.Enum = field(init=False)  # The architecture, see subclasses.

    def __post_init__(self):
        self.detect_arch()

    def detect_arch(self):
        raise NotImplementedError


@dataclass
class WirelessCard(PCIDevice):
    CLASS_CODE: ClassVar[int] = 0x028000  # 00800200 hexswapped
    chipset: enum.Enum = field(init=False)

    def __post_init__(self):
        self.detect_chipset()

    def detect_chipset(self):
        raise NotImplementedError


@dataclass
class NVIDIA(GPU):
    VENDOR_ID: ClassVar[int] = 0x10DE

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        Fermi = "Fermi"
        Tesla = "Tesla"
        Kepler = "Kepler"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        # G80/G80GL
        if self.device_id in PCIIDArray.nvidia_ids.tesla_ids:
            self.arch = NVIDIA.Archs.Tesla
        elif self.device_id in PCIIDArray.nvidia_ids.fermi_ids:
            self.arch = NVIDIA.Archs.Fermi
        elif self.device_id in PCIIDArray.nvidia_ids.kepler_ids:
            self.arch = NVIDIA.Archs.Kepler
        else:
            self.arch = NVIDIA.Archs.Unknown


@dataclass
class AMD(GPU):
    VENDOR_ID: ClassVar[int] = 0x1002

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        Legacy_GCN = "Legacy GCN"
        TeraScale_1 = "TeraScale 1"
        TeraScale_2 = "TeraScale 2"
        Polaris = "Polaris"
        Vega = "Vega"
        Navi = "Navi"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        if self.device_id in PCIIDArray.amd_ids.legacy_gcn_ids:
            self.arch = AMD.Archs.Legacy_GCN
        elif self.device_id in PCIIDArray.amd_ids.terascale_1_ids:
            self.arch = AMD.Archs.TeraScale_1
        elif self.device_id in PCIIDArray.amd_ids.terascale_2_ids:
            self.arch = AMD.Archs.TeraScale_2
        elif self.device_id in PCIIDArray.amd_ids.polaris_ids:
            self.arch = AMD.Archs.Polaris
        elif self.device_id in PCIIDArray.amd_ids.vega_ids:
            self.arch = AMD.Archs.Vega
        elif self.device_id in PCIIDArray.amd_ids.navi_ids:
            self.arch = AMD.Archs.Navi
        else:
            self.arch = AMD.Archs.Unknown


@dataclass
class Intel(GPU):
    VENDOR_ID: ClassVar[int] = 0x8086

    class Archs(enum.Enum):
        # pylint: disable=invalid-name
        Iron_Lake = "Iron Lake"
        Sandy_Bridge = "Sandy Bridge"
        Ivy_Bridge = "Ivy Bridge"
        Unknown = "Unknown"

    arch: Archs = field(init=False)

    def detect_arch(self):
        if self.device_id in PCIIDArray.intel_ids.iron_ids:
            self.arch = Intel.Archs.Iron_Lake
        elif self.device_id in PCIIDArray.intel_ids.sandy_ids:
            self.arch = Intel.Archs.Sandy_Bridge
        elif self.device_id in PCIIDArray.intel_ids.ivy_ids:
            self.arch = Intel.Archs.Ivy_Bridge
        else:
            self.arch = Intel.Archs.Unknown


@dataclass
class Broadcom(WirelessCard):
    VENDOR_ID: ClassVar[int] = 0x14E4

    class Chipsets(enum.Enum):
        # pylint: disable=invalid-name
        AirportBrcmNIC = "AirportBrcmNIC supported"
        AirPortBrcm4360 = "AirPortBrcm4360 supported"
        AirPortBrcm4331 = "AirPortBrcm4331 supported"
        AirPortBrcm43224 = "AppleAirPortBrcm43224 supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)

    def detect_chipset(self):
        if self.device_id in PCIIDArray.broadcom_ids.AirPortBrcmNIC:
            self.chipset = Broadcom.Chipsets.AirportBrcmNIC
        elif self.device_id in PCIIDArray.broadcom_ids.AirPortBrcm4360:
            self.chipset = Broadcom.Chipsets.AirPortBrcm4360
        elif self.device_id in PCIIDArray.broadcom_ids.AirPortBrcm4331:
            self.chipset = Broadcom.Chipsets.AirPortBrcm4331
        elif self.device_id in PCIIDArray.broadcom_ids.AppleAirPortBrcm43224:
            self.chipset = Broadcom.Chipsets.AirPortBrcm43224
        else:
            self.chipset = Broadcom.Chipsets.Unknown


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
        if self.device_id in PCIIDArray.atheros_ids.AtherosWifi:
            self.chipset = Atheros.Chipsets.AirPortAtheros40
        else:
            self.chipset = Atheros.Chipsets.Unknown


@dataclass
class CPU:
    name: str
    flags: list[str]


@dataclass
class Computer:
    real_model: Optional[str] = None
    real_board_id: Optional[str] = None
    reported_model: Optional[str] = None
    reported_board_id: Optional[str] = None
    gpus: list[GPU] = field(default_factory=list)
    igpu: Optional[GPU] = None  # Shortcut for IGPU
    dgpu: Optional[GPU] = None  # Shortcut for GFX0
    wifi: Optional[WirelessCard] = None
    cpu: Optional[CPU] = None
    oclp_version: Optional[str] = None
    ioregistry: Optional[ioreg.IOReg] = None

    @staticmethod
    def probe():
        computer = Computer()
        computer.ioregistry = ioreg.IOReg()
        computer.gpu_probe()
        computer.dgpu_probe()
        computer.igpu_probe()
        computer.wifi_probe()
        computer.smbios_probe()
        computer.cpu_probe()
        return computer

    def gpu_probe(self):
        # Chain together two iterators: one for class code 00000300, the other for class code 00800300
        devices = itertools.chain(self.ioregistry.find(property=("class-code", binascii.a2b_hex("00000300"))), self.ioregistry.find(property=("class-code", binascii.a2b_hex("00800300"))))

        for device in devices:
            vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
            if vendor:
                self.gpus.append(vendor.from_ioregistry(device))  # type: ignore

    def dgpu_probe(self):
        device = next(self.ioregistry.find(name="GFX0"), None)
        if not device:
            # No devices
            return

        vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
        if vendor:
            self.dgpu = vendor.from_ioregistry(device)  # type: ignore

    def igpu_probe(self):
        device = next(self.ioregistry.find(name="IGPU"), None)
        if not device:
            # No devices
            return

        vendor: Type[GPU] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=GPU)  # type: ignore
        if vendor:
            self.igpu = vendor.from_ioregistry(device)  # type: ignore

    def wifi_probe(self):
        # result = subprocess.run("ioreg -r -c IOPCIDevice -a -d2".split(), stdout=subprocess.PIPE).stdout.strip()
        devices = self.ioregistry.find(property=("class-code", binascii.a2b_hex(Utilities.hexswap(hex(WirelessCard.CLASS_CODE)[2:].zfill(8)))))
        # if not result:
        #     # No devices
        #     print("A")
        #     return

        # devices = plistlib.loads(result)
        # devices = [i for i in devices if i["class-code"] == binascii.a2b_hex("00800200")]

        # if not devices:
        #     # No devices
        #     print("B")
        #     return

        for device in devices:
            vendor: Type[WirelessCard] = PCIDevice.from_ioregistry(device).vendor_detect(inherits=WirelessCard)  # type: ignore
            if vendor:
                self.wifi = vendor.from_ioregistry(device, anti_spoof=True)  # type: ignore
                break

    def smbios_probe(self):
        # Reported model
        entry = next(self.ioregistry.find(entry_class="IOPlatformExpertDevice"))
        self.reported_model = entry.properties["model"].strip(b"\0").decode()
        self.reported_board_id = entry.properties.get("board-id", entry.properties.get("target-type", b"")).strip(b"\0").decode()

        # Real model
        # TODO: We previously had logic for OC users using iMacPro1,1 with incorrect ExposeSensitiveData. Add logic?
        self.real_model = Utilities.get_nvram("oem-product", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True) or self.reported_model
        self.real_board_id = Utilities.get_nvram("oem-board", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True) or self.reported_board_id

        # OCLP version
        self.oclp_version = Utilities.get_nvram("OCLP-Version", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", decode=True)

    def cpu_probe(self):
        self.cpu = CPU(
            subprocess.run("sysctl machdep.cpu.brand_string".split(), stdout=subprocess.PIPE).stdout.decode().partition(": ")[2].strip(),
            subprocess.run("sysctl machdep.cpu.features".split(), stdout=subprocess.PIPE).stdout.decode().partition(": ")[2].strip().split(" "),
        )
