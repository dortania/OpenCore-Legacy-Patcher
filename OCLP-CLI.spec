# -*- mode: python ; coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.getcwd()))
from Resources import Constants
block_cipher = None


a = Analysis(['OCLP-CLI.command'],
             pathex=['Resources', 'Data'],
             binaries=[],
             datas=[('payloads', 'payloads')],
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
          [('u', None, 'OPTION')],
          name='OCLP-CLI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )