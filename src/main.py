#!/usr/bin/env python3
"""
Interface principal do compilador de expressões regulares.

Este módulo fornece uma interface de linha de comando para:
1. Compilar expressões regulares em autômatos
2. Testar strings contra expressões regulares
3. Visualizar autômatos gerados
4. Analisar a estrutura das expressões
"""

import argparse
import sys
import os
from typing import List, Optional

# Imports locais
from compiler import RegexCompiler, CompilationError
from visualizer import Visualizer
from dfa import nfa_to_dfa

def compile_regex(regex: str, debug: bool = False, output_dir: str = ".", generate_dfa: bool = False) -> None:
    """
    Compila uma expressão regular e exibe informações.
    
    Args:
        regex: Expressão regular para compilar
        debug: Se deve mostrar informações de debug
        output_dir: Diretório para salvar arquivos de saída
        generate_dfa: Se deve gerar também o AFD
    """
    try:
        print(f"Compilando expressão regular: '{regex}'")
        if debug:
            print("=" * 60)
        
        compiler = RegexCompiler(debug=debug)
        
        # Compilar para NFA
        nfa = compiler.compile(regex, to_dfa=False)
        print("✓ AFND gerado com sucesso!")
        
        # Gerar DFA se solicitado
        dfa = None
        if generate_dfa:
            dfa = nfa_to_dfa(nfa)
            print("✓ AFD gerado com sucesso!")
        
        print()
        
        # Mostrar informações dos autômatos
        if debug:
            print("INFORMAÇÕES DOS AUTÔMATOS GERADOS:")
        
        complexity = compiler.analyze_complexity(regex, include_dfa=generate_dfa)
        
        print("AFND (Autômato Finito Não-Determinístico):")
        nfa_info = complexity['nfa']
        print(f"  Estados: {nfa_info['num_states']}")
        print(f"  Transições: {nfa_info['num_transitions']}")
        print(f"  Transições ε: {nfa_info['num_epsilon_transitions']}")
        print(f"  Alfabeto: {{{', '.join(sorted(nfa.alphabet))}}}")
        print(f"  Estados finais: {nfa_info['num_final_states']}")
        
        if generate_dfa and dfa:
            print()
            print("AFD (Autômato Finito Determinístico):")
            dfa_info = complexity['dfa']
            print(f"  Estados: {dfa_info['num_states']}")
            print(f"  Transições: {dfa_info['num_transitions']}")
            print(f"  Alfabeto: {{{', '.join(sorted(dfa.alphabet))}}}")
            print(f"  Estados finais: {dfa_info['num_final_states']}")
            print(f"  Redução de estados: {dfa_info['reduction_ratio']:.2f}x")
        
        if debug:
            print()
            
            # Gerar visualizações
            visualizer = Visualizer()
            
            # Representação textual
            print("REPRESENTAÇÃO TEXTUAL:")
            print(visualizer.nfa_to_ascii(nfa))
            print()
            
            # Tabela de transições
            print("TABELA DE TRANSIÇÕES:")
            print(visualizer.create_transition_table(nfa))
            print()
            
            # Salvar arquivo DOT
            dot_file = os.path.join(output_dir, f"automato_{regex.replace('|', 'ou').replace('*', 'star').replace('(', '').replace(')', '')}")
            saved_file = visualizer.save_dot_file(nfa, dot_file, f"AFND para '{regex}'")
            print(f"Arquivo DOT salvo: {saved_file}")
            
            # Tentar gerar imagem
            image_file = visualizer.render_to_image(nfa, dot_file, 'png', f"AFND para '{regex}'")
            if image_file and image_file.endswith('.png'):
                print(f"Imagem gerada: {image_file}")
        else:
            print()
            print("Use --debug para ver representação detalhada e salvar arquivos de visualização.")
        
        return nfa
        
    except CompilationError as e:
        print(f"❌ Erro de compilação: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

def test_strings(regex: str, test_strings: List[str], debug: bool = False) -> None:
    """
    Testa uma lista de strings contra uma expressão regular.
    
    Args:
        regex: Expressão regular
        test_strings: Lista de strings para testar
        debug: Se deve mostrar informações de debug
    """
    try:
        compiler = RegexCompiler(debug=debug)
        nfa = compiler.compile(regex)
        visualizer = Visualizer()
        
        print(f"Testando strings contra a expressão regular: '{regex}'")
        print("=" * 60)
        
        for test_string in test_strings:
            result = nfa.simulate(test_string)
            status = "✓ ACEITA" if result else "❌ REJEITA"
            print(f"'{test_string}' → {status}")
            
            if debug:
                print()
                trace = visualizer.generate_simulation_trace(nfa, test_string)
                print(trace)
                print("-" * 40)
        
    except CompilationError as e:
        print(f"❌ Erro de compilação: {e}")
        sys.exit(1)

def interactive_mode():
    """Modo interativo para testar expressões regulares."""
    print("=== COMPILADOR DE EXPRESSÕES REGULARES ===")
    print("Modo interativo - Digite 'quit' para sair")
    print("Operadores suportados: | (união), * (fecho), () (agrupamento)")
    print("Exemplos: a*, a|b, (a|b)*, ab*c")
    print()
    
    compiler = RegexCompiler(debug=False)
    visualizer = Visualizer()
    
    while True:
        try:
            regex = input("regex> ").strip()
            
            if regex.lower() in ['quit', 'exit', 'q']:
                print("Saindo...")
                break
            
            if not regex:
                continue
            
            # Compilar
            try:
                nfa = compiler.compile(regex)
                print(f"✓ Compilado: {len(nfa.states)} estados, {len(nfa.transitions)} transições")
            except CompilationError as e:
                print(f"❌ Erro: {e}")
                continue
            
            # Testar strings
            while True:
                test_input = input(f"  teste (ou 'next' para nova regex)> ").strip()
                
                if test_input.lower() in ['next', 'n', '']:
                    break
                
                result = nfa.simulate(test_input)
                status = "ACEITA" if result else "REJEITA"
                print(f"  '{test_input}' → {status}")
        
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except EOFError:
            print("\nSaindo...")
            break

def main():
    """Função principal do programa."""
    parser = argparse.ArgumentParser(
        description="Compilador de Expressões Regulares para Autômatos Finitos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py "a*"                    # Compila a expressão a*
  python main.py "a|b" --test aa bb ab   # Testa strings contra a|b
  python main.py "(a|b)*" --debug        # Compila com informações de debug
  python main.py --interactive           # Modo interativo
  
Operadores suportados:
  |   união (a|b aceita 'a' ou 'b')
  *   fecho de Kleene (a* aceita '', 'a', 'aa', 'aaa', ...)
  ()  agrupamento ((a|b)* aceita qualquer sequência de a's e b's)
  
Precedência (maior para menor):
  1. Fecho de Kleene (*)
  2. Concatenação (justaposição)
  3. União (|)
        """
    )
    
    parser.add_argument(
        'regex',
        nargs='?',
        help='Expressão regular para compilar'
    )
    
    parser.add_argument(
        '--test', '-t',
        nargs='*',
        metavar='STRING',
        help='Strings para testar contra a expressão regular'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Mostrar informações detalhadas de debug'
    )
    
    parser.add_argument(
        '--dfa',
        action='store_true',
        help='Gerar também o AFD (Autômato Finito Determinístico)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help='Diretório para salvar arquivos de saída (padrão: diretório atual)'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Executar em modo interativo'
    )
    
    args = parser.parse_args()
    
    # Modo interativo
    if args.interactive:
        interactive_mode()
        return
    
    # Verificar se foi fornecida uma expressão regular
    if not args.regex:
        parser.print_help()
        sys.exit(1)
    
    # Criar diretório de saída se não existir
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Compilar e testar
    if args.test is not None:
        test_strings(args.regex, args.test, args.debug)
    else:
        compile_regex(args.regex, args.debug, args.output_dir, args.dfa)

if __name__ == '__main__':
    main()
