"""
GUANO Metadata Editor - GUI Application

A user-friendly graphical interface for reading and editing GUANO metadata
in WAV files containing bat vocalizations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, Any
import sys

from guano_metadata_manager import GuanoMetadataManager, format_value


class GuanoGUI:
    """Main GUI application for GUANO metadata editing."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GUANO Metadata Editor")
        self.root.geometry("1000x700")
        
        # Initialize manager
        self.manager = GuanoMetadataManager()
        self.current_directory = None
        
        # Set up the GUI
        self._create_widgets()
        self._configure_styles()
        
        # Welcome message
        self.log_message("Welcome to GUANO Metadata Editor")
        self.log_message("Select a directory containing WAV files to begin")
    
    def _configure_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'aqua' in available_themes:  # macOS
            style.theme_use('aqua')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='red')
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # === Directory Selection Section ===
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="5")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.dir_entry = ttk.Entry(dir_frame, width=60)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(dir_frame, text="Browse...", 
                  command=self.browse_directory).grid(row=0, column=2, padx=5)
        
        ttk.Button(dir_frame, text="Load Files", 
                  command=self.load_files).grid(row=0, column=3, padx=5)
        
        # File count label
        self.file_count_label = ttk.Label(dir_frame, text="No files loaded")
        self.file_count_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        # === Notebook for metadata display ===
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(1, weight=3)
        
        # Common Fields Tab
        self.common_frame = self._create_common_fields_tab(notebook)
        notebook.add(self.common_frame, text="Common Fields")
        
        # Variable Fields Tab
        self.variable_frame = self._create_variable_fields_tab(notebook)
        notebook.add(self.variable_frame, text="Variable Fields")
        
        # === Action Buttons ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Create Backup", 
                  command=self.create_backup).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Edit Common Fields", 
                  command=self.edit_common_fields).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Refresh View", 
                  command=self.refresh_display).grid(row=0, column=2, padx=5)
        
        # === Log/Status Area ===
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _create_common_fields_tab(self, parent):
        """Create the common fields display tab."""
        frame = ttk.Frame(parent, padding="5")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Create treeview for common fields
        columns = ('Field', 'Value')
        self.common_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        self.common_tree.heading('Field', text='Field Name')
        self.common_tree.heading('Value', text='Value')
        
        self.common_tree.column('Field', width=250)
        self.common_tree.column('Value', width=500)
        
        self.common_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.common_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.common_tree.configure(yscrollcommand=scrollbar.set)
        
        # Info label
        info_label = ttk.Label(frame, 
            text="These fields have identical values across all loaded files and can be edited together.",
            wraplength=700, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        return frame
    
    def _create_variable_fields_tab(self, parent):
        """Create the variable fields display tab."""
        frame = ttk.Frame(parent, padding="5")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Create treeview for variable fields
        columns = ('Field', 'File', 'Value')
        self.variable_tree = ttk.Treeview(frame, columns=columns, show='tree headings', height=15)
        
        self.variable_tree.heading('Field', text='Field Name')
        self.variable_tree.heading('File', text='File')
        self.variable_tree.heading('Value', text='Value')
        
        self.variable_tree.column('#0', width=20)
        self.variable_tree.column('Field', width=200)
        self.variable_tree.column('File', width=300)
        self.variable_tree.column('Value', width=300)
        
        self.variable_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.variable_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.variable_tree.configure(yscrollcommand=scrollbar.set)
        
        # Info label
        info_label = ttk.Label(frame, 
            text="These fields have different values across files. They are shown for reference only.",
            wraplength=700, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        return frame
    
    def browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(
            title="Select Directory Containing WAV Files",
            initialdir=self.current_directory or Path.home()
        )
        
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.current_directory = directory
    
    def load_files(self):
        """Load WAV files from selected directory."""
        directory = self.dir_entry.get()
        
        if not directory:
            messagebox.showwarning("No Directory", "Please select a directory first.")
            return
        
        # Validate directory
        is_valid, message = self.manager.validate_directory(directory)
        if not is_valid:
            messagebox.showerror("Invalid Directory", message)
            return
        
        self.log_message(f"Loading files from: {directory}")
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Load files
            count, errors = self.manager.load_directory(directory)
            
            if count == 0:
                messagebox.showerror("No Files Loaded", 
                    "No WAV files with GUANO metadata were found.\n\n" + 
                    "\n".join(errors[:5]))  # Show first 5 errors
                self.log_message("No files loaded")
                return
            
            # Update display
            self.file_count_label.config(text=f"{count} files loaded with GUANO metadata")
            self.log_message(f"Successfully loaded {count} files")
            
            if errors:
                self.log_message(f"Warnings: {len(errors)} files had issues")
                for error in errors[:3]:  # Log first 3 errors
                    self.log_message(f"  - {error}")
            
            self.refresh_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading files:\n{str(e)}")
            self.log_message(f"Error: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def refresh_display(self):
        """Refresh the metadata display."""
        if self.manager.get_file_count() == 0:
            return
        
        # Clear existing data
        for item in self.common_tree.get_children():
            self.common_tree.delete(item)
        
        for item in self.variable_tree.get_children():
            self.variable_tree.delete(item)
        
        # Populate common fields
        common_fields = self.manager.get_common_fields()
        for field, value in sorted(common_fields.items()):
            self.common_tree.insert('', tk.END, values=(field, format_value(value)))
        
        # Populate variable fields
        variable_fields = self.manager.get_variable_fields()
        for field, values in sorted(variable_fields.items()):
            # Insert parent field
            parent = self.variable_tree.insert('', tk.END, values=(field, '', ''), open=False)
            
            # Insert child values for each file
            for filename, value in values:
                self.variable_tree.insert(parent, tk.END, 
                    values=('', filename, format_value(value)))
        
        self.log_message(f"Display refreshed: {len(common_fields)} common, "
                        f"{len(variable_fields)} variable fields")
    
    def create_backup(self):
        """Create backup of all loaded files."""
        if self.manager.get_file_count() == 0:
            messagebox.showwarning("No Files", "Please load files first.")
            return
        
        # Confirm backup
        if not messagebox.askyesno("Create Backup", 
            f"Create backup copies of {self.manager.get_file_count()} files?\n\n"
            "A timestamped backup folder will be created in the same directory."):
            return
        
        self.log_message("Creating backup...")
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            success, result = self.manager.create_backup()
            
            if success:
                messagebox.showinfo("Backup Complete", 
                    f"Backup created successfully!\n\nLocation: {result}")
                self.log_message(f"Backup created: {result}")
            else:
                messagebox.showerror("Backup Failed", result)
                self.log_message(f"Backup failed: {result}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Backup error: {str(e)}")
            self.log_message(f"Backup error: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def edit_common_fields(self):
        """Open dialog to edit common metadata fields."""
        if self.manager.get_file_count() == 0:
            messagebox.showwarning("No Files", "Please load files first.")
            return
        
        common_fields = self.manager.get_common_fields()
        
        if not common_fields:
            messagebox.showinfo("No Common Fields", 
                "No common fields found across all files.")
            return
        
        # Open edit dialog
        EditDialog(self.root, self, common_fields)
    
    def apply_field_updates(self, updates: Dict[str, Any]):
        """Apply field updates to all files."""
        if not updates:
            self.log_message("No changes to apply")
            return
        
        # Final confirmation
        file_count = self.manager.get_file_count()
        update_list = "\n".join(f"  • {field}: {value}" for field, value in updates.items())
        
        confirm_msg = (
            f"Apply these changes to {file_count} files?\n\n"
            f"{update_list}\n\n"
            f"⚠️ This will modify the files. "
            f"Creating a backup first is strongly recommended!"
        )
        
        if not messagebox.askyesno("Confirm Changes", confirm_msg, icon='warning'):
            self.log_message("Changes cancelled by user")
            return
        
        self.log_message(f"Applying {len(updates)} field updates to {file_count} files...")
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            updated_count, errors = self.manager.update_common_fields(updates)
            
            if updated_count > 0:
                messagebox.showinfo("Update Complete", 
                    f"Successfully updated {updated_count} files!")
                self.log_message(f"Updated {updated_count} files successfully")
                
                if errors:
                    self.log_message(f"Errors occurred in {len(errors)} files:")
                    for error in errors[:3]:
                        self.log_message(f"  - {error}")
                
                # Refresh display
                self.refresh_display()
            else:
                messagebox.showerror("Update Failed", 
                    "No files were updated.\n\n" + "\n".join(errors[:5]))
                self.log_message("Update failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.log_message(f"Error: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def log_message(self, message: str):
        """Add a message to the activity log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()


class EditDialog:
    """Dialog window for editing common metadata fields."""
    
    def __init__(self, parent, main_app, fields: Dict[str, Any]):
        self.main_app = main_app
        self.fields = fields
        self.entries = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Common Fields")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Instructions
        ttk.Label(main_frame, 
            text="Edit the values below. Empty fields will be deleted from all files.",
            style='Header.TLabel', wraplength=550).grid(row=0, column=0, pady=10, sticky=tk.W)
        
        # Create scrollable frame for fields
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Add entry fields
        scrollable_frame.columnconfigure(1, weight=1)
        
        for i, (field, value) in enumerate(sorted(self.fields.items())):
            # Field label
            ttk.Label(scrollable_frame, text=f"{field}:", 
                     font=('Helvetica', 9, 'bold')).grid(
                row=i*2, column=0, sticky=tk.W, padx=5, pady=(5,0))
            
            # Value entry
            entry = ttk.Entry(scrollable_frame, width=50)
            entry.insert(0, format_value(value))
            entry.grid(row=i*2+1, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                      padx=5, pady=(0,5))
            
            self.entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Apply Changes", 
                  command=self.apply_changes).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).grid(row=0, column=1, padx=5)
    
    def apply_changes(self):
        """Collect changes and apply them."""
        updates = {}
        
        for field, entry in self.entries.items():
            new_value = entry.get().strip()
            old_value = format_value(self.fields[field])
            
            # Only include changed fields
            if new_value != old_value:
                updates[field] = new_value if new_value else None
        
        if not updates:
            messagebox.showinfo("No Changes", "No fields were modified.")
            return
        
        # Close dialog and apply
        self.dialog.destroy()
        self.main_app.apply_field_updates(updates)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = GuanoGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
