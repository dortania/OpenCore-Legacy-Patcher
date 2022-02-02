# -*- mode: python ; coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.getcwd()))
from resources import constants
block_cipher = None


a = Analysis(['OpenCore-Patcher.command'],
             pathex=['resources', 'data'],
             binaries=[],
             datas=[('payloads', 'payloads')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['wxPython', 'wxpython'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='OpenCore-Patcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
app = BUNDLE(exe,
         name='OpenCore-Patcher.app',
         icon="payloads/OC-Patcher-TUI.icns",
         bundle_identifier="com.dortania.opencore-legacy-patcher-tui",
         info_plist={
             "CFBundleShortVersionString": constants.Constants().patcher_version,
             "CFBundleExecutable": "MacOS/Launcher",
             "NSHumanReadableCopyright": constants.Constants().copyright_date,
         })