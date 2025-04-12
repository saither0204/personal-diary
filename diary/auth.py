"""
Authentication module for personal diary application.
Handles user authentication and password management.
"""

import os
import sys
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
from pathlib import Path

from diary.crypto import CryptoManager, DecryptionError


class AuthManager:
    def __init__(self, crypto_manager=None, password_file=".password.txt"):
        self.crypto_manager = crypto_manager or CryptoManager()
        self.parent = None  # Will be set when authenticate is called

        # Resolve path to password file
        self.password_file = self._resolve_path(password_file)

    def _resolve_path(self, file_path):
        """Resolve the path to find the file in various possible locations."""
        # If key_path exists, use the same directory for the password file
        key_dir = os.path.dirname(self.crypto_manager.key_path)
        if key_dir:
            pwd_path = os.path.join(key_dir, os.path.basename(file_path))
            if os.path.exists(pwd_path):
                return pwd_path
            # Even if it doesn't exist yet, use this path for consistency
            return pwd_path

        # Check if it's an absolute path
        if os.path.isabs(file_path):
            return file_path

        # Check if running as a frozen app (PyInstaller)
        if getattr(sys, "frozen", False):
            # When running as bundled app, use the same approach as CryptoManager
            if sys.platform == "darwin":  # macOS
                app_support = os.path.join(
                    str(Path.home()), "Library", "Application Support", "PersonalDiary"
                )
                os.makedirs(app_support, exist_ok=True)
                app_path = os.path.join(app_support, file_path)
                if os.path.exists(app_path):
                    return app_path
                return app_path  # Return this path even if it doesn't exist yet

            elif sys.platform == "win32":  # Windows
                app_data = os.environ.get("APPDATA", "")
                if app_data:
                    app_dir = os.path.join(app_data, "PersonalDiary")
                    os.makedirs(app_dir, exist_ok=True)
                    app_path = os.path.join(app_dir, file_path)
                    if os.path.exists(app_path):
                        return app_path
                    return app_path  # Return this path even if it doesn't exist

        # Basic checks for standard Python app
        # Check current directory
        if os.path.exists(file_path):
            return os.path.abspath(file_path)

        # Check in user's home directory
        home_path = os.path.join(str(Path.home()), file_path)
        if os.path.exists(home_path):
            return home_path

        # If we haven't found it, return the path where it should be created
        # For consistency, use the same directory as the key file if possible
        if key_dir and os.path.exists(key_dir):
            return os.path.join(key_dir, os.path.basename(file_path))

        # Fallback to current directory
        return os.path.abspath(file_path)

    def authenticate(self, parent):
        """Prompt for password and authenticate user."""
        self.parent = parent

        # First check if we need to set up an initial password
        if not os.path.exists(self.password_file):
            return self.set_initial_password(parent)

        # Otherwise prompt for existing password
        password = simpledialog.askstring(
            "Password", "Enter the password:", show="*", parent=parent
        )
        if password is None:  # User clicked cancel
            return False

        try:
            stored_password = self.load_password()
            return password == stored_password
        except FileNotFoundError:
            # If file wasn't found, prompt to create a new password
            messagebox.showinfo(
                "First Run", "Welcome! Please set up a password for your diary."
            )
            return self.set_initial_password(parent)
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
                    if not encrypted_password:
                        raise ValueError("Password file is empty")
                return self.crypto_manager.decrypt(encrypted_password)
            except DecryptionError:
                # Don't call reset_password here, just report the error
                # The UI will handle the reset process
                raise ValueError("Password file is corrupted")
            except Exception as e:
                raise ValueError(f"Failed to load password: {str(e)}")
        else:
            raise FileNotFoundError(f"Password file not found at {self.password_file}")

    def set_initial_password(self, parent):
        """Set the initial password if not already set."""
        attempt_count = 0
        max_attempts = 3

        while attempt_count < max_attempts:
            new_password = simpledialog.askstring(
                "Set Password", "Enter a new password:", show="*", parent=parent
            )
            if new_password is None:  # User clicked cancel
                # If this is initial setup and user cancels, exit the application
                if not os.path.exists(self.password_file):
                    messagebox.showinfo(
                        "Setup Cancelled",
                        "Password setup cancelled. You need to set a password to use the diary.",
                    )
                    return False
                else:
                    return False

            # Ensure password is not empty
            if not new_password:
                messagebox.showerror("Error", "Password cannot be empty")
                attempt_count += 1
                continue

            confirm_password = simpledialog.askstring(
                "Confirm Password",
                "Retype the new password:",
                show="*",
                parent=parent,
            )
            if new_password == confirm_password:
                try:
                    self.save_password(new_password)
                    messagebox.showinfo(
                        "Success",
                        f"Password has been set successfully and saved to {self.password_file}!",
                    )
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save password: {str(e)}")
                    return False
            else:
                messagebox.showerror(
                    "Error", "Passwords do not match. Please try again."
                )
                attempt_count += 1

        messagebox.showerror(
            "Error", f"Failed to set password after {max_attempts} attempts."
        )
        return False

    def reset_password(self, parent):
        """Reset the user's password."""
        if parent is None:
            # Create a temporary Tk root window if no parent provided
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
            parent = temp_root

        try:
            new_password = simpledialog.askstring(
                "Reset Password", "Enter a new password:", show="*", parent=parent
            )
            if new_password is None:  # User clicked cancel
                return False

            if not new_password:
                messagebox.showerror("Error", "Password cannot be empty")
                return False

            confirm_password = simpledialog.askstring(
                "Confirm Password",
                "Retype the new password:",
                show="*",
                parent=parent,
            )

            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return False

            self.save_password(new_password)
            messagebox.showinfo(
                "Success",
                f"Password has been reset successfully and saved to {self.password_file}!",
            )
            return True
        finally:
            # If we created a temporary root, destroy it
            if parent != self.parent and hasattr(parent, "destroy"):
                try:
                    parent.destroy()
                except:
                    pass

        return False

    def save_password(self, password):
        """Encrypt and save the password to file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.password_file)), exist_ok=True)

        encrypted_password = self.crypto_manager.encrypt(password)
        with open(self.password_file, "w") as file:
            file.write(encrypted_password)

        # Set secure permissions for the password file
        if os.name != "nt":  # Skip on Windows
            try:
                import stat

                os.chmod(self.password_file, stat.S_IRUSR | stat.S_IWUSR)
            except Exception as e:
                print(f"Warning: Could not set permissions on password file: {str(e)}")
