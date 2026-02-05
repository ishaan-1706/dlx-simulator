#execute/branch_unit.py


def branch(op: str, rs_val: int, rt_val: int, target: int, pc: int, link_reg: int | None = None):
    # Branch Unit.
    # Computes next PC (or next PC + link info for link-returning jumps) based on
    # branch/jump instructions. Returns either an int next_pc or a tuple
    # (next_pc, link_reg, link_val) for link-producing jumps (e.g., JALR).

    # Equality/inequality
    if op == 'BEQ' and rs_val == rt_val:
        return target
    if op == 'BNE' and rs_val != rt_val:
        return target

    # Signed comparisons against zero
    if op == 'BLEZ' and rs_val <= 0:
        return target
    if op == 'BGTZ' and rs_val > 0:
        return target

    # Register-vs-register comparisons
    if op == 'BLT' and rs_val < rt_val:
        return target
    if op == 'BGE' and rs_val >= rt_val:
        return target
    if op == 'BLE' and rs_val <= rt_val:
        return target
    if op == 'BGT' and rs_val > rt_val:
        return target

    # Absolute jumps
    if op in ('J', 'JAL'):
        return target

    # JR and JALR
    if op == 'JR':
        return rs_val

    if op == 'JALR':
        if link_reg is None:
            raise ValueError('JALR requires a destination register (link_reg)')
        # Return tuple: (next_pc, link_reg, link_value)
        return (rs_val, link_reg, pc + 4)

    # default fall-through
    return pc + 4  # default fall-through