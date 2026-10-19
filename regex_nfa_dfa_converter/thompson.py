"""
Thompson's Construction
=======================

Converts a regular expression AST into a Non-deterministic Finite Automaton (NFA)
using Thompson's construction algorithm.

Each basic pattern is converted to an NFA fragment with exactly one start state
and one accept state. Fragments are composed according to the AST operators:

    CHAR  : Create a two-state NFA with a transition on the character.
    CONCAT: Connect the accept state of the first to the start state of the second.
    UNION : Create new start/accept states with ε-transitions to/from both alternatives.
    STAR  : Create new start/accept states with ε-transitions for the loop and bypass.
"""

from regex_parser import ASTNode

# Epsilon symbol used for ε-transitions
EPSILON = 'ε'


class NFAState:
    """Represents a single state in the NFA."""

    _id_counter = 0

    def __init__(self, label=None):
        self.id = NFAState._id_counter
        NFAState._id_counter += 1
        self.label = label if label is not None else f"q{self.id}"
        self.transitions = {}  # symbol -> list of NFAState

    def add_transition(self, symbol, state):
        """Add a transition from this state to another on the given symbol."""
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

    def __repr__(self):
        return self.label

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, NFAState) and self.id == other.id


class NFA:
    """Represents a complete NFA with a start state and an accept state."""

    def __init__(self, start: NFAState, accept: NFAState):
        self.start = start
        self.accept = accept

    def get_all_states(self) -> list[NFAState]:
        """Return all states reachable from the start state (BFS)."""
        visited = set()
        queue = [self.start]
        result = []
        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)
            result.append(state)
            for targets in state.transitions.values():
                for target in targets:
                    if target not in visited:
                        queue.append(target)
        return result

    def get_alphabet(self) -> set[str]:
        """Return the set of all input symbols (excluding ε)."""
        symbols = set()
        for state in self.get_all_states():
            for symbol in state.transitions:
                if symbol != EPSILON:
                    symbols.add(symbol)
        return symbols

    def get_transition_table(self) -> list[dict]:
        """
        Build the NFA transition table.

        Returns
        -------
        list of dict
            Each dict has keys: 'state', then one key per symbol including 'ε'.
            Values are comma-separated state labels or '∅' for no transition.
        """
        states = self.get_all_states()
        alphabet = sorted(self.get_alphabet())
        symbols = alphabet + [EPSILON]

        table = []
        for state in states:
            row = {'State': state.label}
            for sym in symbols:
                targets = state.transitions.get(sym, [])
                if targets:
                    row[sym] = ', '.join(sorted(t.label for t in targets))
                else:
                    row[sym] = '∅'
            # Mark start and accept
            markers = []
            if state == self.start:
                markers.append('→')
            if state == self.accept:
                markers.append('*')
            if markers:
                row['State'] = ' '.join(markers) + ' ' + row['State']
            table.append(row)
        return table


def reset_state_counter():
    """Reset the state ID counter (useful for testing)."""
    NFAState._id_counter = 0


def thompson_construct(ast: ASTNode) -> NFA:
    """
    Apply Thompson's construction to build an NFA from an AST.

    Parameters
    ----------
    ast : ASTNode
        The root of the regular expression AST.

    Returns
    -------
    NFA
        The resulting NFA.

    Algorithm
    ---------
    1. CHAR node: Create start --symbol--> accept.
    2. CONCAT node: Build NFA for left and right; connect left.accept to right.start via ε.
    3. UNION node: New start with ε to both sub-NFA starts; both sub-NFA accepts ε to new accept.
    4. STAR node: New start with ε to sub-NFA start and new accept; sub-NFA accept ε to
       sub-NFA start and new accept.
    """
    if ast.type == 'CHAR':
        start = NFAState()
        accept = NFAState()
        start.add_transition(ast.value, accept)
        return NFA(start, accept)

    elif ast.type == 'CONCAT':
        left_nfa = thompson_construct(ast.left)
        right_nfa = thompson_construct(ast.right)
        # Connect left accept to right start via ε
        left_nfa.accept.add_transition(EPSILON, right_nfa.start)
        return NFA(left_nfa.start, right_nfa.accept)

    elif ast.type == 'UNION':
        start = NFAState()
        accept = NFAState()
        left_nfa = thompson_construct(ast.left)
        right_nfa = thompson_construct(ast.right)
        # New start ε-transitions to both sub-NFA starts
        start.add_transition(EPSILON, left_nfa.start)
        start.add_transition(EPSILON, right_nfa.start)
        # Both sub-NFA accepts ε-transition to new accept
        left_nfa.accept.add_transition(EPSILON, accept)
        right_nfa.accept.add_transition(EPSILON, accept)
        return NFA(start, accept)

    elif ast.type == 'STAR':
        start = NFAState()
        accept = NFAState()
        sub_nfa = thompson_construct(ast.left)
        # Start ε-transitions to sub-NFA start and directly to accept (zero occurrences)
        start.add_transition(EPSILON, sub_nfa.start)
        start.add_transition(EPSILON, accept)
        # Sub-NFA accept ε-transitions back to sub-NFA start (loop) and to new accept
        sub_nfa.accept.add_transition(EPSILON, sub_nfa.start)
        sub_nfa.accept.add_transition(EPSILON, accept)
        return NFA(start, accept)

    else:
        raise ValueError(f"Unknown AST node type: {ast.type}")
