# Chemical Reaction Drawer

A comprehensive Python-based chemical structure drawing and visualization application with advanced 3D capabilities, chemical intelligence, and extensive customization options.

## Features

### 🤖 AI-Powered Molecule Generation (NEW!)
- **Generate from Name**: Type molecule names, get instant structures
- **Amazon Bedrock Integration**: Powered by Claude 3.5 Sonnet
- **Fallback Mode**: Works offline with 17 common molecules
- **Smart Caching**: Fast repeated queries
- **One-Click Addition**: Add generated molecules directly to canvas
- **Keyboard Shortcut**: Ctrl+G for instant access

### Core Chemical Drawing
- **Atom Placement**: Click-to-place atoms with element selection
- **Bond Creation**: Multiple bond types (single, double, triple, wedge, dashed, wavy)
- **Stereochemistry**: Full support for 3D stereochemical representations
- **Chemical Validation**: Real-time valency checking and error detection

### 3D Molecular Visualization
- **Interactive 3D Viewer**: Mouse-controlled rotation and zoom
- **2D to 3D Conversion**: Automatic generation of 3D coordinates
- **Multiple Conformations**: Support for different molecular conformations
- **High-Quality Rendering**: OpenGL-based rendering with element-specific colors

### Chemical Intelligence
- **Automatic Hydrogen Management**: Smart hydrogen addition/removal
- **Aromaticity Detection**: Automatic detection and visualization of aromatic systems
- **Molecular Properties**: Calculation of molecular weight, formula, and basic properties
- **Structure Validation**: Chemical rule checking with helpful suggestions

### Reaction Drawing System
- **Reaction Arrows**: Multiple arrow types (reaction, equilibrium, resonance)
- **Reaction Conditions**: Text annotations for temperature, catalysts, etc.
- **Multi-step Reactions**: Support for complex reaction sequences
- **Side Products**: Branching arrows for byproducts and side reactions

### Advanced Styling
- **Customizable Themes**: 7 built-in themes (Default, Dark, High Contrast, etc.)
- **Color Palettes**: 6 predefined palettes plus custom palette creation
- **Font Management**: Flexible typography controls
- **Publication Ready**: High-quality output suitable for scientific publications

### Template Library
- **Extensive Library**: 100+ built-in templates across multiple categories
- **Smart Search**: Advanced search by structure, properties, and functional groups
- **Custom Templates**: Save and organize your own template structures
- **Auto-Connection**: Intelligent template placement with automatic bonding

### File I/O Support
- **Multiple Formats**: MOL, SDF, ChemDraw CDX format support
- **Image Export**: PNG, SVG, PDF export capabilities
- **3D Coordinate Preservation**: Full 3D information retention
- **Project Files**: Native format for complete project storage

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenGL support for 3D visualization

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- `pytest` - Testing framework
- `hypothesis` - Property-based testing
- `dataclasses` - Data structure support
- `typing` - Type hints support

### Optional (for AI features)
- `boto3` - Amazon Bedrock integration (optional, works without it)

## Quick Start

### AI-Powered Molecule Generation (NEW!)
```python
from chemical_reaction_drawer.ai import AIAssistant

# Initialize AI Assistant
assistant = AIAssistant()

# Generate molecule from name
molecule = assistant.generate_from_name("aspirin")
print(f"Formula: {molecule.get_molecular_formula()}")
print(f"Atoms: {len(molecule.atoms)}")
print(f"Bonds: {len(molecule.bonds)}")

# Works with common molecules even without AWS
molecule = assistant.generate_from_name("caffeine")
```

**GUI Usage:**
1. Press **Ctrl+G** to open AI Assistant
2. Type molecule name (e.g., "aspirin", "caffeine", "benzene")
3. Click **Generate**
4. Click **Add to Canvas**

See [AI_QUICK_START.md](AI_QUICK_START.md) for detailed guide.

### Basic Molecule Creation
```python
from chemical_reaction_drawer.core import Molecule, Point2D

# Create a simple molecule
molecule = Molecule()
carbon = molecule.add_atom("C", Point2D(0.0, 0.0))
hydrogen = molecule.add_atom("H", Point2D(1.0, 0.0))
bond = molecule.add_bond(carbon, hydrogen)

print(f"Molecular formula: {molecule.calculate_molecular_formula()}")
```

### 3D Visualization
```python
from chemical_reaction_drawer.core import Molecule3D, Renderer3D

# Convert to 3D and render
molecule_3d = Molecule3D.from_2d_molecule(molecule)
renderer = Renderer3D()
renderer.render_molecule(molecule_3d)
```

### Template Usage
```python
from chemical_reaction_drawer.core import TemplateLibrary, TemplatePlacement

# Use template library
library = TemplateLibrary()
benzene_template = library.get_template_by_name("Benzene")

# Place template
placement = TemplatePlacement()
result = placement.place_template_at_position(benzene_template, Point2D(5.0, 5.0))
```

### Chemical Validation
```python
from chemical_reaction_drawer.core import ChemicalValidator

validator = ChemicalValidator()
validation_result = validator.validate_molecule(molecule)

if not validation_result.is_valid:
    print("Validation errors:", validation_result.errors)
    print("Suggestions:", validation_result.suggestions)
```

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **AI System** (`ai/`): Amazon Bedrock integration and molecule generation
  - `bedrock_client.py`: AWS Bedrock API client
  - `molecule_generator.py`: SMILES parser and molecule generation
  - `ai_assistant.py`: High-level AI interface
- **Core Models** (`models.py`): Fundamental data structures (Atom, Bond, Molecule)
- **Chemical Engine** (`chemistry.py`): Validation and chemical intelligence
- **3D System** (`molecule_3d.py`, `renderer_3d.py`): 3D visualization and interaction
- **Reaction System** (`reaction.py`): Chemical reaction drawing and management
- **Template System** (`templates.py`, `template_placement.py`): Template library and placement
- **Styling System** (`styling.py`): Visual customization and themes

## Testing

The project uses comprehensive testing with both unit tests and property-based tests:

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Core functionality tests
pytest tests/test_models.py tests/test_chemistry.py

# 3D visualization tests
pytest tests/test_molecule_3d.py tests/test_renderer_3d.py

# Template system tests
pytest tests/test_templates.py tests/test_template_placement.py

# Property-based tests
pytest tests/test_properties.py
```

### Property-Based Testing
The project includes 24 comprehensive property-based tests that verify correctness across the entire input space:

- **Atom Placement Accuracy**: Verifies precise atom positioning
- **Bond Creation**: Tests all bond types and stereochemistry
- **Chemical Validation**: Ensures chemical rule compliance
- **3D Consistency**: Validates 2D/3D conversion accuracy
- **Template Functionality**: Tests template placement and search
- **And many more...**

## Development

### Project Structure
```
chemical_reaction_drawer/
├── ai/                      # AI integration (NEW!)
│   ├── bedrock_client.py   # AWS Bedrock client
│   ├── molecule_generator.py # SMILES parser
│   └── ai_assistant.py     # AI interface
├── core/                    # Core modules
│   ├── models.py           # Basic data structures
│   ├── chemistry.py        # Chemical intelligence
│   ├── molecule_3d.py      # 3D molecular representation
│   ├── renderer_3d.py      # 3D rendering engine
│   ├── reaction.py         # Reaction drawing system
│   ├── styling.py          # Visual styling system
│   ├── templates.py        # Template library
│   └── template_placement.py # Template placement logic
├── gui/                     # GUI components
│   ├── main_window.py      # Main application window
│   ├── ai_dialog.py        # AI Assistant dialog (NEW!)
│   └── ...
├── tests/                   # Test suite
└── .kiro/specs/            # Design specifications
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Quality
- Type hints throughout the codebase
- Comprehensive docstrings
- Property-based testing for robustness
- Modular architecture for maintainability

## Specifications

The project follows a formal specification-driven development approach:
- **Requirements Document**: Detailed user stories and acceptance criteria
- **Design Document**: Architecture and component specifications
- **Property-Based Testing**: Formal correctness properties

See `.kiro/specs/chemical-reaction-drawer/` for complete specifications.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built using modern Python development practices
- Extensive property-based testing with Hypothesis
- OpenGL-based 3D rendering for high performance
- Chemical intelligence based on established chemical rules
- AI-powered features using Amazon Bedrock and Claude 3.5 Sonnet

## Documentation

- [AI Quick Start Guide](AI_QUICK_START.md) - Get started with AI features
- [AI Integration Summary](AI_INTEGRATION_SUMMARY.md) - Technical details of AI implementation
- [Specifications](.kiro/specs/chemical-reaction-drawer/) - Complete design specifications