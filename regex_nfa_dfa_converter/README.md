# Regular Expression to NFA and DFA Converter

A Python application that converts regular expressions into equivalent Non-deterministic
Finite Automata (NFA) and Deterministic Finite Automata (DFA), with visualization and
string testing capabilities.

## Course Information
- **Course:** Compiler Design (PCC-CS501)
- **Semester:** 5th Semester
- **Academic Year:** 2026–2027
- **Student:** Abhradip Pal (Roll: 16900124169)

## Features
- Parse regular expressions with union (`|`), concatenation, and Kleene star (`*`)
- Generate NFA using Thompson's construction algorithm
- Convert NFA to DFA using subset construction
- Compute epsilon-closures
- Generate transition tables for both NFA and DFA
- Visualize NFA and DFA state diagrams (requires Graphviz)
- Test whether input strings are accepted or rejected
- User-friendly Streamlit web interface

## Installation

### Prerequisites
- Python 3.10 or later
- Graphviz (for state diagram generation)

### Steps

1. **Install Graphviz:**
   - Windows: Download from https://graphviz.org/download/ and add to PATH
   - Ubuntu/Debian: `sudo apt install graphviz`
   - macOS: `brew install graphviz`

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   cd regex_nfa_dfa_converter
   streamlit run app.py
   ```

4. **Run the test suite:**
   ```bash
   python tests/test_automata.py
   ```

## Project Structure
```
regex_nfa_dfa_converter/
├── app.py                  # Streamlit web application
├── regex_parser.py         # Tokenizer and recursive descent parser
├── thompson.py             # Thompson's construction (regex AST → NFA)
├── subset_construction.py  # Subset construction (NFA → DFA)
├── simulator.py            # DFA string simulator
├── visualization.py        # Graphviz diagram generator
├── requirements.txt        # Python dependencies
├── tests/
│   └── test_automata.py    # Automated test suite
├── screenshots/            # Application screenshots
└── README.md               # This file
```

## Supported Syntax
| Operator | Symbol | Example | Description |
|----------|--------|---------|-------------|
| Union | `\|` | `a\|b` | Matches `a` or `b` |
| Concatenation | (implicit) | `ab` | Matches `a` followed by `b` |
| Kleene Star | `*` | `a*` | Matches zero or more `a` |
| Grouping | `()` | `(a\|b)*` | Groups sub-expressions |

## Algorithms Used
1. **Thompson's Construction** — Converts regex to NFA with ε-transitions
2. **Subset Construction** — Converts NFA to equivalent DFA
3. **Epsilon-Closure** — Computes reachable states via ε-transitions
4. **DFA Simulation** — Tests string acceptance/rejection
