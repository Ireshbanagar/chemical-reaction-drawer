"""
Implementation of drawing tools for the canvas.
"""

import math
from typing import Tuple, List, Optional
from ..core.models import Point2D, Atom, Bond, BondOrder, BondStereo, Molecule
from .enhanced_tools import ToolType


class ToolImplementations:
    """Implementations for all drawing tools."""
    
    @staticmethod
    def draw_single_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a single bond."""
        # Find or create atoms at start and end points
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.SINGLE)
        return None
    
    @staticmethod
    def draw_double_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a double bond."""
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.DOUBLE)
        return None
    
    @staticmethod
    def draw_triple_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a triple bond."""
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.TRIPLE)
        return None
    
    @staticmethod
    def draw_wedge_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a front wedge bond (solid wedge)."""
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.SINGLE, stereo=BondStereo.WEDGE)
        return None
    
    @staticmethod
    def draw_dash_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a back dash bond (dashed wedge)."""
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.SINGLE, stereo=BondStereo.DASHED)
        return None
    
    @staticmethod
    def draw_wavy_bond(canvas, start: Point2D, end: Point2D, molecule: Molecule) -> Optional[Bond]:
        """Draw a wavy bond (unknown stereochemistry)."""
        atom1 = ToolImplementations._get_or_create_atom(canvas, start, molecule)
        atom2 = ToolImplementations._get_or_create_atom(canvas, end, molecule)
        
        if atom1 and atom2 and atom1 != atom2:
            return molecule.add_bond(atom1, atom2, BondOrder.SINGLE, stereo=BondStereo.WAVY)
        return None
    
    @staticmethod
    def draw_polygon(canvas_widget, center: Point2D, size: float, sides: int) -> List[Tuple[float, float]]:
        """Draw a regular polygon."""
        points = []
        angle_step = 2 * math.pi / sides
        start_angle = -math.pi / 2  # Start from top
        
        for i in range(sides):
            angle = start_angle + i * angle_step
            x = center.x + size * math.cos(angle)
            y = center.y + size * math.sin(angle)
            points.append((x, y))
        
        return points
    
    @staticmethod
    def draw_triangle(canvas_widget, center: Point2D, size: float):
        """Draw a triangle."""
        points = ToolImplementations.draw_polygon(canvas_widget, center, size, 3)
        return canvas_widget.create_polygon(points, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_square(canvas_widget, center: Point2D, size: float):
        """Draw a square."""
        half_size = size / 2
        x1, y1 = center.x - half_size, center.y - half_size
        x2, y2 = center.x + half_size, center.y + half_size
        return canvas_widget.create_rectangle(x1, y1, x2, y2, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_pentagon(canvas_widget, center: Point2D, size: float):
        """Draw a pentagon."""
        points = ToolImplementations.draw_polygon(canvas_widget, center, size, 5)
        return canvas_widget.create_polygon(points, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_hexagon(canvas_widget, center: Point2D, size: float):
        """Draw a hexagon."""
        points = ToolImplementations.draw_polygon(canvas_widget, center, size, 6)
        return canvas_widget.create_polygon(points, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_heptagon(canvas_widget, center: Point2D, size: float):
        """Draw a heptagon."""
        points = ToolImplementations.draw_polygon(canvas_widget, center, size, 7)
        return canvas_widget.create_polygon(points, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_octagon(canvas_widget, center: Point2D, size: float):
        """Draw an octagon."""
        points = ToolImplementations.draw_polygon(canvas_widget, center, size, 8)
        return canvas_widget.create_polygon(points, outline="black", fill="", width=2)
    
    @staticmethod
    def draw_benzene_ring(canvas, center: Point2D, size: float, molecule: Molecule) -> Molecule:
        """Draw a benzene ring with alternating double bonds."""
        # Create hexagon of carbon atoms
        atoms = []
        angle_step = 2 * math.pi / 6
        start_angle = -math.pi / 2
        
        for i in range(6):
            angle = start_angle + i * angle_step
            x = center.x + size * math.cos(angle)
            y = center.y + size * math.sin(angle)
            atom = molecule.add_atom("C", Point2D(x, y))
            atoms.append(atom)
        
        # Create bonds (alternating single and double)
        for i in range(6):
            next_i = (i + 1) % 6
            bond_order = BondOrder.DOUBLE if i % 2 == 0 else BondOrder.SINGLE
            molecule.add_bond(atoms[i], atoms[next_i], bond_order)
        
        return molecule
    
    @staticmethod
    def draw_benzyl_ring(canvas, center: Point2D, size: float, molecule: Molecule) -> Molecule:
        """Draw a benzyl ring with 3 double bonds."""
        # Create hexagon of carbon atoms
        atoms = []
        angle_step = 2 * math.pi / 6
        start_angle = -math.pi / 2
        
        for i in range(6):
            angle = start_angle + i * angle_step
            x = center.x + size * math.cos(angle)
            y = center.y + size * math.sin(angle)
            atom = molecule.add_atom("C", Point2D(x, y))
            atoms.append(atom)
        
        # Create bonds (3 double bonds at positions 0, 2, 4)
        for i in range(6):
            next_i = (i + 1) % 6
            bond_order = BondOrder.DOUBLE if i in [0, 2, 4] else BondOrder.SINGLE
            molecule.add_bond(atoms[i], atoms[next_i], bond_order)
        
        return molecule
    
    @staticmethod
    def draw_reaction_arrow(canvas_widget, start: Point2D, end: Point2D):
        """Draw a reaction arrow."""
        # Main arrow line
        arrow_id = canvas_widget.create_line(
            start.x, start.y, end.x, end.y,
            arrow=tk.LAST, width=2, fill="black"
        )
        return arrow_id
    
    @staticmethod
    def draw_equilibrium_arrow(canvas_widget, start: Point2D, end: Point2D):
        """Draw an equilibrium arrow (double arrow)."""
        # Calculate perpendicular offset
        dx = end.x - start.x
        dy = end.y - start.y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return None
        
        # Perpendicular unit vector
        px = -dy / length * 3
        py = dx / length * 3
        
        # Top arrow
        arrow1 = canvas_widget.create_line(
            start.x + px, start.y + py,
            end.x + px, end.y + py,
            arrow=tk.LAST, width=2, fill="black"
        )
        
        # Bottom arrow
        arrow2 = canvas_widget.create_line(
            end.x - px, end.y - py,
            start.x - px, start.y - py,
            arrow=tk.LAST, width=2, fill="black"
        )
        
        return (arrow1, arrow2)
    
    @staticmethod
    def draw_resonance_arrow(canvas_widget, start: Point2D, end: Point2D):
        """Draw a resonance arrow (double-headed arrow)."""
        arrow_id = canvas_widget.create_line(
            start.x, start.y, end.x, end.y,
            arrow=tk.BOTH, width=2, fill="black"
        )
        return arrow_id
    
    @staticmethod
    def draw_text_box(canvas_widget, position: Point2D, text: str, font_size: int = 12):
        """Draw a text box."""
        text_id = canvas_widget.create_text(
            position.x, position.y,
            text=text,
            font=("Arial", font_size),
            fill="black"
        )
        return text_id
    
    @staticmethod
    def erase_circular(canvas_widget, center: Point2D, radius: float):
        """Erase with circular brush."""
        # Find items within radius
        x1, y1 = center.x - radius, center.y - radius
        x2, y2 = center.x + radius, center.y + radius
        items = canvas_widget.find_overlapping(x1, y1, x2, y2)
        
        for item in items:
            # Check if item is within circular radius
            coords = canvas_widget.coords(item)
            if coords:
                item_x, item_y = coords[0], coords[1]
                dist = math.sqrt((item_x - center.x)**2 + (item_y - center.y)**2)
                if dist <= radius:
                    canvas_widget.delete(item)
    
    @staticmethod
    def erase_square(canvas_widget, center: Point2D, size: float):
        """Erase with square brush."""
        half_size = size / 2
        x1, y1 = center.x - half_size, center.y - half_size
        x2, y2 = center.x + half_size, center.y + half_size
        items = canvas_widget.find_overlapping(x1, y1, x2, y2)
        
        for item in items:
            canvas_widget.delete(item)
    
    @staticmethod
    def erase_random(canvas_widget, center: Point2D, size: float):
        """Erase with random pattern."""
        import random
        # Create random points around center
        for _ in range(10):
            offset_x = random.uniform(-size, size)
            offset_y = random.uniform(-size, size)
            x, y = center.x + offset_x, center.y + offset_y
            
            # Erase small area at each point
            items = canvas_widget.find_overlapping(x-5, y-5, x+5, y+5)
            for item in items:
                canvas_widget.delete(item)
    
    @staticmethod
    def _get_or_create_atom(canvas, position: Point2D, molecule: Molecule, 
                           element: str = "C", tolerance: float = 20.0) -> Optional[Atom]:
        """Get existing atom near position or create new one."""
        # Check if there's an atom near this position
        for atom in molecule.atoms:
            dist = math.sqrt((atom.position.x - position.x)**2 + 
                           (atom.position.y - position.y)**2)
            if dist < tolerance:
                return atom
        
        # Create new atom
        return molecule.add_atom(element, position)


# Import tk for arrow constants
import tkinter as tk
