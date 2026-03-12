# -*- mode: python ; coding: utf-8 -*-
# POS System - PyInstaller Spec File
# Includes libusb DLL and all escpos/usb dependencies for USB printer support

import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all escpos and usb packages
escpos_datas, escpos_binaries, escpos_hiddenimports = collect_all('escpos')
usb_datas, usb_binaries, usb_hiddenimports = collect_all('usb')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[
        # Include libusb DLL from System32
        ('C:\\Windows\\System32\\libusb-1.0.dll', '.'),
        *escpos_binaries,
        *usb_binaries,
    ],
    datas=[
        # Include your project folders
        ('views', 'views'),
        ('controllers', 'controllers'),
        ('database', 'database'),
        ('settings.py', '.'),
        *escpos_datas,
        *usb_datas,
    ],
    hiddenimports=[
        # USB / printer
        'usb',
        'usb.core',
        'usb.util',
        'usb.backend',
        'usb.backend.libusb1',
        'usb.backend.libusb0',
        'usb.backend.openusb',
        'libusb_package',
        'escpos',
        'escpos.printer',
        'escpos.escpos',
        'escpos.constants',
        'escpos.exceptions',
        'escpos.image',
        'escpos.capabilities',
        # PDF / barcode
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.colors',
        'barcode',
        'barcode.writer',
        'PIL',
        'PIL.Image',
        # CustomTkinter
        'customtkinter',
        # Other
        'sqlite3',
        'io',
        'os',
        'sys',
        *escpos_hiddenimports,
        *usb_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='L&L Inventory Management System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # No console window (windowed mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',   # Uncomment and set path if you have an icon
)
