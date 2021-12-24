# Updates build version in OCLP-GUI during CI builds
# Copyright (C) 2021 Mykola Grymalyuk
import plistlib
from pathlib import Path
from resources import constants

app_path = Path.cwd() / Path ("dist/OpenCore-Patcher-Legacy.app/Contents/Info.plist")
info = plistlib.load(Path(app_path).open("rb"))
info["CFBundleExecutable"] = "Launcher"
plistlib.dump(info, Path(app_path).open("wb"), sort_keys=True)