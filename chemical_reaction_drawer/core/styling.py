"""
Styling system for chemical reaction drawer.

This module provides comprehensive styling capabilities including font management,
color palettes, themes, and visual style controls for chemical structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import json
import os
from pathlib import Path


class FontWeight(Enum):
    """Font weight options."""
    LIGHT = "light"
    NORMAL = "normal"
    BOLD = "bold"
    EXTRA_BOLD = "extra_bold"


class FontStyle(Enum):
    """Font style options."""
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class LineStyle(Enum):
    """Line style options for bonds and structural elements."""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"
    DASH_DOT = "dash_dot"


@dataclass
class Color:
    """Represents a color with RGBA values."""
    r: float  # Red component (0.0-1.0)
    g: float  # Green component (0.0-1.0)
    b: float  # Blue component (0.0-1.0)
    a: float = 1.0  # Alpha component (0.0-1.0)
    
    def __post_init__(self):
        """Validate color components."""
        for component in [self.r, self.g, self.b, self.a]:
            if not 0.0 <= component <= 1.0:
                raise ValueError(f"Color components must be between 0.0 and 1.0, got {component}")
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create color from hex string (e.g., '#FF0000' or 'FF0000')."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: {hex_color}")
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return cls(r, g, b)
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: int = 255) -> 'Color':
        """Create color from RGB values (0-255)."""
        return cls(r/255.0, g/255.0, b/255.0, a/255.0)
    
    def to_hex(self) -> str:
        """Convert to hex string."""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_rgb(self) -> Tuple[int, int, int, int]:
        """Convert to RGB tuple (0-255)."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255)
        )


@dataclass
class Font:
    """Font specification for text rendering."""
    family: str = "Arial"
    size: float = 12.0
    weight: FontWeight = FontWeight.NORMAL
    style: FontStyle = FontStyle.NORMAL
    
    def __post_init__(self):
        """Validate font parameters."""
        if self.size <= 0:
            raise ValueError(f"Font size must be positive, got {self.size}")


@dataclass
class Style:
    """Complete style specification for drawable objects."""
    # Text styling
    font: Font = field(default_factory=Font)
    text_color: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))  # Black
    
    # Line styling
    line_color: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))  # Black
    line_width: float = 1.0
    line_style: LineStyle = LineStyle.SOLID
    
    # Fill styling
    fill_color: Optional[Color] = None
    fill_enabled: bool = False
    
    # Transparency
    opacity: float = 1.0
    
    def __post_init__(self):
        """Validate style parameters."""
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError(f"Opacity must be between 0.0 and 1.0, got {self.opacity}")
        if self.line_width <= 0:
            raise ValueError(f"Line width must be positive, got {self.line_width}")
    
    def copy(self) -> 'Style':
        """Create a copy of this style."""
        return Style(
            font=Font(self.font.family, self.font.size, self.font.weight, self.font.style),
            text_color=Color(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a),
            line_color=Color(self.line_color.r, self.line_color.g, self.line_color.b, self.line_color.a),
            line_width=self.line_width,
            line_style=self.line_style,
            fill_color=Color(self.fill_color.r, self.fill_color.g, self.fill_color.b, self.fill_color.a) if self.fill_color else None,
            fill_enabled=self.fill_enabled,
            opacity=self.opacity
        )
    
    def merge(self, other: 'Style') -> 'Style':
        """Merge this style with another, with other taking precedence."""
        merged = self.copy()
        merged.font = Font(other.font.family, other.font.size, other.font.weight, other.font.style)
        merged.text_color = Color(other.text_color.r, other.text_color.g, other.text_color.b, other.text_color.a)
        merged.line_color = Color(other.line_color.r, other.line_color.g, other.line_color.b, other.line_color.a)
        merged.line_width = other.line_width
        merged.line_style = other.line_style
        merged.fill_color = Color(other.fill_color.r, other.fill_color.g, other.fill_color.b, other.fill_color.a) if other.fill_color else None
        merged.fill_enabled = other.fill_enabled
        merged.opacity = other.opacity
        return merged


@dataclass
class ColorPalette:
    """Collection of colors for chemical structure styling."""
    name: str
    colors: Dict[str, Color] = field(default_factory=dict)
    
    def add_color(self, name: str, color: Color) -> None:
        """Add a color to the palette."""
        self.colors[name] = color
    
    def get_color(self, name: str) -> Optional[Color]:
        """Get a color by name."""
        return self.colors.get(name)
    
    def remove_color(self, name: str) -> bool:
        """Remove a color from the palette."""
        if name in self.colors:
            del self.colors[name]
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert palette to dictionary for serialization."""
        return {
            "name": self.name,
            "colors": {name: color.to_hex() for name, color in self.colors.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorPalette':
        """Create palette from dictionary."""
        palette = cls(data["name"])
        for name, hex_color in data["colors"].items():
            palette.add_color(name, Color.from_hex(hex_color))
        return palette


@dataclass
class Theme:
    """Complete visual theme for the application."""
    name: str
    description: str = ""
    
    # Default styles for different object types
    atom_style: Style = field(default_factory=Style)
    bond_style: Style = field(default_factory=Style)
    text_style: Style = field(default_factory=Style)
    arrow_style: Style = field(default_factory=Style)
    background_color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))  # White
    
    # Element-specific colors
    element_colors: Dict[str, Color] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default element colors if not provided."""
        if not self.element_colors:
            self.element_colors = self._get_default_element_colors()
    
    def _get_default_element_colors(self) -> Dict[str, Color]:
        """Get standard CPK element colors."""
        return {
            'H': Color.from_hex('#FFFFFF'),   # White
            'C': Color.from_hex('#000000'),   # Black
            'N': Color.from_hex('#3050F8'),   # Blue
            'O': Color.from_hex('#FF0D0D'),   # Red
            'F': Color.from_hex('#90E050'),   # Green
            'Cl': Color.from_hex('#1FF01F'),  # Green
            'Br': Color.from_hex('#A62929'),  # Brown
            'I': Color.from_hex('#940094'),   # Purple
            'P': Color.from_hex('#FF8000'),   # Orange
            'S': Color.from_hex('#FFFF30'),   # Yellow
            'B': Color.from_hex('#FFB5B5'),   # Pink
            'Si': Color.from_hex('#F0C8A0'),  # Tan
            'Li': Color.from_hex('#CC80FF'),  # Violet
            'Na': Color.from_hex('#AB5CF2'),  # Violet
            'K': Color.from_hex('#8F40D4'),   # Violet
            'Ca': Color.from_hex('#3DFF00'),  # Green
            'Mg': Color.from_hex('#8AFF00'),  # Green
            'Fe': Color.from_hex('#E06633'),  # Orange
            'Zn': Color.from_hex('#7D80B0'),  # Blue-gray
        }
    
    def get_element_color(self, element: str) -> Color:
        """Get color for a specific element."""
        return self.element_colors.get(element, Color(0.5, 0.5, 0.5))  # Gray default
    
    def set_element_color(self, element: str, color: Color) -> None:
        """Set color for a specific element."""
        self.element_colors[element] = color
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "background_color": self.background_color.to_hex(),
            "element_colors": {elem: color.to_hex() for elem, color in self.element_colors.items()},
            # Note: Style serialization would need additional implementation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary."""
        theme = cls(data["name"], data.get("description", ""))
        theme.background_color = Color.from_hex(data["background_color"])
        theme.element_colors = {
            elem: Color.from_hex(hex_color) 
            for elem, hex_color in data["element_colors"].items()
        }
        return theme


class FontManager:
    """Manages font resources and text rendering capabilities."""
    
    def __init__(self):
        self.available_fonts: List[str] = []
        self.current_font: Font = Font()
        self._load_system_fonts()
    
    def _load_system_fonts(self) -> None:
        """Load available system fonts."""
        # Default fonts that should be available on most systems
        self.available_fonts = [
            "Arial", "Helvetica", "Times New Roman", "Courier New",
            "Verdana", "Georgia", "Comic Sans MS", "Impact",
            "Trebuchet MS", "Arial Black", "Palatino", "Garamond"
        ]
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available font families."""
        return self.available_fonts.copy()
    
    def set_font(self, font: Font) -> None:
        """Set the current font."""
        if font.family not in self.available_fonts:
            # Fall back to Arial if font not available
            font.family = "Arial"
        self.current_font = font
    
    def get_current_font(self) -> Font:
        """Get the current font."""
        return Font(
            self.current_font.family,
            self.current_font.size,
            self.current_font.weight,
            self.current_font.style
        )
    
    def calculate_text_size(self, text: str, font: Optional[Font] = None) -> Tuple[float, float]:
        """Calculate the size of rendered text."""
        if font is None:
            font = self.current_font
        
        # Simple approximation - in real implementation would use actual font metrics
        char_width = font.size * 0.6  # Approximate character width
        char_height = font.size * 1.2  # Approximate character height
        
        lines = text.split('\n')
        width = max(len(line) * char_width for line in lines) if lines else 0
        height = len(lines) * char_height
        
        return width, height


class StyleManager:
    """Central manager for all styling operations."""
    
    def __init__(self):
        self.font_manager = FontManager()
        self.color_palettes: Dict[str, ColorPalette] = {}
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.default_style = Style()
        
        # Initialize with default theme
        self._create_default_theme()
        self._create_default_palettes()
    
    def _create_default_theme(self) -> None:
        """Create and set the default theme."""
        default_theme = Theme(
            name="Default",
            description="Standard chemical drawing theme"
        )
        self.add_theme(default_theme)
        
        # Add all predefined themes
        self.add_theme(create_dark_theme())
        self.add_theme(create_high_contrast_theme())
        self.add_theme(create_publication_theme())
        self.add_theme(create_colorful_theme())
        self.add_theme(create_monochrome_theme())
        self.add_theme(create_presentation_theme())
        
        self.set_theme("Default")
    
    def _create_default_palettes(self) -> None:
        """Create default color palettes."""
        # Standard palette
        standard = ColorPalette("Standard")
        standard.add_color("black", Color(0.0, 0.0, 0.0))
        standard.add_color("white", Color(1.0, 1.0, 1.0))
        standard.add_color("red", Color(1.0, 0.0, 0.0))
        standard.add_color("green", Color(0.0, 1.0, 0.0))
        standard.add_color("blue", Color(0.0, 0.0, 1.0))
        standard.add_color("yellow", Color(1.0, 1.0, 0.0))
        standard.add_color("cyan", Color(0.0, 1.0, 1.0))
        standard.add_color("magenta", Color(1.0, 0.0, 1.0))
        self.add_palette(standard)
        
        # Chemical elements palette
        elements = ColorPalette("Chemical Elements")
        if self.current_theme:
            for element, color in self.current_theme.element_colors.items():
                elements.add_color(element, color)
        self.add_palette(elements)
        
        # Grayscale palette
        grayscale = ColorPalette("Grayscale")
        grayscale.add_color("black", Color(0.0, 0.0, 0.0))
        grayscale.add_color("dark_gray", Color(0.25, 0.25, 0.25))
        grayscale.add_color("medium_gray", Color(0.5, 0.5, 0.5))
        grayscale.add_color("light_gray", Color(0.75, 0.75, 0.75))
        grayscale.add_color("white", Color(1.0, 1.0, 1.0))
        self.add_palette(grayscale)
        
        # Vibrant palette
        vibrant = ColorPalette("Vibrant")
        vibrant.add_color("crimson", Color.from_hex("#DC143C"))
        vibrant.add_color("orange", Color.from_hex("#FF8C00"))
        vibrant.add_color("gold", Color.from_hex("#FFD700"))
        vibrant.add_color("lime", Color.from_hex("#32CD32"))
        vibrant.add_color("dodger_blue", Color.from_hex("#1E90FF"))
        vibrant.add_color("purple", Color.from_hex("#9932CC"))
        vibrant.add_color("hot_pink", Color.from_hex("#FF69B4"))
        vibrant.add_color("spring_green", Color.from_hex("#00FF7F"))
        self.add_palette(vibrant)
        
        # Pastel palette
        pastel = ColorPalette("Pastel")
        pastel.add_color("light_pink", Color.from_hex("#FFB6C1"))
        pastel.add_color("light_blue", Color.from_hex("#ADD8E6"))
        pastel.add_color("light_green", Color.from_hex("#90EE90"))
        pastel.add_color("light_yellow", Color.from_hex("#FFFFE0"))
        pastel.add_color("light_coral", Color.from_hex("#F08080"))
        pastel.add_color("light_purple", Color.from_hex("#DDA0DD"))
        pastel.add_color("light_cyan", Color.from_hex("#E0FFFF"))
        pastel.add_color("peach", Color.from_hex("#FFDAB9"))
        self.add_palette(pastel)
        
        # Professional palette
        professional = ColorPalette("Professional")
        professional.add_color("navy", Color.from_hex("#000080"))
        professional.add_color("maroon", Color.from_hex("#800000"))
        professional.add_color("dark_green", Color.from_hex("#006400"))
        professional.add_color("dark_orange", Color.from_hex("#FF8C00"))
        professional.add_color("steel_blue", Color.from_hex("#4682B4"))
        professional.add_color("saddle_brown", Color.from_hex("#8B4513"))
        professional.add_color("dark_slate_gray", Color.from_hex("#2F4F4F"))
        professional.add_color("indigo", Color.from_hex("#4B0082"))
        self.add_palette(professional)
    
    def add_palette(self, palette: ColorPalette) -> None:
        """Add a color palette."""
        self.color_palettes[palette.name] = palette
    
    def get_palette(self, name: str) -> Optional[ColorPalette]:
        """Get a color palette by name."""
        return self.color_palettes.get(name)
    
    def get_palette_names(self) -> List[str]:
        """Get names of all available palettes."""
        return list(self.color_palettes.keys())
    
    def add_theme(self, theme: Theme) -> None:
        """Add a theme."""
        self.themes[theme.name] = theme
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return self.themes.get(name)
    
    def get_theme_names(self) -> List[str]:
        """Get names of all available themes."""
        return list(self.themes.keys())
    
    def set_theme(self, name: str) -> bool:
        """Set the current theme."""
        theme = self.get_theme(name)
        if theme:
            self.current_theme = theme
            return True
        return False
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the current theme."""
        return self.current_theme
    
    def apply_style_to_objects(self, objects: List[Any], style: Style) -> None:
        """Apply a style to a list of objects."""
        for obj in objects:
            if hasattr(obj, 'style'):
                obj.style = style.copy()
            elif hasattr(obj, 'set_style'):
                obj.set_style(style)
    
    def create_custom_palette(self, name: str, colors: Dict[str, Color]) -> ColorPalette:
        """Create a custom color palette."""
        palette = ColorPalette(name)
        for color_name, color in colors.items():
            palette.add_color(color_name, color)
        self.add_palette(palette)
        return palette
    
    def save_palette(self, palette_name: str, file_path: str) -> bool:
        """Save a palette to file."""
        palette = self.get_palette(palette_name)
        if not palette:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(palette.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def load_palette(self, file_path: str) -> Optional[ColorPalette]:
        """Load a palette from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            palette = ColorPalette.from_dict(data)
            self.add_palette(palette)
            return palette
        except Exception:
            return None
    
    def save_theme(self, theme_name: str, file_path: str) -> bool:
        """Save a theme to file."""
        theme = self.get_theme(theme_name)
        if not theme:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def load_theme(self, file_path: str) -> Optional[Theme]:
        """Load a theme from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            theme = Theme.from_dict(data)
            self.add_theme(theme)
            return theme
        except Exception:
            return None
    
    def get_element_style(self, element: str) -> Style:
        """Get the style for a specific chemical element."""
        style = self.default_style.copy()
        if self.current_theme:
            style.line_color = self.current_theme.get_element_color(element)
            style.text_color = self.current_theme.get_element_color(element)
        return style
    
    def set_line_thickness(self, thickness: float) -> None:
        """Set the default line thickness."""
        if thickness > 0:
            self.default_style.line_width = thickness
    
    def get_line_thickness(self) -> float:
        """Get the current default line thickness."""
        return self.default_style.line_width
    
    def duplicate_palette(self, source_name: str, new_name: str) -> Optional[ColorPalette]:
        """Create a duplicate of an existing palette with a new name."""
        source = self.get_palette(source_name)
        if not source:
            return None
        
        duplicate = ColorPalette(new_name)
        for color_name, color in source.colors.items():
            duplicate.add_color(color_name, Color(color.r, color.g, color.b, color.a))
        
        self.add_palette(duplicate)
        return duplicate
    
    def duplicate_theme(self, source_name: str, new_name: str) -> Optional[Theme]:
        """Create a duplicate of an existing theme with a new name."""
        source = self.get_theme(source_name)
        if not source:
            return None
        
        duplicate = Theme(new_name, f"Copy of {source.description}")
        duplicate.background_color = Color(
            source.background_color.r, 
            source.background_color.g, 
            source.background_color.b, 
            source.background_color.a
        )
        
        # Copy element colors
        for element, color in source.element_colors.items():
            duplicate.set_element_color(element, Color(color.r, color.g, color.b, color.a))
        
        # Copy styles (simplified - in full implementation would copy all style properties)
        duplicate.atom_style = source.atom_style.copy()
        duplicate.bond_style = source.bond_style.copy()
        duplicate.text_style = source.text_style.copy()
        duplicate.arrow_style = source.arrow_style.copy()
        
        self.add_theme(duplicate)
        return duplicate
    
    def remove_palette(self, name: str) -> bool:
        """Remove a palette (cannot remove built-in palettes)."""
        built_in_palettes = {
            "Standard", "Chemical Elements", "Grayscale", 
            "Vibrant", "Pastel", "Professional"
        }
        
        if name in built_in_palettes:
            return False  # Cannot remove built-in palettes
        
        if name in self.color_palettes:
            del self.color_palettes[name]
            return True
        return False
    
    def remove_theme(self, name: str) -> bool:
        """Remove a theme (cannot remove built-in themes)."""
        built_in_themes = {
            "Default", "Dark", "High Contrast", "Publication",
            "Colorful", "Monochrome", "Presentation"
        }
        
        if name in built_in_themes:
            return False  # Cannot remove built-in themes
        
        if name in self.themes:
            # Don't remove if it's the current theme
            if self.current_theme and self.current_theme.name == name:
                return False
            
            del self.themes[name]
            return True
        return False
    
    def export_palette_collection(self, palette_names: List[str], file_path: str) -> bool:
        """Export multiple palettes to a single file."""
        try:
            collection = {
                "type": "palette_collection",
                "palettes": []
            }
            
            for name in palette_names:
                palette = self.get_palette(name)
                if palette:
                    collection["palettes"].append(palette.to_dict())
            
            with open(file_path, 'w') as f:
                json.dump(collection, f, indent=2)
            return True
        except Exception:
            return False
    
    def import_palette_collection(self, file_path: str) -> List[str]:
        """Import multiple palettes from a collection file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if data.get("type") != "palette_collection":
                return []
            
            imported_names = []
            for palette_data in data.get("palettes", []):
                palette = ColorPalette.from_dict(palette_data)
                self.add_palette(palette)
                imported_names.append(palette.name)
            
            return imported_names
        except Exception:
            return []
    
    def get_palette_preview(self, name: str, max_colors: int = 8) -> List[Tuple[str, Color]]:
        """Get a preview of colors from a palette for UI display."""
        palette = self.get_palette(name)
        if not palette:
            return []
        
        colors = list(palette.colors.items())
        return colors[:max_colors]
    
    def search_palettes_by_color(self, target_color: Color, tolerance: float = 0.1) -> List[str]:
        """Find palettes containing colors similar to the target color."""
        matching_palettes = []
        
        for palette_name, palette in self.color_palettes.items():
            for color_name, color in palette.colors.items():
                # Simple color distance calculation
                distance = (
                    (color.r - target_color.r) ** 2 +
                    (color.g - target_color.g) ** 2 +
                    (color.b - target_color.b) ** 2
                ) ** 0.5
                
                if distance <= tolerance:
                    matching_palettes.append(palette_name)
                    break  # Found a match in this palette
        
        return matching_palettes
    
    def get_theme_preview_colors(self, name: str) -> Dict[str, Color]:
        """Get preview colors from a theme for UI display."""
        theme = self.get_theme(name)
        if not theme:
            return {}
        
        preview = {
            "background": theme.background_color,
            "text": theme.atom_style.text_color,
            "line": theme.bond_style.line_color,
        }
        
        # Add a few element colors
        common_elements = ["C", "N", "O", "H"]
        for element in common_elements:
            if element in theme.element_colors:
                preview[f"element_{element}"] = theme.element_colors[element]
        
        return preview


# Predefined themes
def create_dark_theme() -> Theme:
    """Create a dark theme for the application."""
    theme = Theme(
        name="Dark",
        description="Dark theme with light text on dark background",
        background_color=Color(0.1, 0.1, 0.1)  # Dark gray
    )
    
    # Adjust default styles for dark theme
    theme.atom_style.text_color = Color(0.9, 0.9, 0.9)  # Light gray
    theme.bond_style.line_color = Color(0.9, 0.9, 0.9)  # Light gray
    theme.text_style.text_color = Color(0.9, 0.9, 0.9)  # Light gray
    theme.arrow_style.line_color = Color(0.9, 0.9, 0.9)  # Light gray
    
    return theme


def create_high_contrast_theme() -> Theme:
    """Create a high contrast theme for accessibility."""
    theme = Theme(
        name="High Contrast",
        description="High contrast theme for better visibility",
        background_color=Color(1.0, 1.0, 1.0)  # White
    )
    
    # Use high contrast colors
    theme.atom_style.text_color = Color(0.0, 0.0, 0.0)  # Black
    theme.bond_style.line_color = Color(0.0, 0.0, 0.0)  # Black
    theme.bond_style.line_width = 2.0  # Thicker lines
    theme.text_style.text_color = Color(0.0, 0.0, 0.0)  # Black
    theme.arrow_style.line_color = Color(0.0, 0.0, 0.0)  # Black
    theme.arrow_style.line_width = 2.0  # Thicker lines
    
    return theme


def create_publication_theme() -> Theme:
    """Create a theme optimized for scientific publications."""
    theme = Theme(
        name="Publication",
        description="Clean theme optimized for scientific publications",
        background_color=Color(1.0, 1.0, 1.0)  # White
    )
    
    # Use clean, professional styling
    theme.atom_style.font = Font("Times New Roman", 12.0, FontWeight.NORMAL)
    theme.atom_style.text_color = Color(0.0, 0.0, 0.0)  # Black
    theme.bond_style.line_color = Color(0.0, 0.0, 0.0)  # Black
    theme.bond_style.line_width = 1.5  # Slightly thicker for clarity
    theme.text_style.font = Font("Times New Roman", 10.0, FontWeight.NORMAL)
    theme.text_style.text_color = Color(0.0, 0.0, 0.0)  # Black
    theme.arrow_style.line_color = Color(0.0, 0.0, 0.0)  # Black
    theme.arrow_style.line_width = 1.5
    
    return theme


def create_colorful_theme() -> Theme:
    """Create a colorful theme with vibrant element colors."""
    theme = Theme(
        name="Colorful",
        description="Vibrant theme with enhanced element colors",
        background_color=Color(0.95, 0.95, 0.95)  # Light gray
    )
    
    # Enhanced element colors for better visibility
    enhanced_colors = {
        'H': Color.from_hex('#FFFFFF'),   # White
        'C': Color.from_hex('#404040'),   # Dark gray (instead of black)
        'N': Color.from_hex('#1E90FF'),   # Dodger blue
        'O': Color.from_hex('#FF4500'),   # Orange red
        'F': Color.from_hex('#32CD32'),   # Lime green
        'Cl': Color.from_hex('#00FF7F'),  # Spring green
        'Br': Color.from_hex('#8B4513'),  # Saddle brown
        'I': Color.from_hex('#9932CC'),   # Dark orchid
        'P': Color.from_hex('#FF8C00'),   # Dark orange
        'S': Color.from_hex('#FFD700'),   # Gold
        'B': Color.from_hex('#FF69B4'),   # Hot pink
        'Si': Color.from_hex('#DEB887'),  # Burlywood
        'Li': Color.from_hex('#DA70D6'),  # Orchid
        'Na': Color.from_hex('#9370DB'),  # Medium purple
        'K': Color.from_hex('#8A2BE2'),   # Blue violet
        'Ca': Color.from_hex('#00FF00'),  # Lime
        'Mg': Color.from_hex('#ADFF2F'),  # Green yellow
        'Fe': Color.from_hex('#CD853F'),  # Peru
        'Zn': Color.from_hex('#4682B4'),  # Steel blue
    }
    
    theme.element_colors.update(enhanced_colors)
    
    return theme


def create_monochrome_theme() -> Theme:
    """Create a monochrome theme using only grayscale colors."""
    theme = Theme(
        name="Monochrome",
        description="Grayscale theme for monochrome displays or printing",
        background_color=Color(1.0, 1.0, 1.0)  # White
    )
    
    # Use different shades of gray for elements
    gray_colors = {
        'H': Color(0.9, 0.9, 0.9),   # Light gray
        'C': Color(0.0, 0.0, 0.0),   # Black
        'N': Color(0.3, 0.3, 0.3),   # Dark gray
        'O': Color(0.2, 0.2, 0.2),   # Very dark gray
        'F': Color(0.4, 0.4, 0.4),   # Medium-dark gray
        'Cl': Color(0.5, 0.5, 0.5),  # Medium gray
        'Br': Color(0.35, 0.35, 0.35), # Dark-medium gray
        'I': Color(0.25, 0.25, 0.25),  # Very dark gray
        'P': Color(0.45, 0.45, 0.45),  # Medium-light gray
        'S': Color(0.6, 0.6, 0.6),     # Light-medium gray
        'B': Color(0.7, 0.7, 0.7),     # Light gray
        'Si': Color(0.55, 0.55, 0.55), # Medium gray
        'Li': Color(0.8, 0.8, 0.8),    # Very light gray
        'Na': Color(0.75, 0.75, 0.75), # Light gray
        'K': Color(0.65, 0.65, 0.65),  # Medium-light gray
        'Ca': Color(0.85, 0.85, 0.85), # Very light gray
        'Mg': Color(0.8, 0.8, 0.8),    # Very light gray
        'Fe': Color(0.4, 0.4, 0.4),    # Medium-dark gray
        'Zn': Color(0.5, 0.5, 0.5),    # Medium gray
    }
    
    theme.element_colors.update(gray_colors)
    
    return theme


def create_presentation_theme() -> Theme:
    """Create a theme optimized for presentations and slides."""
    theme = Theme(
        name="Presentation",
        description="High visibility theme for presentations and slides",
        background_color=Color(0.05, 0.05, 0.15)  # Dark blue
    )
    
    # Use bright colors for good visibility on dark background
    theme.atom_style.font = Font("Arial", 14.0, FontWeight.BOLD)
    theme.atom_style.text_color = Color(1.0, 1.0, 1.0)  # White
    theme.bond_style.line_color = Color(0.9, 0.9, 0.9)  # Light gray
    theme.bond_style.line_width = 2.5  # Thick lines for visibility
    theme.text_style.font = Font("Arial", 12.0, FontWeight.BOLD)
    theme.text_style.text_color = Color(1.0, 1.0, 1.0)  # White
    theme.arrow_style.line_color = Color(0.9, 0.9, 0.9)  # Light gray
    theme.arrow_style.line_width = 2.5
    
    # Bright element colors for dark background
    bright_colors = {
        'H': Color(1.0, 1.0, 1.0),     # White
        'C': Color(0.8, 0.8, 0.8),     # Light gray
        'N': Color(0.4, 0.7, 1.0),     # Light blue
        'O': Color(1.0, 0.3, 0.3),     # Light red
        'F': Color(0.6, 1.0, 0.6),     # Light green
        'Cl': Color(0.5, 1.0, 0.5),    # Light green
        'Br': Color(0.9, 0.5, 0.3),    # Light brown
        'I': Color(0.8, 0.4, 0.8),     # Light purple
        'P': Color(1.0, 0.7, 0.2),     # Light orange
        'S': Color(1.0, 1.0, 0.4),     # Light yellow
        'B': Color(1.0, 0.8, 0.8),     # Light pink
        'Si': Color(0.9, 0.8, 0.7),    # Light tan
        'Li': Color(0.9, 0.7, 1.0),    # Light violet
        'Na': Color(0.8, 0.6, 1.0),    # Light violet
        'K': Color(0.7, 0.5, 0.9),     # Light violet
        'Ca': Color(0.5, 1.0, 0.3),    # Light green
        'Mg': Color(0.7, 1.0, 0.3),    # Light green
        'Fe': Color(1.0, 0.6, 0.4),    # Light orange
        'Zn': Color(0.6, 0.7, 0.9),    # Light blue-gray
    }
    
    theme.element_colors.update(bright_colors)
    
    return theme