"""
View entries by date tab component for the personal diary.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class DateViewTab:
    def __init__(self, parent, storage_manager, status_callback, refresh_callback):
        self.parent = parent
        self.storage_manager = storage_manager
        self.status_callback = status_callback
        self.refresh_callback = refresh_callback
        
        # Main frame
        self.frame = ttk.Frame(parent)
        
        # Create UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Create split view
        date_split_pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        date_split_pane.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left side frame (dates list)
        self.date_left_frame = ttk.Frame(date_split_pane)

        # Right side frame (entry content)
        date_right_frame = ttk.Frame(date_split_pane)

        # Add frames to paned window
        date_split_pane.add(self.date_left_frame, weight=1)
        date_split_pane.add(date_right_frame, weight=3)

        # Create a label for the dates list
        ttk.Label(self.date_left_frame, text="Select Date:", font=("Helvetica", 12, "bold")).pack(
            anchor=tk.W, pady=(0, 10)
        )

        # Create listbox for dates
        self.date_listbox = tk.Listbox(
            self.date_left_frame,
            font=("Helvetica", 11),
            selectbackground="#b3d9ff",
            selectmode=tk.SINGLE,
            exportselection=0,
            height=25,
        )
        self.date_listbox.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar to listbox
        date_list_scrollbar = ttk.Scrollbar(self.date_left_frame, command=self.date_listbox.yview)
        date_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.date_listbox.config(yscrollcommand=date_list_scrollbar.set)

        # Create text widget for displaying date-specific entries
        self.date_entry_text = tk.Text(
            date_right_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            borderwidth=0,
            padx=10,
            pady=10,
            bg="#ffffff",
            fg="#333333",
            highlightthickness=0,
        )
        self.date_entry_text.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar to text widget
        date_text_scrollbar = ttk.Scrollbar(date_right_frame, command=self.date_entry_text.yview)
        date_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.date_entry_text.config(yscrollcommand=date_text_scrollbar.set)

        # Configure text widget tags for styling
        self.date_entry_text.tag_configure("header", font=("Helvetica", 12, "bold"))

        # Add delete button to the View By Date tab
        date_buttons_frame = ttk.Frame(self.date_left_frame)
        date_buttons_frame.pack(fill=tk.X, pady=10)

        delete_date_button = ttk.Button(
            date_buttons_frame,
            text="Delete Date",
            command=self.delete_selected_date,
            style="TButton",
        )
        delete_date_button.pack(side=tk.LEFT, padx=5)

        # Bind selection event
        self.date_listbox.bind("<<ListboxSelect>>", self.show_entries_for_date)
        
    def load_dates(self):
        """Load all dates into the listbox."""
        # Clear the listbox
        self.date_listbox.delete(0, tk.END)

        # Get entries organized by date
        entries_by_date = self.storage_manager.organize_entries_by_date()
        date_list = list(entries_by_date.keys())
        date_list.sort(reverse=True)  # Most recent dates first

        # Populate the listbox with dates
        for date in date_list:
            entry_count = len(entries_by_date[date])
            self.date_listbox.insert(tk.END, f"{date} ({entry_count} entries)")

        # Display entries for first date if available
        if date_list:
            self.date_listbox.select_set(0)
            self.show_entries_for_date(None)
            
    def show_entries_for_date(self, event):
        """Display entries for the selected date."""
        selected_idx = self.date_listbox.curselection()
        if not selected_idx:
            return

        # Get the date from the selected item
        date_with_count = self.date_listbox.get(selected_idx[0])
        selected_date = date_with_count.split(" (")[0]

        # Clear previous content
        self.date_entry_text.config(state=tk.NORMAL)
        self.date_entry_text.delete(1.0, tk.END)

        # Get entries organized by date
        entries_by_date = self.storage_manager.organize_entries_by_date()

        # Display entries for the selected date
        if selected_date in entries_by_date:
            for i, entry in enumerate(entries_by_date[selected_date]):
                if i > 0:
                    self.date_entry_text.insert(tk.END, "\n" + "-" * 50 + "\n\n")

                # Split entry into header and content
                lines = entry.split("\n")
                header = lines[0]
                content = "\n".join(lines[1:])

                # Insert header with styling
                self.date_entry_text.insert(tk.END, header + "\n\n", "header")

                # Insert content
                self.date_entry_text.insert(tk.END, content)

        # Make text read-only
        self.date_entry_text.config(state=tk.DISABLED)
        
    def delete_selected_date(self):
        """Delete all entries for the selected date."""
        selected_idx = self.date_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a date to delete.")
            return

        date_with_count = self.date_listbox.get(selected_idx[0])
        selected_date = date_with_count.split(" (")[0]

        if messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete ALL entries for {selected_date}?",
        ):
            try:
                if self.storage_manager.delete_entries_by_date(selected_date):
                    self.status_callback(f"All entries for {selected_date} deleted successfully")
                    self.refresh_callback()  # Refresh all views
                    
                    # Clear the text view
                    self.date_entry_text.config(state=tk.NORMAL)
                    self.date_entry_text.delete(1.0, tk.END)
                    self.date_entry_text.insert(tk.END, "Entries deleted. Select another date.")
                    self.date_entry_text.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entries: {str(e)}")
        
    def get_frame(self):
        """Return the main frame for this tab."""
        return self.frame