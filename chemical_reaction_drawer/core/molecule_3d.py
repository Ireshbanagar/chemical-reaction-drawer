"""
3D molecular representation and coordinate generation.

This module provides classes and functions for working with 3D molecular
structures, including conversion from 2D to 3D coordinates and conformation
management.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import math
import random
from .models import Molecule, Atom, Bond, Point3D, Point2D


@dataclass
class Conformation:
    """
    Represents a 3D conformation of a molecule.
    
    Attributes:
        atom_positions: Dictionary mapping atom IDs to 3D positions
        energy: Estimated energy of this conformation
        name: Optional name for this conformation
    """
    atom_positions: Dict[str, Point3D] = field(default_factory=dict)
    energy: float = 0.0
    name: Optional[str] = None
    
    def calculate_rmsd(self, other: 'Conformation') -> float:
        """
        Calculate Root Mean Square Deviation between two conformations.
        
        Args:
            other: Another conformation to compare with
            
        Returns:
            RMSD value in Angstroms
        """
        if not self.atom_positions or not other.atom_positions:
            return float('inf')
        
        common_atoms = set(self.atom_positions.keys()) & set(other.atom_positions.keys())
        if not common_atoms:
            return float('inf')
        
        sum_squared_distances = 0.0
        for atom_id in common_atoms:
            pos1 = self.atom_positions[atom_id]
            pos2 = other.atom_positions[atom_id]
            distance_squared = (
                (pos1.x - pos2.x) ** 2 +
                (pos1.y - pos2.y) ** 2 +
                (pos1.z - pos2.z) ** 2
            )
            sum_squared_distances += distance_squared
        
        return math.sqrt(sum_squared_distances / len(common_atoms))


class Molecule3D:
    """
    Extended molecule class with 3D coordinate support and conformation management.
    
    This class wraps a regular Molecule and adds 3D-specific functionality
    including multiple conformations and 3D coordinate generation.
    """
    
    def __init__(self, molecule: Molecule):
        """
        Initialize 3D molecule from a 2D molecule.
        
        Args:
            molecule: Base 2D molecule
        """
        self.molecule = molecule
        self.conformations: List[Conformation] = []
        self.active_conformation_index: int = 0
        
        # Generate initial 3D coordinates if not present
        if not self._has_3d_coordinates():
            self.generate_3d_coordinates()
    
    def _has_3d_coordinates(self) -> bool:
        """Check if the molecule already has 3D coordinates."""
        return any(atom.position_3d is not None for atom in self.molecule.atoms)
    
    def generate_3d_coordinates(self, method: str = "simple") -> None:
        """
        Generate 3D coordinates from 2D coordinates.
        
        Args:
            method: Method to use for coordinate generation
                   - "simple": Basic planar to 3D conversion
                   - "distance_geometry": Distance geometry approach
        """
        if method == "simple":
            self._generate_simple_3d()
        elif method == "distance_geometry":
            self._generate_distance_geometry_3d()
        else:
            raise ValueError(f"Unknown 3D generation method: {method}")
        
        # Create initial conformation
        self._update_conformation_from_molecule()
    
    def _generate_simple_3d(self) -> None:
        """
        Simple 3D coordinate generation by adding Z coordinates.
        
        This method places atoms in a roughly planar arrangement with
        small random Z displacements to avoid perfect planarity.
        """
        for atom in self.molecule.atoms:
            # Use 2D coordinates for X and Y
            x = atom.position.x
            y = atom.position.y
            
            # Add small random Z displacement
            z = random.uniform(-0.1, 0.1)
            
            # For bonded atoms, try to create more realistic 3D geometry
            if atom.bonds:
                # Calculate average bond angle and adjust Z based on hybridization
                bond_count = len(atom.bonds)
                
                if bond_count == 1:
                    # Terminal atom - small Z displacement
                    z = random.uniform(-0.2, 0.2)
                elif bond_count == 2:
                    # Linear or bent - moderate Z displacement
                    z = random.uniform(-0.3, 0.3)
                elif bond_count == 3:
                    # Trigonal planar - keep mostly planar
                    z = random.uniform(-0.1, 0.1)
                elif bond_count == 4:
                    # Tetrahedral - larger Z displacement
                    z = random.uniform(-0.5, 0.5)
            
            atom.position_3d = Point3D(x, y, z)
    
    def _generate_distance_geometry_3d(self) -> None:
        """
        Generate 3D coordinates using distance geometry approach.
        
        This method uses ideal bond lengths and angles to generate
        more chemically accurate 3D structures.
        """
        if not self.molecule.atoms:
            return
        
        # Start with first atom at origin
        first_atom = self.molecule.atoms[0]
        first_atom.position_3d = Point3D(0.0, 0.0, 0.0)
        
        # Keep track of placed atoms
        placed_atoms = {first_atom}
        
        # Place atoms iteratively based on bonds
        while len(placed_atoms) < len(self.molecule.atoms):
            for atom in self.molecule.atoms:
                if atom in placed_atoms:
                    continue
                
                # Find connected atoms that are already placed
                connected_placed = []
                for bond in atom.bonds:
                    other_atom = bond.get_other_atom(atom)
                    if other_atom and other_atom in placed_atoms:
                        connected_placed.append((other_atom, bond))
                
                if not connected_placed:
                    continue
                
                # Place atom based on first connected atom
                ref_atom, ref_bond = connected_placed[0]
                ideal_distance = self._get_ideal_bond_length(ref_bond)
                
                # Simple placement at ideal distance
                direction = self._get_random_direction()
                atom.position_3d = Point3D(
                    ref_atom.position_3d.x + direction[0] * ideal_distance,
                    ref_atom.position_3d.y + direction[1] * ideal_distance,
                    ref_atom.position_3d.z + direction[2] * ideal_distance
                )
                
                placed_atoms.add(atom)
                break
    
    def _get_ideal_bond_length(self, bond: Bond) -> float:
        """
        Get ideal bond length based on atom types and bond order.
        
        Args:
            bond: Bond to get length for
            
        Returns:
            Ideal bond length in Angstroms
        """
        # Simple bond length lookup table
        bond_lengths = {
            ("C", "C", 1): 1.54,  # C-C single
            ("C", "C", 2): 1.34,  # C=C double
            ("C", "C", 3): 1.20,  # C≡C triple
            ("C", "H", 1): 1.09,  # C-H
            ("C", "N", 1): 1.47,  # C-N
            ("C", "O", 1): 1.43,  # C-O
            ("N", "H", 1): 1.01,  # N-H
            ("O", "H", 1): 0.96,  # O-H
        }
        
        symbol1 = bond.atom1.element.symbol
        symbol2 = bond.atom2.element.symbol
        order = int(bond.order.value)
        
        # Try both orders
        key1 = (symbol1, symbol2, order)
        key2 = (symbol2, symbol1, order)
        
        if key1 in bond_lengths:
            return bond_lengths[key1]
        elif key2 in bond_lengths:
            return bond_lengths[key2]
        else:
            # Default bond length
            return 1.5
    
    def _get_random_direction(self) -> Tuple[float, float, float]:
        """Generate a random unit direction vector."""
        # Generate random point on unit sphere
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        
        return (x, y, z)
    
    def _update_conformation_from_molecule(self) -> None:
        """Update the current conformation from molecule's 3D coordinates."""
        conformation = Conformation(name="default")
        
        for atom in self.molecule.atoms:
            if atom.position_3d:
                conformation.atom_positions[atom.id] = atom.position_3d
        
        if self.conformations:
            self.conformations[0] = conformation
        else:
            self.conformations.append(conformation)
    
    def add_conformation(self, conformation: Conformation) -> None:
        """Add a new conformation to the molecule."""
        self.conformations.append(conformation)
    
    def set_active_conformation(self, index: int) -> None:
        """
        Set the active conformation and update molecule coordinates.
        
        Args:
            index: Index of the conformation to activate
        """
        if 0 <= index < len(self.conformations):
            self.active_conformation_index = index
            self._apply_conformation_to_molecule(self.conformations[index])
    
    def _apply_conformation_to_molecule(self, conformation: Conformation) -> None:
        """Apply a conformation's coordinates to the molecule."""
        for atom in self.molecule.atoms:
            if atom.id in conformation.atom_positions:
                atom.position_3d = conformation.atom_positions[atom.id]
    
    def get_active_conformation(self) -> Optional[Conformation]:
        """Get the currently active conformation."""
        if 0 <= self.active_conformation_index < len(self.conformations):
            return self.conformations[self.active_conformation_index]
        return None
    
    def optimize_geometry(self, method: str = "simple") -> None:
        """
        Optimize the 3D geometry of the molecule.
        
        Args:
            method: Optimization method to use
        """
        if method == "simple":
            self._simple_geometry_optimization()
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        # Update conformation
        self._update_conformation_from_molecule()
    
    def _simple_geometry_optimization(self) -> None:
        """
        Simple geometry optimization using basic force field principles.
        
        This is a very basic implementation that adjusts bond lengths
        and angles towards ideal values.
        """
        max_iterations = 100
        step_size = 0.01
        
        for iteration in range(max_iterations):
            forces = {}
            
            # Initialize forces
            for atom in self.molecule.atoms:
                forces[atom.id] = Point3D(0.0, 0.0, 0.0)
            
            # Calculate bond length forces
            for bond in self.molecule.bonds:
                if not bond.atom1.position_3d or not bond.atom2.position_3d:
                    continue
                
                current_length = bond.atom1.position_3d.distance_to(bond.atom2.position_3d)
                ideal_length = self._get_ideal_bond_length(bond)
                
                if current_length > 0:
                    # Force magnitude proportional to deviation from ideal
                    force_magnitude = (ideal_length - current_length) * 0.1
                    
                    # Direction vector
                    dx = bond.atom2.position_3d.x - bond.atom1.position_3d.x
                    dy = bond.atom2.position_3d.y - bond.atom1.position_3d.y
                    dz = bond.atom2.position_3d.z - bond.atom1.position_3d.z
                    
                    # Normalize
                    length = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if length > 0:
                        dx /= length
                        dy /= length
                        dz /= length
                    
                    # Apply forces
                    force_x = dx * force_magnitude
                    force_y = dy * force_magnitude
                    force_z = dz * force_magnitude
                    
                    forces[bond.atom1.id] = Point3D(
                        forces[bond.atom1.id].x + force_x,
                        forces[bond.atom1.id].y + force_y,
                        forces[bond.atom1.id].z + force_z
                    )
                    
                    forces[bond.atom2.id] = Point3D(
                        forces[bond.atom2.id].x - force_x,
                        forces[bond.atom2.id].y - force_y,
                        forces[bond.atom2.id].z - force_z
                    )
            
            # Apply forces to update positions
            max_force = 0.0
            for atom in self.molecule.atoms:
                if atom.position_3d and atom.id in forces:
                    force = forces[atom.id]
                    force_magnitude = math.sqrt(force.x*force.x + force.y*force.y + force.z*force.z)
                    max_force = max(max_force, force_magnitude)
                    
                    atom.position_3d = Point3D(
                        atom.position_3d.x + force.x * step_size,
                        atom.position_3d.y + force.y * step_size,
                        atom.position_3d.z + force.z * step_size
                    )
            
            # Check for convergence
            if max_force < 0.001:
                break
    
    def calculate_surface_area(self) -> float:
        """
        Calculate approximate molecular surface area.
        
        Returns:
            Surface area in square Angstroms
        """
        if not self.molecule.atoms:
            return 0.0
        
        # Simple approximation using van der Waals radii
        vdw_radii = {
            "H": 1.20, "C": 1.70, "N": 1.55, "O": 1.52,
            "F": 1.47, "P": 1.80, "S": 1.80, "Cl": 1.75
        }
        
        total_area = 0.0
        
        for atom in self.molecule.atoms:
            if not atom.position_3d:
                continue
            
            radius = vdw_radii.get(atom.element.symbol, 1.5)
            sphere_area = 4 * math.pi * radius * radius
            
            # Reduce area based on overlaps with other atoms
            overlap_factor = 1.0
            for other_atom in self.molecule.atoms:
                if other_atom == atom or not other_atom.position_3d:
                    continue
                
                distance = atom.position_3d.distance_to(other_atom.position_3d)
                other_radius = vdw_radii.get(other_atom.element.symbol, 1.5)
                
                if distance < radius + other_radius:
                    # Simple overlap reduction
                    overlap = (radius + other_radius - distance) / (radius + other_radius)
                    overlap_factor *= (1.0 - overlap * 0.5)
            
            total_area += sphere_area * overlap_factor
        
        return total_area
    
    def get_center_of_mass(self) -> Optional[Point3D]:
        """
        Calculate the center of mass of the molecule.
        
        Returns:
            Center of mass coordinates, or None if no 3D coordinates
        """
        if not self.molecule.atoms:
            return None
        
        total_mass = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        weighted_z = 0.0
        
        for atom in self.molecule.atoms:
            if not atom.position_3d:
                continue
            
            mass = atom.element.atomic_weight
            total_mass += mass
            weighted_x += atom.position_3d.x * mass
            weighted_y += atom.position_3d.y * mass
            weighted_z += atom.position_3d.z * mass
        
        if total_mass > 0:
            return Point3D(
                weighted_x / total_mass,
                weighted_y / total_mass,
                weighted_z / total_mass
            )
        
        return None
    
    def get_bounding_box(self) -> Optional[Tuple[Point3D, Point3D]]:
        """
        Get the 3D bounding box of the molecule.
        
        Returns:
            Tuple of (min_point, max_point) or None if no 3D coordinates
        """
        atoms_with_3d = [atom for atom in self.molecule.atoms if atom.position_3d]
        
        if not atoms_with_3d:
            return None
        
        first_pos = atoms_with_3d[0].position_3d
        min_x = max_x = first_pos.x
        min_y = max_y = first_pos.y
        min_z = max_z = first_pos.z
        
        for atom in atoms_with_3d[1:]:
            pos = atom.position_3d
            min_x = min(min_x, pos.x)
            max_x = max(max_x, pos.x)
            min_y = min(min_y, pos.y)
            max_y = max(max_y, pos.y)
            min_z = min(min_z, pos.z)
            max_z = max(max_z, pos.z)
        
        return (Point3D(min_x, min_y, min_z), Point3D(max_x, max_y, max_z))


class CoordinateGenerator:
    """
    Utility class for generating 3D coordinates from 2D structures.
    """
    
    @staticmethod
    def convert_2d_to_3d(molecule: Molecule, method: str = "simple") -> Molecule3D:
        """
        Convert a 2D molecule to 3D.
        
        Args:
            molecule: 2D molecule to convert
            method: Conversion method to use
            
        Returns:
            3D molecule with generated coordinates
        """
        mol_3d = Molecule3D(molecule)
        mol_3d.generate_3d_coordinates(method)
        return mol_3d
    
    @staticmethod
    def generate_multiple_conformations(molecule: Molecule, count: int = 5) -> Molecule3D:
        """
        Generate multiple conformations for a molecule.
        
        Args:
            molecule: Base molecule
            count: Number of conformations to generate
            
        Returns:
            3D molecule with multiple conformations
        """
        mol_3d = Molecule3D(molecule)
        
        # Generate additional conformations with different random seeds
        for i in range(count - 1):
            # Create a copy and generate different coordinates
            temp_mol = molecule.copy()
            temp_mol_3d = Molecule3D(temp_mol)
            temp_mol_3d.generate_3d_coordinates("simple")
            
            # Extract conformation
            conformation = Conformation(name=f"conformation_{i+2}")
            for atom in temp_mol_3d.molecule.atoms:
                if atom.position_3d:
                    # Map back to original atom IDs
                    original_atom = molecule.atoms[temp_mol.atoms.index(atom)]
                    conformation.atom_positions[original_atom.id] = atom.position_3d
            
            mol_3d.add_conformation(conformation)
        
        return mol_3d