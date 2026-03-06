"""
AI Assistant for chemical structure generation and analysis.
"""

from typing import Optional, Dict, Any
from .bedrock_client import BedrockClient, BedrockConfig
from .molecule_generator import MoleculeGenerator
from ..core.models import Molecule


class AIAssistant:
    """AI-powered assistant for chemical drawing."""
    
    def __init__(self, config: Optional[BedrockConfig] = None):
        self.bedrock = BedrockClient(config)
        self.generator = MoleculeGenerator()
        self.cache = {}  # Simple in-memory cache
    
    def is_available(self) -> bool:
        """Check if AI features are available."""
        return self.bedrock.is_available()
    
    def generate_from_name(self, molecule_name: str, use_cache: bool = True) -> Optional[Molecule]:
        """Generate molecule structure from name."""
        # Check cache
        if use_cache and molecule_name in self.cache:
            return self.cache[molecule_name]
        
        # Generate molecule
        molecule = self.generator.from_name(molecule_name, self.bedrock)
        
        # Cache result
        if molecule and use_cache:
            self.cache[molecule_name] = molecule
        
        return molecule
    
    def generate_from_smiles(self, smiles: str) -> Optional[Molecule]:
        """Generate molecule structure from SMILES."""
        return self.generator.from_smiles(smiles)
    
    def clear_cache(self):
        """Clear the molecule cache."""
        self.cache.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI assistant status."""
        return {
            'available': self.is_available(),
            'cache_size': len(self.cache),
            'model': self.bedrock.config.model_id if self.bedrock else None,
        }
