import subprocess
from resources import constants

patcher_support_pkg_version = constants.Constants().patcher_support_pkg_version
binary_packages = ["Universal-Binaries"]

for binary_package in binary_packages:
    print(f"- Downloading {binary_package}...")
    download_cmd = f"curl -LO https://github.com/dortania/PatcherSupportPkg/releases/download/{patcher_support_pkg_version}/{binary_package}.zip"
    subprocess.run(download_cmd, shell=True)
    print("- Moving into payloads")
    move_cmd = f"mv {binary_package}.zip ./payloads/"
    subprocess.run(move_cmd, shell=True)
print("- Download complete")
