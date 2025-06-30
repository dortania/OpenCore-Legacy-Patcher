"""
os_data.py: OS Version Data
"""

import enum

from curses.ascii import isdigit


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
    sonoma =        23
    sequoia =       24
    tahoe =         25
    max_os =        99


class os_conversion:

    def os_to_kernel(os: str) -> int:
        """
        Convert OS version to major XNU version

        Parameters:
            os (str): OS version

        Returns:
            int: Major XNU version
        """
        if os.startswith("10."):
            return (int(os.split(".")[1]) + 4)
        else:
            return (int(os.split(".")[0]) + 9)


    def kernel_to_os(kernel: int) -> str:
        """
        Convert major XNU version to OS version

        Parameters:
            kernel (int): Major XNU version

        Returns:
            str: OS version
        """
        if kernel >= os_data.big_sur:
            return str((kernel - 9))
        else:
            return str((f"10.{kernel - 4}"))


    def is_os_newer(source_major: int, source_minor: int, target_major: int, target_minor: int) -> bool:
        """
        Check if OS version 1 is newer than OS version 2

        Parameters:
            source_major (int): Major XNU version of OS version 1
            source_minor (int): Minor XNU version of OS version 1
            target_major (int): Major XNU version of OS version 2
            target_minor (int): Minor XNU version of OS version 2

        Returns:
            bool: True if OS version 1 is newer than OS version 2
        """
        if source_major < target_major:
            return True
        elif source_major == target_major:
            if source_minor < target_minor:
                return True
            else:
                return False


    def convert_kernel_to_marketing_name(kernel: int) -> str:
        """
        Convert major XNU version to Marketing name

        Parameters:
            kernel (int): Major XNU version

        Returns:
            str: Marketing name of OS
        """
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


    def convert_marketing_name_to_kernel(marketing_name: str) -> int:
        """
        Convert Marketing Name to major XNU version

        Parameters:
            marketing_name (str): Marketing Name of OS

        Returns:
            int: Major XNU version
        """
        try:
            # Find os_data enum value
            os_kernel = os_data[marketing_name.lower().replace(" ", "_")]
        except KeyError:
            os_kernel = 0

        return int(os_kernel)


    def find_largest_build(build_array: list) -> str:
        """
        Find the newest version within an array of versions
        These builds will have both numbers and letters in the version
        ex:
        [
            "22A5295i",
            "22A5266r",
            "22A5286j",
            "22A5295h",
        ]
        """

        max_length =        0  # Length of the longest build
        build_array_split = [] # 'build_array', converted into individual array of elements
        final_build =       "" # Largest determined build


        # Convert strings to arrays
        for build in build_array:
            list_build = list(build)
            if len(list_build) > max_length:
                max_length = len(list_build)
            build_array_split.append(list_build)

        # Pad out each array to same length
        for build in build_array_split:
            while len(build) < max_length:
                build.append("0")

        # Convert all letters to int using ord()
        for build in build_array_split:
            for entry in build:
                if not entry.isdigit():
                    build[build.index(entry)] = ord(entry)

        for build_outer_loop in build_array_split:
            for build_inner_loop in list(build_array_split):
                for i in range(len(build_outer_loop)):
                    # remove any builds that are not the largest
                    if int(build_outer_loop[i]) > int(build_inner_loop[i]):
                        build_array_split.remove(build_inner_loop)
                        break
                    if int(build_outer_loop[i]) < int(build_inner_loop[i]):
                        break

        # Convert array back to string
        for entry in build_array_split[0]:
            # Since we split per character, we know that anything above 9 is a letter
            if int(entry) > 9:
                # revert back to letter
                final_build += chr(entry)
            else:
                final_build += str(entry)

        # Since we pad with 0s, we need to next determine how many 0s to remove
        for build in build_array:
            if final_build.startswith(build):
                # Handle cases where Apple added a letter to the build
                # ex. "22A5295" vs "22A5295"
                remaining_strings = final_build.split(build)[1]
                # If all remaining strings are 0s, then we can remove the 0s
                if all(char == "0" for char in remaining_strings):
                    final_build = build

        return final_build