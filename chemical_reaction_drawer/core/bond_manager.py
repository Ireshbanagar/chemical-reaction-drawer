"""
Bond creation and management system.

This module provides functionality for creating, modifying, and managing bonds
in chemical structures, including support for different bond types and stereochemistry.
"""

from typing import Optional, List, Tuple, Dict, Set
from dataclasses import dataclass
from .models import Atom, Bond, Molecule, BondOrder, BondStereo, BondStyle
from .chemistry import ChemicalValidator, ValidationResult


@dataclass
class BondCreationResult:
    """Result of bond creation operation."""
    success: bool
    bond: Optional[Bond] = None
    error_message: Optional[str] = None
    validation_issues: Optional[ValidationResult] = None


@dataclass
class BondDeletionResult:
    """Result of bond deletion operation."""
    success: bool
    deleted_bond: Optional[Bond] = None
    error_message: Optional[str] = None
    validation_issues: Optional[ValidationResult] = None


@dataclass
class BondModificationResult:
    """Result of bond modification operation."""
    success: bool
    bond: Optional[Bond] = None
    old_properties: Optional[Dict] = None
    new_properties: Optional[Dict] = None
    error_message: Optional[str] = None
    validation_issues: Optional[ValidationResult] = None


class BondManager:
    """
    Manages bond creation, modification, and deletion operations.
    
    This class provides high-level operations for creating and managing bonds
    in chemical structures, with validation and error handling.
    """
    
    def __init__(self, validator: Optional[ChemicalValidator] = None):
        """
        Initialize the bond manager.
        
        Args:
            validator: Chemical validator for structure validation (optional)
        """
        self.validator = validator or ChemicalValidator()
        self._default_bond_order = BondOrder.SINGLE
        self._default_stereo = BondStereo.NONE
        self._default_style = BondStyle.SOLID
    
    def create_bond(self, molecule: Molecule, atom1: Atom, atom2: Atom,
                   order: BondOrder = None, stereo: BondStereo = None,
                   style: BondStyle = None, validate: bool = True) -> BondCreationResult:
        """
        Create a new bond between two atoms.
        
        Args:
            molecule: Molecule to add the bond to
            atom1: First atom in the bond
            atom2: Second atom in the bond
            order: Bond order (default: single)
            stereo: Stereochemistry (default: none)
            style: Visual style (default: solid)
            validate: Whether to validate the structure after creation
            
        Returns:
            BondCreationResult with success status and created bond
        """
        # Use defaults if not specified
        if order is None:
            order = self._default_bond_order
        if stereo is None:
            stereo = self._default_stereo
        if style is None:
            style = self._default_style
        
        # Validate inputs
        if atom1 not in molecule.atoms or atom2 not in molecule.atoms:
            return BondCreationResult(
                success=False,
                error_message="Both atoms must be in the molecule"
            )
        
        if atom1 == atom2:
            return BondCreationResult(
                success=False,
                error_message="Cannot create bond between atom and itself"
            )
        
        # Check if bond already exists
        for existing_bond in molecule.bonds:
            if existing_bond.contains_atom(atom1) and existing_bond.contains_atom(atom2):
                return BondCreationResult(
                    success=False,
                    error_message="Bond already exists between these atoms"
                )
        
        try:
            # Create the bond
            bond = molecule.add_bond(atom1, atom2, order=order, stereo=stereo, style=style)
            
            # Validate structure if requested
            validation_result = None
            if validate:
                validation_result = self.validator.validate_structure(molecule)
            
            return BondCreationResult(
                success=True,
                bond=bond,
                validation_issues=validation_result
            )
            
        except Exception as e:
            return BondCreationResult(
                success=False,
                error_message=str(e)
            )
    
    def delete_bond(self, molecule: Molecule, bond: Bond,
                   validate: bool = True) -> BondDeletionResult:
        """
        Delete a bond from the molecule.
        
        Args:
            molecule: Molecule containing the bond
            bond: Bond to delete
            validate: Whether to validate the structure after deletion
            
        Returns:
            BondDeletionResult with success status and deleted bond
        """
        if bond not in molecule.bonds:
            return BondDeletionResult(
                success=False,
                error_message="Bond is not in the specified molecule"
            )
        
        try:
            # Remove the bond
            molecule.remove_bond(bond)
            
            # Validate structure if requested
            validation_result = None
            if validate:
                validation_result = self.validator.validate_structure(molecule)
            
            return BondDeletionResult(
                success=True,
                deleted_bond=bond,
                validation_issues=validation_result
            )
            
        except Exception as e:
            return BondDeletionResult(
                success=False,
                error_message=str(e)
            )
    
    def modify_bond_order(self, bond: Bond, new_order: BondOrder) -> BondModificationResult:
        """
        Modify the order of an existing bond.
        
        Args:
            bond: Bond to modify
            new_order: New bond order
            
        Returns:
            BondModificationResult with success status and change details
        """
        old_order = bond.order
        
        try:
            # Store old properties
            old_properties = {
                "order": old_order,
                "stereo": bond.stereo,
                "style": bond.style
            }
            
            # Modify the bond order
            bond.order = new_order
            
            # Recalculate implicit hydrogens for connected atoms
            bond.atom1.hydrogen_count = bond.atom1._calculate_implicit_hydrogens()
            bond.atom2.hydrogen_count = bond.atom2._calculate_implicit_hydrogens()
            
            # Store new properties
            new_properties = {
                "order": bond.order,
                "stereo": bond.stereo,
                "style": bond.style
            }
            
            return BondModificationResult(
                success=True,
                bond=bond,
                old_properties=old_properties,
                new_properties=new_properties
            )
            
        except Exception as e:
            # Restore original order on failure
            bond.order = old_order
            return BondModificationResult(
                success=False,
                error_message=str(e)
            )
    
    def modify_bond_stereochemistry(self, bond: Bond, new_stereo: BondStereo) -> BondModificationResult:
        """
        Modify the stereochemistry of an existing bond.
        
        Args:
            bond: Bond to modify
            new_stereo: New stereochemistry
            
        Returns:
            BondModificationResult with success status and change details
        """
        old_stereo = bond.stereo
        
        try:
            # Store old properties
            old_properties = {
                "order": bond.order,
                "stereo": old_stereo,
                "style": bond.style
            }
            
            # Modify the stereochemistry
            bond.stereo = new_stereo
            
            # Store new properties
            new_properties = {
                "order": bond.order,
                "stereo": bond.stereo,
                "style": bond.style
            }
            
            return BondModificationResult(
                success=True,
                bond=bond,
                old_properties=old_properties,
                new_properties=new_properties
            )
            
        except Exception as e:
            # Restore original stereochemistry on failure
            bond.stereo = old_stereo
            return BondModificationResult(
                success=False,
                error_message=str(e)
            )
    
    def find_bond_between_atoms(self, molecule: Molecule, atom1: Atom, atom2: Atom) -> Optional[Bond]:
        """
        Find the bond between two specific atoms.
        
        Args:
            molecule: Molecule to search
            atom1: First atom
            atom2: Second atom
            
        Returns:
            Bond between the atoms, or None if no bond exists
        """
        for bond in molecule.bonds:
            if bond.contains_atom(atom1) and bond.contains_atom(atom2):
                return bond
        return None
    
    def get_bonds_for_atom(self, atom: Atom) -> List[Bond]:
        """
        Get all bonds connected to a specific atom.
        
        Args:
            atom: Atom to find bonds for
            
        Returns:
            List of bonds connected to the atom
        """
        return list(atom.bonds)
    
    def get_bond_count_by_type(self, molecule: Molecule) -> Dict[BondOrder, int]:
        """
        Count bonds by their order type.
        
        Args:
            molecule: Molecule to analyze
            
        Returns:
            Dictionary mapping bond orders to their counts
        """
        counts = {}
        for bond in molecule.bonds:
            counts[bond.order] = counts.get(bond.order, 0) + 1
        return counts
    
    def get_stereochemistry_count(self, molecule: Molecule) -> Dict[BondStereo, int]:
        """
        Count bonds by their stereochemistry type.
        
        Args:
            molecule: Molecule to analyze
            
        Returns:
            Dictionary mapping stereochemistry types to their counts
        """
        counts = {}
        for bond in molecule.bonds:
            counts[bond.stereo] = counts.get(bond.stereo, 0) + 1
        return counts
    
    def set_default_bond_properties(self, order: BondOrder = None,
                                   stereo: BondStereo = None,
                                   style: BondStyle = None) -> None:
        """
        Set default properties for new bond creation.
        
        Args:
            order: Default bond order (optional)
            stereo: Default stereochemistry (optional)
            style: Default visual style (optional)
        """
        if order is not None:
            self._default_bond_order = order
        if stereo is not None:
            self._default_stereo = stereo
        if style is not None:
            self._default_style = style
    
    def get_default_bond_properties(self) -> Dict:
        """
        Get current default bond properties.
        
        Returns:
            Dictionary with default order, stereo, and style
        """
        return {
            "order": self._default_bond_order,
            "stereo": self._default_stereo,
            "style": self._default_style
        }