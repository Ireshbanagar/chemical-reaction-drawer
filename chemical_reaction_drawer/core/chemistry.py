"""
Chemical intelligence and validation system.

This module provides chemical validation, property calculation,
and intelligent assistance for molecular structure creation.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from .models import Molecule, Atom, Bond, BondOrder
from .elements import ChemicalElement


class ValidationLevel(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """Represents a chemical validation issue."""
    level: ValidationLevel
    message: str
    atom: Optional[Atom] = None
    bond: Optional[Bond] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of chemical structure validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.level == ValidationLevel.ERROR for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if there are any warning-level issues."""
        return any(issue.level == ValidationLevel.WARNING for issue in self.issues)
    
    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get all issues of a specific severity level."""
        return [issue for issue in self.issues if issue.level == level]


@dataclass
class MolecularProperties:
    """Calculated molecular properties."""
    molecular_weight: float
    molecular_formula: str
    atom_count: int
    bond_count: int
    ring_count: int
    aromatic_ring_count: int
    hydrogen_bond_donors: int
    hydrogen_bond_acceptors: int
    rotatable_bonds: int
    formal_charge: int
    
    # Estimated properties (simplified calculations)
    estimated_logp: Optional[float] = None
    estimated_polar_surface_area: Optional[float] = None


class ChemicalValidator:
    """
    Chemical structure validator and property calculator.
    
    Provides validation of molecular structures according to chemical rules,
    calculation of molecular properties, and intelligent suggestions for
    structure corrections.
    """
    
    def __init__(self):
        """Initialize the chemical validator."""
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Set up chemical validation rules and parameters."""
        # Maximum reasonable valences for common elements
        self.max_valences = {
            "H": 1, "He": 0, "Li": 1, "Be": 2, "B": 4, "C": 4, "N": 4, "O": 2,
            "F": 1, "Ne": 0, "Na": 1, "Mg": 2, "Al": 3, "Si": 4, "P": 5, "S": 6,
            "Cl": 7, "Ar": 0, "K": 1, "Ca": 2, "Br": 7, "I": 7
        }
        
        # Hydrogen bond donor patterns (atoms that can donate H-bonds)
        self.hb_donors = {"N", "O", "S"}  # When bonded to hydrogen
        
        # Hydrogen bond acceptor patterns (atoms with lone pairs)
        self.hb_acceptors = {"N", "O", "S", "F", "Cl", "Br", "I"}
    
    def validate_structure(self, molecule: Molecule) -> ValidationResult:
        """
        Validate a molecular structure for chemical correctness.
        
        Args:
            molecule: Molecule to validate
            
        Returns:
            ValidationResult with issues and overall validity
        """
        issues = []
        
        if molecule.is_empty():
            return ValidationResult(is_valid=True, issues=[])
        
        # Validate each atom
        for atom in molecule.atoms:
            issues.extend(self._validate_atom(atom))
        
        # Validate bonds
        for bond in molecule.bonds:
            issues.extend(self._validate_bond(bond))
        
        # Check for disconnected fragments
        issues.extend(self._check_connectivity(molecule))
        
        # Overall validity (no errors, warnings are acceptable)
        is_valid = not any(issue.level == ValidationLevel.ERROR for issue in issues)
        
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def _validate_atom(self, atom: Atom) -> List[ValidationIssue]:
        """Validate a single atom for chemical correctness."""
        issues = []
        
        # Check valency
        current_valence = self._calculate_atom_valence(atom)
        max_valence = self.max_valences.get(atom.element.symbol, 8)
        
        if current_valence > max_valence:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"{atom.element.symbol} atom has valence {current_valence}, maximum is {max_valence}",
                atom=atom,
                suggestion=f"Remove bonds or change to a different element"
            ))
        
        # Check for unusual valences
        if atom.element.common_valences and current_valence not in atom.element.common_valences:
            if current_valence <= max_valence:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"{atom.element.symbol} has unusual valence {current_valence}",
                    atom=atom,
                    suggestion=f"Common valences are: {atom.element.common_valences}"
                ))
        
        # Check charge reasonableness
        if abs(atom.charge) > 3:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"{atom.element.symbol} has high formal charge: {atom.charge:+d}",
                atom=atom,
                suggestion="Consider redistributing charge or checking structure"
            ))
        
        return issues
    
    def _validate_bond(self, bond: Bond) -> List[ValidationIssue]:
        """Validate a single bond for chemical correctness."""
        issues = []
        
        # Check bond length reasonableness (very basic check)
        bond_length = bond.get_length()
        if bond_length < 0.5:  # Very short bond
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"Very short bond length: {bond_length:.2f} Å",
                bond=bond,
                suggestion="Check atom positions"
            ))
        elif bond_length > 5.0:  # Very long bond
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"Very long bond length: {bond_length:.2f} Å",
                bond=bond,
                suggestion="Check if atoms should be bonded"
            ))
        
        # Check for impossible bond orders
        atom1_symbol = bond.atom1.element.symbol
        atom2_symbol = bond.atom2.element.symbol
        
        # Hydrogen can only form single bonds
        if (atom1_symbol == "H" or atom2_symbol == "H") and bond.order != BondOrder.SINGLE:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Hydrogen can only form single bonds",
                bond=bond,
                suggestion="Change bond order to single"
            ))
        
        return issues
    
    def _check_connectivity(self, molecule: Molecule) -> List[ValidationIssue]:
        """Check for disconnected molecular fragments."""
        issues = []
        
        if len(molecule.atoms) <= 1:
            return issues
        
        # Find connected components using DFS
        visited = set()
        components = []
        
        for atom in molecule.atoms:
            if atom not in visited:
                component = self._dfs_component(atom, visited)
                components.append(component)
        
        if len(components) > 1:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                message=f"Molecule has {len(components)} disconnected fragments",
                suggestion="Consider if all fragments should be connected"
            ))
        
        return issues
    
    def _dfs_component(self, start_atom: Atom, visited: Set[Atom]) -> List[Atom]:
        """Depth-first search to find connected component."""
        component = []
        stack = [start_atom]
        
        while stack:
            atom = stack.pop()
            if atom not in visited:
                visited.add(atom)
                component.append(atom)
                
                # Add connected atoms to stack
                for connected_atom in atom.get_connected_atoms():
                    if connected_atom not in visited:
                        stack.append(connected_atom)
        
        return component
    
    def _calculate_atom_valence(self, atom: Atom) -> int:
        """Calculate the current valence of an atom."""
        valence = 0
        for bond in atom.bonds:
            valence += int(bond.order.value)
        return valence + abs(atom.charge)
    
    def calculate_properties(self, molecule: Molecule) -> MolecularProperties:
        """
        Calculate molecular properties.
        
        Args:
            molecule: Molecule to analyze
            
        Returns:
            MolecularProperties with calculated values
        """
        if molecule.is_empty():
            return MolecularProperties(
                molecular_weight=0.0,
                molecular_formula="",
                atom_count=0,
                bond_count=0,
                ring_count=0,
                aromatic_ring_count=0,
                hydrogen_bond_donors=0,
                hydrogen_bond_acceptors=0,
                rotatable_bonds=0,
                formal_charge=0
            )
        
        # Basic properties
        molecular_weight = molecule.get_molecular_weight()
        molecular_formula = molecule.get_molecular_formula()
        atom_count = molecule.get_atom_count()
        bond_count = len(molecule.bonds)
        
        # Calculate formal charge
        formal_charge = sum(atom.charge for atom in molecule.atoms)
        
        # Count hydrogen bond donors and acceptors
        hb_donors = self._count_hydrogen_bond_donors(molecule)
        hb_acceptors = self._count_hydrogen_bond_acceptors(molecule)
        
        # Count rotatable bonds (single bonds, not in rings, not terminal)
        rotatable_bonds = self._count_rotatable_bonds(molecule)
        
        # Ring analysis
        rings = self._find_rings(molecule)
        ring_count = len(rings)
        
        # Aromaticity detection
        aromaticity_map = self.detect_aromaticity(molecule)
        aromatic_ring_count = sum(1 for is_aromatic in aromaticity_map.values() if is_aromatic)
        
        # Estimated properties (very simplified)
        estimated_logp = self._estimate_logp(molecule)
        estimated_psa = self._estimate_polar_surface_area(molecule)
        
        return MolecularProperties(
            molecular_weight=molecular_weight,
            molecular_formula=molecular_formula,
            atom_count=atom_count,
            bond_count=bond_count,
            ring_count=ring_count,
            aromatic_ring_count=aromatic_ring_count,
            hydrogen_bond_donors=hb_donors,
            hydrogen_bond_acceptors=hb_acceptors,
            rotatable_bonds=rotatable_bonds,
            formal_charge=formal_charge,
            estimated_logp=estimated_logp,
            estimated_polar_surface_area=estimated_psa
        )
    
    def _count_hydrogen_bond_donors(self, molecule: Molecule) -> int:
        """Count hydrogen bond donors (N-H, O-H, S-H)."""
        count = 0
        for atom in molecule.atoms:
            if atom.element.symbol in self.hb_donors:
                # Count hydrogens bonded to this atom
                for bond in atom.bonds:
                    other_atom = bond.get_other_atom(atom)
                    if other_atom and other_atom.element.symbol == "H":
                        count += 1
                # Also count implicit hydrogens
                if atom.hydrogen_count > 0:
                    count += atom.hydrogen_count
        return count
    
    def _count_hydrogen_bond_acceptors(self, molecule: Molecule) -> int:
        """Count hydrogen bond acceptors (atoms with lone pairs)."""
        count = 0
        for atom in molecule.atoms:
            if atom.element.symbol in self.hb_acceptors:
                # Simplified: count each N, O, S, halogen as one acceptor
                count += 1
        return count
    
    def _count_rotatable_bonds(self, molecule: Molecule) -> int:
        """Count rotatable bonds (single bonds, not in rings, not terminal)."""
        count = 0
        for bond in molecule.bonds:
            if (bond.order == BondOrder.SINGLE and 
                not self._is_terminal_bond(bond) and
                not self._is_in_ring(bond, molecule)):
                count += 1
        return count
    
    def _is_terminal_bond(self, bond: Bond) -> bool:
        """Check if bond is terminal (connected to atom with only one bond)."""
        return len(bond.atom1.bonds) == 1 or len(bond.atom2.bonds) == 1
    
    def _is_in_ring(self, bond: Bond, molecule: Molecule) -> bool:
        """Check if bond is part of a ring (simplified check)."""
        # Remove the bond temporarily and check if atoms are still connected
        atom1, atom2 = bond.atom1, bond.atom2
        
        # Create a temporary graph without this bond
        graph = {}
        for atom in molecule.atoms:
            graph[atom] = []
        
        for b in molecule.bonds:
            if b != bond:
                graph[b.atom1].append(b.atom2)
                graph[b.atom2].append(b.atom1)
        
        # Check if there's still a path between atom1 and atom2
        return self._has_path(graph, atom1, atom2)
    
    def _has_path(self, graph: Dict[Atom, List[Atom]], start: Atom, end: Atom) -> bool:
        """Check if there's a path between two atoms in the graph."""
        if start == end:
            return True
        
        visited = set()
        stack = [start]
        
        while stack:
            current = stack.pop()
            if current == end:
                return True
            
            if current not in visited:
                visited.add(current)
                stack.extend(neighbor for neighbor in graph.get(current, []) 
                           if neighbor not in visited)
        
        return False
    
    def _find_rings(self, molecule: Molecule) -> List[List[Atom]]:
        """
        Find all rings in the molecule using depth-first search.
        
        This implementation finds all simple cycles (rings) in the molecular graph.
        Uses a modified DFS algorithm to detect cycles.
        
        Returns:
            List of rings, where each ring is a list of atoms in the cycle
        """
        if len(molecule.atoms) < 3:
            return []  # Need at least 3 atoms to form a ring
        
        rings = []
        visited_global = set()
        
        for start_atom in molecule.atoms:
            if start_atom in visited_global:
                continue
                
            # Find rings starting from this atom
            rings_from_atom = self._find_rings_from_atom(start_atom, molecule)
            
            # Add unique rings (avoid duplicates)
            for ring in rings_from_atom:
                # Normalize ring representation (start with smallest atom ID)
                normalized_ring = self._normalize_ring(ring)
                if normalized_ring not in [self._normalize_ring(r) for r in rings]:
                    rings.append(ring)
            
            visited_global.add(start_atom)
        
        return rings
    
    def _find_rings_from_atom(self, start_atom: Atom, molecule: Molecule) -> List[List[Atom]]:
        """Find all rings that include the given starting atom."""
        rings = []
        
        def dfs(current_atom: Atom, path: List[Atom], visited: Set[Atom]) -> None:
            if len(path) > 1 and current_atom == start_atom:
                # Found a cycle back to start
                if len(path) >= 3:  # Valid ring size
                    rings.append(path[:-1])  # Exclude the duplicate start atom
                return
            
            if len(path) > 8:  # Limit ring size to prevent infinite loops
                return
            
            if current_atom in visited and current_atom != start_atom:
                return  # Already visited this atom in current path
            
            visited.add(current_atom)
            
            # Explore neighbors
            for neighbor in current_atom.get_connected_atoms():
                if len(path) > 1 and neighbor == path[-2]:
                    continue  # Don't go back to previous atom immediately
                
                dfs(neighbor, path + [neighbor], visited.copy())
        
        # Start DFS from the starting atom
        dfs(start_atom, [start_atom], set())
        return rings
    
    def _normalize_ring(self, ring: List[Atom]) -> List[str]:
        """Normalize ring representation for comparison by using atom IDs."""
        if not ring:
            return []
        
        # Find the atom with the smallest ID
        min_idx = 0
        for i, atom in enumerate(ring):
            if atom.id < ring[min_idx].id:
                min_idx = i
        
        # Rotate the ring to start with the smallest ID
        normalized = ring[min_idx:] + ring[:min_idx]
        
        # Check if reverse order gives a smaller representation
        reversed_ring = list(reversed(normalized))
        if reversed_ring[0].id == normalized[0].id:
            # Same starting atom, compare second atoms
            if len(normalized) > 1:
                if reversed_ring[1].id < normalized[1].id:
                    normalized = reversed_ring
        
        return [atom.id for atom in normalized]
    
    def detect_aromaticity(self, molecule: Molecule) -> Dict[Tuple[Atom, ...], bool]:
        """
        Detect aromatic rings in the molecule.
        
        Uses Hückel's rule (4n+2 π electrons) and other aromaticity criteria:
        1. Ring must be planar (assumed for 2D structures)
        2. Ring must be fully conjugated (alternating single/double bonds or all aromatic)
        3. Ring must have 4n+2 π electrons (Hückel's rule)
        4. All atoms in ring must be sp2 hybridized (simplified check)
        
        Returns:
            Dictionary mapping rings (as tuples) to their aromaticity status
        """
        rings = self._find_rings(molecule)
        aromaticity_map = {}
        
        for ring in rings:
            is_aromatic = self._is_ring_aromatic(ring, molecule)
            aromaticity_map[tuple(ring)] = is_aromatic
        
        return aromaticity_map
    
    def _is_ring_aromatic(self, ring: List[Atom], molecule: Molecule) -> bool:
        """
        Check if a specific ring is aromatic.
        
        Args:
            ring: List of atoms forming the ring
            molecule: The molecule containing the ring
            
        Returns:
            True if the ring is aromatic, False otherwise
        """
        if len(ring) < 3:
            return False
        
        # Check if ring size is appropriate for aromaticity (typically 5, 6, 7, 8)
        if len(ring) < 5 or len(ring) > 8:
            return False
        
        # Count π electrons in the ring
        pi_electrons = 0
        double_bond_count = 0
        has_heteroatom_with_lone_pair = False
        
        for i, atom in enumerate(ring):
            next_atom = ring[(i + 1) % len(ring)]
            
            # Find the bond between current and next atom
            bond = self._find_bond_between_atoms(atom, next_atom, molecule)
            if not bond:
                return False  # Ring is not properly connected
            
            # Count π electrons from bonds
            if bond.order == BondOrder.DOUBLE:
                pi_electrons += 2
                double_bond_count += 1
            elif bond.order == BondOrder.TRIPLE:
                pi_electrons += 4
            elif bond.order == BondOrder.AROMATIC:
                # For aromatic bonds, assume the ring already satisfies Hückel's rule
                return True
            # Single bonds contribute 0 π electrons from the bond itself
        
        # Count π electrons from lone pairs on heteroatoms (only once per atom)
        for atom in ring:
            # Only count lone pairs for heteroatoms that can contribute to aromaticity
            if atom.element.symbol == "N":
                # Nitrogen with 2 bonds (pyrrole-like) contributes 2 π electrons from lone pair
                # Nitrogen with 3 bonds (pyridine-like) contributes 0 π electrons from lone pair
                if len(atom.bonds) == 2:
                    pi_electrons += 2
                    has_heteroatom_with_lone_pair = True
            elif atom.element.symbol == "O":
                # Oxygen with 2 bonds (furan-like) contributes 2 π electrons from lone pair
                if len(atom.bonds) == 2:
                    pi_electrons += 2
                    has_heteroatom_with_lone_pair = True
            elif atom.element.symbol == "S":
                # Sulfur with 2 bonds (thiophene-like) contributes 2 π electrons from lone pair
                if len(atom.bonds) == 2:
                    pi_electrons += 2
                    has_heteroatom_with_lone_pair = True
        
        # Special case validation for common ring patterns:
        # 5-membered ring with alternating bonds (all carbon): 2 double bonds = 4 π electrons (NOT aromatic)
        # 6-membered ring with alternating bonds (all carbon): 3 double bonds = 6 π electrons (aromatic - benzene)
        if len(ring) == 5 and double_bond_count == 2 and not has_heteroatom_with_lone_pair:
            # Pure carbon 5-ring with alternating bonds has 4 π electrons (not 4n+2)
            return False
        
        # Apply Hückel's rule: 4n+2 π electrons
        # Common aromatic systems: 6 (benzene), 10 (naphthalene), 14, etc.
        huckel_numbers = [2, 6, 10, 14, 18, 22]  # 4n+2 for n=0,1,2,3,4,5
        
        if pi_electrons in huckel_numbers:
            # Additional checks for aromaticity
            return self._additional_aromaticity_checks(ring, molecule)
        
        return False
    
    def _find_bond_between_atoms(self, atom1: Atom, atom2: Atom, molecule: Molecule) -> Optional[Bond]:
        """Find the bond between two specific atoms."""
        for bond in molecule.bonds:
            if bond.contains_atom(atom1) and bond.contains_atom(atom2):
                return bond
        return None
    
    def _additional_aromaticity_checks(self, ring: List[Atom], molecule: Molecule) -> bool:
        """
        Perform additional checks for aromaticity beyond Hückel's rule.
        
        Args:
            ring: List of atoms in the ring
            molecule: The molecule containing the ring
            
        Returns:
            True if additional aromaticity criteria are met
        """
        # Check if all atoms in ring can participate in π system
        for atom in ring:
            element = atom.element.symbol
            
            # Common aromatic atoms: C, N, O, S
            if element not in ["C", "N", "O", "S"]:
                return False
            
            # Check hybridization (simplified)
            # Atoms in aromatic rings should be sp2 hybridized
            # This is approximated by checking bond count and geometry
            bond_count = len(atom.bonds)
            
            if element == "C":
                # Carbon should have 3 bonds (sp2) or be part of aromatic system
                if bond_count < 2 or bond_count > 3:
                    return False
            elif element == "N":
                # Nitrogen can have 2-3 bonds in aromatic systems
                if bond_count < 2 or bond_count > 3:
                    return False
            elif element == "O":
                # Oxygen typically has 2 bonds in aromatic systems
                if bond_count != 2:
                    return False
        
        # Check for conjugation (alternating or aromatic bonds)
        has_conjugation = True
        for i in range(len(ring)):
            next_i = (i + 1) % len(ring)
            bond = self._find_bond_between_atoms(ring[i], ring[next_i], molecule)
            
            if bond and bond.order not in [BondOrder.SINGLE, BondOrder.DOUBLE, BondOrder.AROMATIC]:
                has_conjugation = False
                break
        
        return has_conjugation
    
    def mark_aromatic_bonds(self, molecule: Molecule) -> None:
        """
        Mark bonds in aromatic rings with aromatic bond order.
        
        This method identifies aromatic rings and updates the bond orders
        of bonds within those rings to BondOrder.AROMATIC.
        
        Args:
            molecule: The molecule to process
        """
        aromaticity_map = self.detect_aromaticity(molecule)
        
        for ring_tuple, is_aromatic in aromaticity_map.items():
            if is_aromatic:
                ring = list(ring_tuple)  # Convert tuple back to list
                # Mark all bonds in this ring as aromatic
                for i in range(len(ring)):
                    next_i = (i + 1) % len(ring)
                    bond = self._find_bond_between_atoms(ring[i], ring[next_i], molecule)
                    
                    if bond:
                        bond.order = BondOrder.AROMATIC
    
    def _estimate_logp(self, molecule: Molecule) -> float:
        """Estimate logP using a very simplified method."""
        # Simplified Crippen method - just count atom types
        logp = 0.0
        
        for atom in molecule.atoms:
            symbol = atom.element.symbol
            if symbol == "C":
                logp += 0.1441  # Simplified carbon contribution
            elif symbol == "N":
                logp -= 0.4806  # Simplified nitrogen contribution
            elif symbol == "O":
                logp -= 0.2893  # Simplified oxygen contribution
            elif symbol in ["F", "Cl", "Br", "I"]:
                logp += 0.2148  # Simplified halogen contribution
        
        return logp
    
    def _estimate_polar_surface_area(self, molecule: Molecule) -> float:
        """Estimate polar surface area using simplified method."""
        psa = 0.0
        
        for atom in molecule.atoms:
            symbol = atom.element.symbol
            if symbol == "N":
                psa += 23.79  # Simplified nitrogen PSA
            elif symbol == "O":
                psa += 23.06  # Simplified oxygen PSA
        
        return psa
    
    def suggest_corrections(self, molecule: Molecule) -> List[str]:
        """
        Suggest corrections for chemical structure issues.
        
        Args:
            molecule: Molecule to analyze
            
        Returns:
            List of suggestion strings
        """
        validation_result = self.validate_structure(molecule)
        suggestions = []
        
        for issue in validation_result.issues:
            if issue.suggestion:
                suggestions.append(issue.suggestion)
        
        return suggestions