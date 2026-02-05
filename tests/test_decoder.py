#tests/test_decoder.py
import pytest
from decoder.decoder import decode

def test_r_type_add():
    instr = 0x00221820  # ADD $3, $1, $2
    decoded = decode(instr, pc=0x1000)
    assert decoded.op == "ADD"
    assert decoded.type == "R"
    assert decoded.rs == 1
    assert decoded.rt == 2
    assert decoded.rd == 3
    assert decoded.funct == 0x20

def test_r_type_shift():
    instr = (0 << 26) | (0 << 21) | (3 << 16) | (2 << 11) | (4 << 6) | 0x00
    decoded = decode(instr)
    assert decoded.op == "SLL"
    assert decoded.shamt == 4

def test_r_type_jr():
    instr = (31 << 21) | 0x08  # JR $31
    decoded = decode(instr)
    assert decoded.op == "JR"
    assert decoded.rs == 31

def test_i_type_load_store():
    instr = (0x23 << 26) | (3 << 21) | (2 << 16) | 0x0004  # LW $2, 4($3)
    decoded = decode(instr)
    assert decoded.op == "LW"
    assert decoded.rs == 3
    assert decoded.rt == 2
    assert decoded.imm == 4

def test_i_type_branch_beq():
    instr = (0x04 << 26) | (1 << 21) | (2 << 16) | 0x0004
    decoded = decode(instr, pc=0x1000)
    assert decoded.op == "BEQ"
    assert decoded.rs == 1
    assert decoded.rt == 2
    assert decoded.imm == 4
    assert decoded.target == 0x1000 + 4 + (4 << 2)

def test_i_type_immediate_arith():
    instr = (0x08 << 26) | (1 << 21) | (2 << 16) | 0x000A  # ADDI
    decoded = decode(instr)
    assert decoded.op == "ADDI"
    assert decoded.rs == 1
    assert decoded.rt == 2
    assert decoded.imm == 10

def test_i_type_immediate_logic():
    instr = (0x0D << 26) | (1 << 21) | (2 << 16) | 0x00FF  # ORI
    decoded = decode(instr)
    assert decoded.op == "ORI"
    assert decoded.rs == 1
    assert decoded.rt == 2
    assert decoded.imm == 0x00FF

def test_j_type_jump():
    instr = (0x02 << 26) | 0x00100000  # J
    decoded = decode(instr, pc=0x1000)
    assert decoded.op == "J"
    assert decoded.type == "J"
    assert decoded.address == 0x00100000
    assert decoded.target == ((0x1000 + 4) & 0xF0000000) | (0x00100000 << 2)

def test_j_type_jal():
    instr = (0x03 << 26) | 0x00100000  # JAL
    decoded = decode(instr, pc=0x1000)
    assert decoded.op == "JAL"
    assert decoded.type == "J"

def test_illegal_r_type_funct():
    instr = (0 << 26) | (1 << 21) | (2 << 16) | (3 << 11) | (0 << 6) | 0x3F
    with pytest.raises(ValueError):
        decode(instr)

def test_illegal_opcode():
    instr = (0x3F << 26)
    with pytest.raises(ValueError):
        decode(instr)