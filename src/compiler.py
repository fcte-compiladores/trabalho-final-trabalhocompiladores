"""
Compilador principal de expressões regulares para autômatos finitos.

Este módulo integra todas as fases do compilador:
1. Análise Léxica (Lexer)
2. Análise Sintática (Parser)  
3. Geração de Código (Construção de AFND)
4. Otimização (conversão para AFD)
"""

from typing import Optional, Dict, Any, Union
from lexer import Lexer, LexicalError
from parser import Parser, SyntaxError as ParseSyntaxError
from ast_nodes import ASTNode
from nfa import NFA, ThompsonConstructor
from dfa import DFA, nfa_to_dfa

class CompilationError(Exception):
    """Exceção geral para erros de compilação."""
    pass

class RegexCompiler:
    """
    Compilador completo para expressões regulares.
    
    Converte expressões regulares em autômatos finitos através das seguintes fases:
    1. Análise Léxica: converte string em tokens
    2. Análise Sintática: converte tokens em AST
    3. Geração de Código: converte AST em AFND
    """
    
    def __init__(self, debug: bool = False):
        """
        Inicializa o compilador.
        
        Args:
            debug: Se deve imprimir informações de depuração
        """
        self.debug = debug
        self.last_tokens = None
        self.last_ast = None
        self.last_nfa = None
        self.last_dfa = None
    
    def compile(self, regex: str, to_dfa: bool = False) -> Union[NFA, DFA]:
        """
        Compila uma expressão regular em um AFND ou AFD.
        
        Args:
            regex: Expressão regular como string
            to_dfa: Se deve converter para AFD
            
        Returns:
            Union[NFA, DFA]: Autômato finito equivalente
            
        Raises:
            CompilationError: Se houver erros em qualquer fase
        """
        try:
            # Fase 1: Análise Léxica
            if self.debug:
                print(f"=== FASE 1: ANÁLISE LÉXICA ===")
                print(f"Entrada: '{regex}'")
            
            lexer = Lexer(regex)
            tokens = lexer.tokenize()
            self.last_tokens = tokens
            
            if self.debug:
                print("Tokens gerados:")
                for token in tokens:
                    print(f"  {token}")
                print()
            
            # Fase 2: Análise Sintática
            if self.debug:
                print(f"=== FASE 2: ANÁLISE SINTÁTICA ===")
            
            parser = Parser(tokens)
            ast = parser.parse()
            self.last_ast = ast
            
            if self.debug:
                print("AST construída:")
                print(parser.pretty_print_ast(ast))
                print()
            
            # Fase 3: Geração de Código (Construção de AFND)
            if self.debug:
                print(f"=== FASE 3: GERAÇÃO DE CÓDIGO ===")
            
            constructor = ThompsonConstructor()
            nfa = constructor.construct(ast)
            self.last_nfa = nfa
            
            if self.debug:
                print("AFND gerado:")
                print(nfa)
                print()
            
            # Fase 4: Conversão para AFD (opcional)
            if to_dfa:
                if self.debug:
                    print(f"=== FASE 4: CONVERSÃO NFA → DFA ===")
                
                dfa = nfa_to_dfa(nfa)
                self.last_dfa = dfa
                
                if self.debug:
                    print("AFD gerado:")
                    print(dfa)
                    print()
                
                return dfa
            
            return nfa
            
        except LexicalError as e:
            raise CompilationError(f"Erro léxico: {e}")
        except ParseSyntaxError as e:
            raise CompilationError(f"Erro sintático: {e}")
        except Exception as e:
            raise CompilationError(f"Erro interno: {e}")
    
    def test_string(self, regex: str, test_string: str, use_dfa: bool = False) -> bool:
        """
        Compila uma expressão regular e testa uma string.
        
        Args:
            regex: Expressão regular
            test_string: String para testar
            use_dfa: Se deve usar AFD em vez de AFND
            
        Returns:
            bool: True se a string é aceita, False caso contrário
        """
        automaton = self.compile(regex, to_dfa=use_dfa)
        return automaton.simulate(test_string)
    
    def get_compilation_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre a última compilação.
        
        Returns:
            Dict: Informações da compilação (tokens, AST, AFND)
        """
        return {
            'tokens': self.last_tokens,
            'ast': self.last_ast,
            'nfa': self.last_nfa,
            'dfa': self.last_dfa
        }
    
    def analyze_complexity(self, regex: str, include_dfa: bool = True) -> Dict[str, Any]:
        """
        Analisa a complexidade da expressão regular compilada.
        
        Args:
            regex: Expressão regular para analisar
            include_dfa: Se deve incluir análise do AFD
            
        Returns:
            Dict: Métricas de complexidade
        """
        nfa = self.compile(regex, to_dfa=False)
        
        result = {
            'nfa': {
                'num_states': len(nfa.states),
                'num_transitions': len(nfa.transitions),
                'alphabet_size': len(nfa.alphabet),
                'num_epsilon_transitions': len([t for t in nfa.transitions if t.is_epsilon()]),
                'num_final_states': len(nfa.final_states)
            }
        }
        
        if include_dfa:
            dfa = nfa_to_dfa(nfa)
            result['dfa'] = {
                'num_states': len(dfa.states),
                'num_transitions': len(dfa.transitions),
                'alphabet_size': len(dfa.alphabet),
                'num_final_states': len(dfa.final_states),
                'reduction_ratio': len(nfa.states) / len(dfa.states) if len(dfa.states) > 0 else 0
            }
        
        return result
