"""
Main application window for the personal diary.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class MainWindow:
    def __init__(self, auth_manager, storage_manager):
        # Suppress macOS NSMenu warnings
        if sys.platform == "darwin":  # macOS
            os.environ["TK_SILENCE_DEPRECATION"] = "1"
            
        self.auth_manager = auth_manager
        self.storage_manager = storage_manager
        
        # Create the main window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide until authenticated
        self.root.title("Personal Diary")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # Set up styles
        self.setup_styles()
        
        # Authentication check
        if not self.authenticate():
            sys.exit(0)
        
        # Initialize UI components
        self.setup_ui()
        
    def authenticate(self):
        """Authenticate the user before showing the main window."""
        # First set initial password if needed
        if not self.auth_manager.set_initial_password(self.root):
            return False
            
        # Then authenticate
        if not self.auth_manager.authenticate(self.root):
            return False
            
        # If authentication succeeded, show the window
        self.root.deiconify()
        return True
        
    def setup_styles(self):
        """Set up the ttk styles for the application."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure styles
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TButton", font=("Helvetica", 11), background="#4CAF50", foreground="black")
        self.style.configure("TLabel", font=("Helvetica", 12), background="#f5f5f5")
        self.style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), background="#f5f5f5", foreground="#333333")
        self.style.configure("Date.TLabel", font=("Helvetica", 14), background="#f5f5f5", foreground="#555555")
        self.style.configure("TNotebook", background="#f5f5f5")
        self.style.configure("TNotebook.Tab", font=("Helvetica", 12), padding=[12, 6])
        
    def setup_ui(self):
        """Set up the main UI components."""
        # Add title label
        self.title_label = ttk.Label(self.root, text="My Personal Diary", style="Title.TLabel")
        self.title_label.pack(pady=(20, 10))
        
        # Add status bar at the bottom
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup menu
        self.setup_menu()
        
    def setup_menu(self):
        """Set up the application menu."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Reset Password", 
                                       command=lambda: self.auth_manager.reset_password(self.root))
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="About",
            command=lambda: messagebox.showinfo(
                "About",
                "Personal Diary\nVersion 1.0\n\nA simple application to record your daily thoughts securely.",
            )
        )
        
    def set_status(self, message):
        """Update the status bar message."""
        self.status_bar.config(text=message)
        
    def run(self):
        """Run the main application loop."""
        self.root.mainloop()