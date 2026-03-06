"""
Main application window for the Chemical Reaction Drawer.

This module provides the main application window with menu system,
toolbar integration, and overall application coordination.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
import os
from pathlib import Path

from .drawing_canvas import DrawingCanvas
from .toolbar import ToolBar
from .tool_palette import ToolPalette
from ..core.models import Molecule
from ..core.file_io import ChemicalFileManager, FileFormat
from ..core.styling import StyleManager
from ..core.chemistry import ChemicalValidator
from ..core.templates import TemplateLibrary
from ..core.reaction import ReactionManager
from ..ai import AIAssistant


class ChemicalDrawerApp:
    """Main application window for the Chemical Reaction Drawer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chemical Reaction Drawer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Application state
        self.current_file = None
        self.is_modified = False
        self.molecules = []
        
        # Error handling and feedback
        self.error_count = 0
        self.last_error_time = 0
        
        # Auto-save and backup
        self.auto_save_enabled = True
        self.auto_save_interval = 300000  # 5 minutes in milliseconds
        self.backup_count = 5
        self.last_auto_save = 0
        
        # Core managers
        self.file_manager = ChemicalFileManager()
        self.style_manager = StyleManager()
        self.chemical_validator = ChemicalValidator()
        self.template_library = TemplateLibrary()
        self.reaction_manager = ReactionManager()
        self.ai_assistant = AIAssistant()  # AI features
        
        # GUI components
        self.canvas = None
        self.toolbar = None
        self.tool_palette = None
        self.status_bar = None
        
        # Initialize GUI with error handling
        try:
            self._setup_gui()
            self._setup_menu()
            self._setup_keyboard_shortcuts()
            self._setup_error_handling()
            self._setup_auto_save()
        except Exception as e:
            self._handle_critical_error("Application initialization failed", e)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_gui(self):
        """Set up the main GUI layout."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create toolbar
        self.toolbar = ToolBar(main_frame, self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Create content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tool palette (left side)
        self.tool_palette = ToolPalette(content_frame, self)
        self.tool_palette.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Create canvas frame
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create drawing canvas
        self.canvas = DrawingCanvas(canvas_frame, self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_bar = ttk.Label(
            main_frame, 
            text="Ready", 
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
    
    def _setup_menu(self):
        """Set up the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="PNG Image...", command=lambda: self.export_image("png"))
        export_menu.add_command(label="SVG Vector...", command=lambda: self.export_image("svg"))
        export_menu.add_command(label="PDF Document...", command=lambda: self.export_image("pdf"))
        export_menu.add_separator()
        export_menu.add_command(label="MOL File...", command=lambda: self.export_chemical("mol"))
        export_menu.add_command(label="SDF File...", command=lambda: self.export_chemical("sdf"))
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=self.delete, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Zoom to Fit", command=self.zoom_to_fit, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Grid", command=self.toggle_grid)
        view_menu.add_checkbutton(label="Snap to Grid", command=self.toggle_snap_to_grid)
        view_menu.add_separator()
        view_menu.add_command(label="3D View", command=self.show_3d_view, accelerator="F3")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Atom Tool", command=lambda: self.set_tool("atom"))
        tools_menu.add_command(label="Bond Tool", command=lambda: self.set_tool("bond"))
        tools_menu.add_command(label="Selection Tool", command=lambda: self.set_tool("select"))
        tools_menu.add_separator()
        tools_menu.add_command(label="Template Library...", command=self.show_template_library)
        tools_menu.add_command(label="Reaction Tools...", command=self.show_reaction_tools)
        tools_menu.add_separator()
        tools_menu.add_command(label="Validate Molecules", command=self.validate_current_molecules)
        tools_menu.add_command(label="Molecular Properties...", command=self.show_molecular_properties)
        tools_menu.add_command(label="Apply Style", command=self.apply_current_style)
        
        # AI menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI Assistant", menu=ai_menu)
        
        # Check AI availability
        ai_status = self.ai_assistant.get_status()
        ai_label = "Generate from Name..." if ai_status['available'] else "Generate from Name... (Fallback Mode)"
        
        ai_menu.add_command(label=ai_label, command=self.show_ai_assistant, accelerator="Ctrl+G")
        ai_menu.add_separator()
        ai_menu.add_command(label="AI Status", command=self.show_ai_status)
        ai_menu.add_command(label="Clear AI Cache", command=self.clear_ai_cache)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts."""
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        
        # Edit operations
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Delete>', lambda e: self.delete())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        
        # View operations
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without numpad
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_to_fit())
        self.root.bind('<F3>', lambda e: self.show_3d_view())
        
        # Tool shortcuts
        self.root.bind('<Key-a>', lambda e: self.set_tool("atom"))
        self.root.bind('<Key-b>', lambda e: self.set_tool("bond"))
        self.root.bind('<Key-s>', lambda e: self.set_tool("select"))
        
        # AI shortcuts
        self.root.bind('<Control-g>', lambda e: self.show_ai_assistant())
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
    
    # File operations
    def new_file(self):
        """Create a new file."""
        if self._check_unsaved_changes():
            self.molecules = []
            self.current_file = None
            self.is_modified = False
            self.canvas.clear()
            self._update_title()
            self.set_status("New file created")
    
    def open_file(self):
        """Open an existing file."""
        try:
            if not self._check_unsaved_changes():
                return
            
            file_path = filedialog.askopenfilename(
                title="Open Chemical Structure",
                filetypes=[
                    ("All Supported", "*.crd;*.mol;*.sdf;*.cdx"),
                    ("Chemical Reaction Drawer", "*.crd"),
                    ("MOL Files", "*.mol"),
                    ("SDF Files", "*.sdf"),
                    ("ChemDraw Files", "*.cdx"),
                    ("All Files", "*.*")
                ]
            )
            
            if file_path:
                # Load molecules from file
                molecules = self.file_manager.load_multiple_molecules(file_path)
                if molecules:
                    self.molecules = molecules
                    self.current_file = file_path
                    self.is_modified = False
                    self.canvas.load_molecules(molecules)
                    self._update_title()
                    self.set_status(f"Opened {os.path.basename(file_path)}")
                    self.show_user_feedback(f"Successfully opened {os.path.basename(file_path)}", "info")
                else:
                    self.show_user_feedback("Failed to load file - file may be corrupted or unsupported", "error")
                    
        except Exception as e:
            self._handle_error("File Open Error", e)
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path = filedialog.asksaveasfilename(
            title="Save Chemical Structure",
            defaultextension=".crd",
            filetypes=[
                ("Chemical Reaction Drawer", "*.crd"),
                ("MOL Files", "*.mol"),
                ("SDF Files", "*.sdf"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """Save molecules to the specified file."""
        try:
            # Get current molecules from canvas
            self.molecules = self.canvas.get_molecules()
            
            if not self.molecules:
                self.show_user_feedback("No molecules to save", "warning")
                return
            
            # Save based on file extension
            success = False
            if file_path.endswith('.crd'):
                # Save as native format with multiple molecules
                success = self.file_manager.native_manager.save_project(
                    file_path, self.molecules
                )
            elif file_path.endswith('.sdf'):
                # Save as SDF with multiple molecules
                success = self.file_manager.sdf_manager.save_sdf(
                    file_path, self.molecules
                )
            else:
                # Save first molecule only for single-molecule formats
                success = self.file_manager.save_file(
                    file_path, self.molecules[0] if self.molecules else Molecule()
                )
            
            if success:
                self.current_file = file_path
                self.is_modified = False
                self._update_title()
                self.set_status(f"Saved {os.path.basename(file_path)}")
                self.show_user_feedback(f"Successfully saved {os.path.basename(file_path)}", "info")
            else:
                self.show_user_feedback("Failed to save file - check file permissions", "error")
                
        except Exception as e:
            self._handle_error("File Save Error", e)
    
    def export_image(self, format_type: str):
        """Export current view as image."""
        file_path = filedialog.asksaveasfilename(
            title=f"Export as {format_type.upper()}",
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}")]
        )
        
        if file_path:
            try:
                success = self.canvas.export_image(file_path, format_type)
                if success:
                    self.set_status(f"Exported {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", f"Failed to export {format_type.upper()}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_chemical(self, format_type: str):
        """Export as chemical file format."""
        file_path = filedialog.asksaveasfilename(
            title=f"Export as {format_type.upper()}",
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}")]
        )
        
        if file_path:
            try:
                molecules = self.canvas.get_molecules()
                if not molecules:
                    messagebox.showwarning("Warning", "No molecules to export")
                    return
                
                success = self.file_manager.save_file(
                    file_path, molecules[0], 
                    FileFormat.MOL if format_type == "mol" else FileFormat.SDF
                )
                
                if success:
                    self.set_status(f"Exported {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", f"Failed to export {format_type.upper()}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    # Edit operations
    def undo(self):
        """Undo the last operation."""
        if self.canvas:
            self.canvas.undo()
            self.set_status("Undo")
    
    def redo(self):
        """Redo the last undone operation."""
        if self.canvas:
            self.canvas.redo()
            self.set_status("Redo")
    
    def cut(self):
        """Cut selected objects."""
        if self.canvas:
            self.canvas.cut()
            self.set_status("Cut")
    
    def copy(self):
        """Copy selected objects."""
        if self.canvas:
            self.canvas.copy()
            self.set_status("Copy")
    
    def paste(self):
        """Paste objects from clipboard."""
        if self.canvas:
            self.canvas.paste()
            self.set_status("Paste")
    
    def delete(self):
        """Delete selected objects."""
        if self.canvas:
            self.canvas.delete_selected()
            self.set_status("Delete")
    
    def select_all(self):
        """Select all objects."""
        if self.canvas:
            self.canvas.select_all()
            self.set_status("Select All")
    
    # View operations
    def zoom_in(self):
        """Zoom in on the canvas."""
        if self.canvas:
            self.canvas.zoom_in()
            self.set_status("Zoom In")
    
    def zoom_out(self):
        """Zoom out on the canvas."""
        if self.canvas:
            self.canvas.zoom_out()
            self.set_status("Zoom Out")
    
    def zoom_to_fit(self):
        """Zoom to fit all content."""
        if self.canvas:
            self.canvas.zoom_to_fit()
            self.set_status("Zoom to Fit")
    
    def toggle_grid(self):
        """Toggle grid display."""
        if self.canvas:
            self.canvas.toggle_grid()
            self.set_status("Grid toggled")
    
    def toggle_snap_to_grid(self):
        """Toggle snap to grid."""
        if self.canvas:
            self.canvas.toggle_snap_to_grid()
            self.set_status("Snap to grid toggled")
    
    def show_3d_view(self):
        """Show 3D view of current molecule."""
        try:
            from .viewer_3d import Viewer3D
            molecules = self.canvas.get_molecules()
            if molecules:
                viewer = Viewer3D(self.root, molecules[0])
                viewer.show()
                self.set_status("3D viewer opened")
            else:
                self.show_user_feedback("No molecule to display in 3D. Create a molecule first.", "info")
        except ImportError as e:
            self._handle_error("3D Viewer Import Error", e)
            self.show_user_feedback("3D viewer not available - missing dependencies", "error")
        except Exception as e:
            self._handle_error("3D Viewer Error", e)
    
    # Tool operations
    def set_tool(self, tool_name: str):
        """Set the active drawing tool."""
        if self.canvas:
            self.canvas.set_tool(tool_name)
            self.set_status(f"Tool: {tool_name.title()}")
        
        # Update tool palette selection
        if self.tool_palette:
            self.tool_palette.set_active_tool(tool_name)
    
    def show_template_library(self):
        """Show the template library dialog."""
        try:
            from .template_dialog import TemplateDialog
            dialog = TemplateDialog(self.root, self)
            dialog.show()
        except ImportError:
            messagebox.showerror("Error", "Template library not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show template library: {str(e)}")
    
    def show_reaction_tools(self):
        """Show the reaction tools dialog."""
        try:
            from .reaction_dialog import ReactionDialog
            dialog = ReactionDialog(self.root, self)
            dialog.show()
        except ImportError:
            messagebox.showerror("Error", "Reaction tools not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show reaction tools: {str(e)}")
    
    def show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About Chemical Reaction Drawer",
            "Chemical Reaction Drawer v1.0\n\n"
            "A comprehensive desktop application for creating,\n"
            "editing, and visualizing chemical structures and reactions.\n\n"
            "Features:\n"
            "• 2D and 3D molecular visualization\n"
            "• Chemical structure drawing and editing\n"
            "• Reaction scheme creation\n"
            "• Multiple file format support\n"
            "• Template library\n"
            "• Chemical validation\n\n"
            "Built with Python and Tkinter"
        )
    
    # Integration methods
    def validate_current_molecules(self):
        """Validate current molecules and show results."""
        try:
            molecules = self.canvas.get_molecules()
            if not molecules:
                messagebox.showinfo("Validation", "No molecules to validate")
                return
            
            validation_results = []
            for i, molecule in enumerate(molecules):
                result = self.chemical_validator.validate_structure(molecule)
                validation_results.append(f"Molecule {i+1}: {'Valid' if result.is_valid else 'Invalid'}")
                if not result.is_valid:
                    validation_results.extend([f"  - {error}" for error in result.errors])
            
            messagebox.showinfo("Chemical Validation", "\n".join(validation_results))
            
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
    
    def show_molecular_properties(self):
        """Show molecular properties for current molecules."""
        try:
            molecules = self.canvas.get_molecules()
            if not molecules:
                messagebox.showinfo("Properties", "No molecules to analyze")
                return
            
            properties_text = []
            for i, molecule in enumerate(molecules):
                properties = self.chemical_validator.calculate_properties(molecule)
                properties_text.append(f"Molecule {i+1}:")
                properties_text.append(f"  Formula: {properties.molecular_formula}")
                properties_text.append(f"  Weight: {properties.molecular_weight:.2f}")
                properties_text.append(f"  Atoms: {len(molecule.atoms)}")
                properties_text.append(f"  Bonds: {len(molecule.bonds)}")
                properties_text.append("")
            
            messagebox.showinfo("Molecular Properties", "\n".join(properties_text))
            
        except Exception as e:
            messagebox.showerror("Error", f"Property calculation failed: {str(e)}")
    
    def apply_current_style(self):
        """Apply current style settings to the canvas."""
        try:
            # Get current style settings
            current_style = self.style_manager.get_current_style()
            
            # Apply to canvas
            if hasattr(self.canvas, 'apply_style'):
                self.canvas.apply_style(current_style)
                self.canvas._redraw_canvas()
                self.set_status("Style applied")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply style: {str(e)}")
    
    def integrate_3d_with_2d(self):
        """Integrate 3D coordinates with 2D drawing."""
        try:
            molecules = self.canvas.get_molecules()
            if not molecules:
                return
            
            # Update 3D coordinates for all molecules
            for molecule in molecules:
                # Generate 3D coordinates if not present
                if not any(atom.position_3d for atom in molecule.atoms):
                    from ..core.molecule_3d import Molecule3D
                    mol_3d = Molecule3D(molecule)
                    mol_3d.generate_3d_coordinates()
            
            self.set_status("3D coordinates updated")
            
        except Exception as e:
            print(f"3D integration error: {e}")
    
    def auto_validate_on_change(self):
        """Automatically validate molecules when they change."""
        try:
            molecules = self.canvas.get_molecules()
            validation_issues = []
            
            for molecule in molecules:
                result = self.chemical_validator.validate_structure(molecule)
                if not result.is_valid:
                    validation_issues.extend(result.errors)
            
            if validation_issues:
                self.set_status(f"Validation issues: {len(validation_issues)}")
            else:
                self.set_status("All molecules valid")
                
        except Exception as e:
            print(f"Auto-validation error: {e}")
    
    # Utility methods
    def set_status(self, message: str):
        """Set the status bar message."""
        if self.status_bar:
            self.status_bar.config(text=message)
    
    def _setup_error_handling(self):
        """Set up comprehensive error handling."""
        # Set up global exception handler
        self.root.report_callback_exception = self._handle_tk_error
    
    def _setup_auto_save(self):
        """Set up auto-save and backup functionality."""
        if self.auto_save_enabled:
            self._schedule_auto_save()
    
    def _schedule_auto_save(self):
        """Schedule the next auto-save."""
        if self.auto_save_enabled:
            self.root.after(self.auto_save_interval, self._perform_auto_save)
    
    def _perform_auto_save(self):
        """Perform auto-save if needed."""
        try:
            if self.is_modified and self.canvas.get_molecules():
                # Create backup filename
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                
                if self.current_file:
                    # Use current file directory
                    file_dir = os.path.dirname(self.current_file)
                    file_name = os.path.splitext(os.path.basename(self.current_file))[0]
                    backup_path = os.path.join(file_dir, f"{file_name}_backup_{timestamp}.crd")
                else:
                    # Use temp directory
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    backup_path = os.path.join(temp_dir, f"chemical_drawer_backup_{timestamp}.crd")
                
                # Save backup
                molecules = self.canvas.get_molecules()
                if self.file_manager.native_manager.save_project(backup_path, molecules):
                    self.set_status(f"Auto-saved backup: {os.path.basename(backup_path)}")
                    self._cleanup_old_backups()
                
        except Exception as e:
            print(f"Auto-save error: {e}")
        
        # Schedule next auto-save
        self._schedule_auto_save()
    
    def _cleanup_old_backups(self):
        """Clean up old backup files."""
        try:
            if self.current_file:
                file_dir = os.path.dirname(self.current_file)
                file_name = os.path.splitext(os.path.basename(self.current_file))[0]
                
                # Find backup files
                backup_files = []
                for file in os.listdir(file_dir):
                    if file.startswith(f"{file_name}_backup_") and file.endswith(".crd"):
                        backup_path = os.path.join(file_dir, file)
                        backup_files.append((backup_path, os.path.getmtime(backup_path)))
                
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda x: x[1], reverse=True)
                
                # Remove old backups
                for backup_path, _ in backup_files[self.backup_count:]:
                    try:
                        os.remove(backup_path)
                    except OSError:
                        pass  # Ignore errors when removing backups
                        
        except Exception as e:
            print(f"Backup cleanup error: {e}")
    
    def create_manual_backup(self):
        """Create a manual backup of the current work."""
        try:
            molecules = self.canvas.get_molecules()
            if not molecules:
                self.show_user_feedback("No molecules to backup", "warning")
                return
            
            # Choose backup location
            backup_path = filedialog.asksaveasfilename(
                title="Create Backup",
                defaultextension=".crd",
                filetypes=[("Chemical Reaction Drawer", "*.crd")],
                initialfilename=f"backup_{time.strftime('%Y%m%d_%H%M%S')}.crd"
            )
            
            if backup_path:
                if self.file_manager.native_manager.save_project(backup_path, molecules):
                    self.show_user_feedback(f"Backup created: {os.path.basename(backup_path)}", "info")
                else:
                    self.show_user_feedback("Failed to create backup", "error")
                    
        except Exception as e:
            self._handle_error("Backup Creation Error", e)
    
    def toggle_auto_save(self):
        """Toggle auto-save functionality."""
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self._schedule_auto_save()
            self.set_status("Auto-save enabled")
        else:
            self.set_status("Auto-save disabled")
    
    def recover_from_backup(self):
        """Recover work from a backup file."""
        try:
            backup_path = filedialog.askopenfilename(
                title="Recover from Backup",
                filetypes=[
                    ("Chemical Reaction Drawer", "*.crd"),
                    ("All Files", "*.*")
                ]
            )
            
            if backup_path:
                if self._check_unsaved_changes():
                    molecules = self.file_manager.load_multiple_molecules(backup_path)
                    if molecules:
                        self.molecules = molecules
                        self.canvas.load_molecules(molecules)
                        self.is_modified = True
                        self._update_title()
                        self.show_user_feedback(f"Recovered from backup: {os.path.basename(backup_path)}", "info")
                    else:
                        self.show_user_feedback("Failed to load backup file", "error")
                        
        except Exception as e:
            self._handle_error("Backup Recovery Error", e)
    
    def _handle_tk_error(self, exc_type, exc_value, exc_traceback):
        """Handle tkinter callback exceptions."""
        import traceback
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self._handle_error("GUI Error", exc_value, error_msg)
    
    def _handle_error(self, title: str, error: Exception, details: str = None):
        """Handle errors with user feedback."""
        import time
        
        # Prevent error spam
        current_time = time.time()
        if current_time - self.last_error_time < 1.0:  # Less than 1 second since last error
            self.error_count += 1
            if self.error_count > 5:  # Too many errors in short time
                return
        else:
            self.error_count = 0
        
        self.last_error_time = current_time
        
        # Log error details
        if details:
            print(f"Error: {title}")
            print(f"Details: {details}")
        
        # Show user-friendly error message
        error_message = str(error)
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        
        self.set_status(f"Error: {error_message}")
        
        # Show detailed error dialog for critical errors
        if "critical" in title.lower() or "initialization" in title.lower():
            messagebox.showerror(title, f"{error_message}\n\nSee console for details.")
    
    def _handle_critical_error(self, title: str, error: Exception):
        """Handle critical errors that may require application restart."""
        import traceback
        error_details = traceback.format_exc()
        
        print(f"CRITICAL ERROR: {title}")
        print(error_details)
        
        messagebox.showerror(
            f"Critical Error: {title}",
            f"A critical error occurred: {str(error)}\n\n"
            "The application may not function correctly.\n"
            "Please restart the application.\n\n"
            "Error details have been printed to the console."
        )
    
    def show_user_feedback(self, message: str, message_type: str = "info"):
        """Show user feedback with different types."""
        if message_type == "info":
            messagebox.showinfo("Information", message)
        elif message_type == "warning":
            messagebox.showwarning("Warning", message)
        elif message_type == "error":
            messagebox.showerror("Error", message)
        
        # Also update status bar
        self.set_status(message)
    
    def mark_modified(self):
        """Mark the document as modified."""
        self.is_modified = True
        self._update_title()
        
        # Auto-validate molecules when they change
        self.auto_validate_on_change()
        
        # Update 3D coordinates
        self.integrate_3d_with_2d()
    
    def _update_title(self):
        """Update the window title."""
        title = "Chemical Reaction Drawer"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.root.title(title)
    
    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user if needed."""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?"
            )
            if result is True:  # Yes - save
                self.save_file()
                return not self.is_modified  # Only proceed if save was successful
            elif result is False:  # No - don't save
                return True
            else:  # Cancel
                return False
        return True
    
    def _on_closing(self):
        """Handle application closing."""
        if self._check_unsaved_changes():
            self.root.destroy()
    
    # AI Assistant methods
    def show_ai_assistant(self):
        """Show the AI Assistant dialog."""
        try:
            from .ai_dialog import AIAssistantDialog
            
            def add_molecule_callback(molecule):
                """Callback to add generated molecule to canvas."""
                if molecule and hasattr(self.canvas, 'add_molecule'):
                    self.canvas.add_molecule(molecule)
                    self.mark_modified()
                    self.set_status(f"Added molecule: {molecule.get_molecular_formula()}")
            
            # Show dialog
            dialog = AIAssistantDialog(self.root, self.ai_assistant, add_molecule_callback)
            dialog.show()
            
        except Exception as e:
            self._handle_error("AI Assistant Error", e)
    
    def show_ai_status(self):
        """Show AI Assistant status information."""
        try:
            status = self.ai_assistant.get_status()
            
            status_text = "AI Assistant Status\n\n"
            
            if status['available']:
                status_text += "✓ Amazon Bedrock: Connected\n"
                status_text += f"Model: {status['model']}\n"
                status_text += "Region: us-east-1\n\n"
                status_text += "Features:\n"
                status_text += "• Generate molecules from names\n"
                status_text += "• AI-powered structure recognition\n"
                status_text += "• Smart molecule suggestions\n"
            else:
                status_text += "⚠ Amazon Bedrock: Not Available\n\n"
                status_text += "Running in fallback mode with built-in database.\n\n"
                status_text += "To enable AI features:\n"
                status_text += "1. Install boto3: pip install boto3\n"
                status_text += "2. Configure AWS credentials\n"
                status_text += "3. Ensure Bedrock access in us-east-1\n"
            
            status_text += f"\nCache: {status['cache_size']} molecules cached"
            
            messagebox.showinfo("AI Assistant Status", status_text)
            
        except Exception as e:
            self._handle_error("AI Status Error", e)
    
    def clear_ai_cache(self):
        """Clear the AI Assistant cache."""
        try:
            self.ai_assistant.clear_cache()
            self.set_status("AI cache cleared")
            messagebox.showinfo("Cache Cleared", "AI molecule cache has been cleared.")
        except Exception as e:
            self._handle_error("Cache Clear Error", e)


def main():
    """Main entry point for the application."""
    app = ChemicalDrawerApp()
    app.run()


if __name__ == "__main__":
    main()