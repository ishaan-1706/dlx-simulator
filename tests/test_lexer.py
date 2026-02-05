#tests/test_lexer.py
from parser.lexer import Lexer


def test_basic_tokens():
    src = "ADD $1, $2, $3"
    lex = Lexer(src)
    tokens = lex.tokenize()
    types = [t.type for t in tokens]
    values = [t.value for t in tokens]
    assert types == ['MNEMONIC', 'REGISTER', 'COMMA', 'REGISTER', 'COMMA', 'REGISTER']
    assert values[0] == 'ADD'
    assert values[1] == '$1'


def test_label_and_comment():
    src = "loop: ADD $1, $1, $2  # increment"
    tokens = Lexer(src).tokenize()
    assert tokens[0].type == 'LABEL_DEF' and tokens[0].value == 'loop'
    assert any(t.type == 'MNEMONIC' and t.value == 'ADD' for t in tokens)


def test_lw_syntax():
    src = "LW $2, 4($3)"
    tokens = Lexer(src).tokenize()
    # Expect MNEMONIC REGISTER COMMA IMMEDIATE LPAREN REGISTER RPAREN
    assert [t.type for t in tokens] == ['MNEMONIC','REGISTER','COMMA','IMMEDIATE','LPAREN','REGISTER','RPAREN']


def test_hex_and_negative_immediates():
    src = "ADDI $1, $2, -0x10"
    tokens = Lexer(src).tokenize()
    assert any(t.type == 'IMMEDIATE' and t.value == '-0x10' for t in tokens)
