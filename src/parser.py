"""
Analisador sintático (parser) para expressões regulares.

Este módulo é responsável por:
1. Receber a sequência de tokens do lexer
2. Construir uma Árvore Sintática Abstrata (AST)
3. Garantir que a precedência de operadores seja respeitada
4. Implementar a gramática formal das expressões regulares

Gramática implementada:
regex       → union
union       → concat ('|' concat)*
concat      → kleene (kleene)*
kleene      → atom ('*')?
atom        → SYMBOL | '(' regex ')'

Precedência (maior para menor):
1. Fecho de Kleene (*)
2. Concatenação (justaposição)
3. União (|)
"""

from typing import List, Optional
from tokens import Token, TokenType
from ast_nodes import (
    ASTNode, SymbolNode, UnionNode, ConcatNode, 
    StarNode, EpsilonNode
)

class SyntaxError(Exception):
    """Exceção lançada quando há erros na análise sintática."""
    pass

class Parser:
    """
    Analisador sintático descendente recursivo para expressões regulares.
    
    Implementa um parser LL(1) que constrói uma AST respeitando a 
    precedência de operadores definida na gramática.
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Inicializa o parser com uma lista de tokens.
        
        Args:
            tokens: Lista de tokens produzida pelo lexer
        """
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, message: str):
        """Lança uma exceção de erro sintático."""
        current_pos = self.current_token.position if self.current_token else "EOF"
        raise SyntaxError(f"Erro sintático na posição {current_pos}: {message}")
    
    def advance(self):
        """Avança para o próximo token."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def match(self, expected_type: TokenType) -> Token:
        """
        Verifica se o token atual é do tipo esperado e avança.
        
        Args:
            expected_type: Tipo de token esperado
            
        Returns:
            Token: O token que foi consumido
            
        Raises:
            SyntaxError: Se o token não for do tipo esperado
        """
        if self.current_token is None:
            self.error(f"Esperado {expected_type}, mas chegou ao fim da entrada")
        
        if self.current_token.type != expected_type:
            self.error(f"Esperado {expected_type}, mas encontrado {self.current_token.type}")
        
        token = self.current_token
        self.advance()
        return token
    
    def parse(self) -> ASTNode:
        """
        Inicia o processo de análise sintática.
        
        Returns:
            ASTNode: Raiz da AST construída
            
        Raises:
            SyntaxError: Se houver erros sintáticos na entrada
        """
        if not self.tokens or self.current_token.type == TokenType.EOF:
            # Expressão vazia - retorna epsilon
            return EpsilonNode()
        
        ast = self.parse_regex()
        
        # Verifica se chegamos ao final da entrada
        if self.current_token and self.current_token.type != TokenType.EOF:
            self.error(f"Entrada não processada completamente. Token inesperado: {self.current_token.type}")
        
        return ast
    
    def parse_regex(self) -> ASTNode:
        """
        regex → union
        
        Returns:
            ASTNode: Nó da AST representando a expressão regular
        """
        return self.parse_union()
    
    def parse_union(self) -> ASTNode:
        """
        union → concat ('|' concat)*
        
        Trata a associatividade à esquerda da união.
        
        Returns:
            ASTNode: Nó da AST representando união(ões)
        """
        left = self.parse_concat()
        
        while (self.current_token and 
               self.current_token.type == TokenType.UNION):
            self.match(TokenType.UNION)
            right = self.parse_concat()
            left = UnionNode(left, right)
        
        return left
    
    def parse_concat(self) -> ASTNode:
        """
        concat → kleene (kleene)*
        
        Concatenação é implícita (justaposição).
        Trata a associatividade à esquerda da concatenação.
        
        Returns:
            ASTNode: Nó da AST representando concatenação(ões)
        """
        left = self.parse_kleene()
        
        # Continua concatenando enquanto há tokens que podem iniciar um 'kleene'
        while (self.current_token and 
               self.current_token.type in [TokenType.SYMBOL, TokenType.LPAREN]):
            right = self.parse_kleene()
            left = ConcatNode(left, right)
        
        return left
    
    def parse_kleene(self) -> ASTNode:
        """
        kleene → atom ('*')?
        
        O fecho de Kleene tem a maior precedência.
        
        Returns:
            ASTNode: Nó da AST representando um átomo opcionalmente com *
        """
        node = self.parse_atom()
        
        if (self.current_token and 
            self.current_token.type == TokenType.STAR):
            self.match(TokenType.STAR)
            node = StarNode(node)
        
        return node
    
    def parse_atom(self) -> ASTNode:
        """
        atom → SYMBOL | '(' regex ')'
        
        Trata símbolos terminais e subexpressões entre parênteses.
        
        Returns:
            ASTNode: Nó da AST representando um átomo
            
        Raises:
            SyntaxError: Se não encontrar um símbolo ou parêntese
        """
        if not self.current_token:
            self.error("Esperado símbolo ou '(', mas chegou ao fim da entrada")
        
        if self.current_token.type == TokenType.SYMBOL:
            token = self.match(TokenType.SYMBOL)
            return SymbolNode(token.value)
        
        elif self.current_token.type == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            node = self.parse_regex()  # Recursão para tratar subexpressão
            self.match(TokenType.RPAREN)
            return node
        
        else:
            self.error(f"Esperado símbolo ou '(', mas encontrado {self.current_token.type}")
    
    def pretty_print_ast(self, node: ASTNode, indent: int = 0) -> str:
        """
        Imprime a AST de forma hierárquica para depuração.
        
        Args:
            node: Nó da AST para imprimir
            indent: Nível de indentação
            
        Returns:
            str: Representação textual da AST
        """
        spaces = "  " * indent
        
        if isinstance(node, SymbolNode):
            return f"{spaces}Symbol: '{node.symbol}'"
        elif isinstance(node, UnionNode):
            return (f"{spaces}Union:\n"
                   f"{self.pretty_print_ast(node.left, indent + 1)}\n"
                   f"{self.pretty_print_ast(node.right, indent + 1)}")
        elif isinstance(node, ConcatNode):
            return (f"{spaces}Concat:\n"
                   f"{self.pretty_print_ast(node.left, indent + 1)}\n"
                   f"{self.pretty_print_ast(node.right, indent + 1)}")
        elif isinstance(node, StarNode):
            return (f"{spaces}Star:\n"
                   f"{self.pretty_print_ast(node.operand, indent + 1)}")
        elif isinstance(node, EpsilonNode):
            return f"{spaces}Epsilon"
        else:
            return f"{spaces}Unknown node: {type(node)}"
