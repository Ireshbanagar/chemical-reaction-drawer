"""
Chemical element definitions and properties.

This module provides comprehensive data about chemical elements including
atomic numbers, symbols, names, atomic weights, and chemical properties
needed for molecular structure validation and property calculations.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum


class ElementGroup(Enum):
    """Chemical element groups for classification."""
    ALKALI_METAL = "alkali_metal"
    ALKALINE_EARTH = "alkaline_earth"
    TRANSITION_METAL = "transition_metal"
    POST_TRANSITION_METAL = "post_transition_metal"
    METALLOID = "metalloid"
    NONMETAL = "nonmetal"
    HALOGEN = "halogen"
    NOBLE_GAS = "noble_gas"
    LANTHANIDE = "lanthanide"
    ACTINIDE = "actinide"


@dataclass(frozen=True)
class ChemicalElement:
    """
    Represents a chemical element with its properties.
    
    Attributes:
        atomic_number: The number of protons in the nucleus
        symbol: Chemical symbol (e.g., 'H', 'C', 'N')
        name: Full element name (e.g., 'Hydrogen', 'Carbon')
        atomic_weight: Average atomic mass in atomic mass units
        valence_electrons: Number of valence electrons
        common_valences: List of common oxidation states/valences
        group: Element group classification
        period: Period number in periodic table
        electronegativity: Pauling electronegativity value
        atomic_radius: Atomic radius in picometers
        color: Default color for visualization (RGB hex)
    """
    atomic_number: int
    symbol: str
    name: str
    atomic_weight: float
    valence_electrons: int
    common_valences: List[int]
    group: ElementGroup
    period: int
    electronegativity: float
    atomic_radius: int  # in picometers
    color: str  # RGB hex color for visualization
    
    def __post_init__(self):
        """Validate element data after initialization."""
        if self.atomic_number <= 0:
            raise ValueError(f"Atomic number must be positive, got {self.atomic_number}")
        if not self.symbol or not self.symbol.isalpha():
            raise ValueError(f"Invalid element symbol: {self.symbol}")
        if self.atomic_weight <= 0:
            raise ValueError(f"Atomic weight must be positive, got {self.atomic_weight}")


# Comprehensive periodic table data
PERIODIC_TABLE: Dict[str, ChemicalElement] = {
    "H": ChemicalElement(
        atomic_number=1, symbol="H", name="Hydrogen", atomic_weight=1.008,
        valence_electrons=1, common_valences=[1, -1], group=ElementGroup.NONMETAL,
        period=1, electronegativity=2.20, atomic_radius=53, color="#FFFFFF"
    ),
    "He": ChemicalElement(
        atomic_number=2, symbol="He", name="Helium", atomic_weight=4.003,
        valence_electrons=2, common_valences=[0], group=ElementGroup.NOBLE_GAS,
        period=1, electronegativity=0.0, atomic_radius=31, color="#D9FFFF"
    ),
    "Li": ChemicalElement(
        atomic_number=3, symbol="Li", name="Lithium", atomic_weight=6.941,
        valence_electrons=1, common_valences=[1], group=ElementGroup.ALKALI_METAL,
        period=2, electronegativity=0.98, atomic_radius=167, color="#CC80FF"
    ),
    "Be": ChemicalElement(
        atomic_number=4, symbol="Be", name="Beryllium", atomic_weight=9.012,
        valence_electrons=2, common_valences=[2], group=ElementGroup.ALKALINE_EARTH,
        period=2, electronegativity=1.57, atomic_radius=112, color="#C2FF00"
    ),
    "B": ChemicalElement(
        atomic_number=5, symbol="B", name="Boron", atomic_weight=10.811,
        valence_electrons=3, common_valences=[3], group=ElementGroup.METALLOID,
        period=2, electronegativity=2.04, atomic_radius=87, color="#FFB5B5"
    ),
    "C": ChemicalElement(
        atomic_number=6, symbol="C", name="Carbon", atomic_weight=12.011,
        valence_electrons=4, common_valences=[4, 2, -4], group=ElementGroup.NONMETAL,
        period=2, electronegativity=2.55, atomic_radius=67, color="#909090"
    ),
    "N": ChemicalElement(
        atomic_number=7, symbol="N", name="Nitrogen", atomic_weight=14.007,
        valence_electrons=5, common_valences=[3, 5, -3], group=ElementGroup.NONMETAL,
        period=2, electronegativity=3.04, atomic_radius=56, color="#3050F8"
    ),
    "O": ChemicalElement(
        atomic_number=8, symbol="O", name="Oxygen", atomic_weight=15.999,
        valence_electrons=6, common_valences=[2, -2], group=ElementGroup.NONMETAL,
        period=2, electronegativity=3.44, atomic_radius=48, color="#FF0D0D"
    ),
    "F": ChemicalElement(
        atomic_number=9, symbol="F", name="Fluorine", atomic_weight=18.998,
        valence_electrons=7, common_valences=[-1], group=ElementGroup.HALOGEN,
        period=2, electronegativity=3.98, atomic_radius=42, color="#90E050"
    ),
    "Ne": ChemicalElement(
        atomic_number=10, symbol="Ne", name="Neon", atomic_weight=20.180,
        valence_electrons=8, common_valences=[0], group=ElementGroup.NOBLE_GAS,
        period=2, electronegativity=0.0, atomic_radius=38, color="#B3E3F5"
    ),
    "Na": ChemicalElement(
        atomic_number=11, symbol="Na", name="Sodium", atomic_weight=22.990,
        valence_electrons=1, common_valences=[1], group=ElementGroup.ALKALI_METAL,
        period=3, electronegativity=0.93, atomic_radius=190, color="#AB5CF2"
    ),
    "Mg": ChemicalElement(
        atomic_number=12, symbol="Mg", name="Magnesium", atomic_weight=24.305,
        valence_electrons=2, common_valences=[2], group=ElementGroup.ALKALINE_EARTH,
        period=3, electronegativity=1.31, atomic_radius=145, color="#8AFF00"
    ),
    "Al": ChemicalElement(
        atomic_number=13, symbol="Al", name="Aluminum", atomic_weight=26.982,
        valence_electrons=3, common_valences=[3], group=ElementGroup.POST_TRANSITION_METAL,
        period=3, electronegativity=1.61, atomic_radius=118, color="#BFA6A6"
    ),
    "Si": ChemicalElement(
        atomic_number=14, symbol="Si", name="Silicon", atomic_weight=28.086,
        valence_electrons=4, common_valences=[4, -4], group=ElementGroup.METALLOID,
        period=3, electronegativity=1.90, atomic_radius=111, color="#F0C8A0"
    ),
    "P": ChemicalElement(
        atomic_number=15, symbol="P", name="Phosphorus", atomic_weight=30.974,
        valence_electrons=5, common_valences=[3, 5, -3], group=ElementGroup.NONMETAL,
        period=3, electronegativity=2.19, atomic_radius=98, color="#FF8000"
    ),
    "S": ChemicalElement(
        atomic_number=16, symbol="S", name="Sulfur", atomic_weight=32.065,
        valence_electrons=6, common_valences=[2, 4, 6, -2], group=ElementGroup.NONMETAL,
        period=3, electronegativity=2.58, atomic_radius=88, color="#FFFF30"
    ),
    "Cl": ChemicalElement(
        atomic_number=17, symbol="Cl", name="Chlorine", atomic_weight=35.453,
        valence_electrons=7, common_valences=[-1, 1, 3, 5, 7], group=ElementGroup.HALOGEN,
        period=3, electronegativity=3.16, atomic_radius=79, color="#1FF01F"
    ),
    "Ar": ChemicalElement(
        atomic_number=18, symbol="Ar", name="Argon", atomic_weight=39.948,
        valence_electrons=8, common_valences=[0], group=ElementGroup.NOBLE_GAS,
        period=3, electronegativity=0.0, atomic_radius=71, color="#80D1E3"
    ),
    "K": ChemicalElement(
        atomic_number=19, symbol="K", name="Potassium", atomic_weight=39.098,
        valence_electrons=1, common_valences=[1], group=ElementGroup.ALKALI_METAL,
        period=4, electronegativity=0.82, atomic_radius=243, color="#8F40D4"
    ),
    "Ca": ChemicalElement(
        atomic_number=20, symbol="Ca", name="Calcium", atomic_weight=40.078,
        valence_electrons=2, common_valences=[2], group=ElementGroup.ALKALINE_EARTH,
        period=4, electronegativity=1.00, atomic_radius=194, color="#3DFF00"
    ),
    "Br": ChemicalElement(
        atomic_number=35, symbol="Br", name="Bromine", atomic_weight=79.904,
        valence_electrons=7, common_valences=[-1, 1, 3, 5, 7], group=ElementGroup.HALOGEN,
        period=4, electronegativity=2.96, atomic_radius=94, color="#A62929"
    ),
    "I": ChemicalElement(
        atomic_number=53, symbol="I", name="Iodine", atomic_weight=126.904,
        valence_electrons=7, common_valences=[-1, 1, 3, 5, 7], group=ElementGroup.HALOGEN,
        period=5, electronegativity=2.66, atomic_radius=115, color="#940094"
    ),
}


def get_element_by_symbol(symbol: str) -> Optional[ChemicalElement]:
    """
    Get element by chemical symbol.
    
    Args:
        symbol: Chemical symbol (case-insensitive)
        
    Returns:
        ChemicalElement if found, None otherwise
    """
    return PERIODIC_TABLE.get(symbol.capitalize())


def get_element_by_number(atomic_number: int) -> Optional[ChemicalElement]:
    """
    Get element by atomic number.
    
    Args:
        atomic_number: Atomic number to search for
        
    Returns:
        ChemicalElement if found, None otherwise
    """
    for element in PERIODIC_TABLE.values():
        if element.atomic_number == atomic_number:
            return element
    return None


def get_elements_by_group(group: ElementGroup) -> List[ChemicalElement]:
    """
    Get all elements in a specific group.
    
    Args:
        group: ElementGroup to filter by
        
    Returns:
        List of elements in the specified group
    """
    return [element for element in PERIODIC_TABLE.values() if element.group == group]


def is_valid_element_symbol(symbol: str) -> bool:
    """
    Check if a symbol represents a valid chemical element.
    
    Args:
        symbol: Chemical symbol to validate
        
    Returns:
        True if valid element symbol, False otherwise
    """
    return symbol.capitalize() in PERIODIC_TABLE