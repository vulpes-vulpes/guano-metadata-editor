# -*- mode: python ; coding: utf-8 -*-

import os
import re

# Read APP_VERSION out of guano_gui.py's source rather than importing the
# module: PyInstaller execs this spec file without the project directory on
# sys.path, so a real import fails with ModuleNotFoundError, and importing
# guano_gui would also pull in guano/tkinter before the build has set up its
# own dependency analysis.
with open(os.path.join(SPECPATH, 'guano_gui.py'), encoding='utf-8') as _f:
    _match = re.search(r'^APP_VERSION\s*=\s*["\'](.+?)["\']', _f.read(), re.MULTILINE)
if not _match:
    raise RuntimeError("Could not find APP_VERSION in guano_gui.py")
APP_VERSION = _match.group(1)

block_cipher = None

a = Analysis(
    ['guano_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('USER_GUIDE.md', '.'),
        ('CHANGELOG.md', '.'),
    ],
    hiddenimports=[
        'guano',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GUANO Metadata Editor',
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

# macOS-specific app bundle
app = BUNDLE(
    exe,
    name='GUANO Metadata Editor.app',
    icon=None,
    bundle_identifier='org.batacoustics.guano-editor',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'NSHumanReadableCopyright': '2026 Bat Acoustic Research Community',
    },
)