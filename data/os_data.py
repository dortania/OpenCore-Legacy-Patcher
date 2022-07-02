import enum


class os_data(enum.IntEnum):
    # OS Versions, Based off Major Kernel Version
    cheetah =       4 # Actually 1.3.1
    puma =          5
    jaguar =        6
    panther =       7
    tiger =         8
    leopard =       9
    snow_leopard =  10
    lion =          11
    mountain_lion = 12
    mavericks =     13
    yosemite =      14
    el_capitan =    15
    sierra =        16
    high_sierra =   17
    mojave =        18
    catalina =      19
    big_sur =       20
    monterey =      21
    ventura =       22
    max_os =        99


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

    def convert_kernel_to_marketing_name(kernel):
        # Convert major XNU version to Marketing Name
        try:
            # Find os_data enum name
            os_name = os_data(kernel).name

            # Remove "_" from the string
            os_name = os_name.replace("_", " ")

            # Upper case the first letter of each word
            os_name = os_name.title()
        except ValueError:
            # Handle cases where no enum value exists
            # Pass kernel_to_os() as a substitute for a proper OS name
            os_name = os_conversion.kernel_to_os(kernel)

        return os_name

    def convert_marketing_name_to_kernel(marketing_name):
        # Convert Marketing Name to major XNU version
        try:
            # Find os_data enum value
            os_kernel = os_data[marketing_name.lower().replace(" ", "_")]
        except KeyError:
            os_kernel = 0

        return int(os_kernel)