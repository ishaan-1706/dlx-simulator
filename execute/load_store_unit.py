#execute/load_store_unit.py

from typing import Optional


def _sign_extend(value: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return (value ^ sign_bit) - sign_bit


# Load/Store Unit.
# Executes memory access instructions. Returns the loaded value for loads,
# and None for stores.
# Supported ops: LW, SW, LB, LBU, LH, LHU, SB, SH
def load_store(op: str, memory, addr: int, rt_val: Optional[int] = None) -> Optional[int]:
    # Validate that store operations include a value for rt_val
    if op in ('SW', 'SB', 'SH') and rt_val is None:
        raise ValueError('Store operations require rt_val')
    if op == 'LW':
        return memory.load_word(addr)

    if op == 'SW':
        memory.store_word(addr, rt_val)
        return None

    # Byte loads/stores
    if op == 'LB':
        val = memory.load_byte(addr)
        return _sign_extend(val, 8)

    if op == 'LBU':
        return memory.load_byte(addr) & 0xFF

    if op == 'SB':
        memory.store_byte(addr, rt_val)
        return None

    # Halfword loads/stores
    if op == 'LH':
        val = memory.load_half(addr)
        return _sign_extend(val, 16)

    if op == 'LHU':
        return memory.load_half(addr) & 0xFFFF

    if op == 'SH':
        memory.store_half(addr, rt_val)
        return None

    # Extend later: other memory ops
    raise ValueError(f'Unsupported memory op {op}')