# -*- mode: python ; coding: utf-8 -*-
# PRODUCTION SPEC FILE

block_cipher = None

a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=[('../assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
#splash = Splash(
#    '../application_files/intrasect_white_bg.png',
#    binaries=a.binaries,
#    datas=a.datas,
#    text_pos=None,
#    text_size=12,
#    minify_script=True,
#    always_on_top=True,
#)

exe = EXE(
    pyz,
    a.scripts,
    #splash,
    [],
    exclude_binaries=True,
    name='Otto Cycle Calculator',
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
    icon=['..\\assets\\Trine.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    #splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Otto Cycle Calculator',
)