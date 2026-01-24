"""
Reaction drawing system for the Chemical Reaction Drawer.

This module provides classes and functionality for creating and managing
chemical reactions, including reaction arrows, annotations, and reaction
component positioning.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .models import Molecule, Point2D


class ArrowType(Enum):
    """Types of reaction arrows."""
    REACTION = "reaction"           # Standard reaction arrow (→)
    EQUILIBRIUM = "equilibrium"     # Equilibrium arrows (⇌)
    RESONANCE = "resonance"         # Resonance arrow (↔)
    CURVED = "curved"              # Curved electron movement arrow
    RETROSYNTHETIC = "retrosynthetic"  # Retrosynthetic arrow (⇒)


class ArrowStyle(Enum):
    """Visual styles for arrows."""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


@dataclass
class ReactionConditions:
    """Reaction conditions and annotations."""
    temperature: Optional[str] = None
    pressure: Optional[str] = None
    catalyst: Optional[str] = None
    solvent: Optional[str] = None
    time: Optional[str] = None
    custom_text: Optional[str] = None
    
    def to_display_text(self) -> str:
        """Convert conditions to display text."""
        parts = []
        if self.temperature:
            parts.append(self.temperature)
        if self.pressure:
            parts.append(self.pressure)
        if self.catalyst:
            parts.append(self.catalyst)
        if self.solvent:
            parts.append(self.solvent)
        if self.time:
            parts.append(self.time)
        if self.custom_text:
            parts.append(self.custom_text)
        return ", ".join(parts)


@dataclass
class TextAnnotation:
    """Text annotation for reactions."""
    text: str
    position: Point2D
    font_size: float = 12.0
    font_family: str = "Arial"
    color: tuple = (0, 0, 0)  # RGB
    alignment: str = "center"  # left, center, right
    
    def get_bounds(self) -> tuple:
        """Get approximate text bounds (width, height)."""
        # Simple approximation - in real implementation would use font metrics
        char_width = self.font_size * 0.6
        char_height = self.font_size
        width = len(self.text) * char_width
        height = char_height
        return (width, height)


class ReactionArrow:
    """Represents a reaction arrow with positioning and styling."""
    
    def __init__(self, arrow_type: ArrowType = ArrowType.REACTION,
                 start_point: Optional[Point2D] = None,
                 end_point: Optional[Point2D] = None):
        self.arrow_type = arrow_type
        self.start_point = start_point or Point2D(0, 0)
        self.end_point = end_point or Point2D(100, 0)
        self.style = ArrowStyle.SOLID
        self.line_width = 2.0
        self.color = (0, 0, 0)  # RGB
        self.conditions = ReactionConditions()
        self.annotations: List[TextAnnotation] = []
        
    def set_position(self, start: Point2D, end: Point2D):
        """Set arrow start and end positions."""
        self.start_point = start
        self.end_point = end
        
    def get_length(self) -> float:
        """Calculate arrow length."""
        return self.start_point.distance_to(self.end_point)
        
    def get_center_point(self) -> Point2D:
        """Get the center point of the arrow."""
        return Point2D(
            (self.start_point.x + self.end_point.x) / 2,
            (self.start_point.y + self.end_point.y) / 2
        )
        
    def get_angle(self) -> float:
        """Get arrow angle in radians."""
        import math
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y
        return math.atan2(dy, dx)
        
    def add_annotation(self, text: str, position: str = "above") -> TextAnnotation:
        """Add text annotation to the arrow."""
        center = self.get_center_point()
        
        # Position annotation relative to arrow
        if position == "above":
            annotation_pos = Point2D(center.x, center.y - 20)
        elif position == "below":
            annotation_pos = Point2D(center.x, center.y + 20)
        elif position == "left":
            annotation_pos = Point2D(center.x - 30, center.y)
        elif position == "right":
            annotation_pos = Point2D(center.x + 30, center.y)
        else:  # center
            annotation_pos = center
            
        annotation = TextAnnotation(text=text, position=annotation_pos)
        self.annotations.append(annotation)
        return annotation
        
    def set_conditions(self, conditions: ReactionConditions):
        """Set reaction conditions."""
        self.conditions = conditions
        # Automatically create annotation for conditions if they exist
        conditions_text = conditions.to_display_text()
        if conditions_text:
            self.add_annotation(conditions_text, "above")
            
    def get_arrow_points(self) -> List[Point2D]:
        """Get points for drawing the arrow shape."""
        import math
        
        # Calculate arrow head points
        angle = self.get_angle()
        head_length = 15.0
        head_angle = math.pi / 6  # 30 degrees
        
        # Arrow head points
        head_left = Point2D(
            self.end_point.x - head_length * math.cos(angle - head_angle),
            self.end_point.y - head_length * math.sin(angle - head_angle)
        )
        head_right = Point2D(
            self.end_point.x - head_length * math.cos(angle + head_angle),
            self.end_point.y - head_length * math.sin(angle + head_angle)
        )
        
        if self.arrow_type == ArrowType.EQUILIBRIUM:
            # Double arrow - return points for both arrows
            offset = 5.0  # Offset between arrows
            perp_angle = angle + math.pi / 2
            
            # Top arrow
            start_top = Point2D(
                self.start_point.x + offset * math.cos(perp_angle),
                self.start_point.y + offset * math.sin(perp_angle)
            )
            end_top = Point2D(
                self.end_point.x + offset * math.cos(perp_angle),
                self.end_point.y + offset * math.sin(perp_angle)
            )
            
            # Bottom arrow (reversed)
            start_bottom = Point2D(
                self.start_point.x - offset * math.cos(perp_angle),
                self.start_point.y - offset * math.sin(perp_angle)
            )
            end_bottom = Point2D(
                self.end_point.x - offset * math.cos(perp_angle),
                self.end_point.y - offset * math.sin(perp_angle)
            )
            
            return [start_top, end_top, head_left, head_right, start_bottom, end_bottom]
        else:
            # Single arrow
            return [self.start_point, self.end_point, head_left, head_right]


class ReactionComponent:
    """Represents a component in a chemical reaction (reactant, product, catalyst)."""
    
    def __init__(self, molecule: Molecule, role: str = "reactant"):
        self.molecule = molecule
        self.role = role  # reactant, product, catalyst, solvent
        self.position = Point2D(0, 0)
        self.coefficient = 1.0  # Stoichiometric coefficient
        
    def set_position(self, position: Point2D):
        """Set the position of this component."""
        self.position = position
        # Update molecule position to match
        if self.molecule.atoms:
            # Calculate offset to move molecule to new position
            current_center = self.molecule.get_center_point()
            offset_x = position.x - current_center.x
            offset_y = position.y - current_center.y
            
            # Move all atoms
            for atom in self.molecule.atoms:
                atom.position = Point2D(
                    atom.position.x + offset_x,
                    atom.position.y + offset_y
                )


class SideProduct:
    """Represents a side product or byproduct in a reaction."""
    
    def __init__(self, molecule: Molecule, yield_percentage: float = 0.0):
        self.molecule = molecule
        self.yield_percentage = yield_percentage  # 0-100
        self.is_major = yield_percentage > 50.0
        self.position = Point2D(0, 0)
        
    def set_position(self, position: Point2D):
        """Set the position of this side product."""
        self.position = position


class Reaction:
    """Represents a complete chemical reaction with all components."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.reactants: List[ReactionComponent] = []
        self.products: List[ReactionComponent] = []
        self.catalysts: List[ReactionComponent] = []
        self.solvents: List[ReactionComponent] = []
        self.side_products: List[SideProduct] = []
        self.arrows: List[ReactionArrow] = []
        self.conditions = ReactionConditions()
        self.reaction_type = "general"  # general, synthesis, decomposition, etc.
        self.yield_percentage: Optional[float] = None
        
    def add_reactant(self, molecule: Molecule, coefficient: float = 1.0) -> ReactionComponent:
        """Add a reactant to the reaction."""
        component = ReactionComponent(molecule, "reactant")
        component.coefficient = coefficient
        self.reactants.append(component)
        return component
        
    def add_product(self, molecule: Molecule, coefficient: float = 1.0) -> ReactionComponent:
        """Add a product to the reaction."""
        component = ReactionComponent(molecule, "product")
        component.coefficient = coefficient
        self.products.append(component)
        return component
        
    def add_catalyst(self, molecule: Molecule) -> ReactionComponent:
        """Add a catalyst to the reaction."""
        component = ReactionComponent(molecule, "catalyst")
        self.catalysts.append(component)
        return component
        
    def add_side_product(self, molecule: Molecule, yield_percentage: float = 0.0) -> SideProduct:
        """Add a side product or byproduct to the reaction."""
        side_product = SideProduct(molecule, yield_percentage)
        self.side_products.append(side_product)
        return side_product
        
    def add_arrow(self, arrow_type: ArrowType = ArrowType.REACTION) -> ReactionArrow:
        """Add a reaction arrow."""
        arrow = ReactionArrow(arrow_type)
        self.arrows.append(arrow)
        return arrow
        
    def set_conditions(self, conditions: ReactionConditions):
        """Set reaction conditions."""
        self.conditions = conditions
        # Apply conditions to all arrows
        for arrow in self.arrows:
            arrow.set_conditions(conditions)
            
    def get_all_molecules(self) -> List[Molecule]:
        """Get all molecules in the reaction."""
        molecules = []
        for component in self.reactants + self.products + self.catalysts + self.solvents:
            molecules.append(component.molecule)
        for side_product in self.side_products:
            molecules.append(side_product.molecule)
        return molecules
        
    def get_reaction_equation(self, include_side_products: bool = False) -> str:
        """Generate a text representation of the reaction equation."""
        def format_components(components: List[ReactionComponent]) -> str:
            parts = []
            for comp in components:
                if comp.coefficient != 1.0:
                    parts.append(f"{comp.coefficient} {comp.molecule.get_molecular_formula()}")
                else:
                    parts.append(comp.molecule.get_molecular_formula())
            return " + ".join(parts)
        
        reactant_str = format_components(self.reactants)
        product_str = format_components(self.products)
        
        # Add side products if requested
        if include_side_products and self.side_products:
            side_product_strs = []
            for sp in self.side_products:
                if sp.yield_percentage > 0:
                    side_product_strs.append(f"{sp.molecule.get_molecular_formula()} ({sp.yield_percentage}%)")
                else:
                    side_product_strs.append(sp.molecule.get_molecular_formula())
            
            if side_product_strs:
                product_str += " + " + " + ".join(side_product_strs)
        
        # Choose arrow symbol based on first arrow type
        arrow_symbol = "→"
        if self.arrows:
            if self.arrows[0].arrow_type == ArrowType.EQUILIBRIUM:
                arrow_symbol = "⇌"
            elif self.arrows[0].arrow_type == ArrowType.RESONANCE:
                arrow_symbol = "↔"
            elif self.arrows[0].arrow_type == ArrowType.RETROSYNTHETIC:
                arrow_symbol = "⇒"
        
        equation = f"{reactant_str} {arrow_symbol} {product_str}"
        
        # Add yield if specified
        if self.yield_percentage is not None:
            equation += f" ({self.yield_percentage}% yield)"
            
        return equation
        
    def auto_position_components(self, canvas_width: float = 800, canvas_height: float = 400):
        """Automatically position reaction components on the canvas."""
        center_y = canvas_height / 2
        
        # Position reactants on the left
        reactant_x_start = 50
        reactant_spacing = 120
        for i, reactant in enumerate(self.reactants):
            x = reactant_x_start + i * reactant_spacing
            reactant.set_position(Point2D(x, center_y))
            
        # Position products on the right
        product_x_start = canvas_width - 200
        product_spacing = 120
        for i, product in enumerate(self.products):
            x = product_x_start + i * product_spacing
            product.set_position(Point2D(x, center_y))
            
        # Position arrow in the center
        if self.arrows:
            arrow_start_x = reactant_x_start + len(self.reactants) * reactant_spacing + 20
            arrow_end_x = product_x_start - 20
            self.arrows[0].set_position(
                Point2D(arrow_start_x, center_y),
                Point2D(arrow_end_x, center_y)
            )
            
        # Position catalysts above the arrow
        if self.catalysts and self.arrows:
            catalyst_y = center_y - 60
            arrow_center = self.arrows[0].get_center_point()
            for i, catalyst in enumerate(self.catalysts):
                x = arrow_center.x + (i - len(self.catalysts)/2) * 80
                catalyst.set_position(Point2D(x, catalyst_y))
                
        # Position side products below the main products
        if self.side_products:
            side_product_y = center_y + 80
            side_product_x_start = product_x_start
            for i, side_product in enumerate(self.side_products):
                x = side_product_x_start + i * 100
                side_product.set_position(Point2D(x, side_product_y))
                
    def calculate_atom_balance(self) -> Dict[str, Dict[str, int]]:
        """Calculate atom balance for the reaction."""
        balance = {}
        
        # Count reactant atoms
        reactant_counts = {}
        for component in self.reactants:
            for atom in component.molecule.atoms:
                element = atom.element.symbol
                count = component.coefficient
                reactant_counts[element] = reactant_counts.get(element, 0) + count
                
                # Add implicit hydrogens
                if atom.hydrogen_count > 0:
                    h_count = atom.hydrogen_count * component.coefficient
                    reactant_counts['H'] = reactant_counts.get('H', 0) + h_count
        
        # Count product atoms (including side products)
        product_counts = {}
        for component in self.products:
            for atom in component.molecule.atoms:
                element = atom.element.symbol
                count = component.coefficient
                product_counts[element] = product_counts.get(element, 0) + count
                
                # Add implicit hydrogens
                if atom.hydrogen_count > 0:
                    h_count = atom.hydrogen_count * component.coefficient
                    product_counts['H'] = product_counts.get('H', 0) + h_count
        
        # Include side products in balance
        for side_product in self.side_products:
            for atom in side_product.molecule.atoms:
                element = atom.element.symbol
                product_counts[element] = product_counts.get(element, 0) + 1
                
                if atom.hydrogen_count > 0:
                    product_counts['H'] = product_counts.get('H', 0) + atom.hydrogen_count
        
        # Combine results
        all_elements = set(reactant_counts.keys()) | set(product_counts.keys())
        for element in all_elements:
            balance[element] = {
                'reactants': reactant_counts.get(element, 0),
                'products': product_counts.get(element, 0),
                'balanced': reactant_counts.get(element, 0) == product_counts.get(element, 0)
            }
            
        return balance


class ReactionSequence:
    """Represents a multi-step reaction sequence."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.steps: List[Reaction] = []
        self.overall_conditions = ReactionConditions()
        
    def add_step(self, reaction: Reaction) -> None:
        """Add a reaction step to the sequence."""
        self.steps.append(reaction)
        
    def get_overall_reactants(self) -> List[ReactionComponent]:
        """Get reactants that are not produced in previous steps."""
        if not self.steps:
            return []
            
        # Start with first step reactants
        overall_reactants = self.steps[0].reactants.copy()
        
        # Remove any that are produced in later steps
        for step in self.steps[1:]:
            for product in step.products:
                # Remove if this product matches any overall reactant
                overall_reactants = [r for r in overall_reactants 
                                   if r.molecule.get_molecular_formula() != 
                                   product.molecule.get_molecular_formula()]
        
        return overall_reactants
        
    def get_overall_products(self) -> List[ReactionComponent]:
        """Get products that are not consumed in subsequent steps."""
        if not self.steps:
            return []
            
        # Start with last step products
        overall_products = self.steps[-1].products.copy()
        
        # Remove any that are consumed in earlier steps
        for step in self.steps[:-1]:
            for reactant in step.reactants:
                # Remove if this reactant matches any overall product
                overall_products = [p for p in overall_products 
                                  if p.molecule.get_molecular_formula() != 
                                  reactant.molecule.get_molecular_formula()]
        
        return overall_products
        
    def get_intermediates(self) -> List[ReactionComponent]:
        """Get intermediate compounds (produced and consumed within sequence)."""
        intermediates = []
        
        for i, step in enumerate(self.steps[:-1]):  # All but last step
            for product in step.products:
                # Check if this product is consumed in a later step
                for later_step in self.steps[i+1:]:
                    for reactant in later_step.reactants:
                        if (product.molecule.get_molecular_formula() == 
                            reactant.molecule.get_molecular_formula()):
                            intermediates.append(product)
                            break
                            
        return intermediates
        
    def validate_sequence(self) -> List[str]:
        """Validate the reaction sequence for consistency."""
        issues = []
        
        if len(self.steps) < 2:
            issues.append("Sequence must have at least 2 steps")
            return issues
            
        # Check that products of one step can be reactants of the next
        for i in range(len(self.steps) - 1):
            current_step = self.steps[i]
            next_step = self.steps[i + 1]
            
            # Get formulas for easier comparison
            current_products = {p.molecule.get_molecular_formula() 
                              for p in current_step.products}
            next_reactants = {r.molecule.get_molecular_formula() 
                            for r in next_step.reactants}
            
            # Check if there's at least one connection
            if not current_products.intersection(next_reactants):
                issues.append(f"No connection between step {i+1} and step {i+2}")
                
        return issues


class SideProduct:
    """Represents a side product or byproduct in a reaction."""
    
    def __init__(self, molecule: Molecule, yield_percentage: float = 0.0):
        self.molecule = molecule
        self.yield_percentage = yield_percentage  # 0-100
        self.is_major = yield_percentage > 50.0
        self.position = Point2D(0, 0)
        
    def set_position(self, position: Point2D):
        """Set the position of this side product."""
        self.position = position


class ReactionBalancer:
    """Provides reaction balancing and validation functionality."""
    
    @staticmethod
    def balance_reaction(reaction: Reaction) -> Dict[str, Any]:
        """
        Attempt to balance a chemical reaction.
        
        Returns:
            Dictionary with balance information and suggested coefficients
        """
        result = {
            'balanced': False,
            'coefficients': {},
            'issues': [],
            'suggestions': []
        }
        
        if not reaction.reactants or not reaction.products:
            result['issues'].append("Reaction must have both reactants and products")
            return result
            
        # Get element counts for reactants and products
        reactant_elements = ReactionBalancer._count_elements(
            [comp.molecule for comp in reaction.reactants]
        )
        product_elements = ReactionBalancer._count_elements(
            [comp.molecule for comp in reaction.products]
        )
        
        # Check if elements are conserved
        all_elements = set(reactant_elements.keys()) | set(product_elements.keys())
        
        unbalanced_elements = []
        for element in all_elements:
            reactant_count = reactant_elements.get(element, 0)
            product_count = product_elements.get(element, 0)
            
            if reactant_count != product_count:
                unbalanced_elements.append({
                    'element': element,
                    'reactant_count': reactant_count,
                    'product_count': product_count,
                    'difference': product_count - reactant_count
                })
        
        if not unbalanced_elements:
            result['balanced'] = True
            result['coefficients'] = {
                comp.molecule.get_molecular_formula(): comp.coefficient 
                for comp in reaction.reactants + reaction.products
            }
        else:
            result['issues'].append("Reaction is not balanced")
            result['unbalanced_elements'] = unbalanced_elements
            
            # Provide simple balancing suggestions
            suggestions = ReactionBalancer._suggest_coefficients(reaction, unbalanced_elements)
            result['suggestions'] = suggestions
            
        return result
        
    @staticmethod
    def _count_elements(molecules: List[Molecule]) -> Dict[str, int]:
        """Count total atoms of each element in a list of molecules."""
        element_counts = {}
        
        for molecule in molecules:
            for atom in molecule.atoms:
                element = atom.element.symbol
                element_counts[element] = element_counts.get(element, 0) + 1
                
                # Add implicit hydrogens
                if atom.hydrogen_count > 0:
                    element_counts['H'] = element_counts.get('H', 0) + atom.hydrogen_count
                    
        return element_counts
        
    @staticmethod
    def _suggest_coefficients(reaction: Reaction, unbalanced_elements: List[Dict]) -> List[str]:
        """Suggest coefficient changes to balance the reaction."""
        suggestions = []
        
        for element_info in unbalanced_elements:
            element = element_info['element']
            difference = element_info['difference']
            
            if difference > 0:
                # Need more of this element on reactant side
                suggestions.append(
                    f"Consider increasing coefficient of reactants containing {element}"
                )
            else:
                # Need more of this element on product side
                suggestions.append(
                    f"Consider increasing coefficient of products containing {element}"
                )
                
        return suggestions
        
    @staticmethod
    def validate_stoichiometry(reaction: Reaction) -> Dict[str, Any]:
        """Validate stoichiometric relationships in a reaction."""
        result = {
            'valid': True,
            'issues': [],
            'mass_balance': {},
            'charge_balance': {}
        }
        
        # Check mass balance
        reactant_mass = sum(
            comp.coefficient * comp.molecule.get_molecular_weight() 
            for comp in reaction.reactants
        )
        product_mass = sum(
            comp.coefficient * comp.molecule.get_molecular_weight() 
            for comp in reaction.products
        )
        
        mass_difference = abs(reactant_mass - product_mass)
        result['mass_balance'] = {
            'reactant_mass': reactant_mass,
            'product_mass': product_mass,
            'difference': mass_difference,
            'balanced': mass_difference < 0.01  # Small tolerance for rounding
        }
        
        if not result['mass_balance']['balanced']:
            result['valid'] = False
            result['issues'].append(f"Mass not conserved: {mass_difference:.3f} amu difference")
            
        # Check charge balance
        reactant_charge = sum(
            sum(atom.charge for atom in comp.molecule.atoms) * comp.coefficient
            for comp in reaction.reactants
        )
        product_charge = sum(
            sum(atom.charge for atom in comp.molecule.atoms) * comp.coefficient
            for comp in reaction.products
        )
        
        charge_difference = reactant_charge - product_charge
        result['charge_balance'] = {
            'reactant_charge': reactant_charge,
            'product_charge': product_charge,
            'difference': charge_difference,
            'balanced': charge_difference == 0
        }
        
        if not result['charge_balance']['balanced']:
            result['valid'] = False
            result['issues'].append(f"Charge not conserved: {charge_difference} charge difference")
            
        return result
    """Manages reaction creation and manipulation operations."""
    
    def __init__(self):
        self.reactions: List[Reaction] = []
        self.active_reaction: Optional[Reaction] = None
        
    def create_reaction(self, name: str = "") -> Reaction:
        """Create a new reaction."""
        reaction = Reaction(name)
        self.reactions.append(reaction)
        self.active_reaction = reaction
        return reaction
        
    def add_reaction_arrow(self, start_point: Point2D, end_point: Point2D,
                          arrow_type: ArrowType = ArrowType.REACTION) -> ReactionArrow:
        """Add a reaction arrow to the active reaction."""
        if not self.active_reaction:
            self.active_reaction = self.create_reaction()
            
        arrow = self.active_reaction.add_arrow(arrow_type)
        arrow.set_position(start_point, end_point)
        return arrow
        
    def add_reaction_component(self, molecule: Molecule, position: Point2D,
                              role: str = "reactant") -> ReactionComponent:
        """Add a component to the active reaction."""
        if not self.active_reaction:
            self.active_reaction = self.create_reaction()
            
        if role == "reactant":
            component = self.active_reaction.add_reactant(molecule)
        elif role == "product":
            component = self.active_reaction.add_product(molecule)
        elif role == "catalyst":
            component = self.active_reaction.add_catalyst(molecule)
        else:
            raise ValueError(f"Unknown role: {role}")
            
        component.set_position(position)
        return component
        
    def set_reaction_conditions(self, conditions: ReactionConditions):
        """Set conditions for the active reaction."""
        if self.active_reaction:
            self.active_reaction.set_conditions(conditions)
            
    def get_reaction_at_point(self, point: Point2D) -> Optional[Reaction]:
        """Find reaction component at the given point."""
        for reaction in self.reactions:
            # Check arrows
            for arrow in reaction.arrows:
                # Simple distance check to arrow line
                distance = self._point_to_line_distance(point, arrow.start_point, arrow.end_point)
                if distance < 10:  # 10 pixel tolerance
                    return reaction
                    
            # Check components
            for component_list in [reaction.reactants, reaction.products, reaction.catalysts]:
                for component in component_list:
                    if component.molecule.contains_point(point):
                        return reaction
                        
        return None
        
    def _point_to_line_distance(self, point: Point2D, line_start: Point2D, line_end: Point2D) -> float:
        """Calculate distance from point to line segment."""
        import math
        
        # Vector from line_start to line_end
        line_vec_x = line_end.x - line_start.x
        line_vec_y = line_end.y - line_start.y
        
        # Vector from line_start to point
        point_vec_x = point.x - line_start.x
        point_vec_y = point.y - line_start.y
        
        # Project point onto line
        line_len_sq = line_vec_x * line_vec_x + line_vec_y * line_vec_y
        if line_len_sq == 0:
            # Line is a point
            return math.sqrt(point_vec_x * point_vec_x + point_vec_y * point_vec_y)
            
        t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_len_sq))
        
        # Find closest point on line
        closest_x = line_start.x + t * line_vec_x
        closest_y = line_start.y + t * line_vec_y
        
        # Calculate distance
        dx = point.x - closest_x
        dy = point.y - closest_y
        return math.sqrt(dx * dx + dy * dy)


# Result classes for operation feedback
@dataclass
class ReactionOperationResult:
    """Result of a reaction operation."""
    success: bool
    reaction: Optional[Reaction] = None
    component: Optional[ReactionComponent] = None
    arrow: Optional[ReactionArrow] = None
    error_message: Optional[str] = None


class ReactionManager:
    """Manages reaction creation and manipulation operations."""
    
    def __init__(self):
        self.reactions: List[Reaction] = []
        self.sequences: List[ReactionSequence] = []
        self.active_reaction: Optional[Reaction] = None
        self.active_sequence: Optional[ReactionSequence] = None
        self.balancer = ReactionBalancer()
        
    def create_reaction(self, name: str = "") -> Reaction:
        """Create a new reaction."""
        reaction = Reaction(name)
        self.reactions.append(reaction)
        self.active_reaction = reaction
        return reaction
        
    def create_reaction_sequence(self, name: str = "") -> ReactionSequence:
        """Create a new reaction sequence."""
        sequence = ReactionSequence(name)
        self.sequences.append(sequence)
        self.active_sequence = sequence
        return sequence
        
    def add_reaction_to_sequence(self, reaction: Reaction, 
                                sequence: Optional[ReactionSequence] = None) -> None:
        """Add a reaction to a sequence."""
        target_sequence = sequence or self.active_sequence
        if target_sequence:
            target_sequence.add_step(reaction)
        else:
            raise ValueError("No active sequence to add reaction to")
            
    def chain_reactions(self, reaction1: Reaction, reaction2: Reaction, 
                       sequence_name: str = "") -> ReactionSequence:
        """Chain two reactions together in a sequence."""
        sequence = self.create_reaction_sequence(sequence_name or "Chained Reaction")
        sequence.add_step(reaction1)
        sequence.add_step(reaction2)
        return sequence
        
    def add_reaction_arrow(self, start_point: Point2D, end_point: Point2D,
                          arrow_type: ArrowType = ArrowType.REACTION) -> ReactionArrow:
        """Add a reaction arrow to the active reaction."""
        if not self.active_reaction:
            self.active_reaction = self.create_reaction()
            
        arrow = self.active_reaction.add_arrow(arrow_type)
        arrow.set_position(start_point, end_point)
        return arrow
        
    def add_reaction_component(self, molecule: Molecule, position: Point2D,
                              role: str = "reactant", coefficient: float = 1.0) -> ReactionComponent:
        """Add a component to the active reaction."""
        if not self.active_reaction:
            self.active_reaction = self.create_reaction()
            
        if role == "reactant":
            component = self.active_reaction.add_reactant(molecule, coefficient)
        elif role == "product":
            component = self.active_reaction.add_product(molecule, coefficient)
        elif role == "catalyst":
            component = self.active_reaction.add_catalyst(molecule)
        else:
            raise ValueError(f"Unknown role: {role}")
            
        component.set_position(position)
        return component
        
    def add_side_product(self, molecule: Molecule, position: Point2D,
                        yield_percentage: float = 0.0) -> SideProduct:
        """Add a side product to the active reaction."""
        if not self.active_reaction:
            self.active_reaction = self.create_reaction()
            
        side_product = self.active_reaction.add_side_product(molecule, yield_percentage)
        side_product.set_position(position)
        return side_product
        
    def set_reaction_conditions(self, conditions: ReactionConditions):
        """Set conditions for the active reaction."""
        if self.active_reaction:
            self.active_reaction.set_conditions(conditions)
            
    def balance_reaction(self, reaction: Optional[Reaction] = None) -> Dict[str, Any]:
        """Balance a reaction using the reaction balancer."""
        target_reaction = reaction or self.active_reaction
        if not target_reaction:
            return {'error': 'No reaction to balance'}
            
        return self.balancer.balance_reaction(target_reaction)
        
    def validate_reaction(self, reaction: Optional[Reaction] = None) -> Dict[str, Any]:
        """Validate a reaction's stoichiometry."""
        target_reaction = reaction or self.active_reaction
        if not target_reaction:
            return {'error': 'No reaction to validate'}
            
        return self.balancer.validate_stoichiometry(target_reaction)
        
    def validate_sequence(self, sequence: Optional[ReactionSequence] = None) -> List[str]:
        """Validate a reaction sequence."""
        target_sequence = sequence or self.active_sequence
        if not target_sequence:
            return ['No sequence to validate']
            
        return target_sequence.validate_sequence()
        
    def auto_balance_reaction(self, reaction: Optional[Reaction] = None) -> Dict[str, Any]:
        """Attempt to automatically balance a reaction by adjusting coefficients."""
        target_reaction = reaction or self.active_reaction
        if not target_reaction:
            return {'error': 'No reaction to balance'}
            
        balance_result = self.balance_reaction(target_reaction)
        
        if balance_result.get('balanced', False):
            return {'success': True, 'message': 'Reaction is already balanced'}
            
        # Simple auto-balancing for common cases
        # This is a simplified implementation - real balancing is more complex
        if len(target_reaction.reactants) == 1 and len(target_reaction.products) == 1:
            # Simple 1:1 reaction
            reactant = target_reaction.reactants[0]
            product = target_reaction.products[0]
            
            # Try to balance by finding the least common multiple
            reactant_formula = reactant.molecule.get_molecular_formula()
            product_formula = product.molecule.get_molecular_formula()
            
            # For demonstration, just suggest equal coefficients
            reactant.coefficient = 1.0
            product.coefficient = 1.0
            
            return {
                'success': True, 
                'message': 'Applied simple 1:1 balancing',
                'coefficients': {
                    reactant_formula: 1.0,
                    product_formula: 1.0
                }
            }
        else:
            return {
                'success': False,
                'message': 'Complex balancing not implemented',
                'suggestions': balance_result.get('suggestions', [])
            }
            
    def get_reaction_at_point(self, point: Point2D) -> Optional[Reaction]:
        """Find reaction component at the given point."""
        for reaction in self.reactions:
            # Check arrows
            for arrow in reaction.arrows:
                # Simple distance check to arrow line
                distance = self._point_to_line_distance(point, arrow.start_point, arrow.end_point)
                if distance < 10:  # 10 pixel tolerance
                    return reaction
                    
            # Check components
            for component_list in [reaction.reactants, reaction.products, reaction.catalysts]:
                for component in component_list:
                    if component.molecule.contains_point(point):
                        return reaction
                        
            # Check side products
            for side_product in reaction.side_products:
                if side_product.molecule.contains_point(point):
                    return reaction
                        
        return None
        
    def get_sequence_statistics(self, sequence: Optional[ReactionSequence] = None) -> Dict[str, Any]:
        """Get statistics about a reaction sequence."""
        target_sequence = sequence or self.active_sequence
        if not target_sequence:
            return {'error': 'No sequence to analyze'}
            
        stats = {
            'step_count': len(target_sequence.steps),
            'total_reactants': len(target_sequence.get_overall_reactants()),
            'total_products': len(target_sequence.get_overall_products()),
            'intermediates': len(target_sequence.get_intermediates()),
            'validation_issues': target_sequence.validate_sequence()
        }
        
        # Calculate overall yield if all steps have yields
        overall_yield = 1.0
        has_yields = True
        for step in target_sequence.steps:
            if step.yield_percentage is not None:
                overall_yield *= (step.yield_percentage / 100.0)
            else:
                has_yields = False
                break
                
        if has_yields and target_sequence.steps:
            stats['overall_yield'] = overall_yield * 100.0
            
        return stats
        
    def _point_to_line_distance(self, point: Point2D, line_start: Point2D, line_end: Point2D) -> float:
        """Calculate distance from point to line segment."""
        import math
        
        # Vector from line_start to line_end
        line_vec_x = line_end.x - line_start.x
        line_vec_y = line_end.y - line_start.y
        
        # Vector from line_start to point
        point_vec_x = point.x - line_start.x
        point_vec_y = point.y - line_start.y
        
        # Project point onto line
        line_len_sq = line_vec_x * line_vec_x + line_vec_y * line_vec_y
        if line_len_sq == 0:
            # Line is a point
            return math.sqrt(point_vec_x * point_vec_x + point_vec_y * point_vec_y)
            
        t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_len_sq))
        
        # Find closest point on line
        closest_x = line_start.x + t * line_vec_x
        closest_y = line_start.y + t * line_vec_y
        
        # Calculate distance
        dx = point.x - closest_x
        dy = point.y - closest_y
        return math.sqrt(dx * dx + dy * dy)