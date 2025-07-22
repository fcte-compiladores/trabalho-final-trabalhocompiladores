"""
Testes para o analisador sintático (parser).
"""

import unittest
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser, SyntaxError as ParseSyntaxError
from ast_nodes import SymbolNode, UnionNode, ConcatNode, StarNode, EpsilonNode

class TestParser(unittest.TestCase):
    """Testes para a classe Parser."""
    
    def parse_regex(self, regex_str):
        """Utilitário para analisar uma expressão regular."""
        lexer = Lexer(regex_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_empty_string(self):
        """Testa parsing de string vazia."""
        ast = self.parse_regex("")
        self.assertIsInstance(ast, EpsilonNode)
    
    def test_single_symbol(self):
        """Testa parsing de símbolo único."""
        ast = self.parse_regex("a")
        
        self.assertIsInstance(ast, SymbolNode)
        self.assertEqual(ast.symbol, "a")
    
    def test_simple_union(self):
        """Testa parsing de união simples."""
        ast = self.parse_regex("a|b")
        
        self.assertIsInstance(ast, UnionNode)
        self.assertIsInstance(ast.left, SymbolNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.left.symbol, "a")
        self.assertEqual(ast.right.symbol, "b")
    
    def test_simple_concatenation(self):
        """Testa parsing de concatenação simples."""
        ast = self.parse_regex("ab")
        
        self.assertIsInstance(ast, ConcatNode)
        self.assertIsInstance(ast.left, SymbolNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.left.symbol, "a")
        self.assertEqual(ast.right.symbol, "b")
    
    def test_simple_star(self):
        """Testa parsing de fecho simples."""
        ast = self.parse_regex("a*")
        
        self.assertIsInstance(ast, StarNode)
        self.assertIsInstance(ast.operand, SymbolNode)
        self.assertEqual(ast.operand.symbol, "a")
    
    def test_parentheses(self):
        """Testa parsing com parênteses."""
        ast = self.parse_regex("(a)")
        
        self.assertIsInstance(ast, SymbolNode)
        self.assertEqual(ast.symbol, "a")
    
    def test_precedence_star_over_concat(self):
        """Testa precedência: * > concatenação."""
        ast = self.parse_regex("ab*")
        
        # Deve ser Concat(a, Star(b)), não Star(Concat(a, b))
        self.assertIsInstance(ast, ConcatNode)
        self.assertIsInstance(ast.left, SymbolNode)
        self.assertIsInstance(ast.right, StarNode)
        self.assertEqual(ast.left.symbol, "a")
        self.assertEqual(ast.right.operand.symbol, "b")
    
    def test_precedence_concat_over_union(self):
        """Testa precedência: concatenação > |."""
        ast = self.parse_regex("ab|c")
        
        # Deve ser Union(Concat(a, b), c), não Concat(a, Union(b, c))
        self.assertIsInstance(ast, UnionNode)
        self.assertIsInstance(ast.left, ConcatNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.left.left.symbol, "a")
        self.assertEqual(ast.left.right.symbol, "b")
        self.assertEqual(ast.right.symbol, "c")
    
    def test_left_associativity_union(self):
        """Testa associatividade à esquerda da união."""
        ast = self.parse_regex("a|b|c")
        
        # Deve ser Union(Union(a, b), c)
        self.assertIsInstance(ast, UnionNode)
        self.assertIsInstance(ast.left, UnionNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.right.symbol, "c")
        
        # Verificar lado esquerdo
        left_union = ast.left
        self.assertEqual(left_union.left.symbol, "a")
        self.assertEqual(left_union.right.symbol, "b")
    
    def test_left_associativity_concat(self):
        """Testa associatividade à esquerda da concatenação."""
        ast = self.parse_regex("abc")
        
        # Deve ser Concat(Concat(a, b), c)
        self.assertIsInstance(ast, ConcatNode)
        self.assertIsInstance(ast.left, ConcatNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.right.symbol, "c")
        
        # Verificar lado esquerdo
        left_concat = ast.left
        self.assertEqual(left_concat.left.symbol, "a")
        self.assertEqual(left_concat.right.symbol, "b")
    
    def test_complex_expression(self):
        """Testa expressão complexa com todos os operadores."""
        ast = self.parse_regex("(a|b)*c")
        
        # Deve ser Concat(Star(Union(a, b)), c)
        self.assertIsInstance(ast, ConcatNode)
        self.assertIsInstance(ast.left, StarNode)
        self.assertIsInstance(ast.right, SymbolNode)
        self.assertEqual(ast.right.symbol, "c")
        
        # Verificar parte do fecho
        star_operand = ast.left.operand
        self.assertIsInstance(star_operand, UnionNode)
        self.assertEqual(star_operand.left.symbol, "a")
        self.assertEqual(star_operand.right.symbol, "b")
    
    def test_nested_parentheses(self):
        """Testa parênteses aninhados."""
        ast = self.parse_regex("((a))")
        
        self.assertIsInstance(ast, SymbolNode)
        self.assertEqual(ast.symbol, "a")
    
    def test_star_on_parentheses(self):
        """Testa fecho em expressão entre parênteses."""
        ast = self.parse_regex("(ab)*")
        
        self.assertIsInstance(ast, StarNode)
        self.assertIsInstance(ast.operand, ConcatNode)
        self.assertEqual(ast.operand.left.symbol, "a")
        self.assertEqual(ast.operand.right.symbol, "b")
    
    def test_multiple_stars(self):
        """Testa múltiplos fechos."""
        ast = self.parse_regex("a*b*")
        
        # Deve ser Concat(Star(a), Star(b))
        self.assertIsInstance(ast, ConcatNode)
        self.assertIsInstance(ast.left, StarNode)
        self.assertIsInstance(ast.right, StarNode)
        self.assertEqual(ast.left.operand.symbol, "a")
        self.assertEqual(ast.right.operand.symbol, "b")
    
    def test_syntax_error_unmatched_parentheses(self):
        """Testa erro de parênteses não balanceados."""
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("(a")
        
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("a)")
    
    def test_syntax_error_star_without_operand(self):
        """Testa erro de * sem operando."""
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("*")
        
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("|*")
    
    def test_syntax_error_union_without_operands(self):
        """Testa erro de | sem operandos."""
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("|")
        
        with self.assertRaises(ParseSyntaxError):
            self.parse_regex("a|")

if __name__ == '__main__':
    unittest.main()
