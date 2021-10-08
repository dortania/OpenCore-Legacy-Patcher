# Defines Model Data

from resources import device_probe
from data import cpu_data, os_data, bluetooth_data

smbios_dictionary = {
    "MacBook1,1": {
        "Board ID": "Mac-F4208CC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBook2,1": {
        "Board ID": "Mac-F4208CA9",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBook3,1": {
        "Board ID": "Mac-F22788C8",
        "FirmwareFeatures": "0xC0001407",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBook4,1": {
        "Board ID": "Mac-F22788A9",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },


    "MacBook5,1": {
        "Board ID": "Mac-F42D89C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBook5,2": {
        "Board ID": "Mac-F22788AA",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBook6,1": {
        "Board ID": "Mac-F22C8AC8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBook7,1": {
        "Board ID": "Mac-F22C89C8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBook8,1": {
        "Board ID": "Mac-BE0E8AC46FE800CC",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,
        "Ethernet Chipset": None,
    },

    "MacBook9,1": {
        "Board ID": "Mac-9AE82516C7C6B903",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,
        "Ethernet Chipset": None,
    },

    "MacBook10,1": {
        "Board ID": "Mac-EE2EBD4B90B839A8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,
        "Ethernet Chipset": None,

    },

    "MacBookAir1,1": {
        "Board ID": "Mac-F42C8CC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir2,1": {
        "Board ID": "Mac-F42D88C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "nForce Chipset": True,
        "Ethernet Chipset": None,
    },


    "MacBookAir3,1": {
        "Board ID": "Mac-942452F5819B1C1B",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 11,
        "nForce Chipset": True,
        "Ethernet Chipset": None,
    },


    "MacBookAir3,2": {
        "Board ID": "Mac-942C5DF58193131B",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "nForce Chipset": True,
        "Ethernet Chipset": None,
    },


    "MacBookAir4,1": {
        "Board ID": "Mac-C08A6BB70A942AC2",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 11,
        "Ethernet Chipset": "Broadcom", # Set for Apple Thunderbolt Adapter
    },


    "MacBookAir4,2": {
        "Board ID": "Mac-742912EFDBEE19B3",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
        "Ethernet Chipset": "Broadcom", # Set for Apple Thunderbolt Adapter
    },


    "MacBookAir5,1": {
        "Board ID": "Mac-66F35F19FE2A0D05",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 11,
        "Ethernet Chipset": None,
    },


    "MacBookAir5,2": {
        "Board ID": "Mac-2E6FAB96566FE58C",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },


    "MacBookAir6,1": {
        "Board ID": "Mac-35C1E88140C3E6CF",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 11,
        "Ethernet Chipset": None,
    },


    "MacBookAir6,2": {
        "Board ID": "Mac-7DF21CB3ED6977E5",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir7,1": {
        "Board ID": "Mac-9F18E312C5C2BF0B",
        "FirmwareFeatures": "0xFF0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 11,
        "Ethernet Chipset": None,
    },

    "MacBookAir7,2": {
        "Board ID": "Mac-937CB26E2E02BB01",
        "FirmwareFeatures": "0xFF0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir8,1": {
        "Board ID": "Mac-827FAC58A8FDFA22",
        "FirmwareFeatures": "0xFD8FF42E",
        "SecureBootModel": "j140k",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir8,2": {
        "Board ID": "Mac-226CB3C6A851A671",
        "FirmwareFeatures": "0xFD8FF42E",
        "SecureBootModel": "j140a",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir9,1": {
        "Board ID": "Mac-0CFF9C7C2B63DF8D",
        "FirmwareFeatures": "0xFFAFF06E",
        "SecureBootModel": "j230k",
        "CPU Generation": cpu_data.cpu_data.ice_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookAir10,1": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j313",
        "CPU Generation": cpu_data.cpu_data.apple_m1.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": None,
    },

    "MacBookPro1,1": {
        "Board ID": "Mac-F425BEC8",
        "FirmwareFeatures": "",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBookPro1,2": {
        "Board ID": "Mac-F42DBEC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 17,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBookPro2,1": {
        "Board ID": "Mac-F42189C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 17,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBookPro2,2": {
        "Board ID": "Mac-F42187C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBookPro3,1": {
        "Board ID": "Mac-F4238BC8",
        "FirmwareFeatures": "0xC0001407",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,  # Shipped with 17 as well
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "MacBookPro4,1": {
        "Board ID": "Mac-F42C89C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,  # Shipped with 17 as well
        "Switchable GPUs": True,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },


    "MacBookPro5,1": {
        "Board ID": "Mac-F42D86C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBookPro5,2": {
        "Board ID": "Mac-F2268EC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 17,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBookPro5,3": {
        "Board ID": "Mac-F22587C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBookPro5,4": {
        "Board ID": "Mac-F22587A1",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBookPro5,5": {
        "Board ID": "Mac-F2268AC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "MacBookPro6,1": {
        "Board ID": "Mac-F22589C8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 17,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro6,2": {
        "Board ID": "Mac-F22586C8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro7,1": {
        "Board ID": "Mac-F222BEC8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "Ethernet Chipset": "Broadcom",
        "nForce Chipset": True,
    },


    "MacBookPro8,1": {
        "Board ID": "Mac-94245B3640C91C81",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro8,2": {
        "Board ID": "Mac-94245A3940C91C80",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro8,3": {
        "Board ID": "Mac-942459F5819B171B",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 17,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro9,1": {
        "Board ID": "Mac-4B7AC7E43945597E",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro9,2": {
        "Board ID": "Mac-6F01561E16C75D06",
        "FirmwareFeatures": "0xC10DF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
        "Ethernet Chipset": "Broadcom",
    },


    "MacBookPro10,1": {
        "Board ID": "Mac-C3EC7CD22292981F",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },


    "MacBookPro10,2": {
        "Board ID": "Mac-AFD8A9D944EA4843",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },


    "MacBookPro11,1": {
        "Board ID": "Mac-189A3D4F975D5FFC",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },


    "MacBookPro11,2": {
        "Board ID": "Mac-3CBD00234E554E41",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Ethernet Chipset": None,
    },


    "MacBookPro11,3": {
        "Board ID": "Mac-2BD1B31983FE1663",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro11,4": {
        "Board ID": "Mac-06F11FD93F0323C5",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Ethernet Chipset": None,
    },

    "MacBookPro11,5": {
        "Board ID": "Mac-06F11F11946D27C5",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro12,1": {
        "Board ID": "Mac-E43C1C25D4880AD6",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro13,1": {
        "Board ID": "Mac-473D31EABEB93F9B",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro13,2": {
        "Board ID": "Mac-66E35819EE2D0D05",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro13,3": {
        "Board ID": "Mac-A5C67F76ED83108C",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro14,1": {
        "Board ID": "Mac-B4831CEBD52A0C4C",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro14,2": {
        "Board ID": "Mac-CAD6701F7CEA0921",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro14,3": {
        "Board ID": "Mac-551B86E5744E2388",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro15,1": {
        "Board ID": "Mac-937A206F2EE63C01",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j680",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro15,2": {
        "Board ID": "Mac-827FB448E656EC26",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j132",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro15,3": {
        "Board ID": "Mac-1E7E29AD0135F9BC",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j780",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro15,4": {
        "Board ID": "Mac-53FDB3D8DB8CA971",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j213",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro16,1": {
        "Board ID": "Mac-E1008331FDC96864",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j152f",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 16,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro16,2": {
        "Board ID": "Mac-5F9802EFE386AA28",
        "FirmwareFeatures": "0xFFAFF06E",
        "SecureBootModel": "j214k",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro16,3": {
        "Board ID": "Mac-E7203C0F68AA0004",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j223",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
        "Ethernet Chipset": None,
    },

    "MacBookPro16,4": {
        "Board ID": "Mac-A61BADE1FDAD7B05",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j215",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 16,
        "Switchable GPUs": True,
        "Ethernet Chipset": None,
    },

    "MacBookPro17,1": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j293",
        "CPU Generation": cpu_data.cpu_data.apple_m1.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": None,
    },

    "Macmini1,1": {
        "Board ID": "Mac-F4208EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Ethernet Chipset": "Marvell",
    },

    "Macmini2,1": {
        "Board ID": "Mac-F4208EAA",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Ethernet Chipset": "Marvell",
    },

    "Macmini3,1": {
        "Board ID": "Mac-F22C86C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "Macmini4,1": {
        "Board ID": "Mac-F2208EC8",
        "FirmwareFeatures": "0xC00C9423",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Ethernet Chipset": "Broadcom",
    },


    "Macmini5,1": {
        "Board ID": "Mac-8ED6AF5B48C039E1",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Ethernet Chipset": "Broadcom",
    },


    "Macmini5,2": {
        "Board ID": "Mac-4BC72D62AD45599E",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Ethernet Chipset": "Broadcom",
    },


    "Macmini5,3": {
        "Board ID": "Mac-7BA5B2794B2CDB12",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Ethernet Chipset": "Broadcom",
    },


    "Macmini6,1": {
        "Board ID": "Mac-031AEE4D24BFF0B1",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Ethernet Chipset": "Broadcom",
    },


    "Macmini6,2": {
        "Board ID": "Mac-F65AE981FFA204ED",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Ethernet Chipset": "Broadcom",
    },

    "Macmini7,1": {
        "Board ID": "Mac-35C5E08120C7EEAF",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "Macmini8,1": {
        "Board ID": "Mac-7BA5B2DFE22DDD8C",
        "FirmwareFeatures": "0xFD8FF466",
        "SecureBootModel": "j174",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "Macmini9,1": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j274",
        "CPU Generation": cpu_data.cpu_data.apple_m1.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac4,1": {
        "Board ID": "Mac-F42786C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "iMac4,2": {
        "Board ID": "Mac-F4218EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah.value,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "iMac5,1": {
        "Board ID": "Mac-F4228EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "iMac5,2": {
        "Board ID": "Mac-F4218EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "iMac6,1": {
        "Board ID": "Mac-F4218FC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },

    "iMac7,1": {
        "Board ID": "Mac-F42386C8",
        "FirmwareFeatures": "0xC0001407",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,  # Stock models shipped with Conroe
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },


    "iMac8,1": {
        "Board ID": "Mac-F227BEC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
        "Ethernet Chipset": "Marvell",
    },


    "iMac9,1": {
        "Board ID": "Mac-F2218FA9",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "iMac10,1": {
        "Board ID": "Mac-F221DCC8",
        # "Board ID": "Mac-F2268CC8",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Nvidia",
        "nForce Chipset": True,
    },


    "iMac11,1": {
        "Board ID": "Mac-F2268DAE",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac11,2": {
        "Board ID": "Mac-F2238AC8",
        "FirmwareFeatures": "0xC00C9423",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac11,3": {
        "Board ID": "Mac-F2238BAE",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac12,1": {
        "Board ID": "Mac-942B5BF58194151B",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac12,2": {
        "Board ID": "Mac-942B59F58194171B",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge.value,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac13,1": {
        "Board ID": "Mac-00BE6ED71E35EB86",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac13,2": {
        "Board ID": "Mac-FC02E91DDD3FA6A4",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac13,3": {
        "Board ID": "Mac-7DF2A3B5E5D671ED",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac14,1": {
        "Board ID": "Mac-031B6874CF7F642A",
        "FirmwareFeatures": "0xFB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac14,2": {
        "Board ID": "Mac-27ADBB7B4CEE8E61",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac14,3": {
        "Board ID": "Mac-77EB7D7DAF985301",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac14,4": {
        "Board ID": "Mac-81E3E92DD6088272",
        "FirmwareFeatures": "0xF00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },


    "iMac15,1": {
        "Board ID": "Mac-42FD25EABCABB274",
        "FirmwareFeatures": "0xF80FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac16,1": {
        "Board ID": "Mac-A369DDC4E67F1C45",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac16,2": {
        "Board ID": "Mac-FFE5EF870D7BA81A",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac17,1": {
        "Board ID": "Mac-DB15BD556843C820",
        # "Board ID": "Mac-65CE76090165799A",
        # "Board ID": "Mac-B809C3757DA9BB8D",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac18,1": {
        "Board ID": "Mac-4B682C642B45593E",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac18,2": {
        "Board ID": "Mac-77F17D7DA9285301",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac18,3": {
        "Board ID": "Mac-BE088AF8C5EB4FA2",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac19,1": {
        "Board ID": "Mac-AA95B1DDAB278B95",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac19,2": {
        "Board ID": "Mac-63001698E7A34814",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac20,1": {
        "Board ID": "Mac-CFF7D910A743CAAF",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": "j185",
        "CPU Generation": cpu_data.cpu_data.comet_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac20,2": {
        "Board ID": "Mac-AF89B6D9451A490B",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": "j185f",
        "CPU Generation": cpu_data.cpu_data.comet_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac21,1": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j456",
        "CPU Generation": cpu_data.cpu_data.apple_m1.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": "Broadcom",
    },

    "iMac21,2": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j457",
        "CPU Generation": cpu_data.cpu_data.apple_m1.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": "Broadcom",
    },


    "iMacPro1,1": {
        "Board ID": "Mac-7BA5B2D9E42DDD94",
        "FirmwareFeatures": "0xFD8FF53E",
        "SecureBootModel": "j137",
        "CPU Generation": cpu_data.cpu_data.skylake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "MacPro1,1": {
        "Board ID": "Mac-F4208DC8",
        "FirmwareFeatures": "0x80000015",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
        "Ethernet Chipset": "Intel 80003ES2LAN",
    },

    "MacPro2,1": {
        "Board ID": "Mac-F4208DA9",
        "FirmwareFeatures": "0xC0000015",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
        "Ethernet Chipset": "Intel 80003ES2LAN",
    },

    "MacPro3,1": {
        "Board ID": "Mac-F42C88C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
        "Ethernet Chipset": "Intel 80003ES2LAN",
    },


    "MacPro4,1": {
        "Board ID": "Mac-F221BEC8",
        "FirmwareFeatures": "0xE001F537",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Intel 82574L",
    },


    "MacPro5,1": {
        "Board ID": "Mac-F221BEC8",
        "FirmwareFeatures": "0xE80FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.mojave,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Ethernet Chipset": "Intel 82574L",
    },

    "MacPro6,1": {
        "Board ID": "Mac-F60DEB81FF30ACF6",
        "FirmwareFeatures": "0xE90FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Ethernet Chipset": "Broadcom",
    },

    "MacPro7,1": {
        "Board ID": "Mac-27AD2F918AE68F61",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j160",
        "CPU Generation": cpu_data.cpu_data.coffee_lake.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Ethernet Chipset": "Broadcom",
    },

    "Xserve1,1": {
        "Board ID": "Mac-F4208AC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
        "UGA Graphics": True,
        "Ethernet Chipset": "Intel 80003ES2LAN",
    },

    "Xserve2,1": {
        "Board ID": "Mac-F42289C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn.value,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
        "UGA Graphics": True,
        "Ethernet Chipset": "Intel 80003ES2LAN",
    },

    "Xserve3,1": {
        "Board ID": "Mac-F223BEC8",
        "FirmwareFeatures": "0xE001F537",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem.value,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
        "Ethernet Chipset": "Intel 82574L",
    },

    "ADP3,2": {
        "Board ID": None,
        "FirmwareFeatures": None,
        "SecureBootModel": "j293",
        "CPU Generation": cpu_data.cpu_data.apple_dtk.value,
        "Max OS Supported": os_data.os_data.max_os,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.PCIe,
        "Ethernet Chipset": "Broadcom",
    },

    "AAPLJ53,1": {
        # AppleInternal MacBookPro11,4
        "Board ID": "Mac-C08A65A66A9A3BA2",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell.value,
        "Max OS Supported": os_data.os_data.mavericks,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

}