"""
AI Assistant dialog for molecule generation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from ..ai import AIAssistant
from ..core.models import Molecule


class AIAssistantDialog:
    """Dialog for AI-powered molecule generation."""
    
    def __init__(self, parent, ai_assistant: AIAssistant, callback: Optional[Callable] = None):
        self.parent = parent
        self.ai_assistant = ai_assistant
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("AI Assistant - Generate Molecule")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_ui()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Generate Molecule from Name",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Status indicator
        status = self.ai_assistant.get_status()
        if status['available']:
            status_text = f"✓ AI Available (Model: Claude 3.5 Sonnet)"
            status_color = "green"
        else:
            status_text = "⚠ AI Unavailable (Using fallback database)"
            status_color = "orange"
        
        status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color
        )
        status_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Molecule Name", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name entry
        self.name_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.name_entry.pack(fill=tk.X, pady=(0, 5))
        self.name_entry.focus()
        
        # Bind Enter key
        self.name_entry.bind('<Return>', lambda e: self._generate())
        
        # Examples
        examples_label = ttk.Label(
            input_frame,
            text="Examples: aspirin, caffeine, glucose, benzene, ethanol",
            font=("Arial", 9),
            foreground="gray"
        )
        examples_label.pack()
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.use_cache_var = tk.BooleanVar(value=True)
        cache_check = ttk.Checkbutton(
            options_frame,
            text="Use cache (faster for repeated queries)",
            variable=self.use_cache_var
        )
        cache_check.pack(anchor=tk.W)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Results text
        self.results_text = tk.Text(
            results_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Generate button
        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate",
            command=self._generate
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add to Canvas button
        self.add_btn = ttk.Button(
            button_frame,
            text="Add to Canvas",
            command=self._add_to_canvas,
            state=tk.DISABLED
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)
    
    def _generate(self):
        """Generate molecule from name."""
        molecule_name = self.name_entry.get().strip()
        
        if not molecule_name:
            self._show_result("Please enter a molecule name.", "error")
            return
        
        # Disable button during generation
        self.generate_btn.config(state=tk.DISABLED)
        self._show_result(f"Generating {molecule_name}...", "info")
        self.dialog.update()
        
        try:
            # Generate molecule
            use_cache = self.use_cache_var.get()
            molecule = self.ai_assistant.generate_from_name(molecule_name, use_cache)
            
            if molecule:
                self.result = molecule
                atom_count = len(molecule.atoms)
                bond_count = len(molecule.bonds)
                formula = molecule.get_molecular_formula()
                
                result_text = f"✓ Successfully generated {molecule_name}\n\n"
                result_text += f"Molecular Formula: {formula}\n"
                result_text += f"Atoms: {atom_count}\n"
                result_text += f"Bonds: {bond_count}\n\n"
                result_text += "Click 'Add to Canvas' to insert the molecule."
                
                self._show_result(result_text, "success")
                self.add_btn.config(state=tk.NORMAL)
            else:
                self._show_result(
                    f"✗ Could not generate {molecule_name}\n\n"
                    "The molecule name was not recognized. Please try:\n"
                    "• A different name or spelling\n"
                    "• A common molecule name\n"
                    "• Checking the examples above",
                    "error"
                )
                self.add_btn.config(state=tk.DISABLED)
        
        except Exception as e:
            self._show_result(f"Error: {str(e)}", "error")
            self.add_btn.config(state=tk.DISABLED)
        
        finally:
            self.generate_btn.config(state=tk.NORMAL)
    
    def _add_to_canvas(self):
        """Add generated molecule to canvas."""
        if self.result and self.callback:
            self.callback(self.result)
            self.dialog.destroy()
    
    def _show_result(self, text: str, result_type: str = "info"):
        """Show result in text widget."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        
        # Color coding
        if result_type == "success":
            self.results_text.tag_add("result", 1.0, tk.END)
            self.results_text.tag_config("result", foreground="green")
        elif result_type == "error":
            self.results_text.tag_add("result", 1.0, tk.END)
            self.results_text.tag_config("result", foreground="red")
        
        self.results_text.config(state=tk.DISABLED)
    
    def show(self):
        """Show the dialog and wait for it to close."""
        self.dialog.wait_window()
        return self.result
