#tests/test_decoder_execute_integration.py
from execute.alu import alu
from execute.branch_unit import branch
from execute.load_store_unit import load_store
from state.memory import Memory
from tests.util import require_field, decode_word


def test_decode_and_alu_add():
    # ADD $3, $1, $2 -> verify alu result when applied
    instr = 0x00221820  # ADD $3, $1, $2
    dec = decode_word(instr)
    assert dec.op == 'ADD'
    res = alu(dec.op, 10, 5)
    assert res == 15


def test_decode_and_branch_beq_taken():
    instr = (0x04 << 26) | (1 << 21) | (2 << 16) | 0x0004
    dec = decode_word(instr, pc=0x1000)
    assert dec.op == 'BEQ'
    # if rs==rt, target should be pc+4+(imm<<2)
    target = require_field(dec, 'target')
    tgt = branch(dec.op, 5, 5, target, pc=0x1000)
    assert tgt == dec.target


def test_decode_and_load_store():
    mem = Memory(size=64)
    # store via load_store and then load
    mem.store_word(8, 0xAABBCCDD)
    res = load_store('LW', mem, 8)
    assert res == 0xAABBCCDD