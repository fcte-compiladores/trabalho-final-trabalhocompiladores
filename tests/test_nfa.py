"""
Testes para o autômato finito não-determinístico (AFND).
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
from parser import Parser
from nfa import NFA, ThompsonConstructor

class TestNFA(unittest.TestCase):
    """Testes para a classe NFA e construção de Thompson."""
    
    def compile_regex(self, regex_str):
        """Utilitário para compilar uma expressão regular em AFND."""
        lexer = Lexer(regex_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        constructor = ThompsonConstructor()
        return constructor.construct(ast)
    
    def test_empty_string(self):
        """Testa AFND para string vazia (epsilon)."""
        nfa = self.compile_regex("")
        
        # Deve aceitar string vazia
        self.assertTrue(nfa.simulate(""))
        
        # Não deve aceitar strings não vazias
        self.assertFalse(nfa.simulate("a"))
    
    def test_single_symbol(self):
        """Testa AFND para símbolo único."""
        nfa = self.compile_regex("a")
        
        # Deve aceitar apenas 'a'
        self.assertTrue(nfa.simulate("a"))
        
        # Não deve aceitar outras strings
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("aa"))
    
    def test_simple_union(self):
        """Testa AFND para união simples."""
        nfa = self.compile_regex("a|b")
        
        # Deve aceitar 'a' e 'b'
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("b"))
        
        # Não deve aceitar outras strings
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("c"))
        self.assertFalse(nfa.simulate("ab"))
    
    def test_simple_concatenation(self):
        """Testa AFND para concatenação simples."""
        nfa = self.compile_regex("ab")
        
        # Deve aceitar apenas 'ab'
        self.assertTrue(nfa.simulate("ab"))
        
        # Não deve aceitar outras strings
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("ba"))
        self.assertFalse(nfa.simulate("abc"))
    
    def test_simple_star(self):
        """Testa AFND para fecho simples."""
        nfa = self.compile_regex("a*")
        
        # Deve aceitar zero ou mais 'a's
        self.assertTrue(nfa.simulate(""))
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("aa"))
        self.assertTrue(nfa.simulate("aaa"))
        
        # Não deve aceitar strings com outros caracteres
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate("ba"))
    
    def test_complex_expression(self):
        """Testa AFND para expressão complexa."""
        nfa = self.compile_regex("(a|b)*")
        
        # Deve aceitar qualquer sequência de a's e b's
        self.assertTrue(nfa.simulate(""))
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("b"))
        self.assertTrue(nfa.simulate("ab"))
        self.assertTrue(nfa.simulate("ba"))
        self.assertTrue(nfa.simulate("aab"))
        self.assertTrue(nfa.simulate("bba"))
        self.assertTrue(nfa.simulate("abab"))
        
        # Não deve aceitar strings com outros caracteres
        self.assertFalse(nfa.simulate("c"))
        self.assertFalse(nfa.simulate("ac"))
        self.assertFalse(nfa.simulate("abc"))
    
    def test_concatenation_with_star(self):
        """Testa concatenação com fecho."""
        nfa = self.compile_regex("ab*c")
        
        # Deve aceitar 'a', zero ou mais 'b's, seguido de 'c'
        self.assertTrue(nfa.simulate("ac"))
        self.assertTrue(nfa.simulate("abc"))
        self.assertTrue(nfa.simulate("abbc"))
        self.assertTrue(nfa.simulate("abbbc"))
        
        # Não deve aceitar outras strings
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("c"))
        self.assertFalse(nfa.simulate("bc"))
        self.assertFalse(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate("acc"))
    
    def test_union_with_concatenation(self):
        """Testa união com concatenação."""
        nfa = self.compile_regex("ab|cd")
        
        # Deve aceitar 'ab' ou 'cd'
        self.assertTrue(nfa.simulate("ab"))
        self.assertTrue(nfa.simulate("cd"))
        
        # Não deve aceitar outras strings
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("c"))
        self.assertFalse(nfa.simulate("d"))
        self.assertFalse(nfa.simulate("ac"))
        self.assertFalse(nfa.simulate("bd"))
        self.assertFalse(nfa.simulate("abcd"))
    
    def test_nested_operations(self):
        """Testa operações aninhadas."""
        nfa = self.compile_regex("(a|b)*(c|d)")
        
        # Deve aceitar qualquer sequência de a's e b's seguida de c ou d
        self.assertTrue(nfa.simulate("c"))
        self.assertTrue(nfa.simulate("d"))
        self.assertTrue(nfa.simulate("ac"))
        self.assertTrue(nfa.simulate("ad"))
        self.assertTrue(nfa.simulate("bc"))
        self.assertTrue(nfa.simulate("bd"))
        self.assertTrue(nfa.simulate("abc"))
        self.assertTrue(nfa.simulate("abd"))
        self.assertTrue(nfa.simulate("bac"))
        self.assertTrue(nfa.simulate("bad"))
        self.assertTrue(nfa.simulate("ababc"))
        
        # Não deve aceitar strings que não terminam com c ou d
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate("ce"))
        self.assertFalse(nfa.simulate("de"))
    
    def test_star_of_star(self):
        """Testa aplicação múltipla de fecho."""
        # Nota: (a*)* é equivalente a a*
        nfa1 = self.compile_regex("a*")
        nfa2 = self.compile_regex("(a*)*")
        
        test_strings = ["", "a", "aa", "aaa", "b", "ab"]
        
        for string in test_strings:
            result1 = nfa1.simulate(string)
            result2 = nfa2.simulate(string)
            self.assertEqual(result1, result2, f"Diferença para string '{string}'")
    
    def test_epsilon_closure(self):
        """Testa cálculo do fecho epsilon."""
        nfa = NFA()
        
        # Criar estados
        q0 = nfa.create_state()
        q1 = nfa.create_state()
        q2 = nfa.create_state()
        
        # Criar transições epsilon: q0 → q1 → q2
        nfa.add_epsilon_transition(q0, q1)
        nfa.add_epsilon_transition(q1, q2)
        
        # Teste do fecho epsilon
        closure = nfa.epsilon_closure({q0})
        expected_states = {q0, q1, q2}
        
        self.assertEqual(closure, expected_states)
    
    def test_nfa_structure(self):
        """Testa estrutura básica do AFND."""
        nfa = self.compile_regex("a")
        
        # Verificar que tem exatamente 2 estados
        self.assertEqual(len(nfa.states), 2)
        
        # Verificar que tem estado inicial
        self.assertIsNotNone(nfa.start_state)
        
        # Verificar que tem exatamente um estado final
        self.assertEqual(len(nfa.final_states), 1)
        
        # Verificar que tem exatamente uma transição
        self.assertEqual(len(nfa.transitions), 1)
        
        # Verificar alfabeto
        self.assertEqual(nfa.alphabet, {"a"})

if __name__ == '__main__':
    unittest.main()
