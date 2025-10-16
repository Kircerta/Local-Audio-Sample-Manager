# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['LMA_GUI.py'],
    pathex=[],
    binaries=[('/Users/kircerta/PycharmProjects/LocalAudioSampleManager/.venv/lib/python3.13/site-packages/pygame/_sdl2/*.so', 'pygame/_sdl2'), ('/opt/homebrew/opt/libsndfile/lib/libsndfile.dylib', '.')],
    datas=[],
    hiddenimports=[],
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
    name='SampleManager',
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
    icon=['LMA.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SampleManager',
)
app = BUNDLE(
    coll,
    name='SampleManager.app',
    icon='LMA.icns',
    bundle_identifier=None,
)
