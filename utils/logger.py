#!/usr/bin/env python3
"""
utils/logger.py - Pipeline State Logging and Visualization

This module provides detailed cycle-by-cycle logging of the DLX pipeline execution.
It shows:
  1. Pipeline stage contents (IF, ID, EX, MEM, WB)
  2. Register changes (deltas only, for brevity)
  3. Memory operations (loads/stores)
  4. Hazard events (forwarding, stalling, branch flushing)
  5. Instruction flow through the pipeline

The logger is called from main.py when --verbose flag is used.
It queries the pipeline object and CPU state to extract information.

Example output:
  [Cycle 3] PC=0x0008
    IF:  ADDI $1, $0, 5     @ 0x0000
    ID:  ADD  $3, $1, $2
    EX:  ADDI $2, $0, 10    ALU: $0(0) + 10 = 10
    MEM: ADDI $1, $0, 5     Write: $1 ← 5
    WB:  (empty)
    Events: [FORWARD] ALU→ALU: $1 from EX to ID
"""

from decoder.decoder import decode


def get_instruction_mnemonic(instruction_word):
    """Extract mnemonic string from 32-bit instruction word.
    
    Args:
        instruction_word (int): 32-bit instruction
        
    Returns:
        str: Instruction mnemonic (e.g., 'ADDI', 'ADD', 'LW') or '(empty)' if 0
    """
    if instruction_word == 0:
        return "(nop)"
    
    try:
        decoded = decode(instruction_word)
        return decoded.op
    except:
        return f"(unknown 0x{instruction_word:08x})"


def format_operands(decoded_instr):
    """Format instruction operands for display.
    
    Args:
        decoded_instr: DecodedInstruction object from decoder
        
    Returns:
        str: Human-readable operands (e.g., '$1, $0, 5')
    """
    parts = []
    
    # Add destination register (for R-type and some I-type)
    if hasattr(decoded_instr, 'rd') and decoded_instr.rd is not None:
        if decoded_instr.op not in ('SW', 'SH', 'SB', 'BEQ', 'BNE', 'BLEZ', 'BGTZ', 
                                     'BLT', 'BGE', 'BLE', 'BGT', 'J', 'JAL', 'JR', 'JALR'):
            # For load/store and branches, rd isn't shown this way
            parts.append(f"${decoded_instr.rd}")
    
    # Add source registers
    if hasattr(decoded_instr, 'rs') and decoded_instr.rs is not None:
        if decoded_instr.op not in ('J', 'JAL'):  # J/JAL don't use rs
            parts.append(f"${decoded_instr.rs}")
    
    if hasattr(decoded_instr, 'rt') and decoded_instr.rt is not None:
        parts.append(f"${decoded_instr.rt}")
    
    # Add immediate or offset
    if hasattr(decoded_instr, 'imm') and decoded_instr.imm is not None:
        if decoded_instr.op in ('LW', 'SW', 'LB', 'SB', 'LH', 'SH', 'LBU', 'LHU'):
            # Format as offset($base)
            parts.append(f"{decoded_instr.imm}(${decoded_instr.rs})")
        else:
            parts.append(str(decoded_instr.imm))
    
    # Add address for jumps
    if hasattr(decoded_instr, 'address') and decoded_instr.address is not None:
        parts.append(f"0x{decoded_instr.address:x}")
    
    # Add shift amount for shift operations
    if hasattr(decoded_instr, 'shamt') and decoded_instr.shamt is not None:
        if decoded_instr.op in ('SLL', 'SRL', 'SRA'):
            parts.append(str(decoded_instr.shamt))
    
    return ', '.join(parts)


def print_pipeline_state(pipeline, cpu, cycle, prev_cpu_state=None, detailed=False):
    """Print detailed pipeline state for the current cycle.
    
    This is the main logging function called each cycle by main.py.
    
    Args:
        pipeline (Pipeline): Pipeline object with if_id, id_ex, ex_mem, mem_wb registers
        cpu (CPUstate): CPU state with registers, memory, PC
        cycle (int): Current cycle number (1-indexed)
        prev_cpu_state (CPUstate): Previous cycle's CPU state (for detecting changes)
        detailed (bool): If True, show ALU results and memory accesses
    
    The function outputs:
    1. Cycle number and current PC
    2. Each pipeline stage with instruction info
    3. Register changes (if prev_cpu_state provided)
    4. Hazard events
    """
    
    print(f"\n[Cycle {cycle:3d}] PC=0x{cpu.pc:04x}")
    
    # ========================================================
    # PIPELINE STAGES
    # ========================================================
    
    # IF Stage: Shows instruction being fetched (just PC)
    print(f"  IF:  Fetching @ 0x{cpu.pc:04x}")
    
    # ID Stage: Shows instruction being decoded
    if pipeline.if_id and pipeline.if_id.instr is not None:
        id_word = pipeline.if_id.instr
        if id_word != 0:  # Not a NOP
            id_mnem = get_instruction_mnemonic(id_word)
            try:
                id_decoded = decode(id_word, pipeline.if_id.pc)
                id_ops = format_operands(id_decoded)
                print(f"  ID:  {id_mnem:7s} {id_ops}")
            except:
                print(f"  ID:  {id_mnem:7s}")
        else:
            print(f"  ID:  (nop)")
    else:
        print(f"  ID:  (empty)")
    
    # EX Stage: Shows instruction in execution (decoded fields)
    if pipeline.id_ex and pipeline.id_ex.op is not None:
        ex_op = pipeline.id_ex.op
        # Build operands from stored fields
        operands = []
        if pipeline.id_ex.rd is not None:
            operands.append(f"${pipeline.id_ex.rd}")
        if pipeline.id_ex.rs is not None:
            operands.append(f"${pipeline.id_ex.rs}")
        if pipeline.id_ex.rt is not None:
            operands.append(f"${pipeline.id_ex.rt}")
        if pipeline.id_ex.imm is not None:
            operands.append(f"0x{pipeline.id_ex.imm:x}" if pipeline.id_ex.imm >= 0 else str(pipeline.id_ex.imm))
        
        ops_str = ", ".join(operands)
        print(f"  EX:  {ex_op:7s} {ops_str}")
    else:
        print(f"  EX:  (empty)")
    
    # MEM Stage: Shows instruction in memory access
    if pipeline.ex_mem and pipeline.ex_mem.op is not None:
        mem_op = pipeline.ex_mem.op
        operands = []
        if pipeline.ex_mem.rd is not None:
            operands.append(f"${pipeline.ex_mem.rd}")
        if pipeline.ex_mem.alu_result is not None:
            operands.append(f"addr=0x{pipeline.ex_mem.alu_result:x}")
        
        ops_str = ", ".join(operands) if operands else ""
        print(f"  MEM: {mem_op:7s} {ops_str}")
    else:
        print(f"  MEM: (empty)")
    
    # WB Stage: Shows instruction writing back
    if pipeline.mem_wb and pipeline.mem_wb.rd is not None:
        wb_rd = pipeline.mem_wb.rd
        if pipeline.mem_wb.mem_data is not None:
            value = pipeline.mem_wb.mem_data
        elif pipeline.mem_wb.alu_result is not None:
            value = pipeline.mem_wb.alu_result
        else:
            value = 0
        
        print(f"  WB:  Write $({wb_rd}) = 0x{value:08x}")
    else:
        print(f"  WB:  (empty)")
    
    # ========================================================
    # REGISTER CHANGES (DELTAS)
    # ========================================================
    
    if prev_cpu_state is not None:
        reg_changes = []
        for i in range(32):
            old_val = prev_cpu_state.registers.read(i)
            new_val = cpu.registers.read(i)
            if old_val != new_val:
                reg_changes.append(f"${i}: 0x{old_val:08x} -> 0x{new_val:08x}")
        
        if reg_changes:
            print(f"  Registers: {', '.join(reg_changes)}")


def print_pipeline_summary(cpu, cycle_count, halt_reason):
    """Print summary of pipeline state after simulation completes.
    
    This shows final register and memory state, useful for verification.
    
    Args:
        cpu (CPUstate): Final CPU state
        cycle_count (int): Total cycles executed
        halt_reason (str): Why simulation halted
    """
    print("\n" + "="*60)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*60)
    print(f"Total Cycles: {cycle_count}")
    print(f"Halt Reason:  {halt_reason}")
    print(f"Final PC:     0x{cpu.pc:04x}")
    print("="*60)
