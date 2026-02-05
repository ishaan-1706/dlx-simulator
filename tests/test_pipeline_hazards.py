# tests/test_pipeline_hazards.py
"""Test pipeline hazard detection, stalling, and forwarding."""
import pytest
from tests.util import assemble
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline
from pipeline.hazards import detect_load_use_hazard
from pipeline.pipeline_regs import ID_EX, EX_MEM


def test_load_use_hazard_detection():
    """Test that detect_load_use_hazard identifies true load-use conflicts."""
    # Create an ID/EX that reads $1 and $2
    id_ex = ID_EX()
    id_ex.rs = 1
    id_ex.rt = 2
    id_ex.op = "ADD"

    # Case 1: EX/MEM loads into $1 -> hazard
    ex_mem = EX_MEM()
    ex_mem.mem_op = "LW"
    ex_mem.rd = 1
    assert detect_load_use_hazard(id_ex, ex_mem) is True

    # Case 2: EX/MEM loads into $2 -> hazard
    ex_mem.rd = 2
    assert detect_load_use_hazard(id_ex, ex_mem) is True

    # Case 3: EX/MEM loads into $3 -> no hazard
    ex_mem.rd = 3
    assert detect_load_use_hazard(id_ex, ex_mem) is False

    # Case 4: EX/MEM is not a load (e.g., ADD) -> no hazard
    ex_mem.mem_op = "ADD"
    ex_mem.rd = 1
    assert detect_load_use_hazard(id_ex, ex_mem) is False

    # Case 5: Load into $0 is ignored -> no hazard
    ex_mem.mem_op = "LW"
    ex_mem.rd = 0
    assert detect_load_use_hazard(id_ex, ex_mem) is False


def test_pipeline_stall_on_load_use():
    """Test that the pipeline stalls on load-use hazard.

    Program:
        LW $1, 0($0)     # Load word from 0 into $1
        ADD $2, $1, $0   # Use loaded $1 immediately (hazard!)
        ADDI $3, $0, 5

    Without stall, ADD would try to use $1 in EX while it's still in MEM.
    With stall, ADD waits one cycle for $1 to be loaded.
    """
    # Pre-populate memory: store 42 at address 0
    src = 'LW $1, 0($0)\nADD $2, $1, $0\nADDI $3, $0, 5'
    machine = assemble(src)

    cpu = CPUstate()
    # Store 42 at memory address 0
    cpu.memory.store_word(0, 42)

    # Load machine code into memory at 0, 4, 8
    for i, word in enumerate(machine):
        cpu.memory.store_word(4 + i * 4, word)

    # Set PC to 4 (where our program starts)
    cpu.pc = 4

    pipeline = Pipeline()

    # Run enough cycles: 3 instructions + stall + pipeline depth
    # Expected timeline:
    # Cycle 0: IF[LW]
    # Cycle 1: ID[LW], IF[ADD]
    # Cycle 2: EX[LW], ID[ADD], IF[ADDI]  <- hazard detected, stall IF/ID and ID/EX
    # Cycle 3: MEM[LW], ID[ADD] (still), IF[ADDI] (still)
    # Cycle 4: WB[LW]=$1=42, EX[ADD]=$2=$1+$0=42, ID[ADDI]
    # Cycle 5: EX[ADDI]=$3=5, WB[ADD]=$2=42
    # Cycle 6: MEM[ADDI]
    # Cycle 7: WB[ADDI]=$3=5
    for _ in range(12):
        pipeline.step(cpu)

    assert cpu.registers.read(1) == 42, "LW should load 42 into $1"
    assert cpu.registers.read(2) == 42, "ADD should compute $1 + $0 = 42 + 0 = 42"
    assert cpu.registers.read(3) == 5, "ADDI should set $3 = 5"


def test_pipeline_stall_on_multiple_load_uses():
    """Test pipeline with multiple sequential load-use patterns."""
    # Program:
    #   SW $0, 0($0)        # Clear memory at 0
    #   ADDI $1, $0, 100
    #   SW $1, 0($0)        # Store 100 at address 0
    #   LW $2, 0($0)        # Load into $2 (value 100)
    #   ADD $3, $2, $2      # Use $2 immediately (stall!)
    #   ADDI $4, $0, 50
    
    src = 'ADDI $1, $0, 100\nSW $1, 0($0)\nLW $2, 0($0)\nADD $3, $2, $2\nADDI $4, $0, 50'
    machine = assemble(src)

    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)

    pipeline = Pipeline()

    # Run for enough cycles to complete all instructions
    for _ in range(20):
        pipeline.step(cpu)

    assert cpu.registers.read(1) == 100
    assert cpu.memory.load_word(0) == 100
    assert cpu.registers.read(2) == 100
    assert cpu.registers.read(3) == 200, "ADD $3, $2, $2 should compute $2 + $2 = 100 + 100 = 200"
    assert cpu.registers.read(4) == 50


def test_pipeline_forwarding_without_stall():
    """Test that non-load-producing instructions forward without stalling.

    Program:
        ADDI $1, $0, 10
        ADD $2, $1, $0      # Use $1, but it's from ADD not LW -> forwarding works
        ADDI $3, $0, 5

    The ADDI produces alu_result which is forwarded to ADD, no stall needed.
    """
    src = 'ADDI $1, $0, 10\nADD $2, $1, $0\nADDI $3, $0, 5'
    machine = assemble(src)

    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)

    pipeline = Pipeline()

    # Should complete without stalls; fewer cycles needed
    for _ in range(10):
        pipeline.step(cpu)

    assert cpu.registers.read(1) == 10
    assert cpu.registers.read(2) == 10
    assert cpu.registers.read(3) == 5
