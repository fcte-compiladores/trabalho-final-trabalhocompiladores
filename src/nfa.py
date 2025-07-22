"""
Implementação de Autômato Finito Não-Determinístico (AFND/NFA).

Este módulo implementa:
1. Estrutura de dados para representar AFNDs
2. Construção de Thompson para converter AST em AFND
3. Operações básicas em AFNDs (união, concatenação, fecho)
4. Simulação de execução do AFND
"""

from typing import Set, Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from ast_nodes import ASTNode, ASTVisitor, SymbolNode, UnionNode, ConcatNode, StarNode, EpsilonNode

@dataclass
class NFAState:
    """Representa um estado no AFND."""
    id: int
    is_final: bool = False
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, NFAState) and self.id == other.id
    
    def __str__(self):
        return f"q{self.id}{'(F)' if self.is_final else ''}"
    
    def __repr__(self):
        return self.__str__()

@dataclass
class NFATransition:
    """Representa uma transição no AFND."""
    from_state: NFAState
    symbol: Optional[str]  # None representa transição epsilon
    to_state: NFAState
    
    def is_epsilon(self) -> bool:
        """Verifica se é uma transição epsilon."""
        return self.symbol is None
    
    def __str__(self):
        symbol_str = 'ε' if self.symbol is None else self.symbol
        return f"{self.from_state} --{symbol_str}--> {self.to_state}"
    
    def __repr__(self):
        return self.__str__()

class NFA:
    """
    Autômato Finito Não-Determinístico.
    
    Implementa um AFND com:
    - Estados (conjunto finito)
    - Alfabeto (conjunto de símbolos)
    - Função de transição (permite múltiplas transições por símbolo)
    - Estado inicial único
    - Conjunto de estados finais
    - Transições epsilon
    """
    
    def __init__(self):
        """Inicializa um AFND vazio."""
        self.states: Set[NFAState] = set()
        self.alphabet: Set[str] = set()
        self.transitions: List[NFATransition] = []
        self.start_state: Optional[NFAState] = None
        self.final_states: Set[NFAState] = set()
        self._state_counter = 0
    
    def create_state(self, is_final: bool = False) -> NFAState:
        """
        Cria um novo estado com ID único.
        
        Args:
            is_final: Se o estado é final
            
        Returns:
            NFAState: Novo estado criado
        """
        state = NFAState(self._state_counter, is_final)
        self._state_counter += 1
        self.states.add(state)
        
        if is_final:
            self.final_states.add(state)
        
        return state
    
    def add_transition(self, from_state: NFAState, symbol: Optional[str], to_state: NFAState):
        """
        Adiciona uma transição ao AFND.
        
        Args:
            from_state: Estado de origem
            symbol: Símbolo da transição (None para epsilon)
            to_state: Estado de destino
        """
        transition = NFATransition(from_state, symbol, to_state)
        self.transitions.append(transition)
        
        if symbol is not None:
            self.alphabet.add(symbol)
    
    def add_epsilon_transition(self, from_state: NFAState, to_state: NFAState):
        """Adiciona uma transição epsilon."""
        self.add_transition(from_state, None, to_state)
    
    def get_transitions_from(self, state: NFAState, symbol: Optional[str] = None) -> List[NFATransition]:
        """
        Obtém todas as transições de um estado para um símbolo específico.
        
        Args:
            state: Estado de origem
            symbol: Símbolo (None para epsilon)
            
        Returns:
            List[NFATransition]: Lista de transições
        """
        return [t for t in self.transitions 
                if t.from_state == state and t.symbol == symbol]
    
    def epsilon_closure(self, states: Set[NFAState]) -> Set[NFAState]:
        """
        Calcula o fecho epsilon de um conjunto de estados.
        
        Args:
            states: Conjunto de estados inicial
            
        Returns:
            Set[NFAState]: Fecho epsilon
        """
        closure = set(states)
        stack = list(states)
        
        while stack:
            current = stack.pop()
            epsilon_transitions = self.get_transitions_from(current, None)
            
            for transition in epsilon_transitions:
                if transition.to_state not in closure:
                    closure.add(transition.to_state)
                    stack.append(transition.to_state)
        
        return closure
    
    def simulate(self, input_string: str) -> bool:
        """
        Simula a execução do AFND em uma string de entrada.
        
        Args:
            input_string: String para testar
            
        Returns:
            bool: True se a string é aceita, False caso contrário
        """
        if self.start_state is None:
            return False
        
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in input_string:
            next_states = set()
            
            for state in current_states:
                transitions = self.get_transitions_from(state, symbol)
                for transition in transitions:
                    next_states.add(transition.to_state)
            
            current_states = self.epsilon_closure(next_states)
            
            if not current_states:
                return False
        
        # Verifica se algum estado final está no conjunto atual
        return bool(current_states.intersection(self.final_states))
    
    def to_dot(self) -> str:
        """
        Gera representação em formato DOT para visualização.
        
        Returns:
            str: Código DOT para o grafo
        """
        lines = ["digraph NFA {", "  rankdir=LR;"]
        
        # Estados
        for state in self.states:
            shape = "doublecircle" if state.is_final else "circle"
            lines.append(f'  {state.id} [shape={shape}, label="q{state.id}"];')
        
        # Estado inicial
        if self.start_state:
            lines.append(f'  start [shape=point];')
            lines.append(f'  start -> {self.start_state.id};')
        
        # Transições
        for transition in self.transitions:
            symbol = 'ε' if transition.symbol is None else transition.symbol
            lines.append(f'  {transition.from_state.id} -> {transition.to_state.id} [label="{symbol}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def __str__(self):
        """Representação textual do AFND."""
        lines = [f"AFND com {len(self.states)} estados:"]
        lines.append(f"Estados: {{{', '.join(str(s) for s in sorted(self.states, key=lambda x: x.id))}}}")
        lines.append(f"Alfabeto: {{{', '.join(sorted(self.alphabet))}}}")
        lines.append(f"Estado inicial: {self.start_state}")
        lines.append(f"Estados finais: {{{', '.join(str(s) for s in sorted(self.final_states, key=lambda x: x.id))}}}")
        lines.append("Transições:")
        
        for transition in sorted(self.transitions, key=lambda x: (x.from_state.id, x.symbol or '', x.to_state.id)):
            lines.append(f"  {transition}")
        
        return "\n".join(lines)

class ThompsonConstructor(ASTVisitor):
    """
    Construtor de Thompson para converter AST em AFND.
    
    Implementa o algoritmo de Thompson que constrói AFNDs a partir
    de expressões regulares usando construções básicas.
    """
    
    def __init__(self):
        self.nfa_stack: List[NFA] = []
    
    def construct(self, ast: ASTNode) -> NFA:
        """
        Constrói um AFND a partir de uma AST.
        
        Args:
            ast: Raiz da AST da expressão regular
            
        Returns:
            NFA: AFND equivalente à expressão regular
        """
        self.nfa_stack = []
        ast.accept(self)
        
        if len(self.nfa_stack) != 1:
            raise ValueError("Erro na construção: pilha deve ter exatamente um AFND")
        
        return self.nfa_stack[0]
    
    def visit_symbol(self, node: SymbolNode) -> None:
        """Constrói AFND para um símbolo."""
        nfa = NFA()
        start = nfa.create_state()
        final = nfa.create_state(is_final=True)
        
        nfa.start_state = start
        nfa.add_transition(start, node.symbol, final)
        
        self.nfa_stack.append(nfa)
    
    def visit_epsilon(self, node: EpsilonNode) -> None:
        """Constrói AFND para epsilon."""
        nfa = NFA()
        start = nfa.create_state(is_final=True)  # Estado inicial é também final
        nfa.start_state = start
        
        self.nfa_stack.append(nfa)
    
    def visit_union(self, node: UnionNode) -> None:
        """Constrói AFND para união."""
        node.right.accept(self)
        node.left.accept(self)
        
        nfa1 = self.nfa_stack.pop()
        nfa2 = self.nfa_stack.pop()
        
        # Criar novo AFND para a união
        nfa = NFA()
        
        # Criar mapeamento de estados antigos para novos
        state_map1 = {}
        state_map2 = {}
        
        # Copiar estados do primeiro NFA
        for state in nfa1.states:
            new_state = nfa.create_state(is_final=False)
            state_map1[state] = new_state
        
        # Copiar estados do segundo NFA
        for state in nfa2.states:
            new_state = nfa.create_state(is_final=False)
            state_map2[state] = new_state
        
        # Copiar transições do primeiro NFA
        for transition in nfa1.transitions:
            from_state = state_map1[transition.from_state]
            to_state = state_map1[transition.to_state]
            if transition.symbol is None:
                nfa.add_epsilon_transition(from_state, to_state)
            else:
                nfa.add_transition(from_state, transition.symbol, to_state)
        
        # Copiar transições do segundo NFA
        for transition in nfa2.transitions:
            from_state = state_map2[transition.from_state]
            to_state = state_map2[transition.to_state]
            if transition.symbol is None:
                nfa.add_epsilon_transition(from_state, to_state)
            else:
                nfa.add_transition(from_state, transition.symbol, to_state)
        
        # Configurar alfabeto
        nfa.alphabet.update(nfa1.alphabet)
        nfa.alphabet.update(nfa2.alphabet)
        
        # Criar novos estados inicial e final
        new_start = nfa.create_state()
        new_final = nfa.create_state(is_final=True)
        
        nfa.start_state = new_start
        nfa.final_states.add(new_final)
        
        # Conectar novo estado inicial aos estados iniciais dos operandos
        nfa.add_epsilon_transition(new_start, state_map1[nfa1.start_state])
        nfa.add_epsilon_transition(new_start, state_map2[nfa2.start_state])
        
        # Conectar estados finais dos operandos ao novo estado final
        for final_state in nfa1.final_states:
            mapped_final = state_map1[final_state]
            nfa.add_epsilon_transition(mapped_final, new_final)
        for final_state in nfa2.final_states:
            mapped_final = state_map2[final_state]
            nfa.add_epsilon_transition(mapped_final, new_final)
        
        self.nfa_stack.append(nfa)
    
    def visit_concat(self, node: ConcatNode) -> None:
        """Constrói AFND para concatenação."""
        node.left.accept(self)
        node.right.accept(self)
        
        nfa2 = self.nfa_stack.pop()
        nfa1 = self.nfa_stack.pop()
        
        # Criar novo AFND para a concatenação
        nfa = NFA()
        
        # Criar mapeamento de estados antigos para novos
        state_map1 = {}
        state_map2 = {}
        
        # Copiar estados do primeiro NFA
        for state in nfa1.states:
            new_state = nfa.create_state(is_final=False)
            state_map1[state] = new_state
        
        # Copiar estados do segundo NFA
        for state in nfa2.states:
            new_state = nfa.create_state(is_final=state.is_final)
            state_map2[state] = new_state
        
        # Copiar transições do primeiro NFA
        for transition in nfa1.transitions:
            from_state = state_map1[transition.from_state]
            to_state = state_map1[transition.to_state]
            if transition.symbol is None:
                nfa.add_epsilon_transition(from_state, to_state)
            else:
                nfa.add_transition(from_state, transition.symbol, to_state)
        
        # Copiar transições do segundo NFA
        for transition in nfa2.transitions:
            from_state = state_map2[transition.from_state]
            to_state = state_map2[transition.to_state]
            if transition.symbol is None:
                nfa.add_epsilon_transition(from_state, to_state)
            else:
                nfa.add_transition(from_state, transition.symbol, to_state)
        
        # Configurar alfabeto
        nfa.alphabet.update(nfa1.alphabet)
        nfa.alphabet.update(nfa2.alphabet)
        
        # Estado inicial é o mapeamento do estado inicial do primeiro AFND
        nfa.start_state = state_map1[nfa1.start_state]
        
        # Estados finais são os mapeamentos dos estados finais do segundo AFND
        nfa.final_states = {state_map2[state] for state in nfa2.final_states}
        
        # Conectar estados finais do primeiro AFND ao estado inicial do segundo
        for final_state in nfa1.final_states:
            mapped_final = state_map1[final_state]
            mapped_initial = state_map2[nfa2.start_state]
            nfa.add_epsilon_transition(mapped_final, mapped_initial)
        
        self.nfa_stack.append(nfa)
    
    def visit_star(self, node: StarNode) -> None:
        """Constrói AFND para fecho de Kleene."""
        node.operand.accept(self)
        
        nfa1 = self.nfa_stack.pop()
        
        # Criar novo AFND para o fecho
        nfa = NFA()
        
        # Criar mapeamento de estados antigos para novos
        state_map = {}
        
        # Copiar estados do NFA operando
        for state in nfa1.states:
            new_state = nfa.create_state(is_final=False)
            state_map[state] = new_state
        
        # Copiar transições do NFA operando
        for transition in nfa1.transitions:
            from_state = state_map[transition.from_state]
            to_state = state_map[transition.to_state]
            if transition.symbol is None:
                nfa.add_epsilon_transition(from_state, to_state)
            else:
                nfa.add_transition(from_state, transition.symbol, to_state)
        
        # Configurar alfabeto
        nfa.alphabet.update(nfa1.alphabet)
        
        # Criar novos estados inicial e final
        new_start = nfa.create_state(is_final=True)  # Aceita string vazia
        new_final = nfa.create_state(is_final=True)
        
        nfa.start_state = new_start
        nfa.final_states.add(new_start)  # Estado inicial também é final (string vazia)
        nfa.final_states.add(new_final)
        
        # Conectar novo estado inicial ao estado inicial do operando
        nfa.add_epsilon_transition(new_start, state_map[nfa1.start_state])
        
        # Conectar estados finais do operando ao novo estado final
        for final_state in nfa1.final_states:
            mapped_final = state_map[final_state]
            nfa.add_epsilon_transition(mapped_final, new_final)
            # Permitir repetição
            nfa.add_epsilon_transition(mapped_final, state_map[nfa1.start_state])
        
        # Permitir pular completamente (string vazia)
        nfa.add_epsilon_transition(new_start, new_final)
        
        self.nfa_stack.append(nfa)
