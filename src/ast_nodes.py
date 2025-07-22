"""
Definição dos nós da Árvore Sintática Abstrata (AST).
"""

from abc import ABC, abstractmethod
from typing import List, Set

class ASTNode(ABC):
    """Classe base para todos os nós da AST."""
    
    @abstractmethod
    def accept(self, visitor):
        """Implementa o padrão Visitor para traversal da AST."""
        pass
    
    @abstractmethod
    def __str__(self):
        pass

class SymbolNode(ASTNode):
    """Nó que representa um símbolo terminal (a, b, 1, etc.)."""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def accept(self, visitor):
        return visitor.visit_symbol(self)
    
    def __str__(self):
        return f"Symbol({self.symbol})"
    
    def __repr__(self):
        return self.__str__()

class UnionNode(ASTNode):
    """Nó que representa a operação de união (|)."""
    
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_union(self)
    
    def __str__(self):
        return f"Union({self.left}, {self.right})"
    
    def __repr__(self):
        return self.__str__()

class ConcatNode(ASTNode):
    """Nó que representa a operação de concatenação."""
    
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_concat(self)
    
    def __str__(self):
        return f"Concat({self.left}, {self.right})"
    
    def __repr__(self):
        return self.__str__()

class StarNode(ASTNode):
    """Nó que representa o fecho de Kleene (*)."""
    
    def __init__(self, operand: ASTNode):
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_star(self)
    
    def __str__(self):
        return f"Star({self.operand})"
    
    def __repr__(self):
        return self.__str__()

class EpsilonNode(ASTNode):
    """Nó que representa a transição epsilon (ε)."""
    
    def accept(self, visitor):
        return visitor.visit_epsilon(self)
    
    def __str__(self):
        return "Epsilon"
    
    def __repr__(self):
        return self.__str__()

# Visitor pattern para traversal da AST
class ASTVisitor(ABC):
    """Interface para implementar visitadores da AST."""
    
    @abstractmethod
    def visit_symbol(self, node: SymbolNode):
        pass
    
    @abstractmethod
    def visit_union(self, node: UnionNode):
        pass
    
    @abstractmethod
    def visit_concat(self, node: ConcatNode):
        pass
    
    @abstractmethod
    def visit_star(self, node: StarNode):
        pass
    
    @abstractmethod
    def visit_epsilon(self, node: EpsilonNode):
        pass
