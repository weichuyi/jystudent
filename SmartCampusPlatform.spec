# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['flask_sqlalchemy']
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('flask_sqlalchemy')


a = Analysis(
    ['C:\\Users\\weichuyi\\Desktop\\jystudent\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static'), ('app.py', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SmartCampusPlatform',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
