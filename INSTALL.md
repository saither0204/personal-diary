# Personal Diary - Installation Guide

This document explains how to install the Personal Diary application on your computer.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- macOS, Windows, or Linux

## Installation Methods

There are two ways to install the Personal Diary application:

### Method 1: Using the Bundled Application (Recommended for regular users)

This method creates a standalone application that doesn't require Python to be installed.

1. Open Terminal
2. Navigate to the project directory:

   ```plaintext
   cd /path/to/personal-diary
   ```

3. Run the build script:

   ```plaintext
   ./build_app.py
   ```

4. The script will:
   - Install required dependencies (PyInstaller, cryptography)
   - Set proper permissions for sensitive files
   - Create an application bundle in the `dist` folder

5. Once complete, you can find the application at:
   - macOS: `dist/PersonalDiary.app`
   - Windows: `dist/PersonalDiary.exe`
   - Linux: `dist/PersonalDiary`

6. To install on macOS:
   - Copy `PersonalDiary.app` to your Applications folder
   - Right-click and select "Open" the first time (to bypass Gatekeeper)

### Method 2: Using pip (For developers)

1. Open Terminal
2. Navigate to the project directory:

   ```plaintext
   cd /path/to/personal-diary
   ```

3. Install using pip:

   ```plaintext
   pip install -e .
   ```

   Or to install for all users (requires admin privileges):

   ```plaintext
   sudo pip install -e .
   ```

4. Once installed, you can run the application by typing:

   ```plaintext
   personal-diary
   ```

## Security Notes

- The application uses two hidden files for security:
  - `.key.key`: Encryption key
  - `.password.txt`: Encrypted password storage

- These files are automatically set with secure permissions (600) during the build process

## Custom Icon

To use a custom icon:

1. Create a `.icns` file (for macOS) or `.ico` file (for Windows)
2. Name it `app_icon.icns` (or `app_icon.ico` on Windows)
3. Place it in the project root directory
4. Run the build script again

## Troubleshooting

If you encounter any issues:

- Make sure Python 3.6+ is installed and in your PATH
- Verify you have write permissions in the project directory
- Check that the cryptography package is properly installed
- On macOS, if the app won't open, try:

  ```plaintext
  xattr -cr /Applications/PersonalDiary.app
  ```

## Uninstallation

- For the bundled app: Simply delete the application
- For pip installation:

  ```plaintext
  pip uninstall personal-diary
  ```
