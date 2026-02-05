#tests/test_assembler_extended.py
import pytest
from parser.lexer import Lexer
from parser.asm_parser import Parser
from parser.assembler import Assembler
from decoder.decoder import decode


from tests.util import assemble_and_decode, assemble


def test_immediates_and_arithmetics():
    decoded = assemble_and_decode('ADDI $1, $2, -5')
    assert decoded[0].op == 'ADDI'
    # Decoder returns sign-extended immediate for ADDI
    assert decoded[0].imm == -5

    decoded = assemble_and_decode('ORI $3, $4, 0xFF')
    assert decoded[0].op == 'ORI'


def test_branch_label_undefined_raises():
    src = 'BEQ $1, $2, missing'
    with pytest.raises(ValueError):
        assemble(src)


def test_jump_label_undefined_raises():
    src = 'J nowhere'
    with pytest.raises(ValueError):
        assemble(src)


def test_bad_register_raises():
    src = 'ADD $32, $1, $2'
    with pytest.raises(ValueError):
        assemble(src)