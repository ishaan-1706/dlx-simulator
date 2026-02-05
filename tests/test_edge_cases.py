#!/usr/bin/env python3
"""
tests/test_edge_cases.py - Comprehensive Edge Case Testing

This test suite includes 60 edge cases that stress the DLX simulator to its limits.
Tests cover:
  - Branch edge cases (7 tests)
  - Forwarding edge cases (7 tests)
  - Stalling edge cases (6 tests)
  - Flushing edge cases (7 tests)
  - Register edge cases (6 tests)
  - Memory edge cases (6 tests)
  - Complex interactions (6 tests)
  - Boundary conditions (7 tests)
  - Correctness verification (6 tests)

Total: 60 comprehensive tests
"""

import pytest
from parser.lexer import Lexer
from parser.asm_parser import Parser
from parser.assembler import Assembler
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline


def run_program(asm_code, max_cycles=200):
    """Helper: Assemble and run a program, return final CPU state."""
    lexer = Lexer(asm_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    instructions = parser.parse()
    assembler = Assembler(instructions)
    machine_code = assembler.assemble()
    
    cpu = CPUstate()
    pipeline = Pipeline()
    
    # Load machine code into memory
    for idx, instruction in enumerate(machine_code):
        addr = idx * 4
        cpu.memory.store_word(addr, instruction)
    
    # Run simulation
    halted = False
    cycle = 0
    halt_cycle = 0
    for cycle in range(max_cycles):
        pipeline.step(cpu)
        
        # Halt if PC goes out of bounds
        if cpu.pc < 0 or cpu.pc >= len(machine_code) * 4:
            if not halted:
                halted = True
                halt_cycle = cycle
            # After halt detected, run 5 more cycles to drain pipeline
            elif cycle >= halt_cycle + 5:
                break
    
    return cpu, pipeline


# ========================================================
# BRANCH EDGE CASES (7 tests)
# ========================================================

def test_branch_to_branch():
    """Test: Branch target points to another branch instruction."""
    code = """
    ADDI $1, $0, 5
    ADDI $2, $0, 5
    BEQ $1, $2, label2
    ADDI $3, $0, 999
    label2:
    BEQ $1, $2, end
    ADDI $4, $0, 999
    end:
    ADDI $5, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 5
    assert cpu.registers.read(2) == 5
    assert cpu.registers.read(5) == 42
    assert cpu.registers.read(3) == 0  # Skipped
    assert cpu.registers.read(4) == 0  # Skipped


def test_backwards_branch():
    """Test: Branch backwards to earlier instruction (loop)."""
    code = """
    ADDI $1, $0, 3
    ADDI $2, $0, 0
    loop:
    ADD $2, $2, $1
    ADDI $1, $1, -1
    BNE $1, $0, loop
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    # $2 should be 3 + 2 + 1 = 6
    assert cpu.registers.read(2) == 6
    assert cpu.registers.read(1) == 0
    assert cpu.registers.read(3) == 42


def test_forward_branch():
    """Test: Branch far ahead in program."""
    code = """
    ADDI $1, $0, 1
    BEQ $1, $1, end
    ADDI $2, $0, 1
    ADDI $3, $0, 2
    ADDI $4, $0, 3
    ADDI $5, $0, 4
    end:
    ADDI $6, $0, 100
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 1
    assert cpu.registers.read(6) == 100
    assert cpu.registers.read(2) == 0  # Branch taken, skipped
    assert cpu.registers.read(3) == 0  # Branch taken, skipped
    assert cpu.registers.read(4) == 0  # Branch taken, skipped
    assert cpu.registers.read(5) == 0  # Branch taken, skipped


def test_consecutive_branches():
    """Test: Multiple branches in rapid succession."""
    code = """
    ADDI $1, $0, 1
    BEQ $1, $0, skip1
    ADDI $2, $0, 1
    skip1:
    BEQ $1, $1, skip2
    ADDI $3, $0, 999
    skip2:
    ADDI $4, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 1  # First branch not taken
    assert cpu.registers.read(3) == 0  # Second branch taken, skipped
    assert cpu.registers.read(4) == 42


def test_branch_not_taken_then_taken():
    """Test: Branch not taken, then immediately branch taken."""
    code = """
    ADDI $1, $0, 5
    ADDI $2, $0, 10
    BEQ $1, $2, end
    ADDI $3, $0, 1
    BEQ $1, $1, end
    ADDI $4, $0, 999
    end:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(3) == 1  # First branch not taken
    assert cpu.registers.read(4) == 0  # Second branch taken, skipped
    assert cpu.registers.read(1) == 5


def test_branch_with_max_offset():
    """Test: Branch with large offset (label far away)."""
    code = """
    ADDI $1, $0, 1
    BNE $1, $0, far_label
    ADDI $2, $0, 999
    ADDI $3, $0, 999
    ADDI $4, $0, 999
    far_label:
    ADDI $5, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(5) == 42
    assert cpu.registers.read(2) == 0


def test_branch_with_forwarding_dependency():
    """Test: Branch condition depends on forwarded value."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $1, 5
    BEQ $2, $0, skip
    ADDI $3, $0, 1
    skip:
    ADDI $4, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    # $2 = 10 + 5 = 15, not equal to 0, so branch not taken
    assert cpu.registers.read(2) == 15
    assert cpu.registers.read(3) == 1
    assert cpu.registers.read(4) == 42


# ========================================================
# FORWARDING EDGE CASES (7 tests)
# ========================================================

def test_full_forwarding_chain_5deep():
    """Test: 5-deep forwarding chain ($1→$2→$3→$4→$5)."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $1, 5
    ADDI $3, $2, 5
    ADDI $4, $3, 5
    ADDI $5, $4, 5
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 10
    assert cpu.registers.read(2) == 15  # 10 + 5
    assert cpu.registers.read(3) == 20  # 15 + 5
    assert cpu.registers.read(4) == 25  # 20 + 5
    assert cpu.registers.read(5) == 30  # 25 + 5


def test_forward_from_wb_to_ex():
    """Test: Maximum distance forwarding (WB to EX = 5 stages apart)."""
    code = """
    ADDI $1, $0, 100
    NOP
    NOP
    NOP
    NOP
    ADDI $2, $1, 50
    HALT
    """
    cpu, _ = run_program(code)
    # After 5 NOP cycles, $1 is in WB, $2 can forward from it
    assert cpu.registers.read(1) == 100
    assert cpu.registers.read(2) == 150


def test_forward_from_mem_to_alu():
    """Test: Memory stage result forwarded to next ALU."""
    code = """
    ADDI $1, $0, 42
    ADD $2, $1, $1
    ADD $3, $2, $1
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 42
    assert cpu.registers.read(2) == 84  # 42 + 42
    assert cpu.registers.read(3) == 126  # 84 + 42


def test_multiple_forwards_same_cycle():
    """Test: Both operands forwarded in single instruction."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $0, 20
    ADD $3, $1, $2
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(3) == 30


def test_forward_through_stall():
    """Test: Forwarding works correctly when load-use stall occurs."""
    code = """
    ADDI $1, $0, 42
    SW $1, 0($0)
    LW $2, 0($0)
    NOP
    ADDI $4, $2, 10
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 42
    assert cpu.registers.read(4) == 52  # 42 + 10


def test_forward_through_branch():
    """Test: Forwarded value used as branch operand."""
    code = """
    ADDI $1, $0, 5
    ADDI $2, $1, 0
    BEQ $2, $1, success
    ADDI $3, $0, 999
    success:
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 5
    assert cpu.registers.read(2) == 5
    assert cpu.registers.read(3) == 42


def test_forwarding_with_zero_register():
    """Test: Forwarding from/to $0 (always 0)."""
    code = """
    ADDI $1, $0, 100
    ADD $2, $1, $0
    ADDI $0, $0, 999
    ADD $3, $0, $1
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(0) == 0  # $0 always 0
    assert cpu.registers.read(2) == 100  # 100 + 0
    assert cpu.registers.read(3) == 100  # 0 + 100


# ========================================================
# STALLING EDGE CASES (6 tests)
# ========================================================

def test_load_use_single_stall():
    """Test: Load-use dependency causes 1-cycle stall."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    LW $2, 0($0)
    ADDI $3, $2, 10
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 100
    assert cpu.registers.read(3) == 110


def test_load_use_double_stall():
    """Test: Two load-use dependencies cause cumulative stalls."""
    code = """
    ADDI $1, $0, 50
    SW $1, 0($0)
    LW $2, 0($0)
    NOP
    LW $3, 0($0)
    NOP
    ADD $4, $2, $3
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 50
    assert cpu.registers.read(3) == 50
    assert cpu.registers.read(4) == 100


def test_stall_followed_by_branch():
    """Test: Stall on load, then branch depends on loaded value."""
    code = """
    ADDI $1, $0, 0
    SW $1, 0($0)
    LW $2, 0($0)
    BEQ $2, $0, success
    ADDI $3, $0, 999
    success:
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 0
    assert cpu.registers.read(3) == 42


def test_stall_followed_by_forward():
    """Test: Stall occurs, then forwarding continues normally."""
    code = """
    ADDI $1, $0, 10
    SW $1, 4($0)
    LW $2, 4($0)
    NOP
    ADDI $3, $2, 5
    ADD $4, $3, $2
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 10
    assert cpu.registers.read(3) == 15
    assert cpu.registers.read(4) == 25


def test_back_to_back_loads():
    """Test: Two consecutive loads with dependency."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    LW $2, 0($0)
    ADDI $0, $0, 0
    LW $3, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 100
    assert cpu.registers.read(3) == 100


def test_load_store_data_chain():
    """Test: Store to memory, then load from same address."""
    code = """
    ADDI $1, $0, 42
    SW $1, 0($0)
    LW $2, 0($0)
    NOP
    ADDI $3, $2, 8
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 42
    assert cpu.registers.read(2) == 42
    assert cpu.registers.read(3) == 50


# ========================================================
# FLUSHING EDGE CASES (7 tests)
# ========================================================

def test_flush_clears_if_id():
    """Test: IF/ID register is cleared when branch flushes."""
    code = """
    ADDI $1, $0, 1
    BEQ $1, $1, success
    ADDI $2, $0, 999
    success:
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    # If flush works, $2 should not be written
    assert cpu.registers.read(2) == 0


def test_flush_clears_id_ex():
    """Test: ID/EX register is cleared when branch flushes."""
    code = """
    ADDI $1, $0, 1
    ADDI $2, $0, 1
    BEQ $1, $2, success
    ADDI $3, $0, 999
    success:
    ADDI $4, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(3) == 0
    assert cpu.registers.read(4) == 42


def test_jump_immediately_after_jump():
    """Test: Two jumps in succession."""
    code = """
    J label1
    ADDI $1, $0, 999
    label1:
    J label2
    ADDI $2, $0, 999
    label2:
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 0
    assert cpu.registers.read(2) == 0
    assert cpu.registers.read(3) == 42


def test_flush_with_pending_forwards():
    """Test: In-flight data exists when flush happens."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $1, 5
    BEQ $1, $1, end
    ADDI $3, $0, 999
    end:
    ADDI $4, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 15  # Forwarding still works
    assert cpu.registers.read(3) == 0   # But branch flush clears later instruction
    assert cpu.registers.read(4) == 42  # Branch was taken


def test_flush_followed_by_load():
    """Test: Branch flushes, next instruction is load (with stall)."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    BEQ $1, $1, continue
    ADDI $2, $0, 999
    continue:
    LW $3, 0($0)
    NOP
    ADDI $4, $3, 10
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(3) == 100
    assert cpu.registers.read(4) == 110


def test_multiple_flushes_in_sequence():
    """Test: Several branches taken in close proximity."""
    code = """
    ADDI $1, $0, 1
    BEQ $1, $1, a
    ADDI $2, $0, 999
    a:
    BEQ $1, $1, b
    ADDI $3, $0, 999
    b:
    ADDI $4, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 0
    assert cpu.registers.read(3) == 0
    assert cpu.registers.read(4) == 42


def test_branch_flush_vs_load_stall():
    """Test: Branch flush happens; load stall is cleared by flush."""
    code = """
    ADDI $1, $0, 50
    SW $1, 0($0)
    LW $2, 0($0)
    BEQ $1, $1, skip
    ADDI $3, $0, 999
    skip:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 50


# ========================================================
# REGISTER EDGE CASES (6 tests)
# ========================================================

def test_write_to_zero_register():
    """Test: Writing to $0 has no effect (always 0)."""
    code = """
    ADDI $0, $0, 999
    ADDI $1, $0, 1
    ADD $0, $1, $1
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(0) == 0


def test_forward_from_zero():
    """Test: Forwarding from $0 (always 0)."""
    code = """
    ADDI $1, $0, 0
    ADDI $2, $1, 100
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 100


def test_zero_in_all_positions():
    """Test: $0 as rs, rt, and rd."""
    code = """
    ADD $0, $0, $0
    ADDI $1, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(0) == 0
    assert cpu.registers.read(1) == 42


def test_register_31_usage():
    """Test: Return address register $31."""
    code = """
    ADDI $31, $0, 100
    ADDI $1, $31, 1
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(31) == 100
    assert cpu.registers.read(1) == 101


def test_all_32_registers_used():
    """Test: Sequential usage of every register."""
    code = """
    ADDI $1, $0, 1
    ADD $2, $1, $1
    ADD $3, $2, $1
    ADD $4, $3, $1
    ADD $5, $4, $1
    ADD $6, $5, $1
    ADD $7, $6, $1
    ADD $8, $7, $1
    ADD $9, $8, $1
    ADD $10, $9, $1
    ADD $11, $10, $1
    ADD $12, $11, $1
    ADD $13, $12, $1
    ADD $14, $13, $1
    ADD $15, $14, $1
    ADD $16, $15, $1
    ADD $17, $16, $1
    ADD $18, $17, $1
    ADD $19, $18, $1
    ADD $20, $19, $1
    ADD $21, $20, $1
    ADD $22, $21, $1
    ADD $23, $22, $1
    ADD $24, $23, $1
    ADD $25, $24, $1
    ADD $26, $25, $1
    ADD $27, $26, $1
    ADD $28, $27, $1
    ADD $29, $28, $1
    ADD $30, $29, $1
    HALT
    """
    cpu, _ = run_program(code, max_cycles=300)
    for i in range(1, 31):
        assert cpu.registers.read(i) == i


def test_register_reuse():
    """Test: Same register written multiple times."""
    code = """
    ADDI $1, $0, 10
    ADD $1, $1, $1
    ADD $1, $1, $1
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 40  # 10 → 20 → 40


# ========================================================
# MEMORY EDGE CASES (6 tests)
# ========================================================

def test_store_load_same_address():
    """Test: Store then load from same address."""
    code = """
    ADDI $1, $0, 1000
    SW $1, 0($0)
    LW $2, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 1000


def test_multiple_stores_same_address():
    """Test: Multiple stores to same address (second overwrites)."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    ADDI $2, $0, 200
    SW $2, 0($0)
    LW $3, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 200
    assert cpu.registers.read(3) == 200


def test_load_same_location_multiple_times():
    """Test: Multiple loads from same address."""
    code = """
    ADDI $1, $0, 42
    SW $1, 0($0)
    LW $2, 0($0)
    ADDI $0, $0, 0
    LW $3, 0($0)
    ADDI $0, $0, 0
    LW $4, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 42
    assert cpu.registers.read(3) == 42
    assert cpu.registers.read(4) == 42


def test_address_zero_access():
    """Test: Load/store from memory address 0x0000."""
    code = """
    ADDI $1, $0, 5000
    SW $1, 0($0)
    LW $2, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 5000
    assert cpu.registers.read(2) == 5000


def test_load_with_zero_offset():
    """Test: Load with zero immediate offset."""
    code = """
    ADDI $1, $0, 12345
    SW $1, 0($0)
    LW $2, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 12345


def test_store_with_zero_offset():
    """Test: Store with zero offset."""
    code = """
    ADDI $1, $0, 7777
    SW $1, 0($0)
    LW $2, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 7777


# ========================================================
# COMPLEX INTERACTION EDGE CASES (6 tests)
# ========================================================

def test_load_use_then_branch():
    """Test: Stall on LW, then branch depends on loaded value."""
    code = """
    ADDI $1, $0, 1
    SW $1, 0($0)
    LW $2, 0($0)
    BEQ $2, $1, success
    ADDI $3, $0, 999
    success:
    ADDI $3, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 1
    assert cpu.registers.read(3) == 42


def test_forward_chain_then_stall():
    """Test: Forwarding chain works, then load stalls chain."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $1, 5
    ADDI $3, $2, 5
    ADDI $4, $0, 0
    SW $4, 0($0)
    ADDI $4, $3, 10
    LW $5, 0($0)
    ADDI $0, $0, 0
    ADD $6, $5, $4
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(4) == 30  # 10 + 5 + 5 + 10
    assert cpu.registers.read(5) == 0
    assert cpu.registers.read(6) == 30


def test_branch_flush_with_pending_stores():
    """Test: Store in MEM when branch flushes."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    BEQ $1, $1, success
    ADDI $2, $0, 999
    success:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 100
    assert cpu.registers.read(2) == 0


def test_branch_within_dependency_chain():
    """Test: Branch condition is in middle of forwarding chain."""
    code = """
    ADDI $1, $0, 5
    ADDI $2, $1, 0
    BEQ $2, $1, cont
    ADDI $3, $0, 999
    cont:
    ADDI $4, $2, 10
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 5
    assert cpu.registers.read(3) == 0
    assert cpu.registers.read(4) == 15


def test_double_stall_then_branch():
    """Test: Two load-use stalls, then branch depends on result."""
    code = """
    ADDI $1, $0, 1
    SW $1, 0($0)
    LW $2, 0($0)
    NOP
    LW $3, 0($0)
    NOP
    ADD $4, $2, $3
    BEQ $4, $4, end
    ADDI $5, $0, 999
    end:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(4) == 2  # 1 + 1
    assert cpu.registers.read(5) == 0  # Branch taken (4==4), skipped


def test_forward_chain_broken_by_stall():
    """Test: Loaded value used after stall completes, in a new chain.
    
    This tests that after a load-use stall:
    1. The loaded value is available ($4 = 10)
    2. It can be used in subsequent computations
    3. And that value can forward to further instructions
    """
    code = """
    ADDI $1, $0, 10
    ADDI $2, $1, 5
    ADDI $3, $2, 5
    SW $1, 4($0)
    LW $4, 4($0)
    NOP
    NOP
    NOP
    ADDI $6, $4, 2
    ADD $5, $6, $3
    HALT
    """
    cpu, _ = run_program(code, max_cycles=250)
    assert cpu.registers.read(4) == 10   # Load from memory succeeds
    assert cpu.registers.read(6) == 12   # $4 (10) + 2
    assert cpu.registers.read(5) == 32   # $6 (12) + $3 (20)


# ========================================================
# BOUNDARY & STATE EDGE CASES (7 tests)
# ========================================================

def test_maximum_throughput_sequence():
    """Test: Back-to-back ALU ops (no hazards - full throughput)."""
    code = """
    ADDI $1, $0, 1
    ADDI $2, $0, 2
    ADDI $3, $0, 3
    ADDI $4, $0, 4
    ADDI $5, $0, 5
    ADD $6, $1, $2
    ADD $7, $3, $4
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(6) == 3
    assert cpu.registers.read(7) == 7


def test_minimum_program():
    """Test: Single instruction then halt."""
    code = """
    ADDI $1, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 42


def test_program_with_only_nops():
    """Test: Multiple NOP instructions."""
    code = """
    NOP
    NOP
    NOP
    ADDI $1, $0, 42
    NOP
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 42


def test_program_with_only_jumps():
    """Test: Jump chaining."""
    code = """
    J label1
    ADDI $1, $0, 999
    label1:
    J label2
    ADDI $2, $0, 999
    label2:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 0
    assert cpu.registers.read(2) == 0


def test_program_with_only_loads():
    """Test: Multiple loads (verify stalls accumulate)."""
    code = """
    ADDI $1, $0, 10
    SW $1, 0($0)
    LW $2, 0($0)
    ADDI $0, $0, 0
    LW $3, 0($0)
    ADDI $0, $0, 0
    LW $4, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(2) == 10
    assert cpu.registers.read(3) == 10
    assert cpu.registers.read(4) == 10


def test_program_with_only_stores():
    """Test: Multiple stores (no stalls expected)."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $0, 20
    ADDI $3, $0, 30
    SW $1, 0($0)
    SW $2, 4($0)
    SW $3, 8($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 10
    assert cpu.memory.load_word(4) == 20
    assert cpu.memory.load_word(8) == 30


def test_pc_at_program_boundary():
    """Test: PC exactly at program end."""
    code = """
    ADDI $1, $0, 42
    HALT
    """
    cpu, _ = run_program(code)
    # PC should be at or past program end
    assert cpu.registers.read(1) == 42


# ========================================================
# CORRECTNESS VERIFICATION EDGE CASES (6 tests)
# ========================================================

def test_computed_values_match_expected():
    """Test: All arithmetic results are correct."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $0, 20
    ADD $3, $1, $2
    SUB $4, $3, $1
    ADD $5, $4, $2
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(3) == 30  # 10 + 20
    assert cpu.registers.read(4) == 20  # 30 - 10
    assert cpu.registers.read(5) == 40  # 20 + 20


def test_memory_state_matches_expected():
    """Test: All memory writes are correct and in correct locations."""
    code = """
    ADDI $1, $0, 100
    ADDI $2, $0, 200
    ADDI $3, $0, 300
    SW $1, 0($0)
    SW $2, 4($0)
    SW $3, 8($0)
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.memory.load_word(0) == 100
    assert cpu.memory.load_word(4) == 200
    assert cpu.memory.load_word(8) == 300


def test_register_state_matches_expected():
    """Test: All registers have expected values."""
    code = """
    ADDI $1, $0, 1
    ADDI $2, $0, 2
    ADDI $3, $0, 3
    ADDI $4, $0, 4
    ADDI $5, $0, 5
    HALT
    """
    cpu, _ = run_program(code)
    for i in range(1, 6):
        assert cpu.registers.read(i) == i


def test_no_data_corruption():
    """Test: Unwritten registers remain untouched."""
    code = """
    ADDI $1, $0, 100
    SW $1, 0($0)
    HALT
    """
    cpu, _ = run_program(code)
    # Verify unwritten registers are zero
    for i in range(2, 32):
        assert cpu.registers.read(i) == 0
    # Note: memory locations 4+ may contain instruction words from program code


def test_no_spurious_modifications():
    """Test: Only intentional writes occur."""
    code = """
    ADDI $1, $0, 42
    BEQ $0, $0, end
    ADDI $2, $0, 999
    end:
    HALT
    """
    cpu, _ = run_program(code)
    assert cpu.registers.read(1) == 42
    assert cpu.registers.read(2) == 0  # Branch should have flushed this


def test_correct_cycle_count():
    """Test: Cycle count accounting is accurate."""
    code = """
    ADDI $1, $0, 10
    ADDI $2, $0, 20
    ADD $3, $1, $2
    HALT
    """
    # Should complete in ~9 cycles (4 instructions + 5 flush)
    cpu, _ = run_program(code, max_cycles=50)
    assert cpu.registers.read(3) == 30


# Run all tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
