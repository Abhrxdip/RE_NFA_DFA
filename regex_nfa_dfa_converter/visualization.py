"""
Visualization Module
====================

Generates state diagrams for NFA and DFA using Graphviz.
Outputs diagrams as PNG images.
"""

import subprocess
import os
from thompson import NFA, EPSILON
from subset_construction import DFA


# Ensure Graphviz bin is in PATH if installed in known locations
_KNOWN_PATHS = [
    r'C:\Users\abhra\graphviz\Graphviz-16.1.0-win64\bin',
    r'C:\Program Files\Graphviz\bin',
    r'C:\Program Files (x86)\Graphviz\bin',
]
for _p in _KNOWN_PATHS:
    if os.path.exists(_p) and _p not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _p + os.pathsep + os.environ.get('PATH', '')

def _check_graphviz():
    """Check if Graphviz is available in the system PATH."""
    try:
        result = subprocess.run(
            ['dot', '-V'],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0 or 'graphviz' in result.stderr.lower()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def generate_nfa_diagram(nfa: NFA, filename: str = 'nfa_diagram',
                         output_dir: str = '.') -> str | None:
    """
    Generate a state diagram for the NFA.

    Parameters
    ----------
    nfa : NFA
        The NFA to visualize.
    filename : str
        Base filename (without extension).
    output_dir : str
        Directory to save the output.

    Returns
    -------
    str or None
        Path to the generated PNG file, or None if Graphviz is not available.
    """
    if not _check_graphviz():
        return None

    dot_lines = [
        'digraph NFA {',
        '    rankdir=LR;',
        '    size="10,5";',
        '    node [shape=circle, fontname="Arial", fontsize=12];',
        '    edge [fontname="Arial", fontsize=11];',
        '',
        '    // Invisible start arrow',
        '    start [shape=point, width=0];',
        f'    start -> {nfa.start.label};',
        '',
        f'    // Accept state',
        f'    {nfa.accept.label} [shape=doublecircle];',
        '',
    ]

    states = nfa.get_all_states()
    for state in states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                label = symbol if symbol != EPSILON else 'ε'
                dot_lines.append(
                    f'    {state.label} -> {target.label} [label="{label}"];'
                )

    dot_lines.append('}')
    dot_content = '\n'.join(dot_lines)

    os.makedirs(output_dir, exist_ok=True)
    dot_path = os.path.join(output_dir, f'{filename}.dot')
    png_path = os.path.join(output_dir, f'{filename}.png')

    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write(dot_content)

    try:
        subprocess.run(
            ['dot', '-Tpng', dot_path, '-o', png_path],
            capture_output=True, text=True, timeout=30, check=True
        )
        return png_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Graphviz error: {e}")
        return None


def generate_dfa_diagram(dfa: DFA, filename: str = 'dfa_diagram',
                         output_dir: str = '.') -> str | None:
    """
    Generate a state diagram for the DFA.

    Parameters
    ----------
    dfa : DFA
        The DFA to visualize.
    filename : str
        Base filename (without extension).
    output_dir : str
        Directory to save the output.

    Returns
    -------
    str or None
        Path to the generated PNG file, or None if Graphviz is not available.
    """
    if not _check_graphviz():
        return None

    dot_lines = [
        'digraph DFA {',
        '    rankdir=LR;',
        '    size="10,5";',
        '    node [shape=circle, fontname="Arial", fontsize=12];',
        '    edge [fontname="Arial", fontsize=11];',
        '',
        '    // Invisible start arrow',
        '    start [shape=point, width=0];',
        f'    start -> {dfa.start.label};',
        '',
    ]

    # Mark accept states
    for state in dfa.states:
        if state.is_accept:
            dot_lines.append(f'    {state.label} [shape=doublecircle];')

    dot_lines.append('')

    # Transitions
    for state in dfa.states:
        # Group transitions to same target by label
        target_labels = {}
        for symbol, target in state.transitions.items():
            key = target.label
            if key not in target_labels:
                target_labels[key] = []
            target_labels[key].append(symbol)

        for target_label, symbols in target_labels.items():
            label = ', '.join(sorted(symbols))
            dot_lines.append(
                f'    {state.label} -> {target_label} [label="{label}"];'
            )

    dot_lines.append('}')
    dot_content = '\n'.join(dot_lines)

    os.makedirs(output_dir, exist_ok=True)
    dot_path = os.path.join(output_dir, f'{filename}.dot')
    png_path = os.path.join(output_dir, f'{filename}.png')

    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write(dot_content)

    try:
        subprocess.run(
            ['dot', '-Tpng', dot_path, '-o', png_path],
            capture_output=True, text=True, timeout=30, check=True
        )
        return png_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Graphviz error: {e}")
        return None


def graphviz_available() -> bool:
    """Check if Graphviz is available."""
    return _check_graphviz()
