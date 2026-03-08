"""
Enhanced tool palette with comprehensive drawing tools.
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Optional, Dict, Callable
from .enhanced_tools import EnhancedToolManager, ToolType, TOOL_CATEGORIES


class EnhancedToolPalette(ttk.Frame):
    """Enhanced tool palette with all drawing tools."""
    
    def __init__(self, parent, app, tool_manager: EnhancedToolManager):
        super().__init__(parent, width=200)
        self.app = app
        self.tool_manager = tool_manager
        self.pack_propagate(False)
        
        # Tool buttons
        self.tool_buttons = {}
        
        # Create scrollable frame
        self._create_scrollable_frame()
        
        # Create tool sections
        self._create_tool_sections()
        
        # Create settings section
        self._create_settings_section()
    
    def _create_scrollable_frame(self):
        """Create scrollable frame for tools."""
        # Create canvas for scrolling
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_tool_sections(self):
        """Create tool sections by category."""
        categories_order = [
            "Basic", "Selection", "Text", "Bonds", 
            "Arrows", "Shapes", "Rings", "Eraser", "Layout"
        ]
        
        for category in categories_order:
            if category in TOOL_CATEGORIES:
                self._create_category_section(category)
    
    def _create_category_section(self, category: str):
        """Create a section for a tool category."""
        # Category label
        label = ttk.Label(
            self.scrollable_frame,
            text=category,
            font=("Arial", 10, "bold"),
            foreground="#2c3e50"
        )
        label.pack(pady=(10, 5), padx=5, anchor="w")
        
        # Tools frame
        tools_frame = ttk.Frame(self.scrollable_frame)
        tools_frame.pack(fill=tk.X, padx=5)
        
        # Get tools in this category
        tools = self.tool_manager.get_tools_by_category(category)
        
        # Create buttons for each tool
        for tool_type in tools:
            config = self.tool_manager.get_tool_config(tool_type)
            self._create_tool_button(tools_frame, tool_type, config)
        
        # Separator
        separator = ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_tool_button(self, parent, tool_type: ToolType, config):
        """Create a button for a tool."""
        # Button frame for icon and text
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=2)
        
        # Create button
        btn_text = f"{config.icon} {config.display_name}"
        if config.shortcut:
            btn_text += f" ({config.shortcut})"
        
        btn = ttk.Button(
            btn_frame,
            text=btn_text,
            command=lambda: self._select_tool(tool_type)
        )
        btn.pack(fill=tk.X)
        
        # Store button reference
        self.tool_buttons[tool_type] = btn
        
        # Tooltip
        self._create_tooltip(btn, config.description)
    
    def _create_tooltip(self, widget, text):
        """Create tooltip for widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip, text=text,
                background="#ffffe0", relief="solid",
                borderwidth=1, font=("Arial", 9)
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def _create_settings_section(self):
        """Create settings section for tool parameters."""
        settings_label = ttk.Label(
            self.scrollable_frame,
            text="Tool Settings",
            font=("Arial", 10, "bold"),
            foreground="#2c3e50"
        )
        settings_label.pack(pady=(10, 5), padx=5, anchor="w")
        
        settings_frame = ttk.Frame(self.scrollable_frame)
        settings_frame.pack(fill=tk.X, padx=5)
        
        # Eraser size
        self._create_slider(
            settings_frame, "Eraser Size:",
            5, 100, 20,
            self.tool_manager.set_eraser_size
        )
        
        # Bond length
        self._create_slider(
            settings_frame, "Bond Length:",
            20, 200, 50,
            self.tool_manager.set_bond_length
        )
        
        # Shape size
        self._create_slider(
            settings_frame, "Shape Size:",
            30, 300, 100,
            self.tool_manager.set_shape_size
        )
        
        # Text font size
        self._create_slider(
            settings_frame, "Text Size:",
            8, 72, 12,
            self.tool_manager.set_text_font_size
        )
        
        # Arrow length
        self._create_slider(
            settings_frame, "Arrow Length:",
            50, 300, 100,
            self.tool_manager.set_arrow_length
        )
    
    def _create_slider(self, parent, label_text: str, from_: int, to: int, 
                      default: int, command: Callable):
        """Create a slider control."""
        # Label
        label = ttk.Label(parent, text=label_text, font=("Arial", 9))
        label.pack(anchor="w", pady=(5, 0))
        
        # Slider frame
        slider_frame = ttk.Frame(parent)
        slider_frame.pack(fill=tk.X, pady=2)
        
        # Value label
        value_var = tk.IntVar(value=default)
        value_label = ttk.Label(slider_frame, textvariable=value_var, width=4)
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = ttk.Scale(
            slider_frame,
            from_=from_, to=to,
            orient=tk.HORIZONTAL,
            variable=value_var,
            command=lambda v: command(int(float(v)))
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _select_tool(self, tool_type: ToolType):
        """Select a tool."""
        self.tool_manager.set_tool(tool_type)
        self._update_button_states()
        
        # Notify app
        if hasattr(self.app, 'on_tool_changed'):
            self.app.on_tool_changed(tool_type)
    
    def _update_button_states(self):
        """Update button states to show active tool."""
        current_tool = self.tool_manager.get_current_tool()
        
        for tool_type, button in self.tool_buttons.items():
            if tool_type == current_tool:
                button.configure(style="Accent.TButton")
            else:
                button.configure(style="TButton")
    
    def set_active_tool(self, tool_type: ToolType):
        """Set active tool externally."""
        self.tool_manager.set_tool(tool_type)
        self._update_button_states()


class CompactToolPalette(ttk.Frame):
    """Compact tool palette with icon-only buttons."""
    
    def __init__(self, parent, app, tool_manager: EnhancedToolManager):
        super().__init__(parent)
        self.app = app
        self.tool_manager = tool_manager
        self.tool_buttons = {}
        
        # Create toolbar
        self._create_toolbar()
    
    def _create_toolbar(self):
        """Create compact toolbar."""
        # Most used tools
        essential_tools = [
            ToolType.SELECT,
            ToolType.ATOM,
            ToolType.BOND_SINGLE,
            ToolType.BOND_DOUBLE,
            ToolType.BOND_TRIPLE,
            ToolType.BOND_WEDGE_FRONT,
            ToolType.BOND_DASH_BACK,
            ToolType.ARROW_REACTION,
            ToolType.RING_BENZENE,
            ToolType.TEXT_BOX,
            ToolType.ERASER_CIRCULAR,
        ]
        
        for tool_type in essential_tools:
            config = self.tool_manager.get_tool_config(tool_type)
            btn = ttk.Button(
                self,
                text=config.icon,
                width=3,
                command=lambda t=tool_type: self._select_tool(t)
            )
            btn.pack(side=tk.LEFT, padx=1)
            self.tool_buttons[tool_type] = btn
            
            # Tooltip
            self._create_tooltip(btn, config.display_name)
        
        # More tools button
        more_btn = ttk.Button(
            self,
            text="⋯",
            width=3,
            command=self._show_all_tools
        )
        more_btn.pack(side=tk.LEFT, padx=1)
    
    def _create_tooltip(self, widget, text):
        """Create tooltip."""
        def show(e):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{e.x_root+10}+{e.y_root+10}")
            tk.Label(tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1).pack()
            widget.tooltip = tooltip
        
        def hide(e):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)
    
    def _select_tool(self, tool_type: ToolType):
        """Select tool."""
        self.tool_manager.set_tool(tool_type)
        self._update_button_states()
        if hasattr(self.app, 'on_tool_changed'):
            self.app.on_tool_changed(tool_type)
    
    def _update_button_states(self):
        """Update button states."""
        current = self.tool_manager.get_current_tool()
        for tool_type, btn in self.tool_buttons.items():
            if tool_type == current:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="TButton")
    
    def _show_all_tools(self):
        """Show all tools dialog."""
        # Create popup with all tools
        popup = tk.Toplevel(self)
        popup.title("All Tools")
        popup.geometry("400x600")
        
        # Create enhanced palette in popup
        palette = EnhancedToolPalette(popup, self.app, self.tool_manager)
        palette.pack(fill=tk.BOTH, expand=True)
