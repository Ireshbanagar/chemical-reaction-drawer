"""
Template placement and advanced search functionality.

This module provides template placement operations and advanced search
capabilities for the chemical template library system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Tuple, Any
import math

from .models import Molecule, Atom, Bond, Point2D, BondOrder
from .templates import Template, TemplateLibrary


class TemplatePlacement:
    """Handles template placement operations."""
    
    def __init__(self):
        self.placement_offset = Point2D(0.0, 0.0)
        self.auto_connect = True
        self.connection_distance_threshold = 2.0  # Maximum distance for auto-connection
    
    def place_template_at_position(self, template: Template, position: Point2D, 
                                 target_molecule: Optional[Molecule] = None) -> 'PlacementResult':
        """
        Place a template at a specific position.
        
        Args:
            template: Template to place
            position: Target position for placement
            target_molecule: Existing molecule to place template into (optional)
            
        Returns:
            PlacementResult with placement information
        """
        # Create a copy of the template structure
        placed_structure = self._copy_template_structure(template)
        
        # Calculate the center of the template structure
        template_center = self._calculate_structure_center(placed_structure)
        
        # Calculate offset needed to move template to target position
        offset = Point2D(position.x - template_center.x, position.y - template_center.y)
        
        # Apply offset to all atoms in the placed structure
        for atom in placed_structure.atoms:
            atom.position = Point2D(
                atom.position.x + offset.x,
                atom.position.y + offset.y
            )
        
        # If target molecule is provided, merge the structures
        if target_molecule:
            merge_result = self._merge_structures(target_molecule, placed_structure, position)
            return PlacementResult(
                success=True,
                placed_atoms=merge_result.new_atoms,
                placed_bonds=merge_result.new_bonds,
                connections_made=merge_result.connections,
                target_molecule=target_molecule
            )
        else:
            return PlacementResult(
                success=True,
                placed_atoms=placed_structure.atoms,
                placed_bonds=placed_structure.bonds,
                connections_made=[],
                target_molecule=placed_structure
            )
    
    def place_template_with_connection(self, template: Template, connection_point: Point2D,
                                     target_atom: Atom, target_molecule: Molecule) -> 'PlacementResult':
        """
        Place a template with a specific connection to an existing atom.
        
        Args:
            template: Template to place
            connection_point: Point in template to connect from
            target_atom: Atom in target molecule to connect to
            target_molecule: Molecule containing the target atom
            
        Returns:
            PlacementResult with placement information
        """
        # Create a copy of the template structure
        placed_structure = self._copy_template_structure(template)
        
        # Find the atom in the placed structure closest to the connection point
        connection_atom = self._find_closest_atom(placed_structure, connection_point)
        
        if not connection_atom:
            return PlacementResult(success=False, error="No suitable connection atom found")
        
        # Calculate offset to align connection atom with target atom
        offset = Point2D(
            target_atom.position.x - connection_atom.position.x,
            target_atom.position.y - connection_atom.position.y
        )
        
        # Apply offset to all atoms in the placed structure
        for atom in placed_structure.atoms:
            atom.position = Point2D(
                atom.position.x + offset.x,
                atom.position.y + offset.y
            )
        
        # Merge structures and create connection
        merge_result = self._merge_structures(target_molecule, placed_structure, target_atom.position)
        
        # Create bond between target atom and connection atom
        try:
            # Find the connection atom in the merged structure
            merged_connection_atom = next(
                atom for atom in merge_result.new_atoms 
                if atom.position.distance_to(target_atom.position) < 0.1
            )
            
            connection_bond = target_molecule.add_bond(target_atom, merged_connection_atom)
            merge_result.connections.append(connection_bond)
            
        except (StopIteration, ValueError):
            pass  # Connection failed, but placement succeeded
        
        return PlacementResult(
            success=True,
            placed_atoms=merge_result.new_atoms,
            placed_bonds=merge_result.new_bonds,
            connections_made=merge_result.connections,
            target_molecule=target_molecule
        )
    
    def _copy_template_structure(self, template: Template) -> Molecule:
        """Create a deep copy of the template structure."""
        return template.copy().structure
    
    def _calculate_structure_center(self, molecule: Molecule) -> Point2D:
        """Calculate the geometric center of a molecular structure."""
        if not molecule.atoms:
            return Point2D(0.0, 0.0)
        
        total_x = sum(atom.position.x for atom in molecule.atoms)
        total_y = sum(atom.position.y for atom in molecule.atoms)
        count = len(molecule.atoms)
        
        return Point2D(total_x / count, total_y / count)
    
    def _find_closest_atom(self, molecule: Molecule, position: Point2D) -> Optional[Atom]:
        """Find the atom closest to a given position."""
        if not molecule.atoms:
            return None
        
        closest_atom = None
        min_distance = float('inf')
        
        for atom in molecule.atoms:
            distance = atom.position.distance_to(position)
            if distance < min_distance:
                min_distance = distance
                closest_atom = atom
        
        return closest_atom
    
    def _merge_structures(self, target: Molecule, source: Molecule, 
                         merge_position: Point2D) -> 'MergeResult':
        """Merge source structure into target structure."""
        new_atoms = []
        new_bonds = []
        connections = []
        atom_mapping = {}
        
        # Add all atoms from source to target
        for source_atom in source.atoms:
            new_atom = target.add_atom(
                source_atom.element.symbol,
                source_atom.position,
                source_atom.charge,
                source_atom.position_3d
            )
            new_atoms.append(new_atom)
            atom_mapping[source_atom] = new_atom
        
        # Add all bonds from source to target
        for source_bond in source.bonds:
            new_atom1 = atom_mapping[source_bond.atom1]
            new_atom2 = atom_mapping[source_bond.atom2]
            
            new_bond = target.add_bond(
                new_atom1, new_atom2,
                source_bond.order,
                source_bond.stereo,
                source_bond.style
            )
            new_bonds.append(new_bond)
        
        # Check for auto-connections if enabled
        if self.auto_connect:
            auto_connections = self._find_auto_connections(target, new_atoms, merge_position)
            connections.extend(auto_connections)
        
        return MergeResult(new_atoms, new_bonds, connections)
    
    def _find_auto_connections(self, molecule: Molecule, new_atoms: List[Atom], 
                             position: Point2D) -> List[Bond]:
        """Find potential automatic connections between new and existing atoms."""
        connections = []
        
        # Get existing atoms (not including the newly added ones)
        existing_atoms = [atom for atom in molecule.atoms if atom not in new_atoms]
        
        for new_atom in new_atoms:
            for existing_atom in existing_atoms:
                distance = new_atom.position.distance_to(existing_atom.position)
                
                # If atoms are close enough and connection makes chemical sense
                if (distance <= self.connection_distance_threshold and 
                    self._should_auto_connect(new_atom, existing_atom)):
                    
                    try:
                        bond = molecule.add_bond(new_atom, existing_atom)
                        connections.append(bond)
                        break  # Only one auto-connection per new atom
                    except ValueError:
                        continue  # Bond already exists or invalid
        
        return connections
    
    def _should_auto_connect(self, atom1: Atom, atom2: Atom) -> bool:
        """Determine if two atoms should be automatically connected."""
        # Simple heuristic: connect if both atoms can accept more bonds
        atom1_available_bonds = self._get_available_bond_count(atom1)
        atom2_available_bonds = self._get_available_bond_count(atom2)
        
        return atom1_available_bonds > 0 and atom2_available_bonds > 0
    
    def _get_available_bond_count(self, atom: Atom) -> int:
        """Get the number of additional bonds an atom can form."""
        if not atom.element.common_valences:
            return 0
        
        max_valence = max(atom.element.common_valences)
        current_bonds = sum(bond.order.value for bond in atom.bonds)
        
        return max(0, int(max_valence - current_bonds))


@dataclass
class PlacementResult:
    """Result of a template placement operation."""
    success: bool
    placed_atoms: List[Atom] = field(default_factory=list)
    placed_bonds: List[Bond] = field(default_factory=list)
    connections_made: List[Bond] = field(default_factory=list)
    target_molecule: Optional[Molecule] = None
    error: Optional[str] = None


@dataclass
class MergeResult:
    """Result of merging two molecular structures."""
    new_atoms: List[Atom]
    new_bonds: List[Bond]
    connections: List[Bond]


class AdvancedTemplateSearch:
    """Advanced search functionality for templates."""
    
    def __init__(self, library: TemplateLibrary):
        self.library = library
        self.search_cache = {}
        self.search_history = []
    
    def search_by_substructure(self, query_structure: Molecule) -> List[Template]:
        """Search for templates containing a specific substructure."""
        matching_templates = []
        
        for template in self.library.get_all_templates():
            if self._contains_substructure(template.structure, query_structure):
                matching_templates.append(template)
        
        return matching_templates
    
    def search_by_similarity(self, reference_template: Template, 
                           similarity_threshold: float = 0.7) -> List[Template]:
        """Search for templates similar to a reference template."""
        matching_templates = []
        
        for template in self.library.get_all_templates():
            if template.id == reference_template.id:
                continue  # Skip the reference template itself
            
            similarity = self._calculate_similarity(reference_template, template)
            if similarity >= similarity_threshold:
                matching_templates.append(template)
        
        # Sort by similarity (highest first)
        matching_templates.sort(
            key=lambda t: self._calculate_similarity(reference_template, t),
            reverse=True
        )
        
        return matching_templates
    
    def search_by_functional_groups(self, functional_groups: List[str]) -> List[Template]:
        """Search for templates containing specific functional groups."""
        matching_templates = []
        
        for template in self.library.get_all_templates():
            template_functional_groups = self._identify_functional_groups(template.structure)
            
            # Check if template contains all requested functional groups
            if all(fg in template_functional_groups for fg in functional_groups):
                matching_templates.append(template)
        
        return matching_templates
    
    def search_by_ring_systems(self, ring_sizes: List[int], 
                             aromatic_only: bool = False) -> List[Template]:
        """Search for templates containing specific ring systems."""
        matching_templates = []
        
        for template in self.library.get_all_templates():
            template_rings = self._find_rings(template.structure)
            
            for ring in template_rings:
                ring_size = len(ring)
                is_aromatic = self._is_aromatic_ring(ring)
                
                if (ring_size in ring_sizes and 
                    (not aromatic_only or is_aromatic)):
                    matching_templates.append(template)
                    break  # Found matching ring, no need to check others
        
        return matching_templates
    
    def search_by_element_composition(self, required_elements: List[str],
                                    forbidden_elements: List[str] = None) -> List[Template]:
        """Search for templates with specific element composition."""
        matching_templates = []
        forbidden_elements = forbidden_elements or []
        
        for template in self.library.get_all_templates():
            template_elements = self._get_element_set(template.structure)
            
            # Check if template contains all required elements
            has_required = all(elem in template_elements for elem in required_elements)
            
            # Check if template contains any forbidden elements
            has_forbidden = any(elem in template_elements for elem in forbidden_elements)
            
            if has_required and not has_forbidden:
                matching_templates.append(template)
        
        return matching_templates
    
    def search_by_molecular_weight_range(self, min_weight: float, max_weight: float) -> List[Template]:
        """Search for templates within a molecular weight range."""
        matching_templates = []
        
        for template in self.library.get_all_templates():
            weight = template.metadata.molecular_weight
            if min_weight <= weight <= max_weight:
                matching_templates.append(template)
        
        return matching_templates
    
    def combined_search(self, criteria: Dict[str, Any]) -> List[Template]:
        """Perform a combined search using multiple criteria."""
        # Start with all templates
        candidates = self.library.get_all_templates()
        
        # Apply each criterion
        if 'text_query' in criteria:
            candidates = [t for t in candidates if t.metadata.matches_search(criteria['text_query'])]
        
        if 'categories' in criteria:
            candidates = [t for t in candidates if t.metadata.category in criteria['categories']]
        
        if 'molecular_weight_range' in criteria:
            min_w, max_w = criteria['molecular_weight_range']
            candidates = [t for t in candidates if min_w <= t.metadata.molecular_weight <= max_w]
        
        if 'required_elements' in criteria:
            candidates = [t for t in candidates 
                         if all(elem in self._get_element_set(t.structure) 
                               for elem in criteria['required_elements'])]
        
        if 'forbidden_elements' in criteria:
            candidates = [t for t in candidates 
                         if not any(elem in self._get_element_set(t.structure) 
                                   for elem in criteria['forbidden_elements'])]
        
        if 'ring_sizes' in criteria:
            candidates = [t for t in candidates 
                         if self._has_rings_of_sizes(t.structure, criteria['ring_sizes'])]
        
        if 'tags' in criteria:
            candidates = [t for t in candidates 
                         if any(tag in t.metadata.tags for tag in criteria['tags'])]
        
        return candidates
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query."""
        suggestions = set()
        query_lower = partial_query.lower()
        
        for template in self.library.get_all_templates():
            # Check template names
            if query_lower in template.metadata.name.lower():
                suggestions.add(template.metadata.name)
            
            # Check keywords
            for keyword in template.metadata.keywords:
                if query_lower in keyword:
                    suggestions.add(keyword)
            
            # Check tags
            for tag in template.metadata.tags:
                if query_lower in tag:
                    suggestions.add(tag)
        
        return sorted(list(suggestions))[:10]  # Return top 10 suggestions
    
    def add_to_search_history(self, query: str, results_count: int) -> None:
        """Add a search to the search history."""
        self.search_history.append({
            'query': query,
            'results_count': results_count,
            'timestamp': None  # Would use datetime in real implementation
        })
        
        # Keep only last 50 searches
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]
    
    def get_popular_searches(self) -> List[str]:
        """Get most popular search queries."""
        query_counts = {}
        for search in self.search_history:
            query = search['query']
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Sort by frequency
        popular = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [query for query, count in popular[:10]]
    
    # Helper methods for advanced search functionality
    
    def _contains_substructure(self, template_structure: Molecule, query_structure: Molecule) -> bool:
        """Check if template contains the query substructure."""
        # Simplified substructure matching - in real implementation would use
        # more sophisticated graph matching algorithms
        
        if len(query_structure.atoms) > len(template_structure.atoms):
            return False
        
        # Check if all elements in query exist in template
        query_elements = self._get_element_set(query_structure)
        template_elements = self._get_element_set(template_structure)
        
        return query_elements.issubset(template_elements)
    
    def _calculate_similarity(self, template1: Template, template2: Template) -> float:
        """Calculate similarity between two templates."""
        # Simple similarity based on common elements and structure size
        elements1 = self._get_element_set(template1.structure)
        elements2 = self._get_element_set(template2.structure)
        
        if not elements1 and not elements2:
            return 1.0
        
        common_elements = elements1.intersection(elements2)
        all_elements = elements1.union(elements2)
        
        element_similarity = len(common_elements) / len(all_elements) if all_elements else 0
        
        # Factor in size similarity
        size1 = len(template1.structure.atoms)
        size2 = len(template2.structure.atoms)
        size_similarity = 1.0 - abs(size1 - size2) / max(size1, size2, 1)
        
        # Combine similarities
        return (element_similarity + size_similarity) / 2.0
    
    def _identify_functional_groups(self, structure: Molecule) -> List[str]:
        """Identify functional groups in a molecular structure."""
        functional_groups = []
        
        for atom in structure.atoms:
            # Simple functional group identification
            if atom.element.symbol == "O":
                # Check for alcohol, aldehyde, ketone, etc.
                connected_atoms = atom.get_connected_atoms()
                
                if len(connected_atoms) == 1:
                    # Might be carbonyl oxygen
                    connected_atom = connected_atoms[0]
                    if connected_atom.element.symbol == "C":
                        # Check if it's aldehyde or ketone
                        carbon_connections = connected_atom.get_connected_atoms()
                        if len(carbon_connections) == 2:  # Aldehyde
                            functional_groups.append("aldehyde")
                        elif len(carbon_connections) == 3:  # Ketone
                            functional_groups.append("ketone")
                
                elif len(connected_atoms) == 2:
                    # Might be alcohol or ether
                    h_count = sum(1 for a in connected_atoms if a.element.symbol == "H")
                    if h_count == 1:
                        functional_groups.append("alcohol")
                    elif h_count == 0:
                        functional_groups.append("ether")
            
            elif atom.element.symbol == "N":
                # Check for amine
                connected_atoms = atom.get_connected_atoms()
                if len(connected_atoms) <= 3:
                    functional_groups.append("amine")
        
        return list(set(functional_groups))  # Remove duplicates
    
    def _find_rings(self, structure: Molecule) -> List[List[Atom]]:
        """Find ring systems in a molecular structure."""
        # Simplified ring detection - would use more sophisticated algorithms in practice
        rings = []
        visited = set()
        
        def dfs_find_rings(atom, path, start_atom):
            if len(path) > 8:  # Avoid very large rings
                return
            
            for connected_atom in atom.get_connected_atoms():
                if connected_atom == start_atom and len(path) >= 3:
                    # Found a ring
                    rings.append(path[:])
                    return
                
                if connected_atom not in path:
                    path.append(connected_atom)
                    dfs_find_rings(connected_atom, path, start_atom)
                    path.pop()
        
        for atom in structure.atoms:
            if atom not in visited:
                dfs_find_rings(atom, [atom], atom)
                visited.add(atom)
        
        return rings
    
    def _is_aromatic_ring(self, ring: List[Atom]) -> bool:
        """Check if a ring is aromatic."""
        # Simple check: if any bond in the ring is aromatic
        for i in range(len(ring)):
            atom1 = ring[i]
            atom2 = ring[(i + 1) % len(ring)]
            
            for bond in atom1.bonds:
                if bond.contains_atom(atom2) and bond.order == BondOrder.AROMATIC:
                    return True
        
        return False
    
    def _get_element_set(self, structure: Molecule) -> Set[str]:
        """Get set of element symbols in a structure."""
        return {atom.element.symbol for atom in structure.atoms}
    
    def _has_rings_of_sizes(self, structure: Molecule, sizes: List[int]) -> bool:
        """Check if structure has rings of specified sizes."""
        rings = self._find_rings(structure)
        ring_sizes = {len(ring) for ring in rings}
        return any(size in ring_sizes for size in sizes)