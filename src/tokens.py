"""
Definição dos tipos de tokens para a análise léxica.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    """Tipos de tokens reconhecidos pelo lexer."""
    SYMBOL = auto()      # Símbolos alfanuméricos (a, b, 1, 2, etc.)
    UNION = auto()       # Operador de união |
    STAR = auto()        # Operador de fecho de Kleene *
    LPAREN = auto()      # Parêntese esquerdo (
    RPAREN = auto()      # Parêntese direito )
    EOF = auto()         # Fim da entrada
    
    def __str__(self):
        return self.name

@dataclass
class Token:
    """Representa um token com seu tipo e valor."""
    type: TokenType
    value: str
    position: int
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', pos={self.position})"
    
    def __repr__(self):
        return self.__str__()
