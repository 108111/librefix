"""
build.py - Build LibreFix.exe

Requirements:
    pip install pyinstaller

Steps:
    1. python embed_adb.py   (embeds ADB into the app)
    2. python build.py       (creates dist/LibreFix.exe)
"""

import subprocess
import sys
import os

def build():
    # Check adb_bundle exists
    if not os.path.exists("adb_bundle.py"):
        print("❌ adb_bundle.py not found.")
        print("   Run: python embed_adb.py first")
        return

    print("Building LibreFix.exe...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "LibreFix",
        "--hidden-import", "adb_bundle",
        "librefix.py"
    ]

    # Add icon if present
    if os.path.exists("icon.ico"):
        cmd += ["--icon", "icon.ico"]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        size = os.path.getsize("dist/LibreFix") / (1024*1024)
        print(f"\nOK - Build successful!")
        print(f"   dist/LibreFix.exe ({size:.1f} MB)")
        print("\nTo release:")
        print("   git tag v1.0.0")
        print("   git push origin v1.0.0")
        print("   GitHub Actions will attach LibreFix.exe to the release automatically")
    else:
        print("\n❌ Build failed")

if __name__ == "__main__":
    build()
