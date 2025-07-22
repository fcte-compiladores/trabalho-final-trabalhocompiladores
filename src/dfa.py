"""
Implementação de Autômato Finito Determinístico (AFD/DFA).

Este módulo implementa:
1. Estrutura de dados para representar AFDs
2. Conversão NFA → DFA (Construção de Subconjuntos)
3. Simulação de execução do AFD
4. Minimização do AFD
"""

from typing import Set, Dict, List, Tuple, Optional, FrozenSet
from dataclasses import dataclass
from nfa import NFA, NFAState


@dataclass
class DFAState:
    """Representa um estado no AFD."""
    id: int
    nfa_states: FrozenSet[NFAState]  # Conjunto de estados do NFA que este estado representa
    is_final: bool = False
    
    def __hash__(self):
        return hash((self.id, self.nfa_states))
    
    def __eq__(self, other):
        return isinstance(other, DFAState) and self.nfa_states == other.nfa_states
    
    def __str__(self):
        nfa_ids = sorted([s.id for s in self.nfa_states])
        final_marker = '(F)' if self.is_final else ''
        return f"q{self.id}{{{','.join(map(str, nfa_ids))}}}{final_marker}"
    
    def __repr__(self):
        return self.__str__()


@dataclass
class DFATransition:
    """Representa uma transição no AFD."""
    from_state: DFAState
    symbol: str
    to_state: DFAState
    
    def __str__(self):
        return f"{self.from_state} --{self.symbol}--> {self.to_state}"
    
    def __repr__(self):
        return self.__str__()


class DFA:
    """
    Autômato Finito Determinístico.
    
    Implementa um AFD com:
    - Estados (conjunto finito)
    - Alfabeto (conjunto de símbolos)
    - Função de transição determinística
    - Estado inicial único
    - Conjunto de estados finais
    """
    
    def __init__(self):
        """Inicializa um AFD vazio."""
        self.states: Set[DFAState] = set()
        self.alphabet: Set[str] = set()
        self.transitions: Dict[Tuple[DFAState, str], DFAState] = {}
        self.start_state: Optional[DFAState] = None
        self.final_states: Set[DFAState] = set()
        self._state_counter = 0
    
    def create_state(self, nfa_states: FrozenSet[NFAState], is_final: bool = False) -> DFAState:
        """
        Cria um novo estado com ID único.
        
        Args:
            nfa_states: Conjunto de estados do NFA que este estado representa
            is_final: Se o estado é final
            
        Returns:
            DFAState: Novo estado criado
        """
        state = DFAState(self._state_counter, nfa_states, is_final)
        self._state_counter += 1
        self.states.add(state)
        
        if is_final:
            self.final_states.add(state)
        
        return state
    
    def add_transition(self, from_state: DFAState, symbol: str, to_state: DFAState):
        """
        Adiciona uma transição ao AFD.
        
        Args:
            from_state: Estado de origem
            symbol: Símbolo da transição
            to_state: Estado de destino
        """
        self.transitions[(from_state, symbol)] = to_state
        self.alphabet.add(symbol)
    
    def get_transition(self, state: DFAState, symbol: str) -> Optional[DFAState]:
        """
        Obtém o estado de destino para uma transição específica.
        
        Args:
            state: Estado de origem
            symbol: Símbolo da transição
            
        Returns:
            Optional[DFAState]: Estado de destino ou None se não existe
        """
        return self.transitions.get((state, symbol))
    
    def simulate(self, input_string: str) -> bool:
        """
        Simula a execução do AFD em uma string de entrada.
        
        Args:
            input_string: String para testar
            
        Returns:
            bool: True se a string é aceita, False caso contrário
        """
        if self.start_state is None:
            return False
        
        current_state = self.start_state
        
        for symbol in input_string:
            next_state = self.get_transition(current_state, symbol)
            if next_state is None:
                return False
            current_state = next_state
        
        return current_state in self.final_states
    
    def to_dot(self) -> str:
        """
        Gera representação em formato DOT para visualização.
        
        Returns:
            str: Código DOT para o grafo
        """
        lines = ["digraph DFA {", "  rankdir=LR;"]
        
        # Estados
        for state in self.states:
            shape = "doublecircle" if state.is_final else "circle"
            nfa_ids = sorted([s.id for s in state.nfa_states])
            label = f"q{state.id}\\n{{{','.join(map(str, nfa_ids))}}}"
            lines.append(f'  {state.id} [shape={shape}, label="{label}"];')
        
        # Estado inicial
        if self.start_state:
            lines.append(f'  start [shape=point];')
            lines.append(f'  start -> {self.start_state.id};')
        
        # Transições
        for (from_state, symbol), to_state in self.transitions.items():
            lines.append(f'  {from_state.id} -> {to_state.id} [label="{symbol}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def __str__(self):
        """Representação textual do AFD."""
        lines = [f"AFD com {len(self.states)} estados:"]
        lines.append(f"Estados: {{{', '.join(str(s) for s in sorted(self.states, key=lambda x: x.id))}}}")
        lines.append(f"Alfabeto: {{{', '.join(sorted(self.alphabet))}}}")
        lines.append(f"Estado inicial: {self.start_state}")
        lines.append(f"Estados finais: {{{', '.join(str(s) for s in sorted(self.final_states, key=lambda x: x.id))}}}")
        lines.append("Transições:")
        
        for (from_state, symbol), to_state in sorted(self.transitions.items(), 
                                                   key=lambda x: (x[0][0].id, x[0][1], x[1].id)):
            lines.append(f"  {from_state} --{symbol}--> {to_state}")
        
        return "\n".join(lines)


class SubsetConstructor:
    """
    Implementa a construção de subconjuntos para converter NFA em DFA.
    
    O algoritmo funciona da seguinte forma:
    1. Calcula o fecho epsilon do estado inicial do NFA
    2. Para cada novo conjunto de estados e cada símbolo do alfabeto:
       - Calcula os estados alcançáveis por transições com esse símbolo
       - Calcula o fecho epsilon desses estados
       - Cria um novo estado no DFA se necessário
    3. Repete até não haver novos conjuntos de estados
    """
    
    def __init__(self):
        self.state_map: Dict[FrozenSet[NFAState], DFAState] = {}
        self.dfa: DFA = DFA()
    
    def construct(self, nfa: NFA) -> DFA:
        """
        Constrói um DFA a partir de um NFA usando construção de subconjuntos.
        
        Args:
            nfa: NFA de entrada
            
        Returns:
            DFA: DFA equivalente
        """
        if nfa.start_state is None:
            return DFA()  # Retorna DFA vazio
        
        self.state_map = {}
        self.dfa = DFA()
        self.dfa.alphabet = nfa.alphabet.copy()
        
        # Passo 1: Calcular o fecho epsilon do estado inicial
        initial_closure = nfa.epsilon_closure({nfa.start_state})
        initial_frozen = frozenset(initial_closure)
        
        # Verificar se o estado inicial contém algum estado final
        is_initial_final = bool(initial_closure.intersection(nfa.final_states))
        
        # Criar estado inicial do DFA
        initial_dfa_state = self.dfa.create_state(initial_frozen, is_initial_final)
        self.dfa.start_state = initial_dfa_state
        self.state_map[initial_frozen] = initial_dfa_state
        
        # Fila de trabalho para processar novos estados
        work_queue = [initial_frozen]
        processed = set()
        
        # Passo 2: Processar todos os conjuntos de estados
        while work_queue:
            current_set = work_queue.pop(0)
            if current_set in processed:
                continue
            
            processed.add(current_set)
            current_dfa_state = self.state_map[current_set]
            
            # Para cada símbolo do alfabeto
            for symbol in nfa.alphabet:
                # Calcular estados alcançáveis por transições com este símbolo
                next_states = set()
                for nfa_state in current_set:
                    transitions = nfa.get_transitions_from(nfa_state, symbol)
                    for transition in transitions:
                        next_states.add(transition.to_state)
                
                if not next_states:
                    continue  # Nenhuma transição com este símbolo
                
                # Calcular fecho epsilon dos estados alcançáveis
                next_closure = nfa.epsilon_closure(next_states)
                next_frozen = frozenset(next_closure)
                
                if not next_frozen:
                    continue  # Conjunto vazio
                
                # Criar novo estado DFA se necessário
                if next_frozen not in self.state_map:
                    # Verificar se contém algum estado final
                    is_final = bool(next_closure.intersection(nfa.final_states))
                    
                    new_dfa_state = self.dfa.create_state(next_frozen, is_final)
                    self.state_map[next_frozen] = new_dfa_state
                    work_queue.append(next_frozen)
                
                # Adicionar transição no DFA
                target_state = self.state_map[next_frozen]
                self.dfa.add_transition(current_dfa_state, symbol, target_state)
        
        return self.dfa
    
    def get_reachable_states(self, nfa: NFA, states: Set[NFAState], symbol: str) -> Set[NFAState]:
        """
        Calcula os estados alcançáveis de um conjunto de estados por um símbolo.
        
        Args:
            nfa: NFA de origem
            states: Conjunto de estados de origem
            symbol: Símbolo da transição
            
        Returns:
            Set[NFAState]: Estados alcançáveis
        """
        reachable = set()
        for state in states:
            transitions = nfa.get_transitions_from(state, symbol)
            for transition in transitions:
                reachable.add(transition.to_state)
        
        return reachable


def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Função de conveniência para converter NFA em DFA.
    
    Args:
        nfa: NFA de entrada
        
    Returns:
        DFA: DFA equivalente
    """
    constructor = SubsetConstructor()
    return constructor.construct(nfa)
