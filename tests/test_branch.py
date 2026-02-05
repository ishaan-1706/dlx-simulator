#tests/test_branch.py
import pytest
from execute.branch_unit import branch


def test_branch_blt():
    # BLT: 1 < 2 -> take target
    target = 0x200
    res = branch('BLT', 1, 2, target, pc=0x100)
    assert res == target


def test_branch_bge():
    # BGE: 2 >= 2 -> take target
    target = 0x300
    res = branch('BGE', 2, 2, target, pc=0x100)
    assert res == target


def test_branch_ble():
    # BLE: 1 <= 2 -> take target
    target = 0x400
    res = branch('BLE', 1, 2, target, pc=0x100)
    assert res == target


def test_branch_bgt():
    # BGT: 3 > 2 -> take target
    target = 0x500
    res = branch('BGT', 3, 2, target, pc=0x100)
    assert res == target


def test_jalr_returns_link():
    # JALR should return tuple (next_pc, link_reg, link_value)
    rs_val = 0x8000
    pc = 0x100
    link_reg = 31
    res = branch('JALR', rs_val, 0, 0, pc=pc, link_reg=link_reg)
    assert isinstance(res, tuple)
    next_pc, reg, link_val = res
    assert next_pc == rs_val
    assert reg == link_reg
    assert link_val == pc + 4


def test_jalr_requires_linkreg():
    with pytest.raises(ValueError):
        branch('JALR', 0x100, 0, 0, pc=0x0)