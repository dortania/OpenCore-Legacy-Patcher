# Probe for OS data

import platform
import subprocess
import plistlib


def detect_kernel_major():
    # Return Major Kernel Version
    # Example Output: 21 (integer)
    return int(platform.uname().release.partition(".")[0])


def detect_kernel_minor():
    # Return Minor Kernel Version
    # Example Output: 1 (integer)
    return int(platform.uname().release.partition(".")[2].partition(".")[0])


def detect_os_version():
    # Return OS version
    # Example Output: 12.0 (string)
    return subprocess.run("sw_vers -productVersion".split(), stdout=subprocess.PIPE).stdout.decode().strip()


def detect_os_build():
    # Return OS build
    # Example Output: 21A5522h (string)

    # With macOS 13.2, Apple implemented the Rapid Security Response system which
    # will change the reported build to the RSR version and not the original host
    # To get the proper versions:
    #  - Host: /System/Library/CoreServices/SystemVersion.plist
    #  - RSR:  /System/Volumes/Preboot/Cryptexes/OS/System/Library/CoreServices/SystemVersion.plist
    return plistlib.load(open("/System/Library/CoreServices/SystemVersion.plist", "rb"))["ProductBuildVersion"]
