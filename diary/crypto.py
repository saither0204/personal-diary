"""
Cryptography module for personal diary application.
Handles encryption and decryption operations for secure storage.
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


class CryptoManager:
    def __init__(self, key_path=".key.key", check_key_exists=True):
        self.key_path = key_path
        # Convert to absolute path if it's a relative path
        if not os.path.isabs(self.key_path):
            # First check if it exists in current directory
            if os.path.exists(self.key_path):
                self.key_path = os.path.abspath(self.key_path)
            # Then check if it exists in the user's home directory
            elif os.path.exists(os.path.join(str(Path.home()), self.key_path)):
                self.key_path = os.path.join(str(Path.home()), self.key_path)

        if check_key_exists:
            self._ensure_key_exists()

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
