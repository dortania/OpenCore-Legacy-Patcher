# Logic for mounting root volume
from data import os_data
from resources import Utilities
import plistlib
import subprocess

def mount_root_volume(os_version, root_disk):

    if os_version >= os_data.os_data.big_sur:
        mount_location = "/System/Volumes/Update/mnt1/"
    else:
        mount_location = "/"
    
def find_root_volume():
    root_partition_info = plistlib.loads(subprocess.run("diskutil info -plist /".split(), stdout=subprocess.PIPE).stdout.decode().strip().encode())
    root_mount_path = root_partition_info["DeviceIdentifier"]
    root_mount_path = root_mount_path[:-2] if root_mount_path.count("s") > 1 else root_mount_path
    return root_mount_path
    
