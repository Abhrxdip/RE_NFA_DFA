"""
DFA Simulator
=============

Simulates the execution of a DFA on an input string to determine
whether the string is accepted or rejected.
"""

from subset_construction import DFA


def simulate_dfa(dfa: DFA, input_string: str) -> dict:
    """
    Simulate the DFA on the given input string.

    The simulator processes the entire input string character by character,
    following DFA transitions. The string is accepted if and only if the
    DFA is in an accept state after consuming ALL characters.

    Parameters
    ----------
    dfa : DFA
        The DFA to simulate.
    input_string : str
        The input string to test.

    Returns
    -------
    dict
        A dictionary with keys:
        - 'accepted': bool, whether the string is accepted.
        - 'path': list of str, the sequence of DFA state labels visited.
        - 'final_state': str, the label of the final state (or 'DEAD' if stuck).
        - 'message': str, a human-readable result message.

    Algorithm
    ---------
    1. Set current_state to the DFA start state.
    2. For each character c in the input string:
        a. If current_state has a transition on c, follow it.
        b. Otherwise, the string is rejected (dead state).
    3. After processing all characters, check if current_state is an accept state.
    4. Return acceptance result and the path taken.
    """
    current = dfa.start
    path = [current.label]

    for i, ch in enumerate(input_string):
        if ch not in dfa.alphabet:
            return {
                'accepted': False,
                'path': path,
                'final_state': current.label,
                'message': (
                    f"Rejected: Character '{ch}' at position {i} "
                    f"is not in the alphabet {sorted(dfa.alphabet)}."
                ),
            }

        if ch in current.transitions:
            current = current.transitions[ch]
            path.append(current.label)
        else:
            return {
                'accepted': False,
                'path': path + ['DEAD'],
                'final_state': 'DEAD',
                'message': (
                    f"Rejected: No transition from state {current.label} "
                    f"on input '{ch}' (position {i}). Reached dead state."
                ),
            }

    accepted = current.is_accept
    status = "Accepted" if accepted else "Rejected"
    return {
        'accepted': accepted,
        'path': path,
        'final_state': current.label,
        'message': (
            f"{status}: After processing "
            f"{'empty string (ε)' if not input_string else repr(input_string)}, "
            f"DFA ended in state {current.label} "
            f"({'accept state' if accepted else 'non-accept state'})."
        ),
    }
