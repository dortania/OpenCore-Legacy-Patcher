import subprocess
from Resources import Constants

patcher_support_pkg_version = Constants.Constants().patcher_support_pkg_version
binary_packages = ["10.14-Mojave", "10.15-Catalina", "11-Big-Sur", "12-Monterey"]

for binary_package in binary_packages:
    print(f"- Downloading {binary_package}...")
    download_cmd = f"curl -LO https://github.com/dortania/PatcherSupportPkg/releases/download/{patcher_support_pkg_version}/{binary_package}.zip"
    subprocess.run(download_cmd, shell=True)
    print("- Moving into payloads")
    move_cmd = f"mv {binary_package}.zip ./payloads/"
    subprocess.run(move_cmd, shell=True)
print("- Download complete")
