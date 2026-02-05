# pipeline/pipeline_stages.py
from decoder.decoder import decode
from execute.alu import alu
from execute.branch_unit import branch
from execute.load_store_unit import load_store


def IF(cpu, next_if_id):
    """Instruction Fetch: read the instruction at PC and write into next IF/ID register.

    This function advances the CPU PC so that the next IF sees the next instruction.
    """
    instr_word = cpu.memory.load_word(cpu.pc)
    next_if_id.pc = cpu.pc
    next_if_id.instr = instr_word
    cpu.step_pc()


def ID(cpu, cur_if_id, next_id_ex):
    """Instruction Decode: read `cur_if_id.instr` and populate `next_id_ex`.

    This copies register numbers and values into ID/EX so later stages have the
    necessary information for execution and hazard detection.
    """
    if cur_if_id.instr is None:
        next_id_ex.clear()
        return

    dec = decode(cur_if_id.instr, pc=cur_if_id.pc)
    next_id_ex.pc = cur_if_id.pc
    next_id_ex.op = dec.op
    next_id_ex.rs = dec.rs
    next_id_ex.rt = dec.rt
    next_id_ex.rs_val = cpu.registers.read(dec.rs) if dec.rs is not None else None
    next_id_ex.rt_val = cpu.registers.read(dec.rt) if dec.rt is not None else None
    next_id_ex.rd = dec.rd
    next_id_ex.imm = dec.imm
    next_id_ex.shamt = dec.shamt  # Shift amount for shift operations
    next_id_ex.branch_target = dec.target  # Store branch/jump target


def EX(cur_id_ex, next_ex_mem):
    """Execute stage: perform ALU ops or compute memory addresses and write to next EX/MEM."""
    next_ex_mem.clear()
    next_ex_mem.pc = cur_id_ex.pc
    next_ex_mem.op = cur_id_ex.op  # Carry forward op for branch detection
    next_ex_mem.rs_val = cur_id_ex.rs_val  # Carry forward rs_val for branch evaluation
    next_ex_mem.rt_val = cur_id_ex.rt_val  # Carry forward rt_val for branch evaluation
    next_ex_mem.branch_target = cur_id_ex.branch_target  # Carry forward branch target

    op = cur_id_ex.op
    if op is None:
        return

    # R-type arithmetic/logic
    if op in ("ADD", "ADDU", "SUB", "SUBU", "AND", "OR", "XOR", "SLT", "SLTU"):
        # Guard: operands must be available after forwarding
        if cur_id_ex.rs_val is None or cur_id_ex.rt_val is None:
            # Incomplete forwarding (should not happen if hazard unit is correct)
            return
        next_ex_mem.alu_result = alu(op, cur_id_ex.rs_val, cur_id_ex.rt_val, shamt=cur_id_ex.shamt or 0)
        next_ex_mem.rd = cur_id_ex.rd

    # I-type immediate arithmetic/logical
    elif op in ("ADDI", "ADDIU"):
        if cur_id_ex.rs_val is None:
            return
        next_ex_mem.alu_result = alu('ADD' if op == 'ADDI' else 'ADDU', cur_id_ex.rs_val, cur_id_ex.imm)
        next_ex_mem.rd = cur_id_ex.rt
    elif op in ("ANDI", "ORI", "XORI"):
        if cur_id_ex.rs_val is None:
            return
        op_map = {"ANDI": "AND", "ORI": "OR", "XORI": "XOR"}
        next_ex_mem.alu_result = alu(op_map[op], cur_id_ex.rs_val, cur_id_ex.imm)
        next_ex_mem.rd = cur_id_ex.rt

    # Load/store address computation
    elif op in ("LW", "SW", "LB", "LBU", "LH", "LHU", "SB", "SH"):
        if cur_id_ex.rs_val is None:
            return
        next_ex_mem.alu_result = cur_id_ex.rs_val + (cur_id_ex.imm or 0)
        next_ex_mem.rt_val = cur_id_ex.rt_val
        next_ex_mem.rd = cur_id_ex.rt
        next_ex_mem.mem_op = op

    else:
        # For unimplemented ops, do nothing except forward pc
        pass


def MEM(cpu, cur_ex_mem, next_mem_wb):
    """Memory stage: perform loads/stores and prepare writeback values."""
    next_mem_wb.clear()
    next_mem_wb.pc = cur_ex_mem.pc

    if cur_ex_mem.mem_op == "LW":
        next_mem_wb.mem_data = load_store("LW", cpu.memory, cur_ex_mem.alu_result)
        next_mem_wb.rd = cur_ex_mem.rd
    elif cur_ex_mem.mem_op == "SW":
        load_store("SW", cpu.memory, cur_ex_mem.alu_result, cur_ex_mem.rt_val)
    elif cur_ex_mem.mem_op in ("LB", "LBU", "LH", "LHU"):
        next_mem_wb.mem_data = load_store(cur_ex_mem.mem_op, cpu.memory, cur_ex_mem.alu_result)
        next_mem_wb.rd = cur_ex_mem.rd
    else:
        next_mem_wb.alu_result = cur_ex_mem.alu_result
        next_mem_wb.rd = cur_ex_mem.rd


def WB(cpu, cur_mem_wb):
    """Writeback: commit results to the register file."""
    if cur_mem_wb.rd is not None:
        val = cur_mem_wb.mem_data if cur_mem_wb.mem_data is not None else cur_mem_wb.alu_result
        if val is not None:
            cpu.registers.write(cur_mem_wb.rd, val)