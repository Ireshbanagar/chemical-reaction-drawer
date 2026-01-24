"""
Core data models for chemical structures.

This module defines the fundamental data structures for representing
chemical molecules, atoms, and bonds in the Chemical Reaction Drawer.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Tuple
from enum import Enum
import uuid
from .elements import ChemicalElement, get_element_by_symbol


class BondOrder(Enum):
    """Bond order enumeration for different types of chemical bonds."""
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    AROMATIC = 1.5


class BondStereo(Enum):
    """Stereochemistry enumeration for bond representation."""
    NONE = "none"
    WEDGE = "wedge"      # Bond projecting forward (solid wedge)
    DASH = "dash"        # Bond projecting backward (dashed)
    WAVY = "wavy"        # Unknown stereochemistry (wavy line)


class BondStyle(Enum):
    """Visual style enumeration for bond rendering."""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


@dataclass
class Point2D:
    """2D coordinate point."""
    x: float
    y: float
    
    def distance_to(self, other: 'Point2D') -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __add__(self, other: 'Point2D') -> 'Point2D':
        return Point2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Point2D') -> 'Point2D':
        return Point2D(self.x - other.x, self.y - other.y)


@dataclass
class Point3D:
    """3D coordinate point."""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Point3D') -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5


@dataclass
class Atom:
    """
    Represents an atom in a chemical structure.
    
    Attributes:
        element: The chemical element this atom represents
        position: 2D coordinates for drawing
        position_3d: Optional 3D coordinates for 3D visualization
        charge: Formal charge on the atom
        hydrogen_count: Number of implicit hydrogen atoms
        id: Unique identifier for this atom
        bonds: Set of bonds connected to this atom
    """
    element: ChemicalElement
    position: Point2D
    position_3d: Optional[Point3D] = None
    charge: int = 0
    hydrogen_count: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bonds: Set['Bond'] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize atom with default hydrogen count based on valency."""
        if self.hydrogen_count == 0:
            self.hydrogen_count = self._calculate_implicit_hydrogens()
    
    def _calculate_implicit_hydrogens(self) -> int:
        """
        Calculate the number of implicit hydrogen atoms based on valency rules.
        
        For charged atoms, we need to account for the formal charge properly:
        Formal charge = valence - non_bonding_electrons - bonding_electrons/2
        
        For most cases with hydrogens:
        Formal charge = valence - (bonds + hydrogens)
        
        Rearranging: hydrogens = valence - bonds - formal_charge
        
        Returns:
            Number of implicit hydrogens needed to satisfy valency
        """
        if not self.element.common_valences:
            return 0
            
        # Count current bond order (sum of bond orders, excluding explicit hydrogens)
        bond_order_sum = 0
        for bond in self.bonds:
            if not self._is_hydrogen_bond(bond):
                bond_order_sum += int(bond.order.value)
        
        # For most elements, prefer the highest reasonable valence
        # This gives more realistic hydrogen counts (e.g., CH4 not CH2)
        valid_valences = [v for v in self.element.common_valences if v >= 0]
        
        if not valid_valences:
            return 0
        
        # Choose the most appropriate valence:
        # For carbon, prefer 4; for nitrogen, prefer 3 or 5; for oxygen, prefer 2
        preferred_valences = []
        if self.element.symbol == "C":
            preferred_valences = [4] if 4 in valid_valences else [max(valid_valences)]
        elif self.element.symbol == "N":
            # For nitrogen, try both 3 and 5 to see which gives reasonable hydrogens
            # For charged nitrogen, prefer valence 5 (e.g., NH4+)
            if self.charge != 0:
                preferred_valences = [5, 3] if 5 in valid_valences else [3] if 3 in valid_valences else [max(valid_valences)]
            else:
                preferred_valences = [3, 5] if 3 in valid_valences else [5] if 5 in valid_valences else [max(valid_valences)]
        elif self.element.symbol == "O":
            preferred_valences = [2] if 2 in valid_valences else [max(valid_valences)]
        else:
            # For other elements, use the highest valid valence
            preferred_valences = [max(valid_valences)]
        
        # Try each preferred valence and pick the one that gives reasonable results
        for valence in preferred_valences:
            # Calculate hydrogens: valence - bonds - formal_charge
            hydrogens_needed = valence - bond_order_sum - self.charge
            
            # Check if this gives a reasonable result (non-negative, not too many)
            if 0 <= hydrogens_needed <= 8:  # Reasonable range
                return hydrogens_needed
        
        # Fallback: try all valid valences
        for valence in sorted(valid_valences, reverse=True):
            hydrogens_needed = valence - bond_order_sum - self.charge
            if 0 <= hydrogens_needed <= 8:
                return hydrogens_needed
        
        return 0
    
    def _is_hydrogen_bond(self, bond: 'Bond') -> bool:
        """Check if a bond connects to a hydrogen atom."""
        other_atom = bond.get_other_atom(self)
        return other_atom and other_atom.element.symbol == "H"
    
    def add_bond(self, bond: 'Bond') -> None:
        """Add a bond to this atom."""
        self.bonds.add(bond)
        self.hydrogen_count = self._calculate_implicit_hydrogens()
    
    def remove_bond(self, bond: 'Bond') -> None:
        """Remove a bond from this atom."""
        self.bonds.discard(bond)
        self.hydrogen_count = self._calculate_implicit_hydrogens()
    
    def get_connected_atoms(self) -> List['Atom']:
        """Get all atoms connected to this atom via bonds."""
        connected = []
        for bond in self.bonds:
            other_atom = bond.get_other_atom(self)
            if other_atom:
                connected.append(other_atom)
        return connected
    
    def get_bond_count(self) -> int:
        """Get the total number of bonds (including bond order)."""
        return sum(bond.order.value for bond in self.bonds)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        return self.id == other.id


@dataclass
class Bond:
    """
    Represents a chemical bond between two atoms.
    
    Attributes:
        atom1: First atom in the bond
        atom2: Second atom in the bond
        order: Bond order (single, double, triple, aromatic)
        stereo: Stereochemistry representation
        style: Visual style for rendering
        id: Unique identifier for this bond
    """
    atom1: Atom
    atom2: Atom
    order: BondOrder = BondOrder.SINGLE
    stereo: BondStereo = BondStereo.NONE
    style: BondStyle = BondStyle.SOLID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Add this bond to both atoms."""
        self.atom1.add_bond(self)
        self.atom2.add_bond(self)
    
    def get_other_atom(self, atom: Atom) -> Optional[Atom]:
        """
        Get the other atom in this bond.
        
        Args:
            atom: One of the atoms in this bond
            
        Returns:
            The other atom, or None if the given atom is not in this bond
        """
        if atom == self.atom1:
            return self.atom2
        elif atom == self.atom2:
            return self.atom1
        return None
    
    def contains_atom(self, atom: Atom) -> bool:
        """Check if this bond contains the given atom."""
        return atom == self.atom1 or atom == self.atom2
    
    def get_length(self) -> float:
        """Calculate the 2D distance between the bonded atoms."""
        return self.atom1.position.distance_to(self.atom2.position)
    
    def get_length_3d(self) -> Optional[float]:
        """Calculate the 3D distance between bonded atoms if 3D coordinates exist."""
        if self.atom1.position_3d and self.atom2.position_3d:
            return self.atom1.position_3d.distance_to(self.atom2.position_3d)
        return None
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Bond):
            return False
        return self.id == other.id


@dataclass
class Molecule:
    """
    Represents a complete molecular structure.
    
    Attributes:
        atoms: List of atoms in the molecule
        bonds: List of bonds in the molecule
        name: Optional name for the molecule
        id: Unique identifier for this molecule
    """
    atoms: List[Atom] = field(default_factory=list)
    bonds: List[Bond] = field(default_factory=list)
    name: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def add_atom(self, element_symbol: str, position: Point2D, 
                 charge: int = 0, position_3d: Optional[Point3D] = None) -> Atom:
        """
        Add a new atom to the molecule.
        
        Args:
            element_symbol: Chemical symbol for the element
            position: 2D position for the atom
            charge: Formal charge (default: 0)
            position_3d: Optional 3D position
            
        Returns:
            The created Atom object
            
        Raises:
            ValueError: If element_symbol is not valid
        """
        element = get_element_by_symbol(element_symbol)
        if not element:
            raise ValueError(f"Invalid element symbol: {element_symbol}")
        
        atom = Atom(
            element=element,
            position=position,
            position_3d=position_3d,
            charge=charge
        )
        self.atoms.append(atom)
        return atom
    
    def add_bond(self, atom1: Atom, atom2: Atom, order: BondOrder = BondOrder.SINGLE,
                 stereo: BondStereo = BondStereo.NONE, style: BondStyle = BondStyle.SOLID) -> Bond:
        """
        Add a new bond between two atoms.
        
        Args:
            atom1: First atom
            atom2: Second atom
            order: Bond order (default: single)
            stereo: Stereochemistry (default: none)
            style: Visual style (default: solid)
            
        Returns:
            The created Bond object
            
        Raises:
            ValueError: If atoms are not in this molecule or bond already exists
        """
        if atom1 not in self.atoms or atom2 not in self.atoms:
            raise ValueError("Both atoms must be in the molecule")
        
        if atom1 == atom2:
            raise ValueError("Cannot create bond between atom and itself")
        
        # Check if bond already exists
        for existing_bond in self.bonds:
            if existing_bond.contains_atom(atom1) and existing_bond.contains_atom(atom2):
                raise ValueError("Bond already exists between these atoms")
        
        bond = Bond(atom1=atom1, atom2=atom2, order=order, stereo=stereo, style=style)
        self.bonds.append(bond)
        return bond
    
    def remove_atom(self, atom: Atom) -> None:
        """
        Remove an atom and all its bonds from the molecule.
        
        Args:
            atom: Atom to remove
        """
        if atom not in self.atoms:
            return
        
        # Remove all bonds connected to this atom
        bonds_to_remove = [bond for bond in self.bonds if bond.contains_atom(atom)]
        for bond in bonds_to_remove:
            self.remove_bond(bond)
        
        # Remove the atom
        self.atoms.remove(atom)
    
    def remove_bond(self, bond: Bond) -> None:
        """
        Remove a bond from the molecule.
        
        Args:
            bond: Bond to remove
        """
        if bond in self.bonds:
            # Remove bond from atoms
            bond.atom1.remove_bond(bond)
            bond.atom2.remove_bond(bond)
            # Remove from molecule
            self.bonds.remove(bond)
    
    def get_molecular_formula(self) -> str:
        """
        Calculate the molecular formula of this molecule.
        
        Returns:
            Molecular formula as a string (e.g., "C6H12O6")
        """
        element_counts: Dict[str, int] = {}
        
        # Count atoms
        for atom in self.atoms:
            symbol = atom.element.symbol
            element_counts[symbol] = element_counts.get(symbol, 0) + 1
            
            # Add implicit hydrogens
            if atom.hydrogen_count > 0:
                element_counts["H"] = element_counts.get("H", 0) + atom.hydrogen_count
        
        # Build formula string with proper ordering
        formula_parts = []
        
        # Check if this is an organic compound (contains carbon)
        has_carbon = "C" in element_counts
        
        if has_carbon:
            # Organic compound: C first, then H, then alphabetical
            # Carbon first
            count = element_counts["C"]
            formula_parts.append("C" if count == 1 else f"C{count}")
            del element_counts["C"]
            
            # Hydrogen second
            if "H" in element_counts:
                count = element_counts["H"]
                formula_parts.append("H" if count == 1 else f"H{count}")
                del element_counts["H"]
            
            # Rest alphabetically
            for symbol in sorted(element_counts.keys()):
                count = element_counts[symbol]
                formula_parts.append(symbol if count == 1 else f"{symbol}{count}")
        else:
            # Inorganic compound: Check for charged atoms to determine cation/anion order
            charged_atoms = [atom for atom in self.atoms if atom.charge != 0]
            
            if charged_atoms:
                # For ionic compounds, put cation first (positive charge)
                cations = [atom for atom in charged_atoms if atom.charge > 0]
                if cations:
                    # Put the cation element first
                    cation_symbol = cations[0].element.symbol
                    if cation_symbol in element_counts:
                        count = element_counts[cation_symbol]
                        formula_parts.append(cation_symbol if count == 1 else f"{cation_symbol}{count}")
                        del element_counts[cation_symbol]
            
            # Add remaining elements alphabetically
            for symbol in sorted(element_counts.keys()):
                count = element_counts[symbol]
                formula_parts.append(symbol if count == 1 else f"{symbol}{count}")
        
        return "".join(formula_parts) if formula_parts else ""
    
    def get_molecular_weight(self) -> float:
        """
        Calculate the molecular weight of this molecule.
        
        Returns:
            Molecular weight in atomic mass units (amu)
        """
        total_weight = 0.0
        
        for atom in self.atoms:
            total_weight += atom.element.atomic_weight
            # Add weight of implicit hydrogens
            total_weight += atom.hydrogen_count * 1.008  # Hydrogen atomic weight
        
        return total_weight
    
    def get_center_point(self) -> Point2D:
        """
        Calculate the geometric center of all atoms in the molecule.
        
        Returns:
            Point2D representing the center of the molecule
        """
        if not self.atoms:
            return Point2D(0, 0)
        
        total_x = sum(atom.position.x for atom in self.atoms)
        total_y = sum(atom.position.y for atom in self.atoms)
        
        return Point2D(total_x / len(self.atoms), total_y / len(self.atoms))
    
    def contains_point(self, point: Point2D, tolerance: float = 20.0) -> bool:
        """
        Check if a point is within the bounds of this molecule.
        
        Args:
            point: Point to check
            tolerance: Distance tolerance in pixels
            
        Returns:
            True if point is within tolerance of any atom
        """
        for atom in self.atoms:
            if atom.position.distance_to(point) <= tolerance:
                return True
        return False
    
    def get_bounding_box(self) -> Tuple[Point2D, Point2D]:
        """
        Get the bounding box of the molecule.
        
        Returns:
            Tuple of (min_point, max_point) defining the bounding box
        """
        if not self.atoms:
            return (Point2D(0, 0), Point2D(0, 0))
        
        min_x = min(atom.position.x for atom in self.atoms)
        max_x = max(atom.position.x for atom in self.atoms)
        min_y = min(atom.position.y for atom in self.atoms)
        max_y = max(atom.position.y for atom in self.atoms)
        
        return (Point2D(min_x, min_y), Point2D(max_x, max_y))
    
    def get_atom_count(self) -> int:
        """Get the total number of atoms including implicit hydrogens."""
        total = len(self.atoms)
        for atom in self.atoms:
            total += atom.hydrogen_count
        return total
    
    def is_empty(self) -> bool:
        """Check if the molecule has no atoms."""
        return len(self.atoms) == 0
    
    def copy(self) -> 'Molecule':
        """Create a deep copy of this molecule."""
        new_molecule = Molecule(name=self.name)
        
        # Create mapping from old atoms to new atoms
        atom_mapping = {}
        
        # Copy atoms
        for atom in self.atoms:
            new_atom = Atom(
                element=atom.element,
                position=Point2D(atom.position.x, atom.position.y),
                position_3d=Point3D(atom.position_3d.x, atom.position_3d.y, atom.position_3d.z) if atom.position_3d else None,
                charge=atom.charge,
                hydrogen_count=atom.hydrogen_count
            )
            new_molecule.atoms.append(new_atom)
            atom_mapping[atom] = new_atom
        
        # Copy bonds
        for bond in self.bonds:
            new_atom1 = atom_mapping[bond.atom1]
            new_atom2 = atom_mapping[bond.atom2]
            new_molecule.add_bond(new_atom1, new_atom2, bond.order, bond.stereo, bond.style)
        
        return new_molecule
    
    def __len__(self):
        return len(self.atoms)
    
    def __bool__(self):
        return not self.is_empty()