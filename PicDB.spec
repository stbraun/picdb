# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.insert(0, "./picdb")

block_cipher = None

def get_venv():
    for exec_path in os.get_exec_path():
        path = Path(exec_path)
        if (path / 'python').exists():
            print(f'found python in {path}')
            return path.parent.absolute()
    raise Exception('venv not found')

added_files = [
    (
        get_venv() / "lib/python3.9/site-packages/postgresql/lib/libsys.sql",
        "postgresql/lib",
    ),
    ("picdb/resources/config_app.yaml", "picdb/resources"),
    ("picdb/resources/config_log.yaml", "picdb/resources"),
    ("picdb/resources/eye.gif", "picdb/resources"),
    ("picdb/resources/not_found.png", "picdb/resources"),
    ("picdb/resources/not_supported.png", "picdb/resources"),
]

a = Analysis(
    ["start_picdb.py"],
    pathex=["/Volumes/EXT/Development/projects/picdb"],
    binaries=[],
    datas=added_files,
    hiddenimports=["postgresql.types.io.builtins", "PIL._tkinter_finder"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PicDB",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
app = BUNDLE(
    exe,
    name="PicDB.app",
    icon="resrc/Icon.icns",
    bundle_identifier="com.stbraun.picdb",
    info_plist={"CFBundleShortVersionString": "1.10.0"},
)
