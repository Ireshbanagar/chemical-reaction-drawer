"""
AI integration module for Chemical Reaction Drawer.

This module provides AI-powered features using Amazon Bedrock.
"""

from .bedrock_client import BedrockClient
from .molecule_generator import MoleculeGenerator
from .ai_assistant import AIAssistant

__all__ = ['BedrockClient', 'MoleculeGenerator', 'AIAssistant']
