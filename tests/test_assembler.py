#tests/test_assembler.py
from tests.util import assemble, assemble_and_decode, decode_word


def test_assemble_add_and_decode():
    src = "ADD $3, $1, $2"
    machine = assemble(src)
    assert len(machine) == 1
    decoded = decode_word(machine[0])
    assert decoded.op == 'ADD'
    assert decoded.type == 'R'
    assert decoded.rs == 1
    assert decoded.rt == 2
    assert decoded.rd == 3


def test_assemble_lw_sw_and_branch():
    src = "start: LW $2, 4($3)\nSW $2, 8($3)\nBEQ $2, $3, start"
    machine = assemble(src)
    # decode and verify ops
    assert decode_word(machine[0]).op == 'LW'
    assert decode_word(machine[1]).op == 'SW'
    assert decode_word(machine[2]).op == 'BEQ'