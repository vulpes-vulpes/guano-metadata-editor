"""
GUANO Metadata Editor - GUI Application

A user-friendly graphical interface for reading and editing GUANO metadata
in WAV files containing bat vocalizations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys
import threading

from guano_metadata_manager import (
    GuanoMetadataManager, format_value,
    GUANO_STANDARD_FIELDS, GUANO_RESERVED_NAMESPACES, GUANO_PROTECTED_FIELDS,
)


class GuanoGUI:
    """Main GUI application for GUANO metadata editing."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GUANO Metadata Editor")
        self.root.geometry("1000x850")
        
        # Initialize manager
        self.manager = GuanoMetadataManager()
        self.current_directory = None
        
        # Pending changes queue: list of (field_name, value, change_type) tuples
        # change_type can be: 'common', 'variable', 'new'
        self.pending_changes = []
        
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
        # Don't give pending changes section expandable weight - keep it fixed size
        # main_frame.rowconfigure(3, weight=1)
        
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
        main_frame.rowconfigure(1, weight=1)  # Let notebook expand, but pending section stays visible
        
        # Common Fields Tab
        self.common_frame = self._create_common_fields_tab(notebook)
        notebook.add(self.common_frame, text="Common Fields")
        
        # Variable Fields Tab
        self.variable_frame = self._create_variable_fields_tab(notebook)
        notebook.add(self.variable_frame, text="Variable Fields")
        
        # === Action Buttons ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Edit Common Fields", 
                  command=self.edit_common_fields).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Edit Variable Fields", 
                  command=self.edit_variable_fields).grid(row=0, column=1, padx=5)

        ttk.Button(button_frame, text="Add Field",
                  command=self.add_new_field).grid(row=0, column=2, padx=5)
        
        # === Pending Changes Section ===
        pending_frame = ttk.LabelFrame(main_frame, text="Pending Changes", padding="5")
        pending_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        pending_frame.columnconfigure(0, weight=1)
        
        # Scrollable list of pending changes
        changes_list_frame = ttk.Frame(pending_frame)
        changes_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        changes_list_frame.columnconfigure(0, weight=1)
        
        # Listbox with scrollbar for pending changes
        list_scroll_frame = ttk.Frame(changes_list_frame)
        list_scroll_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scroll_frame.columnconfigure(0, weight=1)
        
        self.changes_listbox = tk.Listbox(list_scroll_frame, height=4, font=('Courier', 9))
        self.changes_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        changes_scrollbar = ttk.Scrollbar(list_scroll_frame, orient=tk.VERTICAL, 
                                         command=self.changes_listbox.yview)
        changes_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.changes_listbox.configure(yscrollcommand=changes_scrollbar.set)
        
        # Buttons for managing pending changes
        pending_buttons_frame = ttk.Frame(pending_frame)
        pending_buttons_frame.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Button(pending_buttons_frame, text="Remove Selected",
                  command=self.remove_pending_change).grid(row=0, column=0, padx=5)
        
        ttk.Button(pending_buttons_frame, text="Clear All",
                  command=self.clear_pending_changes).grid(row=0, column=1, padx=5)
        
        # Make Apply All Changes button prominent
        self.apply_all_button = ttk.Button(pending_buttons_frame, text="▶ Apply All Changes",
                  command=self.apply_all_pending_changes)
        self.apply_all_button.grid(row=0, column=2, padx=10)
        self.apply_all_button.config(state='disabled')  # Disabled when no changes pending
        
        self.pending_count_label = ttk.Label(pending_buttons_frame, text="No pending changes",
                                             font=('Helvetica', 10, 'italic'))
        self.pending_count_label.grid(row=0, column=3, padx=15)
        
        # === Progress Bar Section (initially hidden) ===
        self.progress_frame = ttk.Frame(main_frame, padding="5")
        self.progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        self.progress_frame.columnconfigure(0, weight=1)
        
        # Progress label
        self.progress_label = ttk.Label(self.progress_frame, text="", font=('Helvetica', 9))
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 2))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        # Progress status (count)
        self.progress_status = ttk.Label(self.progress_frame, text="", font=('Courier', 9))
        self.progress_status.grid(row=2, column=0, sticky=tk.W)
        
        # Hide progress bar initially
        self.progress_frame.grid_remove()
        
        # === Log/Status Area ===
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _show_progress(self, message: str):
        """Show the integrated progress bar."""
        self.progress_label.config(text=message)
        self.progress_var.set(0)
        self.progress_status.config(text="0 / 0")
        self.progress_frame.grid()
        self.root.update_idletasks()
    
    def _update_progress(self, current: int, total: int):
        """Update the integrated progress bar."""
        if total > 0:
            percent = (current / total) * 100
            self.progress_var.set(percent)
            self.progress_status.config(text=f"{current:,} / {total:,}")
            # Don't call update() here - we're already in the event loop
    
    def _hide_progress(self):
        """Hide the integrated progress bar."""
        self.progress_frame.grid_remove()
        self.root.update_idletasks()
    
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
            text="These fields have different values across files. Use 'Edit Variable Fields' to standardize them.",
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
        
        # Show progress bar
        self._show_progress("Scanning and loading WAV files...")
        
        # Variables to store results
        result = {'count': 0, 'errors': [], 'exception': None}
        
        def load_thread():
            """Thread function for loading files."""
            try:
                def progress_callback(current, total):
                    # Update progress from worker thread
                    # Use default arguments to capture values, not references
                    self.root.after_idle(lambda c=current, t=total: self._update_progress(c, t))
                
                # Load files with progress callback
                count, errors = self.manager.load_directory(directory, progress_callback=progress_callback)
                result['count'] = count
                result['errors'] = errors
            except Exception as e:
                result['exception'] = e
        
        # Start loading in a thread
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
        
        # Wait for thread to complete
        while thread.is_alive():
            self.root.update()
            thread.join(timeout=0.1)
        
        # Hide progress bar
        self._hide_progress()
        
        # Handle results
        try:
            if result['exception']:
                raise result['exception']
            
            count = result['count']
            errors = result['errors']
            
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

        EditDialog(self.root, self, common_fields)

    def edit_variable_fields(self):
        """Open dialog to edit variable metadata fields (convert to common)."""
        if self.manager.get_file_count() == 0:
            messagebox.showwarning("No Files", "Please load files first.")
            return

        variable_fields = self.manager.get_variable_fields()

        if not variable_fields:
            messagebox.showinfo("No Variable Fields",
                "No variable fields found. All fields are already common across files.")
            return

        # Open edit dialog
        EditVariableFieldsDialog(self.root, self, variable_fields)

    def add_new_field(self):
        """Open dialog to add a new metadata field to all loaded files."""
        if self.manager.get_file_count() == 0:
            messagebox.showwarning("No Files", "Please load files first.")
            return
        AddFieldDialog(self.root, self)
    
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
        
        # Show progress bar
        self._show_progress("Applying changes to files...")
        
        # Variables to store results
        result = {'updated_count': 0, 'errors': [], 'exception': None}
        
        def update_thread():
            """Thread function for updating files."""
            try:
                def progress_callback(current, total):
                    # Update progress from worker thread
                    # Use default arguments to capture values, not references
                    self.root.after_idle(lambda c=current, t=total: self._update_progress(c, t))
                
                # Update files with progress callback
                updated_count, errors = self.manager.update_common_fields(updates, progress_callback=progress_callback)
                result['updated_count'] = updated_count
                result['errors'] = errors
            except Exception as e:
                result['exception'] = e
        
        # Start updating in a thread
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
        
        # Wait for thread to complete
        while thread.is_alive():
            self.root.update()
            thread.join(timeout=0.1)
        
        # Hide progress bar
        self._hide_progress()
        
        # Handle results
        try:
            if result['exception']:
                raise result['exception']
            
            updated_count = result['updated_count']
            errors = result['errors']
            
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
    
    def add_pending_change(self, field_name: str, value: Any, change_type: str):
        """Add a change to the pending changes queue."""
        # Remove any existing change for this field
        self.pending_changes = [(f, v, t) for f, v, t in self.pending_changes if f != field_name]
        
        # Add new change
        self.pending_changes.append((field_name, value, change_type))
        
        # Update display
        self._update_pending_changes_display()
        
        self.log_message(f"Queued change: {field_name} = {value} ({change_type})")
    
    def remove_pending_change(self):
        """Remove selected change from pending queue."""
        selection = self.changes_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a change to remove.")
            return
        
        index = selection[0]
        if 0 <= index < len(self.pending_changes):
            field_name, value, change_type = self.pending_changes[index]
            self.pending_changes.pop(index)
            self._update_pending_changes_display()
            self.log_message(f"Removed pending change: {field_name}")
    
    def clear_pending_changes(self):
        """Clear all pending changes."""
        if not self.pending_changes:
            return
        
        if messagebox.askyesno("Clear All Changes", 
                              f"Remove all {len(self.pending_changes)} pending changes?"):
            self.pending_changes.clear()
            self._update_pending_changes_display()
            self.log_message("Cleared all pending changes")
    
    def _update_pending_changes_display(self):
        """Update the pending changes listbox display."""
        self.changes_listbox.delete(0, tk.END)
        
        for field_name, value, change_type in self.pending_changes:
            # Format display string
            type_label = {"common": "[C]", "variable": "[V→C]", "new": "[NEW]"}
            display_value = str(value) if value else "<delete>"
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."
            
            display_str = f"{type_label.get(change_type, '[?]')} {field_name}: {display_value}"
            self.changes_listbox.insert(tk.END, display_str)
        
        # Update count label and button state
        count = len(self.pending_changes)
        if count == 0:
            self.pending_count_label.config(text="No pending changes", foreground='gray')
            self.apply_all_button.config(state='disabled')
        else:
            self.pending_count_label.config(
                text=f"⚡ {count} change{'s' if count != 1 else ''} ready to apply",
                foreground='#CC6600',
                font=('Helvetica', 10, 'bold')
            )
            self.apply_all_button.config(state='normal')
    
    def apply_all_pending_changes(self):
        """Apply all pending changes in one batch operation."""
        if not self.pending_changes:
            messagebox.showinfo("No Changes", "No pending changes to apply.")
            return
        
        if self.manager.get_file_count() == 0:
            messagebox.showwarning("No Files", "Please load files first.")
            return
        
        # Build updates dictionary from pending changes
        updates = {field_name: value for field_name, value, _ in self.pending_changes}
        
        # Final confirmation
        file_count = self.manager.get_file_count()
        change_list = "\n".join(
            f"  • {field}: {value if value else '<delete>'}"
            for field, value, _ in self.pending_changes
        )
        
        confirm_msg = (
            f"Apply {len(self.pending_changes)} changes to {file_count} files?\n\n"
            f"{change_list}\n\n"
            f"⚠️ This will modify the files. "
            f"Creating a backup first is strongly recommended!"
        )
        
        if not messagebox.askyesno("Confirm All Changes", confirm_msg, icon='warning'):
            self.log_message("Changes cancelled by user")
            return
        
        self.log_message(f"Applying {len(self.pending_changes)} changes to {file_count} files...")
        
        # Show progress bar
        self._show_progress("Applying all pending changes to files...")
        
        # Variables to store results
        result = {'updated_count': 0, 'errors': [], 'exception': None}
        
        def update_thread():
            """Thread function for updating files."""
            try:
                def progress_callback(current, total):
                    # Update progress from worker thread
                    # Use default arguments to capture values, not references
                    self.root.after_idle(lambda c=current, t=total: self._update_progress(c, t))
                
                # Update files with progress callback
                updated_count, errors = self.manager.update_common_fields(updates, progress_callback=progress_callback)
                result['updated_count'] = updated_count
                result['errors'] = errors
            except Exception as e:
                result['exception'] = e
        
        # Start updating in a thread
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
        
        # Wait for thread to complete
        while thread.is_alive():
            self.root.update()
            thread.join(timeout=0.1)
        
        # Hide progress bar
        self._hide_progress()
        
        # Handle results
        try:
            if result['exception']:
                raise result['exception']
            
            updated_count = result['updated_count']
            errors = result['errors']
            
            if updated_count > 0:
                messagebox.showinfo("Update Complete", 
                    f"Successfully updated {updated_count} files with {len(self.pending_changes)} changes!")
                self.log_message(f"Applied all changes to {updated_count} files successfully")
                
                if errors:
                    self.log_message(f"Errors occurred in {len(errors)} files:")
                    for error in errors[:3]:
                        self.log_message(f"  - {error}")
                
                # Clear pending changes after successful apply
                self.pending_changes.clear()
                self._update_pending_changes_display()
                
                # Refresh display
                self.refresh_display()
            else:
                messagebox.showerror("Update Failed", 
                    "No files were updated.\n\n" + "\n".join(errors[:5]))
                self.log_message("Update failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.log_message(f"Error: {str(e)}")
    
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
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.apply_changes).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).grid(row=0, column=1, padx=5)
    
    def apply_changes(self):
        """Gather all entry values and add them to the pending changes queue."""
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

        # Warn before modifying any protected fields (e.g. GUANO|Version).
        protected_changes = [f for f in updates if f in GUANO_PROTECTED_FIELDS]
        if protected_changes:
            names = ", ".join(protected_changes)
            if not messagebox.askyesno(
                "Protected Field",
                f"You are modifying a required GUANO meta-field: {names}\n\n"
                "Changing it incorrectly may break compatibility with other "
                "GUANO software. Proceed anyway?",
                icon="warning",
            ):
                return

        # Add each change to the queue
        for field, value in updates.items():
            self.main_app.add_pending_change(field, value, 'common')
        
        self.dialog.destroy()
        messagebox.showinfo("Changes Queued", 
            f"{len(updates)} change(s) added to the pending changes queue.\n\n"
            "Click 'Apply All Changes' to process all pending changes.",
            parent=self.main_app.root)


class AddFieldDialog:
    """
    Dialog for adding a new metadata field to all loaded files.

    Two modes are offered via a Notebook:
      - Standard GUANO Field: pick from the full spec-defined list.
      - Custom Field: enter a namespace + field name of your choice.

    The dialog warns the user if the chosen field already exists in any
    loaded file, and requires extra confirmation before modifying the
    protected GUANO|Version field.
    """

    def __init__(self, parent, main_app):
        self.main_app = main_app
        # Maps combobox display string  ->  canonical field name
        self._std_field_map: Dict[str, str] = {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Field")
        self.dialog.geometry("590x510")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        file_count = self.main_app.manager.get_file_count()
        ttk.Label(
            main_frame,
            text=(
                f"The new field will be written to all {file_count} loaded file(s). "
                "If the field already exists its value will be overwritten."
            ),
            wraplength=555, justify=tk.LEFT,
        ).grid(row=0, column=0, pady=(0, 8), sticky=tk.W)

        # ── Notebook (field-type selector) ─────────────────────────────
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self._build_standard_tab()
        self._build_custom_tab()

        # ── Value ─────────────────────────────────────────────────────
        value_frame = ttk.LabelFrame(main_frame, text="Value", padding="5")
        value_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        value_frame.columnconfigure(0, weight=1)

        self.value_var = tk.StringVar()
        ttk.Entry(
            value_frame, textvariable=self.value_var, width=62,
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.type_hint_var = tk.StringVar(value="")
        ttk.Label(
            value_frame, textvariable=self.type_hint_var, foreground="gray",
        ).grid(row=1, column=0, sticky=tk.W, padx=5)

        # ── Conflict warning ───────────────────────────────────────────
        self.field_warning_var = tk.StringVar()
        ttk.Label(
            main_frame,
            textvariable=self.field_warning_var,
            style="Warning.TLabel",
            wraplength=555,
            justify=tk.LEFT,
        ).grid(row=3, column=0, sticky=tk.W, pady=(6, 0))

        # ── Buttons ───────────────────────────────────────────────────
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, pady=(10, 0))
        ttk.Button(
            btn_frame, text="Add to Queue", command=self.apply_changes,
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            btn_frame, text="Cancel", command=self.dialog.destroy,
        ).grid(row=0, column=1, padx=5)

    def _build_standard_tab(self):
        """Standard GUANO Field tab."""
        frame = ttk.Frame(self.notebook, padding="8")
        self.notebook.add(frame, text=" Standard GUANO Field ")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Field:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5,
        )

        display_items = []
        for name, info in sorted(GUANO_STANDARD_FIELDS.items()):
            display = f"{name}  ({info['type']})"
            display_items.append(display)
            self._std_field_map[display] = name

        self.std_field_var = tk.StringVar()
        self.std_combo = ttk.Combobox(
            frame,
            textvariable=self.std_field_var,
            values=display_items,
            state="readonly",
            width=50,
        )
        self.std_combo.grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5,
        )
        self.std_combo.bind("<<ComboboxSelected>>", self._on_std_field_select)

        self.std_desc_var = tk.StringVar(value="Select a standard field above.")
        ttk.Label(
            frame,
            textvariable=self.std_desc_var,
            wraplength=465,
            foreground="gray",
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))

        ttk.Label(
            frame,
            text=(
                "Using standard fields maximises interoperability with other "
                "GUANO-compatible hardware and software."
            ),
            wraplength=465,
            foreground="#555555",
            justify=tk.LEFT,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))

    def _build_custom_tab(self):
        """Custom Field tab."""
        frame = ttk.Frame(self.notebook, padding="8")
        self.notebook.add(frame, text=" Custom Field ")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Namespace:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5,
        )

        ns_options = sorted(GUANO_RESERVED_NAMESPACES.keys()) + ["other\u2026"]
        self.ns_var = tk.StringVar(value="User")
        self.ns_combo = ttk.Combobox(
            frame, textvariable=self.ns_var, values=ns_options, width=24,
        )
        self.ns_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.ns_combo.bind("<<ComboboxSelected>>", self._on_namespace_change)
        self.ns_combo.bind("<KeyRelease>", self._on_namespace_change)

        self.ns_desc_var = tk.StringVar()
        ttk.Label(
            frame,
            textvariable=self.ns_desc_var,
            foreground="gray",
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)

        ttk.Label(frame, text="Field name:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5,
        )
        self.custom_name_var = tk.StringVar()
        custom_name_entry = ttk.Entry(
            frame, textvariable=self.custom_name_var, width=34,
        )
        custom_name_entry.grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5,
        )
        custom_name_entry.bind("<KeyRelease>", self._update_custom_preview)

        self.preview_var = tk.StringVar(value="Full field name:  User|")
        ttk.Label(
            frame,
            textvariable=self.preview_var,
            font=("Helvetica", 9),
            foreground="#333333",
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 4))

        self.ns_warning_var = tk.StringVar()
        ttk.Label(
            frame,
            textvariable=self.ns_warning_var,
            style="Warning.TLabel",
            wraplength=465,
            justify=tk.LEFT,
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)

        ttk.Label(
            frame,
            text=(
                "Tip: use the 'User' namespace for personal custom fields "
                "(e.g. User|MySurveyID). Manufacturer-specific fields should use "
                "the appropriate reserved namespace."
            ),
            wraplength=465,
            foreground="#555555",
            justify=tk.LEFT,
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self._refresh_namespace_ui()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_tab_change(self, event=None):
        """Clear stale warnings when the user switches tabs."""
        self.field_warning_var.set("")
        self.type_hint_var.set("")

    def _on_std_field_select(self, event=None):
        display = self.std_field_var.get()
        field_name = self._std_field_map.get(display)
        if not field_name:
            return
        info = GUANO_STANDARD_FIELDS[field_name]
        req_label = " (required)" if info.get("required") else " (optional)"
        self.std_desc_var.set(f"{info['description']}{req_label}")
        self.type_hint_var.set(f"Expected type: {info['type']}")
        self._check_field_conflict(field_name)

    def _on_namespace_change(self, event=None):
        self._refresh_namespace_ui()
        self._update_custom_preview()

    def _refresh_namespace_ui(self):
        ns = self.ns_var.get().strip()
        if ns == "other\u2026":
            self.ns_desc_var.set(
                "Enter the full field name including your own namespace prefix "
                "in the 'Field name' box below (e.g. ACME|GainSetting)."
            )
        else:
            self.ns_desc_var.set(GUANO_RESERVED_NAMESPACES.get(ns, ""))

        if ns == "GUANO":
            self.ns_warning_var.set(
                "\u26a0 The 'GUANO' namespace is reserved for meta-metadata. "
                "Adding fields here may break compatibility with other software."
            )
        else:
            self.ns_warning_var.set("")

    def _update_custom_preview(self, event=None):
        ns = self.ns_var.get().strip()
        name = self.custom_name_var.get().strip()
        if ns == "other\u2026":
            self.preview_var.set(
                f"Full field name:  {name}" if name else "Full field name: "
            )
        else:
            self.preview_var.set(
                f"Full field name:  {ns}|{name}" if name
                else f"Full field name:  {ns}|"
            )
        full_name = self._resolve_custom_field_name()
        if full_name:
            self._check_field_conflict(full_name)
        else:
            self.field_warning_var.set("")

    def _check_field_conflict(self, field_name: str):
        """Warn the user if the selected field already has data in the loaded files."""
        common = self.main_app.manager.get_common_fields()
        variable = self.main_app.manager.get_variable_fields()
        if field_name in common:
            self.field_warning_var.set(
                f"\u26a0 '{field_name}' already exists with the common value "
                f"{format_value(common[field_name])!r}. "
                "Adding it will overwrite that value in all files."
            )
        elif field_name in variable:
            self.field_warning_var.set(
                f"\u26a0 '{field_name}' already exists with differing values across files. "
                "Adding it will set a single uniform value in all files."
            )
        else:
            self.field_warning_var.set("")

    # ------------------------------------------------------------------
    # Field-name resolution helpers
    # ------------------------------------------------------------------

    def _resolve_std_field_name(self) -> str:
        return self._std_field_map.get(self.std_field_var.get(), "")

    def _resolve_custom_field_name(self) -> str:
        ns = self.ns_var.get().strip()
        name = self.custom_name_var.get().strip()
        if not name:
            return ""
        if ns == "other\u2026":
            return name  # caller should validate namespace presence separately
        return f"{ns}|{name}"

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def apply_changes(self):
        active_tab = self.notebook.index(self.notebook.select())

        if active_tab == 0:  # Standard field
            field_name = self._resolve_std_field_name()
            if not field_name:
                messagebox.showwarning(
                    "No Field Selected",
                    "Please select a standard field from the dropdown.",
                    parent=self.dialog,
                )
                return
        else:  # Custom field
            field_name = self._resolve_custom_field_name()
            if not field_name:
                messagebox.showwarning(
                    "No Field Name",
                    "Please enter a field name.",
                    parent=self.dialog,
                )
                return

            # Reject characters that are structurally significant in GUANO format.
            # ':' is the key-value separator; '\n' terminates a field line.
            # Either character in a key would produce malformed metadata.
            for bad_char, label in ((':', "colon (:)"), ('\n', "newline")):
                if bad_char in field_name:
                    messagebox.showerror(
                        "Invalid Field Name",
                        f"Field names may not contain a {label}.\n\n"
                        "The GUANO specification requires that keys do not "
                        "contain ':' (the key-value separator) or newline characters.",
                        parent=self.dialog,
                    )
                    return

            # Warn when the user typed a bare name with no namespace
            ns = self.ns_var.get().strip()
            if ns == "other\u2026" and "|" not in field_name:
                if not messagebox.askyesno(
                    "No Namespace",
                    f"'{field_name}' has no namespace.\n\n"
                    "The GUANO specification recommends all custom fields use a "
                    f"namespace (e.g. 'User|{field_name}'). Proceed without one?",
                    parent=self.dialog,
                ):
                    return

        value = self.value_var.get().strip()
        if not value:
            messagebox.showwarning(
                "No Value",
                "Please enter a value for the field.",
                parent=self.dialog,
            )
            return

        if field_name in GUANO_PROTECTED_FIELDS:
            if not messagebox.askyesno(
                "Protected Field",
                f"'{field_name}' is a required GUANO meta-field.\n\n"
                "Changing it incorrectly may break compatibility with other "
                "GUANO software. Proceed anyway?",
                icon="warning",
                parent=self.dialog,
            ):
                return

        # Add to pending changes queue
        self.main_app.add_pending_change(field_name, value, 'new')
        
        self.dialog.destroy()
        messagebox.showinfo("Change Queued", 
            f"New field '{field_name}' added to the pending changes queue.\n\n"
            "Click 'Apply All Changes' to process all pending changes.",
            parent=self.main_app.root)


class EditVariableFieldsDialog:
    """Dialog window for editing variable metadata fields (standardizing them)."""
    
    def __init__(self, parent, main_app, variable_fields: Dict[str, List[Tuple[str, Any]]]):
        self.main_app = main_app
        self.variable_fields = variable_fields
        self.entries = {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Variable Fields - Standardize Values")
        self.dialog.geometry("700x550")
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
        main_frame.rowconfigure(2, weight=1)
        
        # Warning label
        warning_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2, padding="10")
        warning_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        warning_frame.columnconfigure(1, weight=1)
        
        ttk.Label(warning_frame, text="⚠️", font=('Helvetica', 16)).grid(
            row=0, column=0, padx=(0, 10), sticky=tk.N)
        
        ttk.Label(warning_frame,
            text="Variable fields have different values across files. "
                 "Entering a new value will OVERWRITE the existing values in ALL files, "
                 "converting the field to a common field.",
            wraplength=600, justify=tk.LEFT, foreground='#CC6600').grid(
            row=0, column=1, sticky=tk.W)
        
        # Instructions
        ttk.Label(main_frame, 
            text="Enter a new value to standardize each field. Leave blank to skip that field.",
            style='Header.TLabel', wraplength=650).grid(row=1, column=0, pady=(0, 10), sticky=tk.W)
        
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
        
        canvas.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        
        # Add entry fields for each variable field
        scrollable_frame.columnconfigure(1, weight=1)
        
        for i, (field, values) in enumerate(sorted(self.variable_fields.items())):
            # Field label with current value info
            field_frame = ttk.LabelFrame(scrollable_frame, text=field, padding="5")
            field_frame.grid(row=i, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                           padx=5, pady=5)
            field_frame.columnconfigure(0, weight=1)
            
            # Show existing values
            values_text = "Current values across files:\n"
            # Show up to 5 examples
            for filename, value in values[:5]:
                display_value = format_value(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                values_text += f"  • {filename}: {display_value}\n"
            
            if len(values) > 5:
                values_text += f"  ... and {len(values) - 5} more file(s)"
            
            ttk.Label(field_frame, text=values_text, 
                     font=('Courier', 9), foreground='#666').grid(
                row=0, column=0, sticky=tk.W, pady=(0, 5))
            
            # New value entry
            entry_frame = ttk.Frame(field_frame)
            entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
            entry_frame.columnconfigure(1, weight=1)
            
            ttk.Label(entry_frame, text="New value:", 
                     font=('Helvetica', 9, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=(0, 5))
            
            entry = ttk.Entry(entry_frame, width=50)
            entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
            
            self.entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.apply_changes).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).grid(row=0, column=1, padx=5)
    
    def apply_changes(self):
        """Collect changes and add them to the pending changes queue."""
        updates = {}
        
        for field, entry in self.entries.items():
            new_value = entry.get().strip()
            
            # Only include fields where user entered a value
            if new_value:
                updates[field] = new_value
        
        if not updates:
            messagebox.showinfo("No Changes", 
                "No fields were modified. Enter values to standardize fields.",
                parent=self.dialog)
            return
        
        # Warn before modifying any protected fields
        protected_changes = [f for f in updates if f in GUANO_PROTECTED_FIELDS]
        if protected_changes:
            names = ", ".join(protected_changes)
            if not messagebox.askyesno(
                "Protected Field",
                f"You are modifying a required GUANO meta-field: {names}\n\n"
                "Changing it incorrectly may break compatibility with other "
                "GUANO software. Proceed anyway?",
                icon="warning",
                parent=self.dialog,
            ):
                return
        
        # Add each change to the queue as 'variable' type
        for field, value in updates.items():
            self.main_app.add_pending_change(field, value, 'variable')
        
        self.dialog.destroy()
        messagebox.showinfo("Changes Queued", 
            f"{len(updates)} variable field standardization(s) added to the pending changes queue.\n\n"
            "Click 'Apply All Changes' to process all pending changes.",
            parent=self.main_app.root)


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
