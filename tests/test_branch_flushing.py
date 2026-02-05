"""Tests for branch flushing in the pipeline."""

from tests.util import assemble
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline


def test_branch_taken_flushes_pipeline():
    """Test that a taken branch flushes the pipeline and redirects PC.
    
    Program:
        ADDI $1, $0, 5       # $1 = 5
        BEQ $1, $1, target   # Branch is TAKEN (jump to target)
        ADDI $2, $0, 100     # Should NOT execute (flushed)
    target:
        ADDI $3, $0, 42      # $3 = 42 (executed after flush)
    """
    src = 'ADDI $1, $0, 5\nBEQ $1, $1, target\nADDI $2, $0, 100\ntarget: ADDI $3, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    # Load machine code into memory at 0, 4, 8, 12
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    # Run enough cycles for the branch to be detected and flushed
    for _ in range(15):
        pipeline.step(cpu)
    
    # Expected: $1 = 5, $3 = 42, $2 should be 0 (never executed)
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(3) == 42, f"Expected $3=42, got {cpu.registers.read(3)}"
    assert cpu.registers.read(2) == 0, f"Expected $2=0 (never executed), got {cpu.registers.read(2)}"


def test_branch_not_taken_no_flush():
    """Test that a branch not taken does NOT flush the pipeline.
    
    Program:
        ADDI $1, $0, 5       # $1 = 5
        ADDI $2, $0, 10      # $2 = 10
        BEQ $1, $2, target   # Branch is NOT TAKEN (fall through)
        ADDI $3, $0, 42      # $3 = 42 (executed normally)
        ADDI $4, $0, 99      # $4 = 99 (also executed, no flush)
    target:
        NOP
    """
    src = 'ADDI $1, $0, 5\nADDI $2, $0, 10\nBEQ $1, $2, target\nADDI $3, $0, 42\nADDI $4, $0, 99\ntarget: ADDI $5, $0, 1'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    # Run enough cycles for all instructions to complete
    for _ in range(20):
        pipeline.step(cpu)
    
    # Expected: all instructions execute since branch is not taken
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 10, f"Expected $2=10, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 42, f"Expected $3=42, got {cpu.registers.read(3)}"
    assert cpu.registers.read(4) == 99, f"Expected $4=99, got {cpu.registers.read(4)}"
    assert cpu.registers.read(5) == 1, f"Expected $5=1, got {cpu.registers.read(5)}"


def test_unconditional_jump_j():
    """Test that J (unconditional jump) always flushes and redirects.
    
    Program:
        J target             # Jump to target
        ADDI $1, $0, 100     # Should NOT execute (flushed)
    target:
        ADDI $2, $0, 42      # $2 = 42 (executed)
    """
    src = 'J target\nADDI $1, $0, 100\ntarget: ADDI $2, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    # Run enough cycles
    for _ in range(15):
        pipeline.step(cpu)
    
    # Expected: $1 = 0 (never executed), $2 = 42 (executed)
    assert cpu.registers.read(1) == 0, f"Expected $1=0 (never executed), got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 42, f"Expected $2=42, got {cpu.registers.read(2)}"


def test_bne_branch_taken():
    """Test BNE (branch not equal) when branch is taken.
    
    Program:
        ADDI $1, $0, 5       # $1 = 5
        BNE $1, $0, target   # $1 != $0, so branch TAKEN
        ADDI $2, $0, 100     # Should NOT execute
    target:
        ADDI $3, $0, 42      # $3 = 42
    """
    src = 'ADDI $1, $0, 5\nBNE $1, $0, target\nADDI $2, $0, 100\ntarget: ADDI $3, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(15):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 0, f"Expected $2=0 (never executed), got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 42, f"Expected $3=42, got {cpu.registers.read(3)}"




def test_blez_branch_taken():
    """Test BLEZ (branch if less than or equal to zero).
    
    Program:
        ADDI $1, $0, -5      # $1 = -5 (< 0)
        BLEZ $1, target      # $1 <= 0, so branch TAKEN
        ADDI $2, $0, 100     # Should NOT execute
    target:
        ADDI $3, $0, 42      # $3 = 42
    """
    src = 'ADDI $1, $0, -5\nBLEZ $1, target\nADDI $2, $0, 100\ntarget: ADDI $3, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(15):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == -5, f"Expected $1=-5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 0, f"Expected $2=0 (never executed), got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 42, f"Expected $3=42, got {cpu.registers.read(3)}"


def test_blez_branch_not_taken():
    """Test BLEZ when branch is NOT taken.
    
    Program:
        ADDI $1, $0, 5       # $1 = 5 (> 0)
        BLEZ $1, target      # $1 <= 0? NO, so fall through
        ADDI $2, $0, 42      # $2 = 42 (executed)
    target:
        ADDI $3, $0, 99      # $3 = 99 (also executed)
    """
    src = 'ADDI $1, $0, 5\nBLEZ $1, target\nADDI $2, $0, 42\ntarget: ADDI $3, $0, 99'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(15):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 42, f"Expected $2=42, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 99, f"Expected $3=99, got {cpu.registers.read(3)}"


def test_bgtz_branch_taken():
    """Test BGTZ (branch if greater than zero).
    
    Program:
        ADDI $1, $0, 10      # $1 = 10 (> 0)
        BGTZ $1, target      # $1 > 0, so branch TAKEN
        ADDI $2, $0, 100     # Should NOT execute
    target:
        ADDI $3, $0, 42      # $3 = 42
    """
    src = 'ADDI $1, $0, 10\nBGTZ $1, target\nADDI $2, $0, 100\ntarget: ADDI $3, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(15):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 10, f"Expected $1=10, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 0, f"Expected $2=0 (never executed), got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 42, f"Expected $3=42, got {cpu.registers.read(3)}"


def test_blt_branch_taken():
    """Test BLT (branch if less than).
    
    Program:
        ADDI $1, $0, 5       # $1 = 5
        ADDI $2, $0, 10      # $2 = 10
        BLT $1, $2, target   # 5 < 10, so branch TAKEN
        ADDI $3, $0, 100     # Should NOT execute
    target:
        ADDI $4, $0, 42      # $4 = 42
    """
    src = 'ADDI $1, $0, 5\nADDI $2, $0, 10\nBLT $1, $2, target\nADDI $3, $0, 100\ntarget: ADDI $4, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(20):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 10, f"Expected $2=10, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 0, f"Expected $3=0 (never executed), got {cpu.registers.read(3)}"
    assert cpu.registers.read(4) == 42, f"Expected $4=42, got {cpu.registers.read(4)}"


def test_bge_branch_taken():
    """Test BGE (branch if greater than or equal).
    
    Program:
        ADDI $1, $0, 10      # $1 = 10
        ADDI $2, $0, 5       # $2 = 5
        BGE $1, $2, target   # 10 >= 5, so branch TAKEN
        ADDI $3, $0, 100     # Should NOT execute
    target:
        ADDI $4, $0, 42      # $4 = 42
    """
    src = 'ADDI $1, $0, 10\nADDI $2, $0, 5\nBGE $1, $2, target\nADDI $3, $0, 100\ntarget: ADDI $4, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(20):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 10, f"Expected $1=10, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 5, f"Expected $2=5, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 0, f"Expected $3=0 (never executed), got {cpu.registers.read(3)}"
    assert cpu.registers.read(4) == 42, f"Expected $4=42, got {cpu.registers.read(4)}"


def test_ble_branch_taken():
    """Test BLE (branch if less than or equal).
    
    Program:
        ADDI $1, $0, 5       # $1 = 5
        ADDI $2, $0, 10      # $2 = 10
        BLE $1, $2, target   # 5 <= 10, so branch TAKEN
        ADDI $3, $0, 100     # Should NOT execute
    target:
        ADDI $4, $0, 42      # $4 = 42
    """
    src = 'ADDI $1, $0, 5\nADDI $2, $0, 10\nBLE $1, $2, target\nADDI $3, $0, 100\ntarget: ADDI $4, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(20):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 5, f"Expected $1=5, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 10, f"Expected $2=10, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 0, f"Expected $3=0 (never executed), got {cpu.registers.read(3)}"
    assert cpu.registers.read(4) == 42, f"Expected $4=42, got {cpu.registers.read(4)}"


def test_bgt_branch_taken():
    """Test BGT (branch if greater than).
    
    Program:
        ADDI $1, $0, 15      # $1 = 15
        ADDI $2, $0, 10      # $2 = 10
        BGT $1, $2, target   # 15 > 10, so branch TAKEN
        ADDI $3, $0, 100     # Should NOT execute
    target:
        ADDI $4, $0, 42      # $4 = 42
    """
    src = 'ADDI $1, $0, 15\nADDI $2, $0, 10\nBGT $1, $2, target\nADDI $3, $0, 100\ntarget: ADDI $4, $0, 42'
    machine = assemble(src)
    
    cpu = CPUstate()
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)
    
    pipeline = Pipeline()
    
    for _ in range(20):
        pipeline.step(cpu)
    
    assert cpu.registers.read(1) == 15, f"Expected $1=15, got {cpu.registers.read(1)}"
    assert cpu.registers.read(2) == 10, f"Expected $2=10, got {cpu.registers.read(2)}"
    assert cpu.registers.read(3) == 0, f"Expected $3=0 (never executed), got {cpu.registers.read(3)}"
    assert cpu.registers.read(4) == 42, f"Expected $4=42, got {cpu.registers.read(4)}"


# Note: Extended branch type support for labels was added to the assembler.
# Now BLT, BGE, BLE, BGT, BLEZ, and BGTZ can all be tested with labels.
