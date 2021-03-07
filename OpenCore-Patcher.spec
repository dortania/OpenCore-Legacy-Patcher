# -*- mode: python ; coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.getcwd()))
from Resources import Constants
block_cipher = None


a = Analysis(['OpenCore-Patcher.command'],
             binaries=[],
             datas=[('payloads', 'payloads'), ('Resources', 'Resources')],
             hiddenimports=[],
             hookspath=[],
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
         icon="OC-Patcher.icns",
         bundle_identifier=None,
         info_plist={
             "CFBundleShortVersionString": Constants.Constants().patcher_version,
             "CFBundleExecutable": "MacOS/Launcher",
             "NSHumanReadableCopyright": "Copyright 2020-2021 Dortania"
         })