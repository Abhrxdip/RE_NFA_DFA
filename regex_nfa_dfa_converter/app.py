"""
Regular Expression to NFA and DFA Converter
============================================

A Streamlit-based web application that converts regular expressions
into equivalent NFA and DFA using Thompson's construction and
subset construction algorithms.

Usage:
    streamlit run app.py
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from regex_parser import parse_regex, validate_regex
from thompson import thompson_construct, reset_state_counter, EPSILON
from subset_construction import subset_construction, reset_dfa_state_counter
from simulator import simulate_dfa
from visualization import (
    generate_nfa_diagram, generate_dfa_diagram, graphviz_available
)


def main():
    """Main entry point for the Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="RE → NFA → DFA Converter",
        page_icon="⚙️",
        layout="wide",
    )

    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E3A5F;
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 1.5em;
    }
    .stDataFrame {
        font-size: 14px;
    }
    .result-accepted {
        padding: 15px;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        font-weight: bold;
    }
    .result-rejected {
        padding: 15px;
        border-radius: 8px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        font-weight: bold;
    }
    .result-error {
        padding: 15px;
        border-radius: 8px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        font-weight: bold;
    }
    .info-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #e7f1ff;
        border: 1px solid #b8daff;
        color: #004085;
        margin-bottom: 1em;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown('<div class="main-title">⚙️ Regular Expression to NFA & DFA Converter</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Thompson\'s Construction &amp; Subset Construction | '
        'Compiler Design (PCC-CS501) Mini Project</div>',
        unsafe_allow_html=True
    )

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        **Project:** Regular Expression to NFA and DFA Converter

        **Course:** Compiler Design (PCC-CS501)

        **Student:** Abhradip Pal

        **Roll No:** 16900124169

        ---

        **Supported Operators:**
        - `|` — Union (alternation)
        - `*` — Kleene star (zero or more)
        - `()` — Grouping
        - Implicit concatenation

        **Alphabet:** `a-z`, `0-9`

        ---

        **Examples:**
        - `a` — Single symbol
        - `a|b` — Union
        - `ab` — Concatenation
        - `a*` — Kleene star
        - `(a|b)*abb` — Combined
        """)

        # Graphviz status
        st.markdown("---")
        if graphviz_available():
            st.success("✅ Graphviz is available")
        else:
            st.warning("⚠️ Graphviz not found. State diagrams will not be generated. "
                       "Install Graphviz and add it to PATH.")

    # Main content
    col_input, col_test = st.columns([3, 2])

    with col_input:
        st.subheader("📝 Enter Regular Expression")
        regex_input = st.text_input(
            "Regular Expression",
            value="(a|b)*abb",
            placeholder="e.g., (a|b)*abb",
            help="Supported: a-z, 0-9, | (union), * (Kleene star), () (grouping)"
        )

    with col_test:
        st.subheader("🧪 Test String")
        test_string = st.text_input(
            "Input String",
            value="aabb",
            placeholder="e.g., aabb",
            help="Enter a string to test against the DFA. Leave empty to test the empty string (ε)."
        )

    # Process button
    if st.button("🚀 Convert & Analyze", type="primary", use_container_width=True):
        process_regex(regex_input, test_string)


def process_regex(regex_input: str, test_string: str):
    """Process the regular expression and display results."""

    # Validate
    error = validate_regex(regex_input)
    if error:
        st.markdown(f'<div class="result-error">❌ Invalid Regular Expression: {error}</div>',
                     unsafe_allow_html=True)
        return

    try:
        # Reset state counters for clean labeling
        reset_state_counter()
        reset_dfa_state_counter()

        # Parse
        ast = parse_regex(regex_input)
        st.success(f"✅ Regular expression `{regex_input}` parsed successfully.")

        # Build NFA
        nfa = thompson_construct(ast)
        st.markdown("---")

        # NFA Section
        st.header("🔄 NFA (Non-deterministic Finite Automaton)")

        col_nfa_table, col_nfa_diag = st.columns([1, 1])

        with col_nfa_table:
            st.subheader("NFA Transition Table")
            nfa_table = nfa.get_transition_table()
            nfa_df = pd.DataFrame(nfa_table)
            st.dataframe(nfa_df, use_container_width=True, hide_index=True)

            # NFA info
            all_states = nfa.get_all_states()
            st.info(
                f"**NFA States:** {len(all_states)} | "
                f"**Start State:** {nfa.start.label} | "
                f"**Accept State:** {nfa.accept.label} | "
                f"**Alphabet:** {{{', '.join(sorted(nfa.get_alphabet()))}}}"
            )

        with col_nfa_diag:
            st.subheader("NFA State Diagram")
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'screenshots')
            nfa_path = generate_nfa_diagram(nfa, 'nfa_diagram', output_dir)
            if nfa_path and os.path.exists(nfa_path):
                st.image(nfa_path, caption=f"NFA for: {regex_input}", use_container_width=True)
            else:
                st.warning("Graphviz is not available. Cannot generate NFA diagram.")

        st.markdown("---")

        # DFA Section
        st.header("✅ DFA (Deterministic Finite Automaton)")

        dfa = subset_construction(nfa)

        col_dfa_table, col_dfa_diag = st.columns([1, 1])

        with col_dfa_table:
            st.subheader("DFA Transition Table")
            dfa_table = dfa.get_transition_table()
            dfa_df = pd.DataFrame(dfa_table)
            st.dataframe(dfa_df, use_container_width=True, hide_index=True)

            # DFA info
            accept_states = [s.label for s in dfa.states if s.is_accept]
            st.info(
                f"**DFA States:** {len(dfa.states)} | "
                f"**Start State:** {dfa.start.label} | "
                f"**Accept States:** {{{', '.join(accept_states)}}} | "
                f"**Alphabet:** {{{', '.join(sorted(dfa.alphabet))}}}"
            )

        with col_dfa_diag:
            st.subheader("DFA State Diagram")
            dfa_path = generate_dfa_diagram(dfa, 'dfa_diagram', output_dir)
            if dfa_path and os.path.exists(dfa_path):
                st.image(dfa_path, caption=f"DFA for: {regex_input}", use_container_width=True)
            else:
                st.warning("Graphviz is not available. Cannot generate DFA diagram.")

        st.markdown("---")

        # String Testing Section
        st.header("🧪 String Testing")

        result = simulate_dfa(dfa, test_string)

        display_str = test_string if test_string else 'ε (empty string)'

        if result['accepted']:
            st.markdown(
                f'<div class="result-accepted">'
                f'✅ ACCEPTED — Input string "{display_str}" is accepted by the DFA.<br>'
                f'Path: {" → ".join(result["path"])}<br>'
                f'Final State: {result["final_state"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-rejected">'
                f'❌ REJECTED — Input string "{display_str}" is rejected by the DFA.<br>'
                f'{result["message"]}<br>'
                f'Path: {" → ".join(result["path"])}'
                f'</div>',
                unsafe_allow_html=True
            )

        # Batch testing section
        st.markdown("---")
        st.header("📋 Batch Test Results")

        batch_tests = get_batch_tests(regex_input)
        if batch_tests:
            results = []
            for test_id, (inp, expected) in enumerate(batch_tests, 1):
                res = simulate_dfa(dfa, inp)
                actual = "Accepted" if res['accepted'] else "Rejected"
                status = "✅ Pass" if actual == expected else "❌ Fail"
                results.append({
                    'Test ID': f'TC-{test_id:02d}',
                    'Input': inp if inp else 'ε (empty)',
                    'Expected': expected,
                    'Actual': actual,
                    'Status': status,
                    'Path': ' → '.join(res['path']),
                })
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True, hide_index=True)

            passed = sum(1 for r in results if '✅' in r['Status'])
            total = len(results)
            if passed == total:
                st.success(f"All {total} test cases passed! ✅")
            else:
                st.warning(f"{passed}/{total} test cases passed.")

    except (ValueError, SyntaxError) as e:
        st.markdown(
            f'<div class="result-error">❌ Error: {str(e)}</div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


def get_batch_tests(regex: str) -> list[tuple[str, str]] | None:
    """Return predefined batch tests for common expressions."""
    tests = {
        'a': [
            ('a', 'Accepted'),
            ('b', 'Rejected'),
            ('', 'Rejected'),
            ('aa', 'Rejected'),
        ],
        'a|b': [
            ('a', 'Accepted'),
            ('b', 'Accepted'),
            ('ab', 'Rejected'),
            ('', 'Rejected'),
            ('c', 'Rejected'),
        ],
        'ab': [
            ('ab', 'Accepted'),
            ('a', 'Rejected'),
            ('b', 'Rejected'),
            ('ba', 'Rejected'),
            ('', 'Rejected'),
        ],
        'a*': [
            ('', 'Accepted'),
            ('a', 'Accepted'),
            ('aaaa', 'Accepted'),
            ('b', 'Rejected'),
            ('ab', 'Rejected'),
        ],
        '(a|b)*abb': [
            ('abb', 'Accepted'),
            ('aabb', 'Accepted'),
            ('babb', 'Accepted'),
            ('aababb', 'Accepted'),
            ('ab', 'Rejected'),
            ('aba', 'Rejected'),
            ('', 'Rejected'),
            ('a', 'Rejected'),
            ('bb', 'Rejected'),
        ],
        'a*b*': [
            ('', 'Accepted'),
            ('a', 'Accepted'),
            ('b', 'Accepted'),
            ('ab', 'Accepted'),
            ('aabb', 'Accepted'),
            ('ba', 'Rejected'),
        ],
        '(ab)*': [
            ('', 'Accepted'),
            ('ab', 'Accepted'),
            ('abab', 'Accepted'),
            ('a', 'Rejected'),
            ('b', 'Rejected'),
            ('aba', 'Rejected'),
        ],
    }
    return tests.get(regex, None)


if __name__ == '__main__':
    main()
