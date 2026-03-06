"""
Amazon Bedrock client for AI-powered chemical features.
"""

import json
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BedrockConfig:
    """Configuration for Bedrock client."""
    region: str = "us-east-1"
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    max_tokens: int = 2048
    temperature: float = 0.3


class BedrockClient:
    """Client for interacting with Amazon Bedrock."""
    
    def __init__(self, config: Optional[BedrockConfig] = None):
        self.config = config or BedrockConfig()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Bedrock client."""
        try:
            import boto3
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.config.region
            )
            print(f"✓ Bedrock client initialized")
        except ImportError:
            print("⚠ boto3 not installed. Install with: pip install boto3")
            self.client = None
        except Exception as e:
            print(f"⚠ Bedrock client unavailable: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available."""
        return self.client is not None
    
    def generate_molecule_from_name(self, molecule_name: str) -> Optional[str]:
        """Generate SMILES from molecule name."""
        if not self.is_available():
            return self._fallback_lookup(molecule_name)
        
        prompt = f"""Generate the SMILES representation for: {molecule_name}

Provide ONLY the SMILES string, nothing else. If unknown, respond with "UNKNOWN".

SMILES:"""
        
        try:
            response = self._invoke_claude(prompt)
            return self._extract_smiles(response)
        except Exception as e:
            print(f"Error: {e}")
            return self._fallback_lookup(molecule_name)
    
    def _invoke_claude(self, prompt: str) -> str:
        """Invoke Claude model."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.client.invoke_model(
            modelId=self.config.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _extract_smiles(self, response: str) -> Optional[str]:
        """Extract SMILES from response."""
        smiles = response.strip()
        
        # Remove prefixes
        for prefix in ["SMILES:", "smiles:", "The SMILES is:"]:
            if smiles.startswith(prefix):
                smiles = smiles[len(prefix):].strip()
        
        if smiles.upper() == "UNKNOWN":
            return None
        
        # Take first line only
        smiles = smiles.split('\n')[0].strip()
        
        return smiles if smiles else None
    
    def _fallback_lookup(self, molecule_name: str) -> Optional[str]:
        """Fallback molecule lookup without AI."""
        # Common molecules database
        molecules = {
            "water": "O",
            "methane": "C",
            "ethane": "CC",
            "propane": "CCC",
            "butane": "CCCC",
            "methanol": "CO",
            "ethanol": "CCO",
            "acetone": "CC(=O)C",
            "benzene": "c1ccccc1",
            "toluene": "Cc1ccccc1",
            "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
            "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "glucose": "C(C1C(C(C(C(O1)O)O)O)O)O",
            "acetic acid": "CC(=O)O",
            "ammonia": "N",
            "carbon dioxide": "O=C=O",
            "formaldehyde": "C=O",
        }
        
        name_lower = molecule_name.lower().strip()
        return molecules.get(name_lower)
