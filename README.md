# Regular Expression to NFA & DFA Converter

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Graphviz](https://img.shields.io/badge/Graphviz-Visualizer-brightgreen.svg)](https://graphviz.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A complete, interactive compiler-design application that translates regular expressions into equivalent **Non-deterministic Finite Automata (NFA)** and **Deterministic Finite Automata (DFA)** with transition tables, graphical state diagrams, and string simulation.

Developed for **Compiler Design (PCC-CS501)**, 5th Semester B.Tech CSE (Academic Year 2026–2027), Bloom's Taxonomy Level **BTL-6 (Create)**, Course Outcome **CO2**.

---

## 🚀 Key Features

- **Lexical Analysis & Syntax Validation**: Tokenizes and parses regular expressions using a recursive-descent parser producing an Abstract Syntax Tree (AST) with precedence rules:
  $$\text{Grouping } () > \text{Kleene Star } * > \text{Concatenation } \cdot > \text{Union } |$$
- **Thompson's Construction**: Generates an $\varepsilon$-NFA fragment for each AST node (Base character, Union, Concatenation, and Kleene star).
- **Subset Construction (Powerset Construction)**: Computes $\varepsilon\text{-closures}$ and $\text{Move}(T, a)$ sets to determinize the NFA into an equivalent DFA.
- **Automated Transition Tables**: Produces structured transition matrices for both NFA and DFA.
- **State Diagram Visualization**: Generates clear, high-resolution vector state diagrams using Graphviz with designated start and accepting states.
- **DFA String Simulation**: Tests input strings with exact character-by-character step tracing and acceptance/rejection reporting.
- **Streamlit Web Application**: An interactive, user-friendly UI for entering expressions, testing strings, and viewing batch test results.

---

## 📁 Repository Structure

```
.
├── .gitignore                      # Git ignore rules (caches, virtualenvs, PDFs)
├── README.md                       # Repository documentation
├── aot_logo.png                    # Academy of Technology official logo
├── generate_report.py              # Academic report generator script
├── take_screenshots.py             # Headless Selenium screenshot utility
└── regex_nfa_dfa_converter/        # Primary application package
    ├── app.py                      # Streamlit interactive web application
    ├── regex_parser.py             # Lexer, AST nodes, and recursive-descent parser
    ├── thompson.py                 # Thompson's construction algorithm (AST -> NFA)
    ├── subset_construction.py      # Epsilon-closure & subset construction (NFA -> DFA)
    ├── simulator.py                # DFA string simulation and path tracing
    ├── visualization.py            # Graphviz state diagram generator
    ├── requirements.txt            # Python dependencies
    ├── README.md                   # Module-specific documentation
    ├── screenshots/                # Application output screenshots and DOT files
    │   ├── nfa_diagram.png
    │   ├── dfa_diagram.png
    │   ├── app_home.png
    │   └── ...
    └── tests/
        └── test_automata.py        # Comprehensive test suite (57 test cases)
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.10+**
- **Graphviz** (system binary):
  - **Windows**: Download from [Graphviz Downloads](https://graphviz.org/download/) or install via winget:
    ```powershell
    winget install Graphviz.Graphviz
    ```
  - **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt update && sudo apt install -y graphviz
    ```
  - **macOS**:
    ```bash
    brew install graphviz
    ```

### 2. Install Python Dependencies
```bash
pip install -r regex_nfa_dfa_converter/requirements.txt
```

---

## 💻 Usage

### Run the Web Interface
Launch the Streamlit web dashboard:
```bash
streamlit run regex_nfa_dfa_converter/app.py
```
Open **`http://localhost:8501`** in your browser.

### Run Automated Tests
Execute the 57-test validation suite:
```bash
python -X utf8 regex_nfa_dfa_converter/tests/test_automata.py
```

---

## 🧪 Supported Grammar & Operators

| Operator | Syntax | Precedence | Associativity | Example |
| :--- | :--- | :--- | :--- | :--- |
| **Grouping** | `( ... )` | Highest (3) | N/A | `(a\|b)` |
| **Kleene Star** | `*` | High (2) | Left | `a*`, `(a\|b)*` |
| **Concatenation** | Implicit (`ab`) | Medium (1) | Left | `ab`, `abb` |
| **Union** | `\|` | Lowest (0) | Left | `a\|b` |

- **Alphabet ($\Sigma$)**: Lowercase letters `a-z`, digits `0-9`.
- **Empty String ($\varepsilon$)**: Handled implicitly for star and epsilon transitions.

---

## 📊 Sample Conversions

### Benchmark: `(a|b)*abb`
- **NFA States**: 11 states ($q_0 \dots q_{10}$), start: $q_0$, accept: $q_{10}$
- **DFA States**: 5 states ($D_0 \dots D_4$), start: $D_0$, accept: $\{D_4\}$
- **Transitions**:
  - $D_0 \xrightarrow{a} D_1, \quad D_0 \xrightarrow{b} D_2$
  - $D_1 \xrightarrow{a} D_1, \quad D_1 \xrightarrow{b} D_3$
  - $D_2 \xrightarrow{a} D_1, \quad D_2 \xrightarrow{b} D_2$
  - $D_3 \xrightarrow{a} D_1, \quad D_3 \xrightarrow{b} D_4$
  - $D_4 \xrightarrow{a} D_1, \quad D_4 \xrightarrow{b} D_2$

---

## 👥 Author

- **Student Name**: Abhradip Pal
- **Roll Number**: 16900124169
- **Department**: Computer Science and Engineering
- **Institution**: Academy of Technology, Adisaptagram, Hooghly
- **Course**: Compiler Design (`PCC-CS501`)
