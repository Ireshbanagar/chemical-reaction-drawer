"""
Molecule generator from SMILES strings.
"""

from typing import Optional, List, Tuple
from ..core.models import Molecule, Atom, Bond, BondOrder, Point2D


class SMILESParser:
    """Parse SMILES strings and generate Molecule objects."""
    
    # Bond symbols to BondOrder mapping
    BOND_MAP = {
        '-': BondOrder.SINGLE,
        '=': BondOrder.DOUBLE,
        '#': BondOrder.TRIPLE,
    }
    
    def __init__(self):
        self.molecule = None
        self.atom_stack = []
        self.ring_atoms = {}
    
    def parse(self, smiles: str) -> Optional[Molecule]:
        """Parse SMILES string and return Molecule object."""
        if not smiles:
            return None
        
        try:
            self.molecule = Molecule()
            self.atom_stack = []
            self.ring_atoms = {}
            
            # Simple SMILES parser
            i = 0
            prev_atom = None
            bond_order = BondOrder.SINGLE
            
            while i < len(smiles):
                char = smiles[i]
                
                # Handle aromatic atoms (lowercase)
                if char.islower():
                    element = char.upper()
                    atom = self._add_atom(element)
                    if prev_atom:
                        self._add_bond(prev_atom, atom, bond_order)
                    prev_atom = atom
                    bond_order = BondOrder.SINGLE
                
                # Handle regular atoms (uppercase)
                elif char.isupper():
                    element = char
                    # Check for two-letter elements
                    if i + 1 < len(smiles) and smiles[i + 1].islower():
                        element += smiles[i + 1]
                        i += 1
                    
                    atom = self._add_atom(element)
                    if prev_atom:
                        self._add_bond(prev_atom, atom, bond_order)
                    prev_atom = atom
                    bond_order = BondOrder.SINGLE
                
                # Handle bonds
                elif char in self.BOND_MAP:
                    bond_order = self.BOND_MAP[char]
                
                # Handle branches
                elif char == '(':
                    self.atom_stack.append(prev_atom)
                
                elif char == ')':
                    if self.atom_stack:
                        prev_atom = self.atom_stack.pop()
                    bond_order = BondOrder.SINGLE
                
                # Handle rings
                elif char.isdigit():
                    ring_num = int(char)
                    if ring_num in self.ring_atoms:
                        # Close ring
                        ring_atom = self.ring_atoms[ring_num]
                        if prev_atom:
                            self._add_bond(ring_atom, prev_atom, bond_order)
                        del self.ring_atoms[ring_num]
                    else:
                        # Open ring
                        self.ring_atoms[ring_num] = prev_atom
                    bond_order = BondOrder.SINGLE
                
                i += 1
            
            # Layout the molecule in 2D
            self._layout_2d()
            
            return self.molecule
            
        except Exception as e:
            print(f"SMILES parsing error: {e}")
            return None
    
    def _add_atom(self, element: str) -> Atom:
        """Add atom to molecule with automatic positioning."""
        # Position will be set by layout algorithm
        position = Point2D(0, 0)
        return self.molecule.add_atom(element, position)
    
    def _add_bond(self, atom1: Atom, atom2: Atom, order: BondOrder):
        """Add bond between two atoms."""
        if atom1 and atom2 and atom1 != atom2:
            self.molecule.add_bond(atom1, atom2, order)
    
    def _layout_2d(self):
        """Simple 2D layout algorithm for molecule."""
        if not self.molecule.atoms:
            return
        
        # Simple linear layout for now
        # In production, use a proper force-directed or ring-based layout
        spacing = 50.0
        x, y = 100.0, 300.0
        
        visited = set()
        
        def layout_from_atom(atom: Atom, pos: Point2D, angle: float = 0):
            """Recursively layout atoms."""
            if atom in visited:
                return
            
            visited.add(atom)
            atom.position = pos
            
            # Layout connected atoms
            connected = atom.get_connected_atoms()
            num_connected = len([a for a in connected if a not in visited])
            
            if num_connected > 0:
                angle_step = 120.0 if num_connected > 1 else 0
                current_angle = angle
                
                for connected_atom in connected:
                    if connected_atom not in visited:
                        # Calculate new position
                        import math
                        rad = math.radians(current_angle)
                        new_x = pos.x + spacing * math.cos(rad)
                        new_y = pos.y + spacing * math.sin(rad)
                        new_pos = Point2D(new_x, new_y)
                        
                        layout_from_atom(connected_atom, new_pos, current_angle)
                        current_angle += angle_step
        
        # Start layout from first atom
        if self.molecule.atoms:
            layout_from_atom(self.molecule.atoms[0], Point2D(x, y))


class MoleculeGenerator:
    """High-level molecule generation from various inputs."""
    
    def __init__(self):
        self.parser = SMILESParser()
    
    def from_smiles(self, smiles: str) -> Optional[Molecule]:
        """Generate molecule from SMILES string."""
        return self.parser.parse(smiles)
    
    def from_name(self, name: str, bedrock_client) -> Optional[Molecule]:
        """Generate molecule from name using Bedrock."""
        # Get SMILES from Bedrock
        smiles = bedrock_client.generate_molecule_from_name(name)
        
        if not smiles:
            return None
        
        # Parse SMILES to Molecule
        return self.from_smiles(smiles)
