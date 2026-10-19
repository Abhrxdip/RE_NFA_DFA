"""
Subset Construction (NFA to DFA)
================================

Converts an NFA into a Deterministic Finite Automaton (DFA) using the
subset construction algorithm (also known as the powerset construction).

Key operations:
    - Epsilon-closure: Compute all states reachable from a set via ε-transitions.
    - Move: Compute the set of states reachable from a set on a given input symbol.
    - Subset construction: Build DFA states as sets of NFA states.
"""

from thompson import NFA, NFAState, EPSILON


class DFAState:
    """
    Represents a single DFA state, which corresponds to a set of NFA states.
    """

    _id_counter = 0

    def __init__(self, nfa_states: frozenset[NFAState], label=None):
        self.id = DFAState._id_counter
        DFAState._id_counter += 1
        self.nfa_states = nfa_states
        self.label = label if label is not None else f"D{self.id}"
        self.transitions = {}  # symbol -> DFAState
        self.is_accept = False

    def __repr__(self):
        return self.label

    def __hash__(self):
        return hash(self.nfa_states)

    def __eq__(self, other):
        return isinstance(other, DFAState) and self.nfa_states == other.nfa_states


class DFA:
    """Represents a complete DFA."""

    def __init__(self, start: DFAState, states: list[DFAState], alphabet: set[str]):
        self.start = start
        self.states = states
        self.alphabet = alphabet

    def get_transition_table(self) -> list[dict]:
        """
        Build the DFA transition table.

        Returns
        -------
        list of dict
            Each dict has 'State', 'NFA States', and one key per alphabet symbol.
        """
        sorted_alpha = sorted(self.alphabet)
        table = []
        for state in self.states:
            nfa_labels = ', '.join(sorted(s.label for s in state.nfa_states))
            row = {
                'State': state.label,
                'NFA States': '{' + nfa_labels + '}',
            }
            for sym in sorted_alpha:
                if sym in state.transitions:
                    row[sym] = state.transitions[sym].label
                else:
                    row[sym] = '∅'
            # Mark start and accept
            markers = []
            if state == self.start:
                markers.append('→')
            if state.is_accept:
                markers.append('*')
            if markers:
                row['State'] = ' '.join(markers) + ' ' + row['State']
            table.append(row)
        return table


def reset_dfa_state_counter():
    """Reset the DFA state ID counter (useful for testing)."""
    DFAState._id_counter = 0


def epsilon_closure(states: set[NFAState]) -> frozenset[NFAState]:
    """
    Compute the epsilon-closure of a set of NFA states.

    The epsilon-closure of a set S is the set of all NFA states reachable
    from any state in S following only ε-transitions.

    Parameters
    ----------
    states : set of NFAState
        The initial set of NFA states.

    Returns
    -------
    frozenset of NFAState
        The epsilon-closure.

    Algorithm
    ---------
    1. Initialize a stack with all states in S.
    2. Initialize the closure with S.
    3. While the stack is not empty:
        a. Pop a state t.
        b. For each state u reachable from t on ε:
            i. If u is not already in the closure, add it and push it.
    4. Return the closure.
    """
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        for target in state.transitions.get(EPSILON, []):
            if target not in closure:
                closure.add(target)
                stack.append(target)
    return frozenset(closure)


def move(states: frozenset[NFAState], symbol: str) -> set[NFAState]:
    """
    Compute the move of a set of NFA states on a given symbol.

    Parameters
    ----------
    states : frozenset of NFAState
        The current set of NFA states.
    symbol : str
        The input symbol.

    Returns
    -------
    set of NFAState
        The set of NFA states reachable from any state in `states` on `symbol`.
    """
    result = set()
    for state in states:
        for target in state.transitions.get(symbol, []):
            result.add(target)
    return result


def subset_construction(nfa: NFA) -> DFA:
    """
    Convert an NFA to a DFA using the subset construction algorithm.

    Parameters
    ----------
    nfa : NFA
        The input NFA.

    Returns
    -------
    DFA
        The equivalent DFA.

    Algorithm
    ---------
    1. Compute ε-closure({start_nfa}) as the start DFA state.
    2. Add the start DFA state to a worklist.
    3. While the worklist is not empty:
        a. Remove a DFA state T from the worklist.
        b. For each input symbol a in the alphabet:
            i.  Compute U = ε-closure(move(T, a)).
            ii. If U is not empty and not already a DFA state, create it and add to worklist.
            iii. Add transition T --a--> U.
    4. A DFA state is an accept state if it contains the NFA accept state.
    """
    reset_dfa_state_counter()
    alphabet = nfa.get_alphabet()

    # Start state
    start_closure = epsilon_closure({nfa.start})
    start_dfa = DFAState(start_closure)
    start_dfa.is_accept = nfa.accept in start_closure

    # Map from frozenset of NFA states to DFAState
    dfa_states_map = {start_closure: start_dfa}
    worklist = [start_dfa]
    all_states = [start_dfa]

    while worklist:
        current = worklist.pop(0)
        for symbol in sorted(alphabet):
            moved = move(current.nfa_states, symbol)
            if not moved:
                continue
            target_closure = epsilon_closure(moved)
            if not target_closure:
                continue

            if target_closure not in dfa_states_map:
                new_state = DFAState(target_closure)
                new_state.is_accept = nfa.accept in target_closure
                dfa_states_map[target_closure] = new_state
                worklist.append(new_state)
                all_states.append(new_state)

            current.transitions[symbol] = dfa_states_map[target_closure]

    return DFA(start_dfa, all_states, alphabet)
