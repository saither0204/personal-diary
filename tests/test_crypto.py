"""
Basic tests for the personal diary application.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to sys.path to allow importing diary modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from diary.crypto import CryptoManager


def test_crypto_manager_init():
    """Test that CryptoManager can be initialized."""
    crypto = CryptoManager(check_key_exists=False)
    assert crypto is not None


def test_crypto_key_generation():
    """Test key generation and encryption/decryption."""
    # Use a temporary path for the key
    temp_key_path = "temp_test_key.key"

    try:
        # Create a crypto manager with no key checking
        crypto = CryptoManager(key_path=temp_key_path, check_key_exists=False)

        # Generate a new key
        key = crypto.generate_key()
        assert key is not None
        assert len(key) == 44  # Fernet key is 32 bytes, base64 encoded

        # Test encryption and decryption
        original_text = "Test encryption and decryption"
        encrypted = crypto.encrypt(original_text)
        decrypted = crypto.decrypt(encrypted)

        assert encrypted != original_text
        assert decrypted == original_text
    finally:
        # Clean up the temporary key file
        if os.path.exists(temp_key_path):
            os.remove(temp_key_path)


def test_path_resolution():
    """Test that path resolution works correctly."""
    crypto = CryptoManager(check_key_exists=False)
    key_path = crypto._resolve_path("test.key")

    # Path should be an absolute path
    assert os.path.isabs(key_path)
