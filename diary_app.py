"""
Main application file for the personal diary.
This module ties together all components and provides the entry point.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import shutil
from pathlib import Path

from diary.crypto import CryptoManager
from diary.auth import AuthManager
from diary.storage import EntryStorage
from diary.ui.main_window import MainWindow
from diary.ui.write_tab import WriteTab
from diary.ui.view_tab import ViewAllTab
from diary.ui.date_tab import DateViewTab


class DiaryApplication:
    def __init__(self):
        # Initialize application by setting up root window first
        # This is important to prevent Toplevel errors
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window until we're fully initialized

        try:
            # First, check if we need to migrate from old to new hidden files
            self.check_and_migrate_files()

            # Initialize crypto manager first
            self.crypto_manager = CryptoManager()

            # Get the actual path being used
            key_path = self.crypto_manager.key_path

            # Check if key exists, otherwise generate one
            if not os.path.exists(key_path):
                self.create_key_generation_dialog()

            # Initialize other managers
            self.auth_manager = AuthManager(self.crypto_manager)
            self.storage_manager = EntryStorage(self.crypto_manager)

            # Create the main window
            self.main_window = MainWindow(
                self.auth_manager, self.storage_manager, root=self.root
            )

            # Set up tabs
            self.setup_tabs()

            # Now show the main window
            self.root.deiconify()
        except Exception as e:
            # Handle initialization errors
            messagebox.showerror(
                "Initialization Error", f"Failed to start application: {str(e)}"
            )
            self.root.destroy()
            sys.exit(1)

    def check_and_migrate_files(self):
        """Check if old files exist and migrate them to new hidden files."""
        crypto_manager = CryptoManager(check_key_exists=False)
        key_path = crypto_manager.key_path

        # Determine the directory for the new key file
        key_dir = os.path.dirname(key_path)

        # Check for old key file in current directory
        if os.path.exists("key.key") and not os.path.exists(key_path):
            try:
                # Create directory if it doesn't exist
                os.makedirs(key_dir, exist_ok=True)

                # Copy the file to maintain the same key
                shutil.copy("key.key", key_path)
                messagebox.showinfo(
                    "Migration",
                    f"Encryption key migrated to {key_path}.\n"
                    "The original key.key file can now be deleted.",
                )
            except Exception as e:
                messagebox.showerror(
                    "Migration Error", f"Failed to migrate key file: {str(e)}"
                )

        # Similarly for password file
        # Get the appropriate path for password file
        pwd_path = os.path.join(key_dir, ".password.txt")

        # Check for old password file
        if os.path.exists("password.txt") and not os.path.exists(pwd_path):
            try:
                # Create directory if it doesn't exist
                os.makedirs(key_dir, exist_ok=True)

                # Copy the file to maintain the same password
                shutil.copy("password.txt", pwd_path)
                messagebox.showinfo(
                    "Migration",
                    f"Password file migrated to {pwd_path}.\n"
                    "The original password.txt file can now be deleted.",
                )
            except Exception as e:
                messagebox.showerror(
                    "Migration Error", f"Failed to migrate password file: {str(e)}"
                )

    def create_key_generation_dialog(self):
        """Create a dialog for key generation."""
        # Create a simple dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Encryption Key")
        dialog.geometry("400x200")
        dialog.configure(bg="#f5f5f5")
        dialog.grab_set()  # Make dialog modal

        # Set up styling
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("TLabel", font=("Helvetica", 12), background="#f5f5f5")

        # Create a main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add a label
        label = ttk.Label(
            main_frame,
            text=f"No encryption key found at:\n{self.crypto_manager.key_path}\n\nA new one needs to be generated.\nClick 'Generate' to create a new key.",
            justify=tk.CENTER,
        )
        label.pack(pady=20)

        # Add the generate key button
        def generate_key():
            try:
                # Generate a new key using our already initialized crypto manager
                self.crypto_manager.generate_key()
                messagebox.showinfo(
                    "Success",
                    f"Encryption key generated and saved at:\n{self.crypto_manager.key_path}",
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to generate encryption key: {str(e)}"
                )

        generate_button = ttk.Button(
            main_frame, text="Generate New Key", command=generate_key, width=20
        )
        generate_button.pack(pady=10)

        # Add a close button
        close_button = ttk.Button(
            main_frame, text="Exit", command=lambda: sys.exit(1), width=20
        )
        close_button.pack(pady=10)

        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry("{}x{}+{}+{}".format(width, height, x, y))

        # Wait for dialog to close
        dialog.wait_window()

        # Check if key was created
        if not os.path.exists(self.crypto_manager.key_path):
            messagebox.showerror(
                "Error",
                f"Key generation failed. Cannot continue without an encryption key at {self.crypto_manager.key_path}",
            )
            sys.exit(1)

    def setup_tabs(self):
        """Set up the notebook tabs for the application."""
        # Create notebook
        self.notebook = ttk.Notebook(self.main_window.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create tabs
        self.write_tab = WriteTab(
            self.notebook, self.storage_manager, self.main_window.set_status
        )

        self.view_all_tab = ViewAllTab(
            self.notebook,
            self.storage_manager,
            self.main_window.set_status,
            self.refresh_views,
        )

        self.date_view_tab = DateViewTab(
            self.notebook,
            self.storage_manager,
            self.main_window.set_status,
            self.refresh_views,
        )

        # Add tabs to notebook
        self.notebook.add(self.write_tab.get_frame(), text="Write Entry")
        self.notebook.add(self.view_all_tab.get_frame(), text="View All Entries")
        self.notebook.add(self.date_view_tab.get_frame(), text="View By Date")

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        """Handle tab change events."""
        tab_id = self.notebook.index(self.notebook.select())
        if tab_id == 1:  # View All Entries tab
            self.view_all_tab.load_entries()
        elif tab_id == 2:  # View By Date tab
            self.date_view_tab.load_dates()

    def refresh_views(self):
        """Refresh all views that display entries."""
        self.view_all_tab.load_entries()
        self.date_view_tab.load_dates()

    def run(self):
        """Run the application."""
        self.main_window.run()


def main():
    """Entry point for the application."""
    try:
        app = DiaryApplication()
        app.run()
    except Exception as e:
        # Catch any unexpected errors
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {str(e)}")
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    main()
