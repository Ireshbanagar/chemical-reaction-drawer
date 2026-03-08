"""
Enhanced tool system for Chemical Reaction Drawer.

Provides comprehensive drawing tools including:
- Text box
- Erasers (circular, square, random)
- Bond line drawers (single, double, triple, wedge, dash, wavy)
- Reaction arrows
- Shape drawers (triangle, square, pentagon, hexagon, heptagon, octagon)
- Ring templates (benzene, benzyl)
- Selection tools
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List


class ToolType(Enum):
    """Available tool types."""
    # Selection and editing
    SELECT = "select"
    TEXT_BOX = "text_box"
    
    # Erasers
    ERASER_CIRCULAR = "eraser_circular"
    ERASER_SQUARE = "eraser_square"
    ERASER_RANDOM = "eraser_random"
    
    # Bond line drawers
    BOND_SINGLE = "bond_single"
    BOND_DOUBLE = "bond_double"
    BOND_TRIPLE = "bond_triple"
    BOND_WEDGE_FRONT = "bond_wedge_front"  # Front bond (solid wedge)
    BOND_DASH_BACK = "bond_dash_back"      # Back bond (dashed wedge)
    BOND_WAVY_UNKNOWN = "bond_wavy_unknown"  # Unknown stereochemistry
    
    # Reaction arrows
    ARROW_REACTION = "arrow_reaction"
    ARROW_EQUILIBRIUM = "arrow_equilibrium"
    ARROW_RESONANCE = "arrow_resonance"
    
    # Table drawer
    TABLE = "table"
    
    # Shape drawers
    SHAPE_TRIANGLE = "shape_triangle"
    SHAPE_SQUARE = "shape_square"
    SHAPE_PENTAGON = "shape_pentagon"
    SHAPE_HEXAGON = "shape_hexagon"
    SHAPE_HEPTAGON = "shape_heptagon"
    SHAPE_OCTAGON = "shape_octagon"
    
    # Ring templates
    RING_BENZENE = "ring_benzene"  # Benzene with alternating double bonds
    RING_BENZYL = "ring_benzyl"    # Benzyl with 3 double bonds
    
    # Atom tool
    ATOM = "atom"


@dataclass
class ToolConfig:
    """Configuration for a drawing tool."""
    name: str
    display_name: str
    icon: str
    category: str
    description: str
    shortcut: Optional[str] = None


class EnhancedToolManager:
    """Manager for all drawing tools."""
    
    def __init__(self):
        self.current_tool = ToolType.SELECT
        self.tool_configs = self._initialize_tool_configs()
        
        # Tool-specific settings
        self.eraser_size = 20  # pixels
        self.bond_length = 50  # pixels
        self.shape_size = 100  # pixels
        self.text_font_size = 12
        self.arrow_length = 100  # pixels
    
    def _initialize_tool_configs(self) -> dict:
        """Initialize tool configurations."""
        return {
            # Selection and Editing
            ToolType.SELECT: ToolConfig(
                "select", "Selection Tool", "🖱️", "Selection",
                "Select and move objects", "S"
            ),
            ToolType.TEXT_BOX: ToolConfig(
                "text_box", "Text Box", "T", "Text",
                "Add text annotations", "T"
            ),
            
            # Erasers
            ToolType.ERASER_CIRCULAR: ToolConfig(
                "eraser_circular", "Circular Eraser", "⭕", "Eraser",
                "Erase with circular brush", "E"
            ),
            ToolType.ERASER_SQUARE: ToolConfig(
                "eraser_square", "Square Eraser", "⬜", "Eraser",
                "Erase with square brush", None
            ),
            ToolType.ERASER_RANDOM: ToolConfig(
                "eraser_random", "Random Eraser", "🎲", "Eraser",
                "Erase with random pattern", None
            ),
            
            # Bond Line Drawers
            ToolType.BOND_SINGLE: ToolConfig(
                "bond_single", "Single Bond", "─", "Bonds",
                "Draw single bond", "1"
            ),
            ToolType.BOND_DOUBLE: ToolConfig(
                "bond_double", "Double Bond", "═", "Bonds",
                "Draw double bond", "2"
            ),
            ToolType.BOND_TRIPLE: ToolConfig(
                "bond_triple", "Triple Bond", "≡", "Bonds",
                "Draw triple bond", "3"
            ),
            ToolType.BOND_WEDGE_FRONT: ToolConfig(
                "bond_wedge_front", "Front Bond (Wedge)", "▶", "Bonds",
                "Draw front stereochemical bond", "W"
            ),
            ToolType.BOND_DASH_BACK: ToolConfig(
                "bond_dash_back", "Back Bond (Dash)", "⋯", "Bonds",
                "Draw back stereochemical bond", "D"
            ),
            ToolType.BOND_WAVY_UNKNOWN: ToolConfig(
                "bond_wavy_unknown", "Unknown Bond (Wavy)", "〰", "Bonds",
                "Draw unknown stereochemistry bond", "U"
            ),
            
            # Reaction Arrows
            ToolType.ARROW_REACTION: ToolConfig(
                "arrow_reaction", "Reaction Arrow", "→", "Arrows",
                "Draw reaction arrow", "R"
            ),
            ToolType.ARROW_EQUILIBRIUM: ToolConfig(
                "arrow_equilibrium", "Equilibrium Arrow", "⇌", "Arrows",
                "Draw equilibrium arrow", None
            ),
            ToolType.ARROW_RESONANCE: ToolConfig(
                "arrow_resonance", "Resonance Arrow", "↔", "Arrows",
                "Draw resonance arrow", None
            ),
            
            # Table
            ToolType.TABLE: ToolConfig(
                "table", "Table", "⊞", "Layout",
                "Insert table", None
            ),
            
            # Shapes
            ToolType.SHAPE_TRIANGLE: ToolConfig(
                "shape_triangle", "Triangle", "△", "Shapes",
                "Draw triangle", None
            ),
            ToolType.SHAPE_SQUARE: ToolConfig(
                "shape_square", "Square", "□", "Shapes",
                "Draw square", None
            ),
            ToolType.SHAPE_PENTAGON: ToolConfig(
                "shape_pentagon", "Pentagon", "⬠", "Shapes",
                "Draw pentagon", None
            ),
            ToolType.SHAPE_HEXAGON: ToolConfig(
                "shape_hexagon", "Hexagon", "⬡", "Shapes",
                "Draw hexagon", None
            ),
            ToolType.SHAPE_HEPTAGON: ToolConfig(
                "shape_heptagon", "Heptagon", "⬢", "Shapes",
                "Draw heptagon", None
            ),
            ToolType.SHAPE_OCTAGON: ToolConfig(
                "shape_octagon", "Octagon", "⬣", "Shapes",
                "Draw octagon", None
            ),
            
            # Ring Templates
            ToolType.RING_BENZENE: ToolConfig(
                "ring_benzene", "Benzene Ring", "⬡", "Rings",
                "Draw benzene ring (alternating double bonds)", "B"
            ),
            ToolType.RING_BENZYL: ToolConfig(
                "ring_benzyl", "Benzyl Ring", "⬢", "Rings",
                "Draw benzyl ring (3 double bonds)", None
            ),
            
            # Atom
            ToolType.ATOM: ToolConfig(
                "atom", "Atom Tool", "⚛", "Basic",
                "Place atoms", "A"
            ),
        }
    
    def set_tool(self, tool_type: ToolType):
        """Set the current tool."""
        self.current_tool = tool_type
    
    def get_current_tool(self) -> ToolType:
        """Get the current tool."""
        return self.current_tool
    
    def get_tool_config(self, tool_type: ToolType) -> ToolConfig:
        """Get configuration for a tool."""
        return self.tool_configs.get(tool_type)
    
    def get_tools_by_category(self, category: str) -> List[ToolType]:
        """Get all tools in a category."""
        return [
            tool_type for tool_type, config in self.tool_configs.items()
            if config.category == category
        ]
    
    def get_all_categories(self) -> List[str]:
        """Get all tool categories."""
        categories = set(config.category for config in self.tool_configs.values())
        return sorted(categories)
    
    def set_eraser_size(self, size: int):
        """Set eraser size."""
        self.eraser_size = max(5, min(100, size))
    
    def set_bond_length(self, length: int):
        """Set default bond length."""
        self.bond_length = max(20, min(200, length))
    
    def set_shape_size(self, size: int):
        """Set default shape size."""
        self.shape_size = max(30, min(300, size))
    
    def set_text_font_size(self, size: int):
        """Set text font size."""
        self.text_font_size = max(8, min(72, size))
    
    def set_arrow_length(self, length: int):
        """Set arrow length."""
        self.arrow_length = max(50, min(300, length))


# Tool categories for organization
TOOL_CATEGORIES = {
    "Basic": "Basic drawing tools",
    "Selection": "Selection and editing tools",
    "Text": "Text annotation tools",
    "Eraser": "Eraser tools with different patterns",
    "Bonds": "Chemical bond drawing tools",
    "Arrows": "Reaction arrow tools",
    "Shapes": "Geometric shape tools",
    "Rings": "Chemical ring templates",
    "Layout": "Layout and organization tools"
}
