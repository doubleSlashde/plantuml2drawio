# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import glob
import site
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Current directory
current_dir = os.path.dirname(os.path.abspath('p2dapp.py'))

# Get site-packages directory - trying both potential locations
site_packages = None
for sp in site.getsitepackages():
    if os.path.exists(sp):
        site_packages = sp
        break

if not site_packages:
    # Fallback to the one from the Python Store app if detectable
    store_site_packages = os.path.expanduser(r"~\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages")
    if os.path.exists(store_site_packages):
        site_packages = store_site_packages

# Manually add customtkinter files
customtkinter_datas = []
if site_packages:
    customtkinter_dir = os.path.join(site_packages, 'customtkinter')
    if os.path.exists(customtkinter_dir):
        # Add the entire customtkinter directory
        for root, dirs, files in os.walk(customtkinter_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, site_packages)
                target_dir = os.path.dirname(rel_path)
                customtkinter_datas.append((full_path, target_dir))

# Tcl/Tk data
tk_datas = []
# Try to locate and include specific Tcl/Tk directories
for base_dir in [sys.base_prefix, site_packages]:
    for tcl_dir in ['tcl', 'Tcl']:
        tcl_tk_dir = os.path.join(base_dir, tcl_dir, 'tcl8.6')
        if os.path.exists(tcl_tk_dir):
            tk_datas.append((tcl_tk_dir, './tcl/tcl8.6'))
        
        tcl_tk_dir = os.path.join(base_dir, tcl_dir, 'tk8.6')
        if os.path.exists(tcl_tk_dir):
            tk_datas.append((tcl_tk_dir, './tcl/tk8.6'))

# Additional CustomTkinter theme data
for theme_dir in glob.glob(os.path.join(site_packages, 'customtkinter', 'assets', '*')):
    if os.path.isdir(theme_dir):
        theme_name = os.path.basename(theme_dir)
        target_dir = os.path.join('customtkinter', 'assets', theme_name)
        tk_datas.append((theme_dir, target_dir))

# Add any customtkinter submodules we can find
customtkinter_imports = []
if os.path.exists(os.path.join(site_packages, 'customtkinter')):
    for item in os.listdir(os.path.join(site_packages, 'customtkinter')):
        if os.path.isdir(os.path.join(site_packages, 'customtkinter', item)) and not item.startswith('__'):
            customtkinter_imports.append(f'customtkinter.{item}')
            # Also add submodules
            for subitem in os.listdir(os.path.join(site_packages, 'customtkinter', item)):
                if subitem.endswith('.py') and not subitem.startswith('__'):
                    submodule = subitem[:-3]  # Remove .py extension
                    customtkinter_imports.append(f'customtkinter.{item}.{submodule}')

# Add p2dcore.py as a module
a = Analysis(
    ['p2dapp.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        *customtkinter_datas,  # Add customtkinter data files
        *tk_datas,            # Add tcl/tk data
        ('p2dapp_icon.ico', '.'),  # Include the icon file
        ('p2dapp_icon.png', '.'),  # Include the PNG icon for cross-platform support
        ('p2dcore.py', '.'),  # Include core module explicitly
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        're',  # include regex module
        'p2dcore',  # include our core module
        'xml.etree.ElementTree',
        'darkdetect',  # required by customtkinter
        *customtkinter_imports,  # Add all discovered customtkinter submodules
    ],
    hookspath=[current_dir],  # Look for hooks in current directory
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
    name='p2dapp_win',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='p2dapp_icon.ico'
)
