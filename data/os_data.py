import enum


class os_data(enum.IntEnum):
    # OS Versions, Based off Major Kernel Version
    tiger = 8
    leopard = 9
    snow_leopard = 10
    lion = 11
    mountain_lion = 12
    mavericks = 13
    yosemite = 14
    el_capitan = 15
    sierra = 16
    high_sierra = 17
    mojave = 18
    catalina = 19
    big_sur = 20
    monterey = 21
    max_os = 99


class os_conversion:

    def os_to_kernel(os):
        # Convert OS version to major XNU version
        if os.startswith("10."):
            return (int(os.split(".")[1]) + 4)
        else:
            return (int(os.split(".")[0]) + 9)

    def kernel_to_os(kernel):
        # Convert major XNU version to OS version
        if kernel >= os_data.big_sur:
            return str((kernel - 9))
        else:
            return str((f"10.{kernel - 4}"))

    def is_os_newer(source_major, source_minor, target_major, target_minor):
        # Check if OS version 1 is newer than OS version 2
        if source_major < target_major:
            return True
        elif source_major == target_major:
            if source_minor < target_minor:
                return True
            else:
                return False