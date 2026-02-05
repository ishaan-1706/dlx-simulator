#tests/test_parser.py
from parser.lexer import Lexer
from parser.asm_parser import Parser


def test_parse_simple_instruction():
    src = "ADD $3, $1, $2"
    tokens = Lexer(src).tokenize()
    parsed = Parser(tokens).parse()
    assert len(parsed) == 1
    instr = parsed[0]
    assert instr.mnemonic == 'ADD'
    assert instr.operands == ['$3', '$1', '$2']


def test_parse_label_and_instruction():
    src = "loop: SUB $1, $2, $3\nJ loop"
    tokens = Lexer(src).tokenize()
    p = Parser(tokens)
    instructions = p.parse()
    assert instructions[0].label == 'loop'
    assert p.labels['loop'] == 0
    # second instruction should be J with operand 'loop'
    assert instructions[1].mnemonic == 'J'
    assert instructions[1].operands == ['loop']
