"""
Regular Expression Parser
=========================

Tokenizes and parses regular expressions into an Abstract Syntax Tree (AST).

Supported Grammar (in order of increasing precedence):
    expr   -> term ('|' term)*
    term   -> factor factor*
    factor -> atom ('*')*
    atom   -> CHAR | '(' expr ')'

Supported Operators:
    |   Union (alternation)
    .   Concatenation (implicit – inserted during tokenization)
    *   Kleene star (zero or more)
    ()  Grouping

Alphabet:
    Any lowercase letter a-z or digit 0-9. The special symbol ε (epsilon)
    is handled internally and does not appear in user input.
"""


class Token:
    """Represents a single token from the regular expression."""

    # Token types
    CHAR = 'CHAR'
    UNION = 'UNION'         # |
    STAR = 'STAR'           # *
    LPAREN = 'LPAREN'       # (
    RPAREN = 'RPAREN'       # )
    CONCAT = 'CONCAT'       # . (implicit)
    END = 'END'

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {self.value!r})"
        return f"Token({self.type})"


class ASTNode:
    """Abstract Syntax Tree node for a parsed regular expression."""

    def __init__(self, type_, value=None, left=None, right=None):
        """
        Parameters
        ----------
        type_ : str
            One of 'CHAR', 'UNION', 'CONCAT', 'STAR'.
        value : str or None
            The character value (only for CHAR nodes).
        left  : ASTNode or None
            Left child (or the single operand for STAR).
        right : ASTNode or None
            Right child (for UNION and CONCAT).
        """
        self.type = type_
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        if self.type == 'CHAR':
            return f"Char({self.value!r})"
        if self.type == 'STAR':
            return f"Star({self.left})"
        return f"{self.type}({self.left}, {self.right})"


def validate_regex(regex: str) -> str | None:
    """
    Validate a regular expression string.

    Returns
    -------
    str or None
        An error message if the regex is invalid, or None if it is valid.
    """
    if not regex:
        return "Empty regular expression."

    # Check for balanced parentheses
    depth = 0
    for i, ch in enumerate(regex):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                return f"Unmatched closing parenthesis at position {i}."
    if depth > 0:
        return f"Unmatched opening parenthesis ({depth} unclosed)."

    # Check for invalid characters
    allowed = set('abcdefghijklmnopqrstuvwxyz0123456789|*()')
    for i, ch in enumerate(regex):
        if ch not in allowed:
            return f"Invalid character '{ch}' at position {i}. Allowed: a-z, 0-9, |, *, (, )."

    # Check for empty union operands
    for i, ch in enumerate(regex):
        if ch == '|':
            if i == 0:
                return "Union operator '|' at position 0 has no left operand."
            if i == len(regex) - 1:
                return f"Union operator '|' at position {i} has no right operand."
            if regex[i - 1] == '(' or regex[i - 1] == '|':
                return f"Union operator '|' at position {i} has no left operand."
            if regex[i + 1] == ')' or regex[i + 1] == '|':
                return f"Union operator '|' at position {i} has no right operand."

    # Check for empty parentheses
    for i in range(len(regex) - 1):
        if regex[i] == '(' and regex[i + 1] == ')':
            return f"Empty parentheses at position {i}."

    # Check for * without operand
    if regex[0] == '*':
        return "Kleene star '*' at position 0 has no operand."
    for i in range(1, len(regex)):
        if regex[i] == '*' and regex[i - 1] in ('|', '('):
            return f"Kleene star '*' at position {i} has no operand."

    return None


def tokenize(regex: str) -> list[Token]:
    """
    Tokenize a regular expression string, inserting explicit CONCAT tokens.

    Concatenation is implicit in regular expressions. This function inserts
    an explicit CONCAT token between adjacent symbols where concatenation
    is implied:
        - CHAR followed by CHAR         e.g. ab
        - CHAR followed by LPAREN       e.g. a(
        - RPAREN followed by CHAR       e.g. )a
        - RPAREN followed by LPAREN     e.g. )(
        - STAR followed by CHAR         e.g. a*b
        - STAR followed by LPAREN       e.g. a*(
    """
    tokens = []
    i = 0
    while i < len(regex):
        ch = regex[i]
        if ch == '|':
            tokens.append(Token(Token.UNION, '|'))
        elif ch == '*':
            tokens.append(Token(Token.STAR, '*'))
        elif ch == '(':
            tokens.append(Token(Token.LPAREN, '('))
        elif ch == ')':
            tokens.append(Token(Token.RPAREN, ')'))
        else:
            tokens.append(Token(Token.CHAR, ch))
        i += 1

    # Insert explicit CONCAT tokens
    result = []
    for j in range(len(tokens)):
        result.append(tokens[j])
        if j + 1 < len(tokens):
            t1 = tokens[j]
            t2 = tokens[j + 1]
            # Insert CONCAT between these pairs
            if t1.type in (Token.CHAR, Token.STAR, Token.RPAREN) and \
               t2.type in (Token.CHAR, Token.LPAREN):
                result.append(Token(Token.CONCAT, '.'))

    result.append(Token(Token.END))
    return result


class Parser:
    """
    Recursive descent parser for regular expressions.

    Builds an AST respecting operator precedence:
        1. Kleene star (highest)
        2. Concatenation
        3. Union (lowest)
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        """Return the current token without consuming it."""
        return self.tokens[self.pos]

    def consume(self, expected_type: str = None) -> Token:
        """Consume and return the current token."""
        token = self.tokens[self.pos]
        if expected_type and token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, got {token.type} at position {self.pos}."
            )
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        """Parse the token stream and return the AST root."""
        node = self.parse_expr()
        if self.peek().type != Token.END:
            raise SyntaxError(
                f"Unexpected token {self.peek()} at position {self.pos}."
            )
        return node

    def parse_expr(self) -> ASTNode:
        """Parse: expr -> term ('|' term)*"""
        node = self.parse_term()
        while self.peek().type == Token.UNION:
            self.consume(Token.UNION)
            right = self.parse_term()
            node = ASTNode('UNION', left=node, right=right)
        return node

    def parse_term(self) -> ASTNode:
        """Parse: term -> factor (CONCAT factor)*"""
        node = self.parse_factor()
        while self.peek().type == Token.CONCAT:
            self.consume(Token.CONCAT)
            right = self.parse_factor()
            node = ASTNode('CONCAT', left=node, right=right)
        return node

    def parse_factor(self) -> ASTNode:
        """Parse: factor -> atom ('*')*"""
        node = self.parse_atom()
        while self.peek().type == Token.STAR:
            self.consume(Token.STAR)
            node = ASTNode('STAR', left=node)
        return node

    def parse_atom(self) -> ASTNode:
        """Parse: atom -> CHAR | '(' expr ')'"""
        token = self.peek()
        if token.type == Token.CHAR:
            self.consume(Token.CHAR)
            return ASTNode('CHAR', value=token.value)
        elif token.type == Token.LPAREN:
            self.consume(Token.LPAREN)
            node = self.parse_expr()
            self.consume(Token.RPAREN)
            return node
        else:
            raise SyntaxError(
                f"Unexpected token {token} at position {self.pos}."
            )


def parse_regex(regex: str) -> ASTNode:
    """
    Parse a regular expression string into an AST.

    Parameters
    ----------
    regex : str
        The regular expression to parse.

    Returns
    -------
    ASTNode
        The root of the abstract syntax tree.

    Raises
    ------
    ValueError
        If the regular expression is invalid.
    """
    error = validate_regex(regex)
    if error:
        raise ValueError(error)
    tokens = tokenize(regex)
    parser = Parser(tokens)
    return parser.parse()
