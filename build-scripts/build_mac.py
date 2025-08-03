#!/usr/bin/env python3
"""
Build script for creating amacOS (.app) bundle
Run this *on macOS* - PyInstaller cannot cross-compile
"""
import subprocess
import sys
import os
import platform
from pathlib import Path
import argparse
import shutil
import tempfile

def build_mac(codesign=False, identity=None, entitlements=None, notarize=False, team_id=None, apple_id=None, asc_password=None):
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    dist_dir = project_root / "dist" / "mac"
    build_dir = project_root / "build" / "mac"

    shutil.rmtree(dist_dir, ignore_errors=True)
    shutil.rmtree(build_dir, ignore_errors=True)

    cmd = [
        "python", "-m", "PyInstaller",
        "--name=PlantUML2DrawIO",
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",
        "--paths=src",
        "--add-data=src/plantuml2drawio:plantuml2drawio",
        "--hidden-import=plantuml2drawio",
        "--icon=resources/icons/p2d_icon.icns",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "src/plantuml2drawio/app.py"
    ]

    print("Building macOS application bundle…")
    print("Command:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        app_path = dist_dir / "PlantUML2DrawIO.app"
        print(f"Built: {app_path}")

        # Set execute permissions on the executable
        executable_path = app_path / "Contents" / "MacOS" / "PlantUML2DrawIO"
        if executable_path.exists():
            os.chmod(executable_path, 0o755)
            print(f"Set execute permissions on: {executable_path}")

        if codesign:
            sign_app(app_path, identity, entitlements)
            if notarize:
                notarize_app(app_path, team_id, apple_id, asc_password)

    except subprocess.CalledProcessError as e:
        print("Build failed")
        print(e.stdout or "", e.stderr or "")
        sys.exit(1)

def sign_app(app_path, identity, entitlements=None):
    """Code-sign the .app so Gatekeeper lets it run on other Macs."""
    if not identity:
        print("--codesign supplied but no --identity given; skipping codesign.")
        return
    cmd = [
        "codesign", "--deep", "--force",
        "--options", "runtime",
        "--sign", identity,
        str(app_path)
    ]
    if entitlements:
        cmd.extend(["--entitlements", str(entitlements)])

    print("Signing…")
    subprocess.run(cmd, check=True)
    print("Signed")

def notarize_app(app_path, team_id, apple_id, asc_password):
    """Submit the .app (zipped) to Apple notarization and staple the ticket."""
    if not (team_id and apple_id and asc_password):
        print("⚠️  --notarize needs --team-id, --apple-id and --asc-password.")
        return

    zip_path = Path(tempfile.gettempdir()) / (app_path.stem + ".zip")
    shutil.make_archive(zip_path.with_suffix(""), 'zip', root_dir=app_path)
    print("Uploading to Apple notarization service…")

    submit = [
        "xcrun", "notarytool",
        "submit", str(zip_path),
        "--team-id", team_id,
        "--apple-id", apple_id,
        "--password", asc_password,
        "--wait"              # waits until approval / failure
    ]
    subprocess.run(submit, check=True)

    print("Stapling ticket…")
    subprocess.run(["xcrun", "stapler", "staple", str(app_path)], check=True)
    print("Notarized & stapled")

if __name__ == "__main__":
    if platform.system() != "Darwin":
        sys.exit("⚠️  This script must be run on macOS (Darwin).")

    p = argparse.ArgumentParser(description="Build macOS .app bundle")
    p.add_argument("--codesign", action="store_true",
                   help="Code-sign the resulting .app")
    p.add_argument("--identity",  help="Developer ID Application identity")
    p.add_argument("--entitlements", help="Path to entitlements.plist")
    p.add_argument("--notarize", action="store_true",
                   help="After signing, notarize the app with Apple")
    p.add_argument("--team-id",     help="Apple Team ID (10 chars)")
    p.add_argument("--apple-id",    help="Apple ID used for notarization")
    p.add_argument("--asc-password",help="App-specific password or keychain item")

    args = p.parse_args()
    build_mac(args.codesign, args.identity, args.entitlements,
              args.notarize, args.team_id, args.apple_id, args.asc_password)
