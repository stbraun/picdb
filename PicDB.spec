# -*- mode: python -*-

import sys
sys.path.insert(0, './picdb')

from version import get_version

block_cipher = None

added_files = [('venv/lib/python3.7/site-packages/postgresql/lib/libsys.sql',
                'postgresql/lib'),
               ('picdb/resources/config_app.yaml', 'picdb/resources'),
               ('picdb/resources/config_log.yaml', 'picdb/resources'),
               ('picdb/resources/eye.gif', 'picdb/resources'),
               ('picdb/resources/not_found.png', 'picdb/resources'),
               ('picdb/resources/not_supported.png', 'picdb/resources')]


a = Analysis(['start_picdb.py'],
             pathex=['/Volumes/B3T/Development/projects/picdb'],
             binaries=[],
             datas=added_files,
             hiddenimports=['postgresql.types.io.builtins',
                            'PIL._tkinter_finder'],
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
          name='PicDB',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='PicDB.app',
             icon='resrc/Icon.icns',
             bundle_identifier='com.stbraun.picdb',
             info_plist={
                         'CFBundleShortVersionString': get_version()
                        },
             )
