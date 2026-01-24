"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
from hypothesis import settings, Verbosity
from chemical_reaction_drawer.core.models import Molecule, Atom, Bond, Point2D, BondOrder
from chemical_reaction_drawer.core.elements import get_element_by_symbol
from chemical_reaction_drawer.core.chemistry import ChemicalValidator


# Configure hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.load_profile("default")


@pytest.fixture
def empty_molecule():
    """Create an empty molecule for testing."""
    return Molecule()


@pytest.fixture
def simple_molecule():
    """Create a simple molecule (methane) for testing."""
    molecule = Molecule(name="Methane")
    carbon = molecule.add_atom("C", Point2D(0.0, 0.0))
    return molecule


@pytest.fixture
def ethane_molecule():
    """Create ethane molecule for testing."""
    molecule = Molecule(name="Ethane")
    c1 = molecule.add_atom("C", Point2D(0.0, 0.0))
    c2 = molecule.add_atom("C", Point2D(1.5, 0.0))
    molecule.add_bond(c1, c2, BondOrder.SINGLE)
    return molecule


@pytest.fixture
def benzene_molecule():
    """Create benzene molecule for testing."""
    molecule = Molecule(name="Benzene")
    
    # Create carbon atoms in a hexagonal arrangement
    import math
    atoms = []
    for i in range(6):
        angle = i * math.pi / 3
        x = math.cos(angle) * 1.4  # Typical C-C bond length
        y = math.sin(angle) * 1.4
        atom = molecule.add_atom("C", Point2D(x, y))
        atoms.append(atom)
    
    # Create bonds (alternating single/double for aromatic representation)
    for i in range(6):
        next_i = (i + 1) % 6
        bond_order = BondOrder.DOUBLE if i % 2 == 0 else BondOrder.SINGLE
        molecule.add_bond(atoms[i], atoms[next_i], bond_order)
    
    return molecule


@pytest.fixture
def chemical_validator():
    """Create a chemical validator instance for testing."""
    return ChemicalValidator()


@pytest.fixture
def sample_elements():
    """Provide common elements for testing."""
    return {
        "H": get_element_by_symbol("H"),
        "C": get_element_by_symbol("C"),
        "N": get_element_by_symbol("N"),
        "O": get_element_by_symbol("O"),
        "F": get_element_by_symbol("F"),
        "Cl": get_element_by_symbol("Cl"),
    }