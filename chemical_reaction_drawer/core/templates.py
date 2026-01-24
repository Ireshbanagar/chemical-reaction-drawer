"""
Template library system for chemical reaction drawer.

This module provides template data structures, storage, and management
for common chemical structures and functional groups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import json
import os
import hashlib
from pathlib import Path

from .models import Molecule, Atom, Bond, Point2D, BondOrder
from .elements import get_element_by_symbol


class TemplateCategory(Enum):
    """Categories for organizing templates."""
    RINGS = "rings"
    FUNCTIONAL_GROUPS = "functional_groups"
    AMINO_ACIDS = "amino_acids"
    NUCLEOTIDES = "nucleotides"
    COMMON_MOLECULES = "common_molecules"
    CUSTOM = "custom"
    FAVORITES = "favorites"


@dataclass
class TemplateMetadata:
    """Metadata for a chemical template."""
    name: str
    description: str = ""
    category: TemplateCategory = TemplateCategory.CUSTOM
    keywords: List[str] = field(default_factory=list)
    molecular_formula: str = ""
    molecular_weight: float = 0.0
    created_date: str = ""
    author: str = ""
    tags: Set[str] = field(default_factory=set)
    
    def add_keyword(self, keyword: str) -> None:
        """Add a keyword for searching."""
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword.lower())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag for categorization."""
        if tag:
            self.tags.add(tag.lower())
    
    def matches_search(self, query: str) -> bool:
        """Check if template matches search query."""
        query_lower = query.lower()
        
        # Search in name and description
        if query_lower in self.name.lower() or query_lower in self.description.lower():
            return True
        
        # Search in keywords
        if any(query_lower in keyword for keyword in self.keywords):
            return True
        
        # Search in tags
        if any(query_lower in tag for tag in self.tags):
            return True
        
        # Search in molecular formula
        if query_lower in self.molecular_formula.lower():
            return True
        
        return False


@dataclass
class Template:
    """A chemical structure template."""
    metadata: TemplateMetadata
    structure: Molecule
    thumbnail_data: Optional[bytes] = None
    
    def __post_init__(self):
        """Initialize template after creation."""
        if not self.metadata.molecular_formula:
            self.metadata.molecular_formula = self.structure.get_molecular_formula()
        if not self.metadata.molecular_weight:
            self.metadata.molecular_weight = self.structure.get_molecular_weight()
    
    @property
    def id(self) -> str:
        """Generate unique ID for template based on structure."""
        # Create hash from structure data
        structure_data = f"{self.metadata.name}_{len(self.structure.atoms)}_{len(self.structure.bonds)}"
        return hashlib.md5(structure_data.encode()).hexdigest()[:12]
    
    def copy(self) -> 'Template':
        """Create a copy of this template."""
        # Deep copy the structure
        new_structure = Molecule()
        atom_mapping = {}
        
        # Copy atoms
        for atom in self.structure.atoms:
            new_atom = new_structure.add_atom(
                element_symbol=atom.element.symbol,
                position=Point2D(atom.position.x, atom.position.y),
                charge=atom.charge,
                position_3d=atom.position_3d
            )
            atom_mapping[atom] = new_atom
        
        # Copy bonds
        for bond in self.structure.bonds:
            new_atom1 = atom_mapping[bond.atom1]
            new_atom2 = atom_mapping[bond.atom2]
            new_structure.add_bond(
                atom1=new_atom1,
                atom2=new_atom2,
                order=bond.order,
                stereo=bond.stereo,
                style=bond.style
            )
        
        # Copy metadata
        new_metadata = TemplateMetadata(
            name=self.metadata.name,
            description=self.metadata.description,
            category=self.metadata.category,
            keywords=self.metadata.keywords.copy(),
            molecular_formula=self.metadata.molecular_formula,
            molecular_weight=self.metadata.molecular_weight,
            created_date=self.metadata.created_date,
            author=self.metadata.author,
            tags=self.metadata.tags.copy()
        )
        
        return Template(new_metadata, new_structure, self.thumbnail_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "category": self.metadata.category.value,
                "keywords": self.metadata.keywords,
                "molecular_formula": self.metadata.molecular_formula,
                "molecular_weight": self.metadata.molecular_weight,
                "created_date": self.metadata.created_date,
                "author": self.metadata.author,
                "tags": list(self.metadata.tags)
            },
            "structure": self.structure.to_dict(),
            "thumbnail": self.thumbnail_data.hex() if self.thumbnail_data else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create template from dictionary."""
        metadata_data = data["metadata"]
        metadata = TemplateMetadata(
            name=metadata_data["name"],
            description=metadata_data.get("description", ""),
            category=TemplateCategory(metadata_data.get("category", "custom")),
            keywords=metadata_data.get("keywords", []),
            molecular_formula=metadata_data.get("molecular_formula", ""),
            molecular_weight=metadata_data.get("molecular_weight", 0.0),
            created_date=metadata_data.get("created_date", ""),
            author=metadata_data.get("author", ""),
            tags=set(metadata_data.get("tags", []))
        )
        
        structure = Molecule.from_dict(data["structure"])
        
        thumbnail_data = None
        if data.get("thumbnail"):
            thumbnail_data = bytes.fromhex(data["thumbnail"])
        
        return cls(metadata, structure, thumbnail_data)


class TemplateLibrary:
    """Library for managing chemical structure templates."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.templates: Dict[str, Template] = {}
        self.categories: Dict[TemplateCategory, List[str]] = {
            category: [] for category in TemplateCategory
        }
        self.storage_path = storage_path or "templates"
        self.search_index: Dict[str, Set[str]] = {}  # keyword -> template_ids
        
        # Initialize with built-in templates
        self._create_builtin_templates()
    
    def _create_builtin_templates(self) -> None:
        """Create built-in chemical templates."""
        # Ring systems
        self._create_benzene_template()
        self._create_cyclohexane_template()
        self._create_cyclopentane_template()
        
        # Functional groups
        self._create_alcohol_template()
        self._create_aldehyde_template()
        self._create_ketone_template()
        
        # Common molecules
        self._create_water_template()
        self._create_methane_template()
    
    def _create_benzene_template(self) -> None:
        """Create benzene ring template."""
        molecule = Molecule()
        
        # Create 6 carbon atoms in hexagonal arrangement
        import math
        radius = 1.4  # Typical C-C bond length
        atoms = []
        
        for i in range(6):
            angle = i * math.pi / 3
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            carbon = molecule.add_atom("C", Point2D(x, y))
            atoms.append(carbon)
        
        # Create bonds (aromatic)
        for i in range(6):
            next_i = (i + 1) % 6
            bond = molecule.add_bond(atoms[i], atoms[next_i], BondOrder.AROMATIC)
        
        metadata = TemplateMetadata(
            name="Benzene",
            description="Benzene ring - aromatic 6-membered carbon ring",
            category=TemplateCategory.RINGS,
            keywords=["benzene", "aromatic", "ring", "phenyl"],
            tags={"aromatic", "ring", "6-membered"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_cyclohexane_template(self) -> None:
        """Create cyclohexane ring template."""
        molecule = Molecule()
        
        # Create 6 carbon atoms in chair conformation
        import math
        atoms = []
        
        # Simplified chair conformation coordinates
        positions = [
            (1.4, 0.0), (0.7, 1.2), (-0.7, 1.2),
            (-1.4, 0.0), (-0.7, -1.2), (0.7, -1.2)
        ]
        
        for x, y in positions:
            carbon = molecule.add_atom("C", Point2D(x, y))
            atoms.append(carbon)
        
        # Create single bonds
        for i in range(6):
            next_i = (i + 1) % 6
            bond = molecule.add_bond(atoms[i], atoms[next_i], BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Cyclohexane",
            description="Cyclohexane ring - saturated 6-membered carbon ring",
            category=TemplateCategory.RINGS,
            keywords=["cyclohexane", "saturated", "ring", "chair"],
            tags={"saturated", "ring", "6-membered"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_cyclopentane_template(self) -> None:
        """Create cyclopentane ring template."""
        molecule = Molecule()
        
        # Create 5 carbon atoms in pentagonal arrangement
        import math
        radius = 1.4
        atoms = []
        
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2  # Start from top
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            carbon = molecule.add_atom("C", Point2D(x, y))
            atoms.append(carbon)
        
        # Create single bonds
        for i in range(5):
            next_i = (i + 1) % 5
            bond = molecule.add_bond(atoms[i], atoms[next_i], BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Cyclopentane",
            description="Cyclopentane ring - saturated 5-membered carbon ring",
            category=TemplateCategory.RINGS,
            keywords=["cyclopentane", "saturated", "ring"],
            tags={"saturated", "ring", "5-membered"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_alcohol_template(self) -> None:
        """Create alcohol functional group template."""
        molecule = Molecule()
        
        # Create -OH group
        carbon = molecule.add_atom("C", Point2D(0.0, 0.0))
        oxygen = molecule.add_atom("O", Point2D(1.4, 0.0))
        hydrogen = molecule.add_atom("H", Point2D(2.0, 0.8))
        
        # Create bonds
        co_bond = molecule.add_bond(carbon, oxygen, BondOrder.SINGLE)
        oh_bond = molecule.add_bond(oxygen, hydrogen, BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Alcohol",
            description="Alcohol functional group (-OH)",
            category=TemplateCategory.FUNCTIONAL_GROUPS,
            keywords=["alcohol", "hydroxyl", "oh", "functional group"],
            tags={"functional_group", "alcohol", "hydroxyl"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_aldehyde_template(self) -> None:
        """Create aldehyde functional group template."""
        molecule = Molecule()
        
        # Create -CHO group
        carbon1 = molecule.add_atom("C", Point2D(0.0, 0.0))
        carbon2 = molecule.add_atom("C", Point2D(1.4, 0.0))
        oxygen = molecule.add_atom("O", Point2D(2.1, 1.2))
        hydrogen = molecule.add_atom("H", Point2D(2.1, -1.2))
        
        # Create bonds
        cc_bond = molecule.add_bond(carbon1, carbon2, BondOrder.SINGLE)
        co_bond = molecule.add_bond(carbon2, oxygen, BondOrder.DOUBLE)
        ch_bond = molecule.add_bond(carbon2, hydrogen, BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Aldehyde",
            description="Aldehyde functional group (-CHO)",
            category=TemplateCategory.FUNCTIONAL_GROUPS,
            keywords=["aldehyde", "carbonyl", "cho", "functional group"],
            tags={"functional_group", "aldehyde", "carbonyl"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_ketone_template(self) -> None:
        """Create ketone functional group template."""
        molecule = Molecule()
        
        # Create -CO- group
        carbon1 = molecule.add_atom("C", Point2D(0.0, 0.0))
        carbon2 = molecule.add_atom("C", Point2D(1.4, 0.0))
        oxygen = molecule.add_atom("O", Point2D(1.4, 1.4))
        carbon3 = molecule.add_atom("C", Point2D(2.8, 0.0))
        
        # Create bonds
        c1c2_bond = molecule.add_bond(carbon1, carbon2, BondOrder.SINGLE)
        co_bond = molecule.add_bond(carbon2, oxygen, BondOrder.DOUBLE)
        c2c3_bond = molecule.add_bond(carbon2, carbon3, BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Ketone",
            description="Ketone functional group (-CO-)",
            category=TemplateCategory.FUNCTIONAL_GROUPS,
            keywords=["ketone", "carbonyl", "co", "functional group"],
            tags={"functional_group", "ketone", "carbonyl"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_water_template(self) -> None:
        """Create water molecule template."""
        molecule = Molecule()
        
        # Create H2O
        oxygen = molecule.add_atom("O", Point2D(0.0, 0.0))
        hydrogen1 = molecule.add_atom("H", Point2D(-0.8, 0.6))
        hydrogen2 = molecule.add_atom("H", Point2D(0.8, 0.6))
        
        # Create bonds
        oh1_bond = molecule.add_bond(oxygen, hydrogen1, BondOrder.SINGLE)
        oh2_bond = molecule.add_bond(oxygen, hydrogen2, BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Water",
            description="Water molecule (H2O)",
            category=TemplateCategory.COMMON_MOLECULES,
            keywords=["water", "h2o", "solvent"],
            tags={"common", "solvent", "inorganic"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def _create_methane_template(self) -> None:
        """Create methane molecule template."""
        molecule = Molecule()
        
        # Create CH4
        carbon = molecule.add_atom("C", Point2D(0.0, 0.0))
        hydrogen1 = molecule.add_atom("H", Point2D(1.0, 0.0))
        hydrogen2 = molecule.add_atom("H", Point2D(-1.0, 0.0))
        hydrogen3 = molecule.add_atom("H", Point2D(0.0, 1.0))
        hydrogen4 = molecule.add_atom("H", Point2D(0.0, -1.0))
        
        # Create bonds
        ch1_bond = molecule.add_bond(carbon, hydrogen1, BondOrder.SINGLE)
        ch2_bond = molecule.add_bond(carbon, hydrogen2, BondOrder.SINGLE)
        ch3_bond = molecule.add_bond(carbon, hydrogen3, BondOrder.SINGLE)
        ch4_bond = molecule.add_bond(carbon, hydrogen4, BondOrder.SINGLE)
        
        metadata = TemplateMetadata(
            name="Methane",
            description="Methane molecule (CH4)",
            category=TemplateCategory.COMMON_MOLECULES,
            keywords=["methane", "ch4", "alkane"],
            tags={"common", "alkane", "hydrocarbon"}
        )
        
        template = Template(metadata, molecule)
        self.add_template(template)
    
    def add_template(self, template: Template) -> None:
        """Add a template to the library."""
        template_id = template.id
        self.templates[template_id] = template
        
        # Add to category
        category = template.metadata.category
        if template_id not in self.categories[category]:
            self.categories[category].append(template_id)
        
        # Update search index
        self._update_search_index(template)
    
    def remove_template(self, template_id: str) -> bool:
        """Remove a template from the library."""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        
        # Remove from category
        category = template.metadata.category
        if template_id in self.categories[category]:
            self.categories[category].remove(template_id)
        
        # Remove from search index
        self._remove_from_search_index(template)
        
        # Remove template
        del self.templates[template_id]
        return True
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[Template]:
        """Get all templates in a category."""
        template_ids = self.categories.get(category, [])
        return [self.templates[tid] for tid in template_ids if tid in self.templates]
    
    def get_all_templates(self) -> List[Template]:
        """Get all templates."""
        return list(self.templates.values())
    
    def search_templates(self, query: str) -> List[Template]:
        """Search templates by query."""
        if not query:
            return self.get_all_templates()
        
        matching_templates = []
        query_lower = query.lower()
        
        # Search using metadata
        for template in self.templates.values():
            if template.metadata.matches_search(query):
                matching_templates.append(template)
        
        return matching_templates
    
    def search_by_molecular_formula(self, formula: str) -> List[Template]:
        """Search templates by molecular formula."""
        matching_templates = []
        formula_lower = formula.lower()
        
        for template in self.templates.values():
            if formula_lower in template.metadata.molecular_formula.lower():
                matching_templates.append(template)
        
        return matching_templates
    
    def search_by_properties(self, 
                           min_weight: Optional[float] = None,
                           max_weight: Optional[float] = None,
                           categories: Optional[List[TemplateCategory]] = None,
                           tags: Optional[List[str]] = None) -> List[Template]:
        """Search templates by molecular properties."""
        matching_templates = []
        
        for template in self.templates.values():
            # Check molecular weight
            if min_weight is not None and template.metadata.molecular_weight < min_weight:
                continue
            if max_weight is not None and template.metadata.molecular_weight > max_weight:
                continue
            
            # Check categories
            if categories is not None and template.metadata.category not in categories:
                continue
            
            # Check tags
            if tags is not None:
                template_tags = {tag.lower() for tag in template.metadata.tags}
                search_tags = {tag.lower() for tag in tags}
                if not search_tags.intersection(template_tags):
                    continue
            
            matching_templates.append(template)
        
        return matching_templates
    
    def get_favorites(self) -> List[Template]:
        """Get favorite templates."""
        return self.get_templates_by_category(TemplateCategory.FAVORITES)
    
    def add_to_favorites(self, template_id: str) -> bool:
        """Add a template to favorites."""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        
        # Create a copy in favorites category
        favorite_template = template.copy()
        favorite_template.metadata.category = TemplateCategory.FAVORITES
        
        self.add_template(favorite_template)
        return True
    
    def remove_from_favorites(self, template_id: str) -> bool:
        """Remove a template from favorites."""
        template = self.get_template(template_id)
        if not template or template.metadata.category != TemplateCategory.FAVORITES:
            return False
        
        return self.remove_template(template_id)
    
    def create_custom_template(self, name: str, structure: Molecule, 
                             description: str = "", keywords: List[str] = None,
                             tags: Set[str] = None) -> Template:
        """Create a custom template from a molecule structure."""
        metadata = TemplateMetadata(
            name=name,
            description=description,
            category=TemplateCategory.CUSTOM,
            keywords=keywords or [],
            tags=tags or set()
        )
        
        template = Template(metadata, structure)
        self.add_template(template)
        return template
    
    def generate_thumbnail(self, template: Template, size: Tuple[int, int] = (64, 64)) -> bytes:
        """Generate a thumbnail image for a template."""
        # This is a placeholder implementation
        # In a real implementation, this would render the molecule structure
        # and return the image data as bytes
        
        # For now, return a simple placeholder
        width, height = size
        # Create a simple bitmap representation
        thumbnail_data = bytearray(width * height * 3)  # RGB
        
        # Fill with a simple pattern based on template properties
        color_value = hash(template.metadata.name) % 256
        for i in range(0, len(thumbnail_data), 3):
            thumbnail_data[i] = color_value  # R
            thumbnail_data[i + 1] = (color_value + 50) % 256  # G
            thumbnail_data[i + 2] = (color_value + 100) % 256  # B
        
        return bytes(thumbnail_data)
    
    def update_thumbnail(self, template_id: str, size: Tuple[int, int] = (64, 64)) -> bool:
        """Update the thumbnail for a template."""
        template = self.get_template(template_id)
        if not template:
            return False
        
        template.thumbnail_data = self.generate_thumbnail(template, size)
        return True
    
    def _update_search_index(self, template: Template) -> None:
        """Update the search index with template keywords."""
        template_id = template.id
        
        # Index all searchable terms
        terms = []
        terms.extend(template.metadata.keywords)
        terms.extend(template.metadata.tags)
        terms.append(template.metadata.name.lower())
        terms.append(template.metadata.description.lower())
        terms.append(template.metadata.molecular_formula.lower())
        
        for term in terms:
            if term not in self.search_index:
                self.search_index[term] = set()
            self.search_index[term].add(template_id)
    
    def _remove_from_search_index(self, template: Template) -> None:
        """Remove template from search index."""
        template_id = template.id
        
        # Remove from all index entries
        for term_set in self.search_index.values():
            term_set.discard(template_id)
        
        # Clean up empty entries
        empty_terms = [term for term, ids in self.search_index.items() if not ids]
        for term in empty_terms:
            del self.search_index[term]
    
    def save_library(self, file_path: str) -> bool:
        """Save the entire library to a file."""
        try:
            library_data = {
                "templates": {tid: template.to_dict() for tid, template in self.templates.items()},
                "categories": {cat.value: ids for cat, ids in self.categories.items()},
                "version": "1.0"
            }
            
            with open(file_path, 'w') as f:
                json.dump(library_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_library(self, file_path: str) -> bool:
        """Load a library from a file."""
        try:
            with open(file_path, 'r') as f:
                library_data = json.load(f)
            
            # Clear current library
            self.templates.clear()
            for category in self.categories:
                self.categories[category].clear()
            self.search_index.clear()
            
            # Load templates
            for template_data in library_data["templates"].values():
                template = Template.from_dict(template_data)
                self.add_template(template)
            
            return True
        except Exception:
            return False
    
    def export_templates(self, template_ids: List[str], file_path: str) -> bool:
        """Export selected templates to a file."""
        try:
            export_data = {
                "templates": [],
                "exported_count": 0,
                "version": "1.0"
            }
            
            for template_id in template_ids:
                template = self.get_template(template_id)
                if template:
                    export_data["templates"].append(template.to_dict())
                    export_data["exported_count"] += 1
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def import_templates(self, file_path: str) -> int:
        """Import templates from a file. Returns number of imported templates."""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for template_data in import_data.get("templates", []):
                template = Template.from_dict(template_data)
                self.add_template(template)
                imported_count += 1
            
            return imported_count
        except Exception:
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = {
            "total_templates": len(self.templates),
            "categories": {},
            "average_molecular_weight": 0.0,
            "most_common_tags": []
        }
        
        # Category counts
        for category, template_ids in self.categories.items():
            stats["categories"][category.value] = len(template_ids)
        
        # Average molecular weight
        if self.templates:
            total_weight = sum(t.metadata.molecular_weight for t in self.templates.values())
            stats["average_molecular_weight"] = total_weight / len(self.templates)
        
        # Most common tags
        tag_counts = {}
        for template in self.templates.values():
            for tag in template.metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        stats["most_common_tags"] = sorted(tag_counts.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]
        
        return stats