import enum


class bluetooth_data(enum.IntEnum):
    # Bluetooth Chipsets
    NonApplicable =   0
    APPLE_CSR =       1  # BT 2.0 - Apple rebranded CSR chipset
    BRCM2046 =        2  # BT 2.1
    BRCM2070 =        3  # BT 2.1
    BRCM20702_v1 =    4  # BT 4.0 - 2011/2012
    BRCM20702_v2 =    5  # BT 4.0 - 2013+
    BRCM20703 =       6  # BT 4.2
    BRCM20703_UART =  9  # BRCM20703 over UART, BT 4.2
    UART =           10  # T2
    PCIe =           20  # Apple Silicon
