"""
Analisador léxico (lexer) para expressões regulares.

Este módulo é responsável por:
1. Percorrer a string de entrada caracter por caracter
2. Reconhecer tokens (símbolos, operadores, delimitadores)
3. Classificar cada token na categoria adequada
4. Preparar uma sequência de tokens para a análise sintática
"""

from typing import List, Iterator
from tokens import Token, TokenType

class LexicalError(Exception):
    """Exceção lançada quando há erros na análise léxica."""
    pass

class Lexer:
    """
    Analisador léxico para expressões regulares.
    
    Reconhece os seguintes tokens:
    - SYMBOL: caracteres alfanuméricos [a-zA-Z0-9]
    - UNION: operador | 
    - STAR: operador *
    - LPAREN: parêntese esquerdo (
    - RPAREN: parêntese direito )
    - EOF: fim da entrada
    """
    
    def __init__(self, input_string: str):
        """
        Inicializa o lexer com a string de entrada.
        
        Args:
            input_string: A expressão regular a ser tokenizada
        """
        self.input = input_string
        self.position = 0
        self.current_char = self.input[0] if input_string else None
    
    def error(self, message: str):
        """Lança uma exceção de erro léxico."""
        raise LexicalError(f"Erro léxico na posição {self.position}: {message}")
    
    def advance(self):
        """Avança para o próximo caractere na entrada."""
        self.position += 1
        if self.position >= len(self.input):
            self.current_char = None
        else:
            self.current_char = self.input[self.position]
    
    def skip_whitespace(self):
        """Pula espaços em branco na entrada."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def is_symbol_char(self, char: str) -> bool:
        """
        Verifica se um caractere é um símbolo válido.
        
        Args:
            char: Caractere a ser verificado
            
        Returns:
            True se o caractere é alfanumérico, False caso contrário
        """
        return char is not None and char.isalnum()
    
    def get_next_token(self) -> Token:
        """
        Extrai e retorna o próximo token da entrada.
        
        Returns:
            Token: O próximo token reconhecido
            
        Raises:
            LexicalError: Se um caractere inválido for encontrado
        """
        while self.current_char is not None:
            current_pos = self.position
            
            # Pular espaços em branco
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Reconhecer símbolos alfanuméricos
            if self.is_symbol_char(self.current_char):
                symbol = self.current_char
                self.advance()
                return Token(TokenType.SYMBOL, symbol, current_pos)
            
            # Reconhecer operador de união |
            if self.current_char == '|':
                self.advance()
                return Token(TokenType.UNION, '|', current_pos)
            
            # Reconhecer operador de fecho de Kleene *
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.STAR, '*', current_pos)
            
            # Reconhecer parêntese esquerdo
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', current_pos)
            
            # Reconhecer parêntese direito
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', current_pos)
            
            # Caractere inválido
            self.error(f"Caractere inválido '{self.current_char}'")
        
        # Fim da entrada
        return Token(TokenType.EOF, '', self.position)
    
    def tokenize(self) -> List[Token]:
        """
        Tokeniza toda a entrada e retorna uma lista de tokens.
        
        Returns:
            List[Token]: Lista com todos os tokens da entrada
        """
        tokens = []
        
        while True:
            token = self.get_next_token()
            tokens.append(token)
            
            if token.type == TokenType.EOF:
                break
        
        return tokens
    
    def __iter__(self) -> Iterator[Token]:
        """Permite iterar sobre os tokens."""
        while True:
            token = self.get_next_token()
            yield token
            
            if token.type == TokenType.EOF:
                break
