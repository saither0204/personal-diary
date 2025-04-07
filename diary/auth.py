"""
Authentication module for personal diary application.
Handles user authentication and password management.
"""

import os
import hashlib
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox

from diary.crypto import CryptoManager, DecryptionError


class AuthManager:
    def __init__(self, crypto_manager=None, password_file=".password.txt"):
        self.password_file = password_file
        self.crypto_manager = crypto_manager or CryptoManager()

    def authenticate(self, parent):
        """Prompt for password and authenticate user."""
        password = simpledialog.askstring(
            "Password", "Enter the password:", show="*", parent=parent
        )
        if password is None:  # User clicked cancel
            return False

        try:
            stored_password = self.load_password()
            return password == stored_password
        except Exception as e:
            messagebox.showerror(
                "Authentication Error", f"Error during authentication: {str(e)}"
            )
            return False

    def load_password(self):
        """Load and decrypt the password from file."""
        if os.path.exists(self.password_file):
            try:
                with open(self.password_file, "r") as file:
                    encrypted_password = file.read().strip()
                return self.crypto_manager.decrypt(encrypted_password)
            except DecryptionError:
                messagebox.showerror(
                    "Error", "Password file is corrupted. Please reset the password."
                )
                self.reset_password(None)  # None because we don't have parent yet
                return self.load_password()
        return "mypassword"  # Default password

    def set_initial_password(self, parent):
        """Set the initial password if not already set."""
        if not os.path.exists(self.password_file):
            while True:
                new_password = simpledialog.askstring(
                    "Set Password", "Enter a new password:", show="*", parent=parent
                )
                if new_password is None:  # User clicked cancel
                    return False

                confirm_password = simpledialog.askstring(
                    "Confirm Password",
                    "Retype the new password:",
                    show="*",
                    parent=parent,
                )
                if new_password == confirm_password and new_password:
                    self.save_password(new_password)
                    messagebox.showinfo(
                        "Success", "Password has been set successfully!"
                    )
                    return True
                else:
                    messagebox.showerror(
                        "Error", "Passwords do not match. Please try again."
                    )
        return True

    def reset_password(self, parent):
        """Reset the user's password."""
        new_password = simpledialog.askstring(
            "Reset Password", "Enter a new password:", show="*", parent=parent
        )
        if new_password:
            self.save_password(new_password)
            messagebox.showinfo("Success", "Password has been reset successfully!")
            return True
        return False

    def save_password(self, password):
        """Encrypt and save the password to file."""
        encrypted_password = self.crypto_manager.encrypt(password)
        with open(self.password_file, "w") as file:
            file.write(encrypted_password)
