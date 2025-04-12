#!/usr/bin/env python3
"""
Build script for Personal Diary application.
Creates a standalone executable package using PyInstaller.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import stat

APP_NAME = "Personal Diary"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "diary_app.py"
ICON_FILE = "app_icon.icns"  # We'll create this later


def setup_environment():
    """Check and install dependencies, set file permissions."""
    print("Setting up build environment...")

    # Check if PyInstaller is installed
    try:
        import PyInstaller

        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    # Check if cryptography is installed
    try:
        import cryptography

        print("Cryptography library is already installed.")
    except ImportError:
        print("Installing cryptography library...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "cryptography"], check=True
        )

    # Set appropriate permissions for sensitive files if they exist
    key_file = ".key.key"
    password_file = ".password.txt"

    for file_path in [key_file, password_file]:
        if os.path.exists(file_path):
            print(f"Setting secure permissions for {file_path}")
            # 0o600 = owner can read and write, no permissions for group or others
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)


def create_temp_icon():
    """Create a simple icon file for the application if not present."""
    if os.path.exists(ICON_FILE):
        print(f"Icon file {ICON_FILE} already exists, using existing file.")
        return

    print("Icon file not found. Creating a simple icon...")
    try:
        # Create a simple text file to explain how to add a custom icon
        with open("icon_instructions.txt", "w") as f:
            f.write(
                f"""
To use a custom icon for your {APP_NAME} application:

1. Create a .icns file (macOS) or .ico file (Windows)
2. Name it '{ICON_FILE}' and place it in the same directory as this build script
3. Run the build script again

For macOS, you can convert images to .icns using tools like:
- iconutil (command line)
- Image2Icon (GUI application)
- Online converters like https://iconverticons.com/
            """
            )

        print("Created icon_instructions.txt with guidance on adding a custom icon.")
        print("Using default PyInstaller icon for now.")
    except Exception as e:
        print(f"Warning: Failed to create icon instructions: {str(e)}")


def build_app():
    """Build the application using PyInstaller."""
    print(f"Building {APP_NAME} {APP_VERSION}...")

    # Create a temporary icon if needed
    create_temp_icon()

    # Platform-specific settings
    if sys.platform == "darwin":  # macOS
        separator = ":"
        bundle_type = "--onedir"  # Create a directory-based app bundle on macOS
    else:  # Windows/Linux
        separator = ";" if sys.platform == "win32" else ":"
        bundle_type = "--onefile"  # Create a single executable on Windows/Linux

    # Basic PyInstaller command
    cmd = [
        "pyinstaller",
        "--name",
        APP_NAME.replace(" ", ""),
        "--noconfirm",
        "--clean",
        "--windowed",  # Create a windowed application (no console)
        bundle_type,
        "--add-data",
        f"diary{separator}diary",  # Include the diary package
    ]

    # Add icon if available
    if os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])

    # Add main script
    cmd.append(MAIN_SCRIPT)

    # Run PyInstaller
    print("Running PyInstaller with command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Additional steps for macOS
    if sys.platform == "darwin":
        # The .app package is created in dist folder
        app_path = os.path.join("dist", f"{APP_NAME.replace(' ', '')}.app")

        if os.path.exists(app_path):
            print(f"Successfully created {app_path}")
            print(f"\nTo install {APP_NAME}:")
            print(f"1. Copy {app_path} to your Applications folder")
            print(
                "2. You may need to right-click and select 'Open' the first time to bypass Gatekeeper"
            )
    else:
        # For Windows/Linux, the executable is in the dist folder
        exe_path = os.path.join("dist", APP_NAME.replace(" ", ""))
        if os.path.exists(exe_path) or os.path.exists(exe_path + ".exe"):
            print(f"Successfully created executable in {os.path.abspath('dist')}")
            print(f"\nTo run {APP_NAME}, simply double-click the executable file.")


if __name__ == "__main__":
    # Make sure setup is done before building
    setup_environment()
    build_app()
