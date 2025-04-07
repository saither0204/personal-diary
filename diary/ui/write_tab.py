"""
Write entry tab component for the personal diary.
"""
import datetime
import tkinter as tk
from tkinter import ttk

class WriteTab:
    def __init__(self, parent, storage_manager, status_callback):
        self.parent = parent
        self.storage_manager = storage_manager
        self.status_callback = status_callback
        
        # Main frame
        self.frame = ttk.Frame(parent)
        
        # Create UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Date label
        self.current_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.date_label = ttk.Label(self.frame, text=self.current_date, style="Date.TLabel")
        self.date_label.pack(pady=(0, 20))
        
        # Create a main frame to hold content
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create a frame for the text area with a border
        text_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a scrollbar to the text area
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add text area
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
            bg="#ffffff",
            fg="#333333",
            insertbackground="#555555",
            selectbackground="#b3d9ff",
            yscrollcommand=scrollbar.set,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        # Add a mood selector
        mood_frame = ttk.Frame(main_frame)
        mood_frame.pack(fill=tk.X, pady=10)

        mood_label = ttk.Label(mood_frame, text="Today's Mood:", style="TLabel")
        mood_label.pack(side=tk.LEFT, padx=(0, 10))

        self.mood_var = tk.StringVar()
        mood_choices = ["😊 Happy", "😐 Neutral", "😔 Sad", "😡 Angry", "🤔 Thoughtful"]
        self.mood_combobox = ttk.Combobox(
            mood_frame, textvariable=self.mood_var, values=mood_choices, width=15, state="readonly"
        )
        self.mood_combobox.current(0)
        self.mood_combobox.pack(side=tk.LEFT)

        # Create a button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)

        # Add buttons
        save_button = ttk.Button(
            button_frame, text="Save Entry", command=self.save_entry, style="TButton", width=15
        )
        save_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(
            button_frame, text="Clear Entry", command=self.clear_entry, style="TButton", width=15
        )
        clear_button.pack(side=tk.LEFT, padx=10)

    def save_entry(self):
        """Save the current diary entry."""
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            if self.storage_manager.save_entry(content, self.mood_var.get(), self.current_date):
                self.text_area.delete("1.0", tk.END)
                tk.messagebox.showinfo("Saved", "Your diary entry has been securely saved!")
                self.status_callback("Entry saved and encrypted")
                # Signal tab change to update views
                return True
        return False
    
    def clear_entry(self):
        """Clear the text area."""
        self.text_area.delete("1.0", tk.END)
        
    def get_frame(self):
        """Return the main frame for this tab."""
        return self.frame