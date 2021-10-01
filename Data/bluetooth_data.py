class bluetooth_data:
    # Bluetooth Chipsets
    NonApplicable = 0
    BRCM2045 = 1 # TODO: Rename chipset, currently guessing MacPro1,1-3,1 name
    BRCM2046 = 2 # BT 2.1
    BRCM2070 = 3 # BT 2.1
    BRCM20702_v1 = 4 # BT 4.0 - 2012
    BRCM20702_v2 = 5 # BT 4.0 - 2013+
    BRCM20703 = 6 # BT 4.2
    BRCM20703_UART = 9 # BRCM20703 over UART, BT 4.2
    UART = 10