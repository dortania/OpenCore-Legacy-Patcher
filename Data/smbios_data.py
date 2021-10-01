# Defines Model Data

from Resources import device_probe
from Data import cpu_data, os_data, bluetooth_data

smbios_dictionary = {
    "MacBook1,1": {
        "Board ID": "Mac-F4208CC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,

    },

    "MacBook2,1": {
        "Board ID": "Mac-F4208CA9",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,
    },

    "MacBook3,1": {
        "Board ID": "Mac-F22788C8",
        "FirmwareFeatures": "0xC0001407",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 13,
        "UGA Graphics": True,
    },

    "MacBook4,1": {
        "Board ID": "Mac-F22788A9",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
        "UGA Graphics": True,
    },


    "MacBook5,1": {
        "Board ID": "Mac-F42D89C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBook5,2": {
        "Board ID": "Mac-F22788AA",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBook6,1": {
        "Board ID": "Mac-F22C8AC8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
    },


    "MacBook7,1": {
        "Board ID": "Mac-F22C89C8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
    },


    "MacBook8,1": {
        "Board ID": "Mac-BE0E8AC46FE800CC",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,
    },

    "MacBook9,1": {
        "Board ID": "Mac-9AE82516C7C6B903",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,
    },

    "MacBook10,1": {
        "Board ID": "Mac-EE2EBD4B90B839A8",
        "FirmwareFeatures": "0xFC0FE13F",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 12,

    },

    "MacBookAir1,1": {
        "Board ID": "Mac-F42C8CC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },

    "MacBookAir2,1": {
        "Board ID": "Mac-F42D88C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBookAir3,1": {
        "Board ID": "Mac-942452F5819B1C1B",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 11,
    },


    "MacBookAir3,2": {
        "Board ID": "Mac-942C5DF58193131B",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBookAir4,1": {
        "Board ID": "Mac-C08A6BB70A942AC2",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 11,
    },


    "MacBookAir4,2": {
        "Board ID": "Mac-742912EFDBEE19B3",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
    },


    "MacBookAir5,1": {
        "Board ID": "Mac-66F35F19FE2A0D05",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 11,
    },


    "MacBookAir5,2": {
        "Board ID": "Mac-2E6FAB96566FE58C",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
    },


    "MacBookAir6,1": {
        "Board ID": "Mac-35C1E88140C3E6CF",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 11,
    },


    "MacBookAir6,2": {
        "Board ID": "Mac-7DF21CB3ED6977E5",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
    },

    "MacBookAir7,1": {
        "Board ID": "Mac-9F18E312C5C2BF0B",
        "FirmwareFeatures": "0xFF0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 11,
    },

    "MacBookAir7,2": {
        "Board ID": "Mac-937CB26E2E02BB01",
        "FirmwareFeatures": "0xFF0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
    },

    "MacBookAir8,1": {
        "Board ID": "Mac-827FAC58A8FDFA22",
        "FirmwareFeatures": "0xFD8FF42E",
        "SecureBootModel": "j140kap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookAir8,2": {
        "Board ID": "Mac-226CB3C6A851A671",
        "FirmwareFeatures": "0xFD8FF42E",
        "SecureBootModel": "j140aap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookAir9,1": {
        "Board ID": "Mac-0CFF9C7C2B63DF8D",
        "FirmwareFeatures": "0xFFAFF06E",
        "SecureBootModel": "j230kap",
        "CPU Generation": cpu_data.cpu_data.ice_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookPro1,1": {
        "Board ID": "Mac-F425BEC8",
        "FirmwareFeatures": "",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,
        "UGA Graphics": True,
    },

    "MacBookPro1,2": {
        "Board ID": "Mac-F42DBEC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 17,
        "UGA Graphics": True,
    },

    "MacBookPro2,1": {
        "Board ID": "Mac-F42189C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 17,
        "UGA Graphics": True,
    },

    "MacBookPro2,2": {
        "Board ID": "Mac-F42187C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,
        "UGA Graphics": True,
    },

    "MacBookPro3,1": {
        "Board ID": "Mac-F4238BC8",
        "FirmwareFeatures": "0xC0001407",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "Screen Size": 15,  # Shipped with 17 as well
        "UGA Graphics": True,
    },

    "MacBookPro4,1": {
        "Board ID": "Mac-F42C89C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,  # Shipped with 17 as well
        "Switchable GPUs": True,
        "UGA Graphics": True,
    },


    "MacBookPro5,1": {
        "Board ID": "Mac-F42D86C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro5,2": {
        "Board ID": "Mac-F2268EC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 17,
        "Switchable GPUs": True,
    },


    "MacBookPro5,3": {
        "Board ID": "Mac-F22587C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro5,4": {
        "Board ID": "Mac-F22587A1",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro5,5": {
        "Board ID": "Mac-F2268AC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBookPro6,1": {
        "Board ID": "Mac-F22589C8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 17,
        "Switchable GPUs": True,
    },


    "MacBookPro6,2": {
        "Board ID": "Mac-F22586C8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro7,1": {
        "Board ID": "Mac-F222BEC8",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "Screen Size": 13,
    },


    "MacBookPro8,1": {
        "Board ID": "Mac-94245B3640C91C81",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 13,
    },


    "MacBookPro8,2": {
        "Board ID": "Mac-94245A3940C91C80",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro8,3": {
        "Board ID": "Mac-942459F5819B171B",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
        "Screen Size": 17,
        "Switchable GPUs": True,
    },


    "MacBookPro9,1": {
        "Board ID": "Mac-4B7AC7E43945597E",
        "FirmwareFeatures": "0xC00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro9,2": {
        "Board ID": "Mac-6F01561E16C75D06",
        "FirmwareFeatures": "0xC10DF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
    },


    "MacBookPro10,1": {
        "Board ID": "Mac-C3EC7CD22292981F",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },


    "MacBookPro10,2": {
        "Board ID": "Mac-AFD8A9D944EA4843",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
        "Screen Size": 13,
    },


    "MacBookPro11,1": {
        "Board ID": "Mac-189A3D4F975D5FFC",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
    },


    "MacBookPro11,2": {
        "Board ID": "Mac-3CBD00234E554E41",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
    },


    "MacBookPro11,3": {
        "Board ID": "Mac-2BD1B31983FE1663",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro11,4": {
        "Board ID": "Mac-06F11FD93F0323C5",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
    },

    "MacBookPro11,5": {
        "Board ID": "Mac-06F11F11946D27C5",
        "FirmwareFeatures": "0xEB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro12,1": {
        "Board ID": "Mac-E43C1C25D4880AD6",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
        "Screen Size": 13,
    },

    "MacBookPro13,1": {
        "Board ID": "Mac-473D31EABEB93F9B",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
    },

    "MacBookPro13,2": {
        "Board ID": "Mac-66E35819EE2D0D05",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
    },

    "MacBookPro13,3": {
        "Board ID": "Mac-A5C67F76ED83108C",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro14,1": {
        "Board ID": "Mac-B4831CEBD52A0C4C",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
    },

    "MacBookPro14,2": {
        "Board ID": "Mac-CAD6701F7CEA0921",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 13,
    },

    "MacBookPro14,3": {
        "Board ID": "Mac-551B86E5744E2388",
        "FirmwareFeatures": "0xFF0FF57E",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703_UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro15,1": {
        "Board ID": "Mac-937A206F2EE63C01",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j680ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro15,2": {
        "Board ID": "Mac-827FB448E656EC26",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j132ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookPro15,3": {
        "Board ID": "Mac-1E7E29AD0135F9BC",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j780ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 15,
        "Switchable GPUs": True,
    },

    "MacBookPro15,4": {
        "Board ID": "Mac-53FDB3D8DB8CA971",
        "FirmwareFeatures": "0xFD8FF426",
        "SecureBootModel": "j213ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookPro16,1": {
        "Board ID": "Mac-E1008331FDC96864",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j152fap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 16,
        "Switchable GPUs": True,
    },

    "MacBookPro16,2": {
        "Board ID": "Mac-5F9802EFE386AA28",
        "FirmwareFeatures": "0xFFAFF06E",
        "SecureBootModel": "j214kap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookPro16,3": {
        "Board ID": "Mac-E7203C0F68AA0004",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j223ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 13,
    },

    "MacBookPro16,4": {
        "Board ID": "Mac-A61BADE1FDAD7B05",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j215ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
        "Screen Size": 16,
        "Switchable GPUs": True,
    },

    "Macmini1,1": {
        "Board ID": "Mac-F4208EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
    },

    "Macmini2,1": {
        "Board ID": "Mac-F4208EAA",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
    },

    "Macmini3,1": {
        "Board ID": "Mac-F22C86C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "Macmini4,1": {
        "Board ID": "Mac-F2208EC8",
        "FirmwareFeatures": "0xC00C9423",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
    },


    "Macmini5,1": {
        "Board ID": "Mac-8ED6AF5B48C039E1",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
    },


    "Macmini5,2": {
        "Board ID": "Mac-4BC72D62AD45599E",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
    },


    "Macmini5,3": {
        "Board ID": "Mac-7BA5B2794B2CDB12",
        "FirmwareFeatures": "0xD00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2070,
    },


    "Macmini6,1": {
        "Board ID": "Mac-031AEE4D24BFF0B1",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
    },


    "Macmini6,2": {
        "Board ID": "Mac-F65AE981FFA204ED",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
    },

    "Macmini7,1": {
        "Board ID": "Mac-35C5E08120C7EEAF",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "Macmini8,1": {
        "Board ID": "Mac-7BA5B2DFE22DDD8C",
        "FirmwareFeatures": "0xFD8FF466",
        "SecureBootModel": "j174ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "iMac4,1": {
        "Board ID": "Mac-F42786C8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
    },

    "iMac4,2": {
        "Board ID": "Mac-F4218EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.yonah,
        "Max OS Supported": os_data.os_data.snow_leopard,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
    },

    "iMac5,1": {
        "Board ID": "Mac-F4228EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
    },

    "iMac5,2": {
        "Board ID": "Mac-F4218EC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
    },

    "iMac6,1": {
        "Board ID": "Mac-F4218FC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
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
    },


    "iMac8,1": {
        "Board ID": "Mac-F227BEC8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
        "UGA Graphics": True,
    },


    "iMac9,1": {
        "Board ID": "Mac-F2218FA9",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac10,1": {
        "Board ID": "Mac-F221DCC8",
        # "Board ID": "Mac-F2268CC8",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac11,1": {
        "Board ID": "Mac-F2268DAE",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac11,2": {
        "Board ID": "Mac-F2238AC8",
        "FirmwareFeatures": "0xC00C9423",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac11,3": {
        "Board ID": "Mac-F2238BAE",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac12,1": {
        "Board ID": "Mac-942B5BF58194151B",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac12,2": {
        "Board ID": "Mac-942B59F58194171B",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.sandy_bridge,
        "Max OS Supported": os_data.os_data.high_sierra,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "iMac13,1": {
        "Board ID": "Mac-00BE6ED71E35EB86",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
    },


    "iMac13,2": {
        "Board ID": "Mac-FC02E91DDD3FA6A4",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
    },


    "iMac13,3": {
        "Board ID": "Mac-7DF2A3B5E5D671ED",
        "FirmwareFeatures": "0xE00DE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4360,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v1,
    },


    "iMac14,1": {
        "Board ID": "Mac-031B6874CF7F642A",
        "FirmwareFeatures": "0xFB0FF577",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },


    "iMac14,2": {
        "Board ID": "Mac-27ADBB7B4CEE8E61",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },


    "iMac14,3": {
        "Board ID": "Mac-77EB7D7DAF985301",
        "FirmwareFeatures": "0xE00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.catalina,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },


    "iMac14,4": {
        "Board ID": "Mac-81E3E92DD6088272",
        "FirmwareFeatures": "0xF00FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },


    "iMac15,1": {
        "Board ID": "Mac-42FD25EABCABB274",
        "FirmwareFeatures": "0xF80FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.haswell,
        "Max OS Supported": os_data.os_data.big_sur,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "iMac16,1": {
        "Board ID": "Mac-A369DDC4E67F1C45",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "iMac16,2": {
        "Board ID": "Mac-FFE5EF870D7BA81A",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.broadwell,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "iMac17,1": {
        "Board ID": "Mac-DB15BD556843C820",
        # "Board ID": "Mac-65CE76090165799A",
        # "Board ID": "Mac-B809C3757DA9BB8D",
        "FirmwareFeatures": "0xFC0FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "iMac18,1": {
        "Board ID": "Mac-4B682C642B45593E",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
    },

    "iMac18,2": {
        "Board ID": "Mac-77F17D7DA9285301",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
    },

    "iMac18,3": {
        "Board ID": "Mac-BE088AF8C5EB4FA2",
        "FirmwareFeatures": "0xFD0FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.kaby_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20703,
    },

    "iMac19,1": {
        "Board ID": "Mac-AA95B1DDAB278B95",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "iMac19,2": {
        "Board ID": "Mac-63001698E7A34814",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "iMac20,1": {
        "Board ID": "Mac-CFF7D910A743CAAF",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": "j185ap",
        "CPU Generation": cpu_data.cpu_data.comet_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "iMac20,2": {
        "Board ID": "Mac-AF89B6D9451A490B",
        "FirmwareFeatures": "0xFD8FF576",
        "SecureBootModel": "j185fap",
        "CPU Generation": cpu_data.cpu_data.comet_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "iMacPro1,1": {
        "Board ID": "Mac-7BA5B2D9E42DDD94",
        "FirmwareFeatures": "0xFD8FF53E",
        "SecureBootModel": "j137ap",
        "CPU Generation": cpu_data.cpu_data.skylake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "MacPro1,1": {
        "Board ID": "Mac-F4208DC8",
        "FirmwareFeatures": "0x80000015",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
    },

    "MacPro2,1": {
        "Board ID": "Mac-F4208DA9",
        "FirmwareFeatures": "0xC0000015",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
    },

    "MacPro3,1": {
        "Board ID": "Mac-F42C88C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm43224,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2045,
        "UGA Graphics": True,
    },


    "MacPro4,1": {
        "Board ID": "Mac-F221BEC8",
        "FirmwareFeatures": "0xE001F537",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": device_probe.Atheros.Chipsets.AirPortAtheros40,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },


    "MacPro5,1": {
        "Board ID": "Mac-F221BEC8",
        "FirmwareFeatures": "0xE80FE137",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.mojave,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirPortBrcm4331,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM2046,
    },

    "MacPro6,1": {
        "Board ID": "Mac-F60DEB81FF30ACF6",
        "FirmwareFeatures": "0xE90FF576",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.ivy_bridge,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AirportBrcmNIC,
        "Bluetooth Model": bluetooth_data.bluetooth_data.BRCM20702_v2,
    },

    "MacPro7,1": {
        "Board ID": "Mac-27AD2F918AE68F61",
        "FirmwareFeatures": "0xFDAFF066",
        "SecureBootModel": "j160ap",
        "CPU Generation": cpu_data.cpu_data.coffee_lake,
        "Max OS Supported": None,
        "Wireless Model": device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
        "Bluetooth Model": bluetooth_data.bluetooth_data.UART,
    },

    "Xserve1,1": {
        "Board ID": "Mac-F4208AC8",
        "FirmwareFeatures": None,
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.conroe,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
        "UGA Graphics": True,
    },

    "Xserve2,1": {
        "Board ID": "Mac-F42289C8",
        "FirmwareFeatures": "0xC0001403",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.penryn,
        "Max OS Supported": os_data.os_data.lion,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
        "UGA Graphics": True,
    },

    "Xserve3,1": {
        "Board ID": "Mac-F223BEC8",
        "FirmwareFeatures": "0xE001F537",
        "SecureBootModel": None,
        "CPU Generation": cpu_data.cpu_data.nehalem,
        "Max OS Supported": os_data.os_data.el_capitan,
        "Wireless Model": None,
        "Bluetooth Model": bluetooth_data.bluetooth_data.NonApplicable,
    },

}
