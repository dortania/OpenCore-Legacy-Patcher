# Probe for OS data

import platform
import subprocess


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
    return subprocess.run("sw_vers -buildVersion".split(), stdout=subprocess.PIPE).stdout.decode().strip()
