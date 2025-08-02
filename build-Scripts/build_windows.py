#!/usr/bin/env python3
"""
Build script for creating signed Windows executable
"""
import subprocess
import sys
import os
from pathlib import Path
import argparse

def build_windows(sign_exe=False, cert_path=None, cert_password=None):
    """Build Windows executable using PyInstaller"""

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    cmd = [
        "python", "-m", "PyInstaller",
        "--name=PlantUML2DrawIO",
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",
        "--paths=src",
        "--add-data=src/plantuml2drawio;plantuml2drawio",
        "--hidden-import=plantuml2drawio",
        "--icon=resources/icons/p2d_icon.ico",
        "--distpath=dist/windows",
        "src/plantuml2drawio/app.py"
    ]

    print("Building Windows executable...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")

        exe_path = Path("dist/windows/PlantUML2Drawio.exe")
        print(f"Executable created: {exe_path}")

        if sign_exe and cert_path:
            sign_executable(exe_path, cert_path, cert_password)
        elif sign_exe:
            print("Warning: Code signing requested but no certificate path provided")

    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)

def sign_executable(exe_path, cert_path, cert_password=None):
    """Sign the Windows executable with a code signing certificate"""
    print(f"Signing executable: {exe_path}")

    sign_cmd = [
        "signtool.exe", "sign",
        "/f", str(cert_path),
        "/fd", "SHA256",
        "/tr", "http://timestamp.digicert.com",
        "/td", "SHA256",
        "/v",
        str(exe_path)
    ]

    if cert_password:
        sign_cmd.extend(["/p", cert_password])

    try:
        result = subprocess.run(sign_cmd, check=True, capture_output=True, text=True)
        print("Code signing succesful")
        print(result.stdout)

    
    except subprocess.CalledProcessError as e:
        print(f"Code signing failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        print("\nNote: Make sure you have:")
        print("1. Windows SDK installed (for signtool.exe)")
        print("2. Valid code signing certificate")
        print("3. Certificate is in the correct format (.p12/.pfx)")

def verify_signature(exe_path):
    """Verify the digital signature of the executable"""
    print("Verifying digital signature...")
    
    verify_cmd = [
        "signtool.exe", "verify",
        "/pa",  # Use default authentication verification policy
        "/v",   # Verbose output
        str(exe_path)
    ]
    
    try:
        result = subprocess.run(verify_cmd, check=True, capture_output=True, text=True)
        print("Signature verification successful!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Signature verification failed: {e}")

def create_installer():
    """Create Windows installer using NSIS (if available)"""
    print("Creating Windows installer...")
    
    # This would require an NSIS script
    nsis_script = Path("build_scripts/installer.nsi")
    if nsis_script.exists():
        installer_cmd = ["makensis", str(nsis_script)]
        try:
            subprocess.run(installer_cmd, check=True)
            print("Installer created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Installer creation failed: {e}")
    else:
        print("NSIS script not found. Skipping installer creation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Windows executable")
    parser.add_argument("--sign", action="store_true", help="Sign the executable")
    parser.add_argument("--cert", help="Path to code signing certificate (.p12/.pfx)")
    parser.add_argument("--password", help="Certificate password")
    parser.add_argument("--installer", action="store_true", help="Create installer")
    
    args = parser.parse_args()
    
    build_windows(args.sign, args.cert, args.password)
    
    if args.installer:
        create_installer() 
