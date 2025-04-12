"""
Cryptography module for personal diary application.
Handles encryption and decryption operations for secure storage.
"""

import os
import sys
import base64
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


class CryptoManager:
    def __init__(self, key_path=".key.key", check_key_exists=True):
        self.key_path = self._resolve_path(key_path)

        if check_key_exists:
            self._ensure_key_exists()

    def _resolve_path(self, key_path):
        """Resolve the path to the key file, trying multiple possible locations."""
        # If it's an absolute path, use it directly
        if os.path.isabs(key_path):
            return key_path

        # Check if running as a frozen app (PyInstaller)
        if getattr(sys, "frozen", False):
            # When running as bundled app, check for the key in the application directory
            if sys.platform == "darwin":  # macOS
                # Use the Resources directory inside the .app bundle
                bundle_dir = os.path.dirname(sys.executable)
                if ".app/Contents/MacOS" in bundle_dir:
                    resources_dir = bundle_dir.replace("MacOS", "Resources")
                    app_key_path = os.path.join(resources_dir, key_path)
                    if os.path.exists(app_key_path):
                        return app_key_path

                # Try app-specific directories in user's home
                app_support = os.path.join(
                    str(Path.home()), "Library", "Application Support", "PersonalDiary"
                )
                os.makedirs(app_support, exist_ok=True)
                app_key_path = os.path.join(app_support, key_path)
                if os.path.exists(app_key_path):
                    return app_key_path
                return app_key_path  # Return this path even if it doesn't exist yet

            elif sys.platform == "win32":  # Windows
                # Use %APPDATA% for Windows
                app_data = os.environ.get("APPDATA", "")
                if app_data:
                    app_dir = os.path.join(app_data, "PersonalDiary")
                    os.makedirs(app_dir, exist_ok=True)
                    app_key_path = os.path.join(app_dir, key_path)
                    if os.path.exists(app_key_path):
                        return app_key_path
                    return app_key_path  # Return this path even if it doesn't exist yet

        # Standard checks for non-bundled app
        # 1. Check current directory
        current_dir_path = os.path.abspath(key_path)
        if os.path.exists(current_dir_path):
            return current_dir_path

        # 2. Check user's home directory
        home_path = os.path.join(str(Path.home()), key_path)
        if os.path.exists(home_path):
            return home_path

        # 3. Check for hidden version in home directory
        hidden_home_path = os.path.join(str(Path.home()), ".personal-diary", key_path)
        if os.path.exists(hidden_home_path):
            return hidden_home_path

        # 4. If path doesn't exist anywhere, default to a writable location
        if getattr(sys, "frozen", False):
            # If bundled, use app-specific directory
            if sys.platform == "darwin":
                app_support = os.path.join(
                    str(Path.home()), "Library", "Application Support", "PersonalDiary"
                )
                os.makedirs(app_support, exist_ok=True)
                return os.path.join(app_support, key_path)
            elif sys.platform == "win32":
                app_data = os.environ.get("APPDATA", "")
                if app_data:
                    app_dir = os.path.join(app_data, "PersonalDiary")
                    os.makedirs(app_dir, exist_ok=True)
                    return os.path.join(app_dir, key_path)

        # Final fallback - use current directory
        return os.path.abspath(key_path)

    def _ensure_key_exists(self):
        """Check if encryption key exists, otherwise create it."""
        if not os.path.exists(self.key_path):
            try:
                # Try to generate a new key
                self.generate_key()
                print(f"Generated new encryption key at {self.key_path}")
            except Exception as e:
                raise FileNotFoundError(
                    f"Encryption key not found at {self.key_path} and could not be created: {str(e)}"
                )

    def load_key(self):
        """Load the encryption key from file."""
        try:
            with open(self.key_path, "rb") as key_file:
                key_data = key_file.read()
                # Validate that this is actually a valid Fernet key
                if len(key_data) != 44 and not self._is_valid_key(key_data):
                    raise ValueError("Invalid key format")
                return key_data
        except Exception as e:
            # If there's any issue loading the key, generate a new one
            print(f"Error loading key: {str(e)}. Generating new key.")
            return self.generate_key()

    def _is_valid_key(self, key):
        """Validate if the key is in correct format."""
        try:
            # A valid Fernet key is 32 bytes of base64-encoded data
            if len(key) != 44:  # 32 bytes encoded in base64 is 44 chars
                return False

            # Try to decode it
            base64.urlsafe_b64decode(key)

            # Try to initialize Fernet with it
            Fernet(key)
            return True
        except Exception:
            return False

    def generate_key(self):
        """Generate a new encryption key and save it to file."""
        key = Fernet.generate_key()

        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.key_path)), exist_ok=True)

        # Write the key to file with secure permissions
        with open(self.key_path, "wb") as key_file:
            key_file.write(key)

        # Set secure permissions (read/write only for owner)
        if os.name != "nt":  # Skip on Windows
            try:
                import stat

                os.chmod(self.key_path, stat.S_IRUSR | stat.S_IWUSR)
            except Exception as e:
                print(f"Warning: Could not set permissions on key file: {str(e)}")

        return key

    def encrypt(self, data):
        """Encrypt the given data."""
        key = self.load_key()
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        """Decrypt the given encrypted data."""
        key = self.load_key()
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()

    def try_decrypt(self, encrypted_data):
        """Attempt to decrypt data and handle exceptions."""
        try:
            return self.decrypt(encrypted_data)
        except (InvalidToken, ValueError) as e:
            raise DecryptionError(
                "Failed to decrypt data. The data may be corrupted."
            ) from e


class DecryptionError(Exception):
    """Exception raised when decryption fails."""

    pass
