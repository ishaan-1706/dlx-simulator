#execute/alu.py


def alu(op: str, a: int, b: int, shamt: int = 0) -> int:
    """
    Arithmetic Logic Unit (ALU).
    Executes R-type and I-type arithmetic/logic instructions.
    """
    if op == "ADD": return a + b
    if op == "ADDU": return (a + b) & 0xFFFFFFFF
    if op == "SUB": return a - b
    if op == "SUBU": return (a - b) & 0xFFFFFFFF
    if op == "AND": return a & b
    if op == "OR":  return a | b
    if op == "XOR": return a ^ b
    if op == "NOR": return ~(a | b) & 0xFFFFFFFF
    if op == "SLT": return 1 if a < b else 0
    if op == "SLTU": return 1 if (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF) else 0
    if op == "SLL": return (b << shamt) & 0xFFFFFFFF
    if op == "SRL": return (b & 0xFFFFFFFF) >> shamt
    if op == "SRA": return b >> shamt
    raise ValueError(f"Unsupported ALU op {op}")