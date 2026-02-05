#tests/test_alu.py
import pytest
from execute.alu import alu


def test_add_and_addu():
    assert alu('ADD', 1, 2) == 3
    # ADDU wraps to 32-bit
    assert alu('ADDU', 0xFFFFFFFF, 1) == 0x00000000


def test_sub_and_subu():
    assert alu('SUB', 10, 3) == 7
    assert alu('SUBU', 0, 1) == (0 - 1) & 0xFFFFFFFF


def test_logic_ops():
    assert alu('AND', 0b1010, 0b1100) == 0b1000
    assert alu('OR', 1, 2) == 3
    assert alu('XOR', 0xF0F0, 0x0F0F) == 0xFFFF
    assert alu('NOR', 0, 0) == 0xFFFFFFFF


def test_set_and_unsigned_set():
    assert alu('SLT', 1, 2) == 1
    assert alu('SLT', 2, 1) == 0
    # SLTU compares unsigned
    assert alu('SLTU', 0xFFFFFFFF, 0) == 0


def test_shifts():
    # SLL: shift left logical
    assert alu('SLL', 0, 1, shamt=4) == (1 << 4) & 0xFFFFFFFF
    # SRL: logical right
    assert alu('SRL', 0, 0x80000000, shamt=31) == 1
    # SRA: arithmetic right preserves sign
    assert alu('SRA', 0, -1, shamt=1) == -1


def test_unsupported_op_raises():
    with pytest.raises(ValueError):
        alu('MUL', 1, 2)  # MUL not implemented yet
