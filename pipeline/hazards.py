# pipeline/hazards.py
from typing import List, Tuple, Optional


# All branch and jump instructions
BRANCH_INSTRUCTIONS = {
    'BEQ', 'BNE', 'BLEZ', 'BGTZ', 'BLT', 'BGE', 'BLE', 'BGT',  # conditional branches
    'J', 'JAL',  # unconditional jumps
    'JR', 'JALR'  # register jumps
}


def is_branch(op: Optional[str]) -> bool:
    """Check if an instruction is a branch or jump."""
    return op in BRANCH_INSTRUCTIONS


def evaluate_branch(op: str, rs_val: int, rt_val: int) -> bool:
    """Evaluate if a branch should be taken.

    Returns True if the branch condition is satisfied, False otherwise.
    Note: J, JAL, JR, JALR are always taken.
    """
    if op == 'BEQ':
        return rs_val == rt_val
    elif op == 'BNE':
        return rs_val != rt_val
    elif op == 'BLEZ':
        return rs_val <= 0
    elif op == 'BGTZ':
        return rs_val > 0
    elif op == 'BLT':
        return rs_val < rt_val
    elif op == 'BGE':
        return rs_val >= rt_val
    elif op == 'BLE':
        return rs_val <= rt_val
    elif op == 'BGT':
        return rs_val > rt_val
    elif op in ('J', 'JAL', 'JR', 'JALR'):
        # Unconditional jumps are always taken
        return True
    else:
        return False


def detect_raw(id_ex_reg, ex_mem_reg, mem_wb_reg) -> List[str]:
    """Detect Read-After-Write hazards by comparing register numbers.

    Compares ID/EX source registers (rs, rt) against EX/MEM.rd and MEM/WB.rd.
    Returns a list of human-readable hazard descriptions (empty if none).
    """
    hazards: List[str] = []
    for src_name in ('rs', 'rt'):
        src = getattr(id_ex_reg, src_name, None)
        if src is None:
            continue
        if ex_mem_reg.rd is not None and src == ex_mem_reg.rd and ex_mem_reg.rd != 0:
            hazards.append(f"RAW between ID/EX.{src_name} and EX/MEM.rd (${ex_mem_reg.rd})")
        if mem_wb_reg.rd is not None and src == mem_wb_reg.rd and mem_wb_reg.rd != 0:
            hazards.append(f"RAW between ID/EX.{src_name} and MEM/WB.rd (${mem_wb_reg.rd})")
    return hazards


def forwarding(id_ex_reg, ex_mem_reg, mem_wb_reg):
    """Apply forwarding to ID/EX values if possible.

    This updates id_ex_reg.rs_val and id_ex_reg.rt_val when a matching producer
    exists in EX/MEM or MEM/WB with an available value (alu_result or mem_data).
    
    Note: For load operations in EX/MEM, we don't forward the address (alu_result)
    because the actual loaded value hasn't been computed yet. We wait for MEM/WB.
    """
    # Forward from EX/MEM first (most recent), but NOT from loads
    # (loads have the address in alu_result, not the loaded value)
    is_load_in_ex = ex_mem_reg.mem_op in ("LW", "LB", "LBU", "LH", "LHU")
    if not is_load_in_ex and ex_mem_reg.rd is not None and ex_mem_reg.alu_result is not None and ex_mem_reg.rd != 0:
        if id_ex_reg.rs == ex_mem_reg.rd:
            id_ex_reg.rs_val = ex_mem_reg.alu_result
        if id_ex_reg.rt == ex_mem_reg.rd:
            id_ex_reg.rt_val = ex_mem_reg.alu_result

    # Then from MEM/WB (if not already forwarded)
    if mem_wb_reg.rd is not None and mem_wb_reg.rd != 0:
        wb_val = mem_wb_reg.mem_data if mem_wb_reg.mem_data is not None else mem_wb_reg.alu_result
        if wb_val is None:
            return
        if id_ex_reg.rs == mem_wb_reg.rd and id_ex_reg.rs_val is None:
            id_ex_reg.rs_val = wb_val
        if id_ex_reg.rt == mem_wb_reg.rd and id_ex_reg.rt_val is None:
            id_ex_reg.rt_val = wb_val


def detect_load_use_hazard(id_ex_reg, ex_mem_reg) -> bool:
    """Detect a load-use hazard: ID/EX instruction uses a register being loaded in EX/MEM.

    Returns True if a stall is needed, False otherwise.
    A load-use hazard occurs when:
    - EX/MEM has a load operation (LW, LB, LBU, LH, LHU)
    - ID/EX reads the same register that EX/MEM is loading into
    """
    if ex_mem_reg.mem_op is None or ex_mem_reg.rd is None or ex_mem_reg.rd == 0:
        return False

    # Check if it's a load operation
    is_load = ex_mem_reg.mem_op in ("LW", "LB", "LBU", "LH", "LHU")
    if not is_load:
        return False

    # Check if ID/EX reads the register being loaded
    if id_ex_reg.rs == ex_mem_reg.rd or id_ex_reg.rt == ex_mem_reg.rd:
        return True

    return False


def detect_branch_taken(ex_mem_reg) -> Tuple[bool, Optional[int]]:
    """Detect if a branch in EX/MEM is taken and return target address.
    
    Returns (is_taken, target_address) where:
    - is_taken: True if the branch condition is met (or it's an unconditional jump)
    - target_address: PC address to jump to, or None if branch not taken
    
    This function is called after the EX stage so branch_target is already computed.
    """
    if ex_mem_reg.op is None or not is_branch(ex_mem_reg.op):
        return False, None
    
    # Get the operand values from EX/MEM (they've been forwarded from earlier stages)
    rs_val = ex_mem_reg.rs_val if ex_mem_reg.rs_val is not None else 0
    rt_val = ex_mem_reg.rt_val if ex_mem_reg.rt_val is not None else 0
    
    # Evaluate the branch condition
    taken = evaluate_branch(ex_mem_reg.op, rs_val, rt_val)
    
    if taken:
        # Return the target address (computed during decode)
        return True, ex_mem_reg.branch_target
    else:
        return False, None
