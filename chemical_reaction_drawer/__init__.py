"""
Chemical Reaction Drawer - A desktop application for creating, editing, and visualizing chemical structures and reactions.

This package provides comprehensive chemical structure drawing and 3D visualization capabilities
with advanced drawing tools, customizable styling options, and support for multiple chemical file formats.
"""

__version__ = "0.1.0"
__author__ = "Chemical Reaction Drawer Team"
__email__ = "contact@chemreactiondrawer.com"

# Core modules
from .core.models import Atom, Bond, Molecule, ChemicalElement
from .core.chemistry import ChemicalValidator, MolecularProperties
from .core.atom_manager import AtomManager, AtomPlacementResult, AtomDeletionResult, ElementChangeResult

__all__ = [
    "Atom",
    "Bond", 
    "Molecule",
    "ChemicalElement",
    "ChemicalValidator",
    "MolecularProperties",
    "AtomManager",
    "AtomPlacementResult",
    "AtomDeletionResult",
    "ElementChangeResult"
]