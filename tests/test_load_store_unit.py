#tests/test_load_store_unit.py
import pytest
from execute.load_store_unit import load_store
from state.memory import Memory


def test_lw_and_sw_word():
    mem = Memory(size=64)
    # store word then load it back
    load_store('SW', mem, 4, 0x11223344)
    assert load_store('LW', mem, 4) == 0x11223344


def test_lb_lbu_and_sb():
    mem = Memory(size=32)
    mem.mem[10] = 0xFF  # -1 signed
    assert load_store('LB', mem, 10) == -1
    assert load_store('LBU', mem, 10) == 0xFF

    # store byte
    load_store('SB', mem, 11, 0x7F)
    assert mem.mem[11] == 0x7F


def test_lh_lhu_and_sh():
    mem = Memory(size=32)
    # write half as two bytes and read as LH
    mem.mem[20] = 0xFF
    mem.mem[21] = 0x80  # 0xFF80 -> signed -128
    assert load_store('LH', mem, 20) == -128
    assert load_store('LHU', mem, 20) == 0xFF80

    load_store('SH', mem, 22, 0x1234)
    assert mem.mem[22] == 0x12
    assert mem.mem[23] == 0x34


def test_alignment_and_bounds_checks():
    mem = Memory(size=16)
    with pytest.raises(ValueError):
        load_store('LW', mem, 2)  # unaligned

    with pytest.raises(ValueError):
        load_store('SH', mem, 15, 1)  # halfword out of bounds

    with pytest.raises(ValueError):
        load_store('LW', mem, 65536)  # out of bounds


def test_store_requires_rt_val():
    mem = Memory(size=16)
    with pytest.raises(ValueError):
        load_store('SW', mem, 0, None)

    with pytest.raises(ValueError):
        load_store('SB', mem, 0, None)

    with pytest.raises(ValueError):
        load_store('SH', mem, 0, None)


def test_unsupported_memory_op_raises():
    mem = Memory(size=8)
    with pytest.raises(ValueError):
        load_store('FOO', mem, 0)
