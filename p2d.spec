# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/plantuml2drawio/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=['plantuml2drawio'],
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
    [],
    exclude_binaries=True,
    name='p2d',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icons/p2d_icon.icns'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='p2d'
)

app = BUNDLE(
    coll,
    name='p2d.app',
    icon='resources/icons/p2d_icon.icns',
    bundle_identifier=None,
)
