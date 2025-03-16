@echo off
echo ============================================================
echo Building PlantUML to Draw.io Converter for Windows 
echo ============================================================

echo Cleaning old build files...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Building executable...
python -m PyInstaller --clean p2d.spec

