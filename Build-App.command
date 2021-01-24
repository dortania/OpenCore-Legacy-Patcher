#!/usr/bin/env python
from __future__ import print_function

from shutil import copy
from shutil import rmtree
from distutils.dir_util import copy_tree

import os
import json
import subprocess
import sys
import zipfile

os.chdir(os.path.dirname(os.path.realpath(__file__)))
current_path = os.getcwd()

print(current_path)

# File location
command_path = os.path.join(current_path, "OpenCore-Patcher.command")
resources_path = os.path.join(current_path, "Resources/")
payloads_path = os.path.join(current_path, "payloads/")
icns_path = os.path.join(current_path, "OC-Patcher.icns")
plist_path = os.path.join(current_path, "Info.plist")

app_path = os.path.join(current_path, "App/")
app_app_path = os.path.join(current_path, "App/OpenCore-Patcher.app/")
contents_path = os.path.join(current_path, "App/OpenCore-Patcher.app/Contents/")
app_macos_path = os.path.join(current_path, "App/OpenCore-Patcher.app/Contents/MacOS/")
app_macos_payload_path = os.path.join(current_path, "App/OpenCore-Patcher.app/Contents/MacOS/payloads")
app_macos_resources_path = os.path.join(current_path, "App/OpenCore-Patcher.app/Contents/MacOS/Resources")
app_resources_path = os.path.join(current_path, "App/OpenCore-Patcher.app/Contents/Resources/")


if os.path.exists(app_path):
    print("Cleaning App folder")
    rmtree(app_path)

print("Creating new App folder")
os.mkdir(app_path)
os.mkdir(app_app_path)
os.mkdir(contents_path)
os.mkdir(app_macos_path)
os.mkdir(app_resources_path)

copy(command_path, app_macos_path)
copy_tree(resources_path, app_macos_resources_path)
copy_tree(payloads_path, app_macos_payload_path)
copy(icns_path, app_resources_path)
copy(plist_path, contents_path)
copy(icns_path, app_macos_path)

