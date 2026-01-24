"""
Core chemical structure engine for the Chemical Reaction Drawer.

This module contains the fundamental data models and chemical intelligence
systems that form the foundation of the application.
"""

from .models import Atom, Bond, Molecule, ChemicalElement, Point2D, Point3D, BondOrder, BondStereo, BondStyle
from .chemistry import ChemicalValidator, MolecularProperties
from .elements import PERIODIC_TABLE, get_element_by_symbol, get_element_by_number
from .atom_manager import AtomManager, AtomPlacementResult, AtomDeletionResult, ElementChangeResult
from .bond_manager import BondManager, BondCreationResult, BondDeletionResult, BondModificationResult
from .reaction import (
    Reaction, ReactionArrow, ReactionComponent, ReactionManager,
    ReactionSequence, SideProduct, ReactionBalancer,
    ArrowType, ArrowStyle, ReactionConditions, TextAnnotation,
    ReactionOperationResult
)
from .styling import (
    Color, Font, Style, ColorPalette, Theme, FontManager, StyleManager,
    FontWeight, FontStyle, LineStyle, create_dark_theme, create_high_contrast_theme,
    create_publication_theme, create_colorful_theme, create_monochrome_theme,
    create_presentation_theme
)
from .templates import (
    Template, TemplateMetadata, TemplateLibrary, TemplateCategory
)
from .template_placement import (
    TemplatePlacement, PlacementResult, AdvancedTemplateSearch
)

__all__ = [
    "Atom",
    "Bond",
    "Molecule", 
    "ChemicalElement",
    "Point2D",
    "Point3D",
    "BondOrder",
    "BondStereo",
    "BondStyle",
    "ChemicalValidator",
    "MolecularProperties",
    "AtomManager",
    "AtomPlacementResult",
    "AtomDeletionResult",
    "ElementChangeResult",
    "BondManager",
    "BondCreationResult",
    "BondDeletionResult",
    "BondModificationResult",
    "PERIODIC_TABLE",
    "get_element_by_symbol",
    "get_element_by_number",
    # Reaction system
    "Reaction",
    "ReactionArrow", 
    "ReactionComponent",
    "ReactionManager",
    "ReactionSequence",
    "SideProduct",
    "ReactionBalancer",
    "ArrowType",
    "ArrowStyle", 
    "ReactionConditions",
    "TextAnnotation",
    "ReactionOperationResult",
    # Styling system
    "Color",
    "Font",
    "Style",
    "ColorPalette",
    "Theme",
    "FontManager",
    "StyleManager",
    "FontWeight",
    "FontStyle",
    "LineStyle",
    "create_dark_theme",
    "create_high_contrast_theme",
    "create_publication_theme",
    "create_colorful_theme",
    "create_monochrome_theme",
    "create_presentation_theme",
    # Template system
    "Template",
    "TemplateMetadata",
    "TemplateLibrary",
    "TemplateCategory",
    "TemplatePlacement",
    "PlacementResult",
    "AdvancedTemplateSearch"
]