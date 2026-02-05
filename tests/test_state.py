#tests/test_state.py
import pytest
from state.cpu_state import CPUstate

def test_register_read_write():
    cpu = CPUstate()

    # Write values into registers
    cpu.registers.write(1, 42)
    cpu.registers.write(2, 99)
    cpu.registers.write(0, 123)  # $0 should remain 0

    # Assertions
    assert cpu.registers.read(1) == 42
    assert cpu.registers.read(2) == 99
    assert cpu.registers.read(0) == 0  # $0 must always be 0

def test_memory_store_and_load():
    cpu = CPUstate()
    address = 100
    value = 0xDEADBEEF

    cpu.memory.store_word(address, value)
    loaded = cpu.memory.load_word(address)

    assert loaded == value

def test_pc_stepping():
    cpu = CPUstate()

    # Initial PC
    assert cpu.pc == 0

    # Step once
    cpu.step_pc()
    assert cpu.pc == 4

    # Step with custom offset
    cpu.step_pc(8)
    assert cpu.pc == 12