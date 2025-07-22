"""
Testes para o analisador léxico (lexer).
"""

import unittest
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer, LexicalError
from tokens import Token, TokenType

class TestLexer(unittest.TestCase):
    """Testes para a classe Lexer."""
    
    def test_empty_string(self):
        """Testa tokenização de string vazia."""
        lexer = Lexer("")
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_single_symbol(self):
        """Testa tokenização de símbolo único."""
        lexer = Lexer("a")
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.SYMBOL)
        self.assertEqual(tokens[0].value, "a")
        self.assertEqual(tokens[1].type, TokenType.EOF)
    
    def test_multiple_symbols(self):
        """Testa tokenização de múltiplos símbolos."""
        lexer = Lexer("abc")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.SYMBOL, "a"),
            (TokenType.SYMBOL, "b"),
            (TokenType.SYMBOL, "c"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 4)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_union_operator(self):
        """Testa tokenização do operador de união."""
        lexer = Lexer("a|b")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.SYMBOL, "a"),
            (TokenType.UNION, "|"),
            (TokenType.SYMBOL, "b"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 4)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_star_operator(self):
        """Testa tokenização do operador de fecho."""
        lexer = Lexer("a*")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.SYMBOL, "a"),
            (TokenType.STAR, "*"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 3)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_parentheses(self):
        """Testa tokenização de parênteses."""
        lexer = Lexer("(a)")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.LPAREN, "("),
            (TokenType.SYMBOL, "a"),
            (TokenType.RPAREN, ")"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 4)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_complex_expression(self):
        """Testa tokenização de expressão complexa."""
        lexer = Lexer("(a|b)*c")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.LPAREN, "("),
            (TokenType.SYMBOL, "a"),
            (TokenType.UNION, "|"),
            (TokenType.SYMBOL, "b"),
            (TokenType.RPAREN, ")"),
            (TokenType.STAR, "*"),
            (TokenType.SYMBOL, "c"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 8)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_whitespace_handling(self):
        """Testa tratamento de espaços em branco."""
        lexer = Lexer(" a | b ")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.SYMBOL, "a"),
            (TokenType.UNION, "|"),
            (TokenType.SYMBOL, "b"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 4)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_numeric_symbols(self):
        """Testa símbolos numéricos."""
        lexer = Lexer("1|2*")
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.SYMBOL, "1"),
            (TokenType.UNION, "|"),
            (TokenType.SYMBOL, "2"),
            (TokenType.STAR, "*"),
            (TokenType.EOF, "")
        ]
        
        self.assertEqual(len(tokens), 5)
        for i, (expected_type, expected_value) in enumerate(expected):
            self.assertEqual(tokens[i].type, expected_type)
            self.assertEqual(tokens[i].value, expected_value)
    
    def test_invalid_character(self):
        """Testa caractere inválido."""
        lexer = Lexer("a@b")
        
        with self.assertRaises(LexicalError) as context:
            lexer.tokenize()
        
        self.assertIn("Caractere inválido '@'", str(context.exception))
    
    def test_token_positions(self):
        """Testa posições dos tokens."""
        lexer = Lexer("a|b")
        tokens = lexer.tokenize()
        
        expected_positions = [0, 1, 2, 3]  # a=0, |=1, b=2, EOF=3
        
        for i, expected_pos in enumerate(expected_positions):
            self.assertEqual(tokens[i].position, expected_pos)

if __name__ == '__main__':
    unittest.main()
