"""
Módulo de inicialização do pacote src.
"""

# Versão do compilador
__version__ = "1.0.0"

# Informações do projeto
__author__ = "Trabalho de Compiladores"
__description__ = "Compilador de Expressões Regulares para Autômatos Finitos"

# Exportar classes principais
from .compiler import RegexCompiler
from .nfa import NFA
from .visualizer import Visualizer

__all__ = [
    'RegexCompiler',
    'NFA', 
    'Visualizer'
]
