"""
Storage module for personal diary application.
Handles reading and writing diary entries.
"""

import os
import sys
import shutil
import datetime
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from pathlib import Path
from diary.crypto import CryptoManager, DecryptionError


class EntryStorage:
    def __init__(self, crypto_manager=None, data_file=".diary_data"):
        self.crypto_manager = crypto_manager or CryptoManager()

        # Resolve path for the data file
        self.data_file = self._resolve_data_file_path(data_file)

        # Check if migration is needed
        self._check_migration()

    def _resolve_data_file_path(self, data_file):
        """Resolve the path for the data file, similar to how CryptoManager resolves key paths."""
        # If the crypto manager exists, store data in the same directory as the key
        key_dir = os.path.dirname(self.crypto_manager.key_path)
        if key_dir:
            data_path = os.path.join(key_dir, data_file)
            return data_path

        # Check if running as a frozen app (PyInstaller)
        if getattr(sys, "frozen", False):
            # When running as bundled app, use app-specific directories
            if sys.platform == "darwin":  # macOS
                app_support = os.path.join(
                    str(Path.home()), "Library", "Application Support", "PersonalDiary"
                )
                os.makedirs(app_support, exist_ok=True)
                return os.path.join(app_support, data_file)
            elif sys.platform == "win32":  # Windows
                app_data = os.environ.get("APPDATA", "")
                if app_data:
                    app_dir = os.path.join(app_data, "PersonalDiary")
                    os.makedirs(app_dir, exist_ok=True)
                    return os.path.join(app_dir, data_file)

        # Fallback to current directory
        return os.path.abspath(data_file)

    def _check_migration(self):
        """Check if we need to migrate from old files to new hidden files."""
        # Check if the old data file exists but the new one doesn't
        if os.path.exists("diary_entries.txt") and not os.path.exists(self.data_file):
            try:
                self._migrate_old_entries()
            except Exception as e:
                messagebox.showerror(
                    "Migration Error", f"Failed to migrate old entries: {str(e)}"
                )

    def _migrate_old_entries(self):
        """Migrate entries from old plaintext file to new encrypted format."""
        if not messagebox.askyesno(
            "Migrate Data",
            "Old diary entries found. Would you like to migrate them to the new encrypted format?",
        ):
            return

        try:
            # Read old entries
            with open("diary_entries.txt", "r") as file:
                old_entries = file.read().split("\n--- Entry on ")

            # Process and save each entry
            for i, entry in enumerate(old_entries):
                if i == 0 and not entry.startswith("--- Entry on "):
                    # Skip initial content if it doesn't start with an entry header
                    continue

                if i > 0:
                    # Add the header part back for all but the first entry
                    entry = "--- Entry on " + entry

                # Extract date and content
                lines = entry.split("\n")
                header = lines[0]
                content = "\n".join(lines[1:])

                # Get date from header, default to "Unknown" if not found
                date = "Unknown"
                if "--- Entry on " in header:
                    date = header.replace("--- Entry on ", "").replace(" ---", "")

                # Save in new encrypted format
                self.save_entry(content, "😐 Neutral", date)

            # Backup old file
            os.rename("diary_entries.txt", "diary_entries.txt.bak")
            messagebox.showinfo(
                "Migration Successful",
                "Your diary entries have been migrated to the new encrypted format.\n"
                "The original file has been backed up as 'diary_entries.txt.bak'.",
            )
        except Exception as e:
            raise StorageError(f"Failed to migrate entries: {str(e)}")

    def save_entry(self, content, mood, date=None):
        """Encrypt and save a diary entry."""
        if not content.strip():
            return False

        try:
            # Make sure the directory exists
            data_dir = os.path.dirname(os.path.abspath(self.data_file))
            os.makedirs(data_dir, exist_ok=True)

            date = date or datetime.datetime.now().strftime("%B %d, %Y")
            entry_with_metadata = f"--- Entry on {date} | Mood: {mood} ---\n{content}"
            encrypted_entry = self.crypto_manager.encrypt(entry_with_metadata)

            with open(self.data_file, "a") as file:
                file.write(encrypted_entry + "\n")

            # Set secure permissions for the data file
            if os.name != "nt":  # Skip on Windows
                try:
                    import stat

                    os.chmod(self.data_file, stat.S_IRUSR | stat.S_IWUSR)
                except Exception as e:
                    print(f"Warning: Could not set permissions on data file: {str(e)}")

            return True
        except Exception as e:
            print(f"Error saving entry: {str(e)}")
            raise StorageError(f"Failed to save entry: {str(e)}")

    def read_entries(self):
        """Read and decrypt all diary entries."""
        entries = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as file:
                    encrypted_entries = file.readlines()

                    # Check if there are entries that can't be decrypted
                    if encrypted_entries and not self._can_decrypt_any(
                        encrypted_entries
                    ):
                        # Look for backup or original key files
                        key_options = []

                        # Check for common key file names
                        for key_file in [
                            "key.key",
                            "key.key.bak",
                            "key.key.backup",
                            ".key.key.bak",
                        ]:
                            if os.path.exists(key_file):
                                key_options.append(key_file)

                        if key_options:
                            selected_key = self._show_key_recovery_dialog(key_options)
                            if selected_key:
                                # Backup current key before replacing it
                                if os.path.exists(".key.key"):
                                    shutil.copy(".key.key", ".key.key.previous")

                                # Copy the selected key to the active key location
                                shutil.copy(selected_key, ".key.key")
                                messagebox.showinfo(
                                    "Key Restored",
                                    f"Encryption key has been restored from {selected_key}. "
                                    "The application will now restart to apply the changes.",
                                )

                                # Restart the application
                                python = sys.executable
                                os.execl(python, python, *sys.argv)
                                return []  # This line won't be reached due to restart
                        else:
                            # No key options found, ask if they want to create a new key
                            if messagebox.askyesno(
                                "Decryption Failed",
                                "Your diary entries cannot be decrypted with the current key, "
                                "and no backup keys were found.\n\n"
                                "Would you like to create a backup of your encrypted entries "
                                "before continuing? (Recommended)",
                            ):
                                # Create backup of encrypted entries
                                self._backup_encrypted_entries()

                    # Try to decrypt each entry
                    decryption_failures = 0
                    for encrypted_entry in encrypted_entries:
                        if encrypted_entry.strip():
                            try:
                                decrypted_entry = self.crypto_manager.decrypt(
                                    encrypted_entry.strip()
                                )
                                entries.append(decrypted_entry)
                            except Exception:
                                decryption_failures += 1
                                continue

                    # Alert if there were decryption failures
                    if decryption_failures > 0 and decryption_failures == len(
                        encrypted_entries
                    ):
                        # All entries failed to decrypt
                        messagebox.showwarning(
                            "Decryption Failed",
                            f"Failed to decrypt any diary entries. The encryption key may have changed.\n"
                            f"Total entries failed: {decryption_failures}\n\n"
                            f"To resolve this, find your original key.key file and place it in this folder.",
                        )
                    elif decryption_failures > 0:
                        # Some entries failed
                        messagebox.showwarning(
                            "Partial Decryption",
                            f"Some diary entries could not be decrypted and have been skipped.\n"
                            f"Entries loaded: {len(entries)}, Entries skipped: {decryption_failures}",
                        )

            except Exception as e:
                raise StorageError(f"Failed to read diary entries: {str(e)}")
        return entries

    def _show_key_recovery_dialog(self, key_options):
        """Show a dialog to let the user select which key to recover from."""
        dialog = tk.Toplevel()
        dialog.title("Recover Encryption Key")
        dialog.geometry("500x300")
        dialog.configure(bg="#f5f5f5")
        dialog.grab_set()  # Make dialog modal

        # Create a main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add a label
        ttk.Label(
            main_frame,
            text="Your diary entries cannot be decrypted with the current key.\n"
            "Select a key file to restore:",
            justify=tk.CENTER,
        ).pack(pady=10)

        # Create a listbox for the key options
        key_listbox = tk.Listbox(
            main_frame,
            font=("Helvetica", 11),
            selectbackground="#b3d9ff",
            selectmode=tk.SINGLE,
            height=len(key_options) + 1,
        )
        key_listbox.pack(fill=tk.X, pady=10)

        # Add the key options to the listbox
        for key_file in key_options:
            key_listbox.insert(tk.END, key_file)

        # Add explanation label
        ttk.Label(
            main_frame,
            text="The selected key will replace your current encryption key.\n"
            "Your current key will be backed up as .key.key.previous",
            justify=tk.CENTER,
        ).pack(pady=10)

        # Add button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        selected_key = [
            None
        ]  # List to store the selected key (using list for mutable reference)

        # Function to handle key selection
        def select_key():
            selection = key_listbox.curselection()
            if selection:
                selected_key[0] = key_options[selection[0]]
                dialog.destroy()

        # Add buttons
        ttk.Button(
            button_frame, text="Use Selected Key", command=select_key, width=20
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=20).pack(
            side=tk.RIGHT, padx=10
        )

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry("{}x{}+{}+{}".format(width, height, x, y))

        # Wait for dialog to close
        dialog.wait_window()

        return selected_key[0]

    def _backup_encrypted_entries(self):
        """Create a backup of the encrypted entries."""
        if os.path.exists(self.data_file):
            backup_file = f"{self.data_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy(self.data_file, backup_file)
                messagebox.showinfo(
                    "Backup Created",
                    f"A backup of your encrypted entries has been created at:\n{backup_file}",
                )
                return True
            except Exception as e:
                messagebox.showerror(
                    "Backup Failed", f"Failed to create backup: {str(e)}"
                )
                return False
        return False

    def _can_decrypt_any(self, encrypted_entries):
        """Test if any entries can be decrypted with the current key."""
        for entry in encrypted_entries:
            if not entry.strip():
                continue
            try:
                self.crypto_manager.decrypt(entry.strip())
                return True  # Successfully decrypted one entry
            except:
                continue
        return False  # Couldn't decrypt any entries

    def delete_entry(self, entry_to_delete):
        """Delete a specific entry."""
        try:
            entries = self.read_entries()
            entries = [entry for entry in entries if entry != entry_to_delete]
            return self.rewrite_entries(entries)
        except Exception as e:
            raise StorageError(f"Failed to delete entry: {str(e)}")

    def delete_entries_by_date(self, date_str):
        """Delete all entries for a specific date."""
        try:
            entries = self.read_entries()
            filtered_entries = []

            for entry in entries:
                try:
                    header_line = entry.split("\n")[0]
                    entry_date = (
                        header_line.split("|")[0].replace("--- Entry on ", "").strip()
                    )
                    if entry_date != date_str:
                        filtered_entries.append(entry)
                except:
                    # If we can't parse the date, keep the entry
                    filtered_entries.append(entry)

            return self.rewrite_entries(filtered_entries)
        except Exception as e:
            raise StorageError(f"Failed to delete entries by date: {str(e)}")

    def rewrite_entries(self, entries):
        """Rewrite all entries to the file (used after deletion)."""
        try:
            with open(self.data_file, "w") as file:
                for entry in entries:
                    encrypted_entry = self.crypto_manager.encrypt(entry)
                    file.write(encrypted_entry + "\n")
            return True
        except Exception as e:
            raise StorageError(f"Failed to rewrite entries: {str(e)}")

    def export_entries(self, export_file):
        """Export all entries to a plain text file."""
        try:
            entries = self.read_entries()
            with open(export_file, "w") as destination:
                for entry in entries:
                    destination.write(entry + "\n\n")
            return True
        except Exception as e:
            raise StorageError(f"Failed to export entries: {str(e)}")

    def organize_entries_by_date(self):
        """Organize all entries by date."""
        entries_by_date = {}
        entries = self.read_entries()

        for entry in entries:
            try:
                header_line = entry.split("\n")[0]
                date_str = (
                    header_line.split("|")[0].replace("--- Entry on ", "").strip()
                )

                if date_str in entries_by_date:
                    entries_by_date[date_str].append(entry)
                else:
                    entries_by_date[date_str] = [entry]
            except:
                # If entry doesn't have expected format, skip it
                continue

        return entries_by_date


class StorageError(Exception):
    """Exception raised when storage operations fail."""

    pass
