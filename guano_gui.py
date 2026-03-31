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

from guano_metadata_manager import (
    GuanoMetadataManager, format_value,
    GUANO_STANDARD_FIELDS, GUANO_RESERVED_NAMESPACES, GUANO_PROTECTED_FIELDS,
)


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
        
        ttk.Button(button_frame, text="Edit Variable Fields", 
                  command=self.edit_variable_fields).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="Refresh View",
                  command=self.refresh_display).grid(row=0, column=3, padx=5)

        ttk.Button(button_frame, text="Add Field",
                  command=self.add_new_field).grid(row=0, column=4, padx=5)
        
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

        # Close dialog and apply
        self.dialog.destroy()
        self.main_app.apply_field_updates(updates)


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
            btn_frame, text="Add Field", command=self.apply_changes,
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

        self.dialog.destroy()
        self.main_app.apply_field_updates({field_name: value})


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
        
        ttk.Button(button_frame, text="Apply Changes", 
                  command=self.apply_changes).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).grid(row=0, column=1, padx=5)
    
    def apply_changes(self):
        """Collect changes and apply them."""
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
        
        # Final confirmation
        file_count = self.main_app.manager.get_file_count()
        update_list = "\n".join(f"  • {field}: {value}" for field, value in updates.items())
        
        confirm_msg = (
            f"⚠️ This will OVERWRITE existing values in {file_count} files:\n\n"
            f"{update_list}\n\n"
            f"This action will standardize these variable fields. Continue?"
        )
        
        if not messagebox.askyesno("Confirm Overwrite", confirm_msg, 
                                   icon='warning', parent=self.dialog):
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
