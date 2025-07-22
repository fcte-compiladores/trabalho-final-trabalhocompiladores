"""
Módulo para visualização de autômatos finitos.

Fornece funcionalidades para:
1. Gerar representações visuais dos autômatos
2. Exportar em diferentes formatos (DOT, ASCII)
3. Criar diagramas de transição de estados
"""

import os
import tempfile
import subprocess
from typing import Optional, Set, Dict, List
from nfa import NFA, NFAState, NFATransition

class Visualizer:
    """
    Classe para visualização de autômatos finitos.
    
    Suporta diferentes formatos de saída e métodos de renderização.
    """
    
    def __init__(self):
        """Inicializa o visualizador."""
        pass
    
    def nfa_to_dot(self, nfa: NFA, title: str = "AFND") -> str:
        """
        Converte um AFND para formato DOT (Graphviz).
        
        Args:
            nfa: Autômato finito não-determinístico
            title: Título do grafo
            
        Returns:
            str: Código DOT para o grafo
        """
        lines = [
            f'digraph "{title}" {{',
            '  rankdir=LR;',
            '  node [fontname="Arial"];',
            '  edge [fontname="Arial"];',
            f'  label="{title}";',
            '  labelloc="t";',
            ''
        ]
        
        # Configuração dos estados
        for state in sorted(nfa.states, key=lambda s: s.id):
            if state.is_final:
                lines.append(f'  q{state.id} [shape=doublecircle, label="q{state.id}"];')
            else:
                lines.append(f'  q{state.id} [shape=circle, label="q{state.id}"];')
        
        # Estado inicial (seta de entrada)
        if nfa.start_state:
            lines.append('')
            lines.append('  start [shape=point, width=0];')
            lines.append(f'  start -> q{nfa.start_state.id};')
        
        # Transições
        lines.append('')
        
        # Agrupar transições por (origem, destino) para evitar múltiplas setas
        transition_groups: Dict[tuple, List[str]] = {}
        
        for transition in nfa.transitions:
            key = (transition.from_state.id, transition.to_state.id)
            symbol = 'ε' if transition.symbol is None else transition.symbol
            
            if key not in transition_groups:
                transition_groups[key] = []
            transition_groups[key].append(symbol)
        
        # Gerar transições agrupadas
        for (from_id, to_id), symbols in transition_groups.items():
            label = ', '.join(sorted(symbols))
            lines.append(f'  q{from_id} -> q{to_id} [label="{label}"];')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def nfa_to_ascii(self, nfa: NFA) -> str:
        """
        Converte um AFND para representação textual ASCII.
        
        Args:
            nfa: Autômato finito não-determinístico
            
        Returns:
            str: Representação ASCII do autômato
        """
        lines = []
        lines.append("=" * 50)
        lines.append("AUTÔMATO FINITO NÃO-DETERMINÍSTICO")
        lines.append("=" * 50)
        lines.append("")
        
        # Informações gerais
        lines.append(f"Estados: {len(nfa.states)}")
        lines.append(f"Alfabeto: {{{', '.join(sorted(nfa.alphabet))}}}")
        lines.append(f"Transições: {len(nfa.transitions)}")
        lines.append("")
        
        # Estados
        lines.append("ESTADOS:")
        for state in sorted(nfa.states, key=lambda s: s.id):
            marker = ""
            if state == nfa.start_state:
                marker += "→ "
            if state.is_final:
                marker += "★ "
            lines.append(f"  {marker}q{state.id}")
        lines.append("")
        
        # Função de transição
        lines.append("FUNÇÃO DE TRANSIÇÃO:")
        lines.append("  δ(estado, símbolo) = {estados}")
        lines.append("")
        
        # Agrupar transições por estado de origem
        transitions_by_state: Dict[int, List[NFATransition]] = {}
        for transition in nfa.transitions:
            state_id = transition.from_state.id
            if state_id not in transitions_by_state:
                transitions_by_state[state_id] = []
            transitions_by_state[state_id].append(transition)
        
        for state_id in sorted(transitions_by_state.keys()):
            transitions = transitions_by_state[state_id]
            
            # Agrupar por símbolo
            by_symbol: Dict[Optional[str], List[int]] = {}
            for t in transitions:
                if t.symbol not in by_symbol:
                    by_symbol[t.symbol] = []
                by_symbol[t.symbol].append(t.to_state.id)
            
            for symbol, target_states in by_symbol.items():
                symbol_str = 'ε' if symbol is None else symbol
                targets = '{' + ', '.join(f'q{s}' for s in sorted(target_states)) + '}'
                lines.append(f"  δ(q{state_id}, {symbol_str}) = {targets}")
        
        lines.append("")
        lines.append("=" * 50)
        
        return '\n'.join(lines)
    
    def save_dot_file(self, nfa: NFA, filename: str, title: str = "AFND") -> str:
        """
        Salva um AFND em arquivo DOT.
        
        Args:
            nfa: Autômato finito não-determinístico
            filename: Nome do arquivo (sem extensão)
            title: Título do grafo
            
        Returns:
            str: Caminho do arquivo criado
        """
        dot_content = self.nfa_to_dot(nfa, title)
        filepath = f"{filename}.dot"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        
        return filepath
    
    def render_to_image(self, nfa: NFA, filename: str, format: str = 'png', title: str = "AFND") -> Optional[str]:
        """
        Renderiza um AFND para imagem usando Graphviz.
        
        Args:
            nfa: Autômato finito não-determinístico
            filename: Nome do arquivo (sem extensão)
            format: Formato da imagem ('png', 'svg', 'pdf')
            title: Título do grafo
            
        Returns:
            Optional[str]: Caminho do arquivo gerado ou None se houver erro
        """
        try:
            # Verificar se o Graphviz está disponível
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
            
            # Gerar arquivo DOT temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as temp_file:
                temp_file.write(self.nfa_to_dot(nfa, title))
                temp_path = temp_file.name
            
            # Renderizar para imagem
            output_path = f"{filename}.{format}"
            subprocess.run([
                'dot', '-T' + format, temp_path, '-o', output_path
            ], check=True)
            
            # Limpar arquivo temporário
            os.unlink(temp_path)
            
            return output_path
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Aviso: Graphviz não está instalado. Salvando apenas arquivo DOT.")
            return self.save_dot_file(nfa, filename, title)
    
    def create_transition_table(self, nfa: NFA) -> str:
        """
        Cria uma tabela de transições do AFND.
        
        Args:
            nfa: Autômato finito não-determinístico
            
        Returns:
            str: Tabela de transições formatada
        """
        if not nfa.alphabet:
            return "Nenhuma transição encontrada."
        
        # Preparar cabeçalho
        symbols = sorted(nfa.alphabet) + ['ε']
        states = sorted(nfa.states, key=lambda s: s.id)
        
        # Calcular larguras das colunas
        state_width = max(len(f"q{s.id}") for s in states) + 2
        symbol_widths = {sym: max(len(sym), 8) for sym in symbols}
        
        lines = []
        
        # Cabeçalho
        header = "Estado".ljust(state_width)
        for sym in symbols:
            header += sym.ljust(symbol_widths[sym] + 2)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Linhas da tabela
        for state in states:
            # Marcadores para estado inicial e final
            state_marker = ""
            if state == nfa.start_state:
                state_marker += "→"
            if state.is_final:
                state_marker += "★"
            
            state_str = f"{state_marker}q{state.id}".ljust(state_width)
            row = state_str
            
            for symbol in symbols:
                sym_val = None if symbol == 'ε' else symbol
                transitions = nfa.get_transitions_from(state, sym_val)
                
                if transitions:
                    targets = [f"q{t.to_state.id}" for t in transitions]
                    cell_content = "{" + ",".join(targets) + "}"
                else:
                    cell_content = "∅"
                
                row += cell_content.ljust(symbol_widths[symbol] + 2)
            
            lines.append(row)
        
        return '\n'.join(lines)
    
    def generate_simulation_trace(self, nfa: NFA, input_string: str) -> str:
        """
        Gera um trace da simulação do AFND em uma string.
        
        Args:
            nfa: Autômato finito não-determinístico
            input_string: String para simular
            
        Returns:
            str: Trace da execução
        """
        if nfa.start_state is None:
            return "Erro: AFND não possui estado inicial."
        
        lines = []
        lines.append(f"SIMULAÇÃO DO AFND")
        lines.append(f"Entrada: '{input_string}'")
        lines.append("-" * 40)
        
        current_states = nfa.epsilon_closure({nfa.start_state})
        
        def format_states(states: Set[NFAState]) -> str:
            if not states:
                return "∅"
            return "{" + ", ".join(f"q{s.id}" for s in sorted(states, key=lambda x: x.id)) + "}"
        
        lines.append(f"Estado inicial (após ε-closure): {format_states(current_states)}")
        lines.append("")
        
        for i, symbol in enumerate(input_string):
            lines.append(f"Passo {i+1}: Processando '{symbol}'")
            
            # Mostrar transições possíveis
            next_states = set()
            for state in current_states:
                transitions = nfa.get_transitions_from(state, symbol)
                for transition in transitions:
                    lines.append(f"  q{state.id} --{symbol}--> q{transition.to_state.id}")
                    next_states.add(transition.to_state)
            
            if not next_states:
                lines.append("  Nenhuma transição possível!")
                lines.append(f"  Estados atuais: ∅")
                lines.append("  REJEITA")
                return '\n'.join(lines)
            
            # Aplicar ε-closure
            current_states = nfa.epsilon_closure(next_states)
            lines.append(f"  Estados após ε-closure: {format_states(current_states)}")
            lines.append("")
        
        # Verificar aceitação
        final_intersection = current_states.intersection(nfa.final_states)
        if final_intersection:
            lines.append(f"Estados finais atingidos: {format_states(final_intersection)}")
            lines.append("ACEITA")
        else:
            lines.append("Nenhum estado final atingido.")
            lines.append("REJEITA")
        
        return '\n'.join(lines)
