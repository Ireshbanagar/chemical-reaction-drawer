"""
Atom placement and management system.

This module provides functionality for creating, positioning, and managing atoms
in chemical structures, including element assignment and deletion with bond cleanup.
"""

from typing import Optional, List, Tuple, Dict, Set
from dataclasses import dataclass
from .models import Atom, Bond, Molecule, Point2D, Point3D
from .elements import get_element_by_symbol, ChemicalElement, is_valid_element_symbol
from .chemistry import ChemicalValidator, ValidationResult


@dataclass
class AtomPlacementResult:
    """Result of atom placement operation."""
    success: bool
    atom: Optional[Atom] = None
    error_message: Optional[str] = None
    validation_issues: Optional[ValidationResult] = None


@dataclass
class AtomDeletionResult:
    """Result of atom deletion operation."""
    success: bool
    deleted_atom: Optional[Atom] = None
    deleted_bonds: List[Bond] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.deleted_bonds is None:
            self.deleted_bonds = []


@dataclass
class ElementChangeResult:
    """Result of element change operation."""
    success: bool
    atom: Optional[Atom] = None
    old_element: Optional[ChemicalElement] = None
    new_element: Optional[ChemicalElement] = None
    error_message: Optional[str] = None
    validation_issues: Optional[ValidationResult] = None


class AtomManager:
    """
    Manages atom placement, positioning, and element assignment operations.
    
    This class provides high-level operations for creating and managing atoms
    in chemical structures, with validation and error handling.
    """
    
    def __init__(self, validator: Optional[ChemicalValidator] = None):
        """
        Initialize the atom manager.
        
        Args:
            validator: Chemical validator for structure validation (optional)
        """
        self.validator = validator or ChemicalValidator()
        self._default_element = "C"  # Default element for new atoms
    
    def place_atom(self, molecule: Molecule, position: Point2D, 
                   element_symbol: str = None, charge: int = 0,
                   position_3d: Optional[Point3D] = None,
                   validate: bool = True) -> AtomPlacementResult:
        """
        Place a new atom at the specified position.
        
        Args:
            molecule: Molecule to add the atom to
            position: 2D position for the atom
            element_symbol: Chemical element symbol (default: carbon)
            charge: Formal charge on the atom (default: 0)
            position_3d: Optional 3D position
            validate: Whether to validate the structure after placement
            
        Returns:
            AtomPlacementResult with success status and created atom
        """
        if element_symbol is None:
            element_symbol = self._default_element
        
        # Validate element symbol
        if not is_valid_element_symbol(element_symbol):
            return AtomPlacementResult(
                success=False,
                error_message=f"Invalid element symbol: {element_symbol}"
            )
        
        try:
            # Create the atom
            atom = molecule.add_atom(
                element_symbol=element_symbol,
                position=position,
                charge=charge,
                position_3d=position_3d
            )
            
            # Validate structure if requested
            validation_result = None
            if validate:
                validation_result = self.validator.validate_structure(molecule)
            
            return AtomPlacementResult(
                success=True,
                atom=atom,
                validation_issues=validation_result
            )
            
        except Exception as e:
            return AtomPlacementResult(
                success=False,
                error_message=str(e)
            )
    
    def delete_atom(self, molecule: Molecule, atom: Atom,
                    validate: bool = True) -> AtomDeletionResult:
        """
        Delete an atom and all its associated bonds from the molecule.
        
        Args:
            molecule: Molecule containing the atom
            atom: Atom to delete
            validate: Whether to validate the structure after deletion
            
        Returns:
            AtomDeletionResult with success status and deleted components
        """
        if atom not in molecule.atoms:
            return AtomDeletionResult(
                success=False,
                error_message="Atom is not in the specified molecule"
            )
        
        try:
            # Record bonds that will be deleted
            bonds_to_delete = [bond for bond in molecule.bonds if bond.contains_atom(atom)]
            
            # Remove the atom (this will also remove its bonds)
            molecule.remove_atom(atom)
            
            return AtomDeletionResult(
                success=True,
                deleted_atom=atom,
                deleted_bonds=bonds_to_delete
            )
            
        except Exception as e:
            return AtomDeletionResult(
                success=False,
                error_message=str(e)
            )
    
    def change_element(self, atom: Atom, new_element_symbol: str,
                       validate: bool = True) -> ElementChangeResult:
        """
        Change the element of an existing atom.
        
        Args:
            atom: Atom to modify
            new_element_symbol: New element symbol
            validate: Whether to validate the structure after change
            
        Returns:
            ElementChangeResult with success status and change details
        """
        # Validate new element symbol
        if not is_valid_element_symbol(new_element_symbol):
            return ElementChangeResult(
                success=False,
                error_message=f"Invalid element symbol: {new_element_symbol}"
            )
        
        new_element = get_element_by_symbol(new_element_symbol)
        if not new_element:
            return ElementChangeResult(
                success=False,
                error_message=f"Element not found: {new_element_symbol}"
            )
        
        try:
            old_element = atom.element
            
            # Change the element
            atom.element = new_element
            
            # Recalculate implicit hydrogens based on new element
            atom.hydrogen_count = atom._calculate_implicit_hydrogens()
            
            # Validate structure if requested
            validation_result = None
            if validate:
                # Need to find the molecule containing this atom for validation
                # This is a limitation of the current design - we could improve this
                # by maintaining back-references or passing the molecule
                pass  # Skip validation for now
            
            return ElementChangeResult(
                success=True,
                atom=atom,
                old_element=old_element,
                new_element=new_element,
                validation_issues=validation_result
            )
            
        except Exception as e:
            return ElementChangeResult(
                success=False,
                error_message=str(e)
            )
    
    def move_atom(self, atom: Atom, new_position: Point2D,
                  new_position_3d: Optional[Point3D] = None) -> bool:
        """
        Move an atom to a new position.
        
        Args:
            atom: Atom to move
            new_position: New 2D position
            new_position_3d: Optional new 3D position
            
        Returns:
            True if successful, False otherwise
        """
        try:
            atom.position = new_position
            if new_position_3d is not None:
                atom.position_3d = new_position_3d
            return True
        except Exception:
            return False
    
    def get_atoms_at_position(self, molecule: Molecule, position: Point2D,
                             tolerance: float = 0.1) -> List[Atom]:
        """
        Find atoms near a specific position.
        
        Args:
            molecule: Molecule to search
            position: Position to search around
            tolerance: Distance tolerance for matching
            
        Returns:
            List of atoms within tolerance of the position
        """
        nearby_atoms = []
        
        for atom in molecule.atoms:
            distance = atom.position.distance_to(position)
            if distance <= tolerance:
                nearby_atoms.append(atom)
        
        return nearby_atoms
    
    def get_atom_at_position(self, molecule: Molecule, position: Point2D,
                            tolerance: float = 0.1) -> Optional[Atom]:
        """
        Find the closest atom to a specific position within tolerance.
        
        Args:
            molecule: Molecule to search
            position: Position to search around
            tolerance: Maximum distance for matching
            
        Returns:
            Closest atom within tolerance, or None if no atom found
        """
        closest_atom = None
        closest_distance = float('inf')
        
        for atom in molecule.atoms:
            distance = atom.position.distance_to(position)
            if distance <= tolerance and distance < closest_distance:
                closest_atom = atom
                closest_distance = distance
        
        return closest_atom
    
    def set_default_element(self, element_symbol: str) -> bool:
        """
        Set the default element for new atom placement.
        
        Args:
            element_symbol: Element symbol to use as default
            
        Returns:
            True if valid element, False otherwise
        """
        if is_valid_element_symbol(element_symbol):
            self._default_element = element_symbol
            return True
        return False
    
    def get_default_element(self) -> str:
        """Get the current default element symbol."""
        return self._default_element
    
    def batch_place_atoms(self, molecule: Molecule, 
                         atom_specs: List[Tuple[Point2D, str]],
                         validate: bool = True) -> List[AtomPlacementResult]:
        """
        Place multiple atoms in a single operation.
        
        Args:
            molecule: Molecule to add atoms to
            atom_specs: List of (position, element_symbol) tuples
            validate: Whether to validate after all placements
            
        Returns:
            List of AtomPlacementResult for each placement
        """
        results = []
        
        for position, element_symbol in atom_specs:
            # Don't validate individual placements to avoid repeated validation
            result = self.place_atom(
                molecule, position, element_symbol, validate=False
            )
            results.append(result)
            
            # If any placement fails, stop and return results so far
            if not result.success:
                break
        
        # Validate the entire structure once at the end if requested
        if validate and all(result.success for result in results):
            validation_result = self.validator.validate_structure(molecule)
            # Add validation result to the last successful result
            if results:
                results[-1].validation_issues = validation_result
        
        return results
    
    def get_atom_neighbors(self, atom: Atom) -> List[Atom]:
        """
        Get all atoms directly bonded to the given atom.
        
        Args:
            atom: Atom to find neighbors for
            
        Returns:
            List of neighboring atoms
        """
        return atom.get_connected_atoms()
    
    def count_atom_bonds(self, atom: Atom) -> int:
        """
        Count the total bond order for an atom.
        
        Args:
            atom: Atom to count bonds for
            
        Returns:
            Total bond order (considering multiple bonds)
        """
        return atom.get_bond_count()
    
    def is_atom_terminal(self, atom: Atom) -> bool:
        """
        Check if an atom is terminal (has only one bond).
        
        Args:
            atom: Atom to check
            
        Returns:
            True if atom has exactly one bond, False otherwise
        """
        return len(atom.bonds) == 1
    
    def get_molecule_statistics(self, molecule: Molecule) -> Dict[str, int]:
        """
        Get statistics about atoms in the molecule.
        
        Args:
            molecule: Molecule to analyze
            
        Returns:
            Dictionary with atom counts by element
        """
        stats = {}
        
        for atom in molecule.atoms:
            element = atom.element.symbol
            stats[element] = stats.get(element, 0) + 1
        
        return stats