"""
View all entries tab component for the personal diary.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class ViewAllTab:
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
        # Create a frame for all entries
        all_entries_frame = ttk.Frame(self.frame)
        all_entries_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add a scrollbar
        all_entries_scrollbar = ttk.Scrollbar(all_entries_frame)
        all_entries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a text area for displaying all entries
        self.all_entries_text = tk.Text(
            all_entries_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
            bg="#ffffff",
            fg="#333333",
            yscrollcommand=all_entries_scrollbar.set,
        )
        self.all_entries_text.pack(fill=tk.BOTH, expand=True)
        all_entries_scrollbar.config(command=self.all_entries_text.yview)

        # Configure text styling
        self.all_entries_text.tag_configure("header", font=("Helvetica", 12, "bold"))
        
    def load_entries(self):
        """Load and display all entries."""
        self.all_entries_text.config(state=tk.NORMAL)
        self.all_entries_text.delete(1.0, tk.END)

        entries = self.storage_manager.read_entries()

        if entries:
            # Sort entries by date (most recent first)
            try:
                entries.sort(key=lambda x: x.split("\n")[0].split("|")[0], reverse=True)
            except:
                pass  # If sorting fails, use original order

            for i, entry in enumerate(entries):
                if i > 0:
                    self.all_entries_text.insert(tk.END, "\n" + "=" * 70 + "\n\n")

                # Split entry into header and content
                lines = entry.split("\n")
                header = lines[0]
                content = "\n".join(lines[1:])

                # Insert header with styling
                self.all_entries_text.insert(tk.END, header + "\n\n", "header")

                # Insert partial content (first 100 chars)
                short_content = content[:100] + ("..." if len(content) > 100 else "")
                self.all_entries_text.insert(tk.END, short_content + "\n\n")
                
                # Create a frame for buttons directly
                button_frame = ttk.Frame(self.all_entries_text)
                
                # Insert the frame into the text widget
                self.all_entries_text.window_create(tk.END, window=button_frame)
                
                # Add View button
                view_button = ttk.Button(
                    button_frame,
                    text="View",
                    width=10,
                    command=lambda entry=entry: self.view_entry(entry)
                )
                view_button.pack(side=tk.LEFT, padx=5)
                
                # Add Delete button
                delete_button = ttk.Button(
                    button_frame,
                    text="Delete",
                    width=10,
                    command=lambda entry=entry: self.delete_entry(entry)
                )
                delete_button.pack(side=tk.LEFT, padx=5)
                
                self.all_entries_text.insert(tk.END, "\n")
        else:
            self.all_entries_text.insert(
                tk.END, "No diary entries yet. Start writing in the 'Write Entry' tab!"
            )

        self.all_entries_text.config(state=tk.DISABLED)  # Make read-only
        
    def view_entry(self, entry_content):
        """Show a detailed view of an entry."""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("Entry Details")
        detail_window.geometry("600x500")
        detail_window.configure(bg="#f5f5f5")

        # Create frame for content
        content_frame = ttk.Frame(detail_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add text area with scrollbar
        detail_scrollbar = ttk.Scrollbar(content_frame)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        detail_text = tk.Text(
            content_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            padx=10,
            pady=10,
            bg="#ffffff",
            fg="#333333",
            yscrollcommand=detail_scrollbar.set,
        )
        detail_text.pack(fill=tk.BOTH, expand=True)
        detail_scrollbar.config(command=detail_text.yview)

        # Insert the entry content
        lines = entry_content.split("\n")
        header = lines[0]
        content = "\n".join(lines[1:])

        detail_text.insert(tk.END, header + "\n\n", "header")
        detail_text.insert(tk.END, content)
        detail_text.tag_configure("header", font=("Helvetica", 12, "bold"))
        detail_text.config(state=tk.DISABLED)

        # Add button frame
        button_frame = ttk.Frame(detail_window)
        button_frame.pack(fill=tk.X, pady=10)

        # Add delete button
        delete_button = ttk.Button(
            button_frame,
            text="Delete Entry",
            command=lambda: self.delete_and_close(entry_content, detail_window),
            style="TButton",
            width=15,
        )
        delete_button.pack(side=tk.LEFT, padx=10)

        # Add close button
        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=detail_window.destroy,
            style="TButton",
            width=15,
        )
        close_button.pack(side=tk.RIGHT, padx=10)
        
    def delete_and_close(self, entry, window):
        """Delete an entry and close the detail window."""
        if self.delete_entry(entry):
            window.destroy()
            
    def delete_entry(self, entry_to_delete):
        """Delete a specific entry."""
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this entry?"):
            try:
                if self.storage_manager.delete_entry(entry_to_delete):
                    self.status_callback("Entry deleted successfully")
                    self.refresh_callback()  # Refresh all views
                    return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {str(e)}")
        return False
        
    def get_frame(self):
        """Return the main frame for this tab."""
        return self.frame