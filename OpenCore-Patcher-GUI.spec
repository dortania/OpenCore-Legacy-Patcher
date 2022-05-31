# -*- mode: python ; coding: utf-8 -*-

import sys, os, time, subprocess
sys.path.append(os.path.abspath(os.getcwd()))
from resources import constants
block_cipher = None


a = Analysis(['OpenCore-Patcher-GUI.command'],
             pathex=[],
             binaries=[],
             datas=[('payloads.dmg', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='OpenCore-Patcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='OpenCore-Patcher')
app = BUNDLE(coll,
             name='OpenCore-Patcher.app',
             icon="payloads/OC-Patcher.icns",
             bundle_identifier="com.dortania.opencore-legacy-patcher",
             info_plist={
                "CFBundleShortVersionString": constants.Constants().patcher_version,
                "NSHumanReadableCopyright": constants.Constants().copyright_date,
                "LSMinimumSystemVersion": "10.10.0",
                "NSRequiresAquaSystemAppearance": False,
                "NSHighResolutionCapable": True,
                "Build Date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "BuildMachineOSBuild": subprocess.run("sw_vers -buildVersion".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode().strip(),
                "NSPrincipalClass": "NSApplication",
             })
