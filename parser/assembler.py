#parser/assembler.py
from typing import List
from .asm_parser import Instruction

# Opcode and funct mappings must align with decoder/decoder.py
OPCODES = {
    'ADDI': 0x08,
    'ADDIU': 0x09,
    'SLTI': 0x0A,
    'SLTIU': 0x0B,
    'ANDI': 0x0C,
    'ORI': 0x0D,
    'XORI': 0x0E,
    'LB': 0x20,
    'LBU': 0x24,
    'LH': 0x21,
    'LHU': 0x25,
    'LW': 0x23,
    'SB': 0x28,
    'SH': 0x29,
    'SW': 0x2B,
    'BEQ': 0x04,
    'BNE': 0x05,
    'BLEZ': 0x06,
    'BGTZ': 0x07,
    'BLT': 0x10,  # Pseudo-instruction for testing branch flushing
    'BGE': 0x11,  # Pseudo-instruction for testing branch flushing
    'BLE': 0x12,  # Pseudo-instruction for testing branch flushing
    'BGT': 0x13,  # Pseudo-instruction for testing branch flushing
    'J': 0x02,
    'JAL': 0x03,
}

FUNCTS = {
    'ADD': 0x20,
    'ADDU': 0x21,
    'SUB': 0x22,
    'SUBU': 0x23,
    'AND': 0x24,
    'OR': 0x25,
    'XOR': 0x26,
    'SLT': 0x2A,
    'SLTU': 0x2B,
    'SLL': 0x00,
    'SRL': 0x02,
    'SRA': 0x03,
    'JR': 0x08,
    'JALR': 0x09,
}


def reg_num(reg: str) -> int:
    # Validate register format and range ($0 - $31)
    if not reg.startswith('$'):
        raise ValueError(f"Invalid register format: {reg}")
    try:
        n = int(reg[1:])
    except ValueError:
        raise ValueError(f"Invalid register number: {reg}")
    if not (0 <= n < 32):
        raise ValueError(f"Register out of range (0-31): {reg}")
    return n


def parse_imm(imm: str) -> int:
    if imm.startswith('0x') or imm.startswith('-0x'):
        return int(imm, 16)
    return int(imm)

class Assembler:
    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.labels = {instr.label: idx for idx, instr in enumerate(instructions) if instr.label}
        # Track if HALT is present (signals pipeline flush needed)
        self.has_halt = any(instr.mnemonic == 'HALT' for instr in instructions)

    def assemble(self) -> List[int]:
        machine: List[int] = []
        for idx, instr in enumerate(self.instructions):
            op = instr.mnemonic
            
            # HALT: Generate a NOP (all zeros = no-op in DLX)
            # HALT signals the end of the program, but we still need an instruction word
            if op == 'HALT':
                # NOP = ADD $0, $0, $0 (0x00000000)
                # This does nothing, allowing pipeline to flush naturally
                word = 0x00000000
                machine.append(word)
            elif op in FUNCTS:
                # R-type
                if op == 'SLL' or op == 'SRL' or op == 'SRA':
                    # syntax: SLL rd, rt, shamt
                    rd = reg_num(instr.operands[0])
                    rt = reg_num(instr.operands[1])
                    shamt = int(instr.operands[2]) & 0x1F
                    word = (0 << 26) | (0 << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | FUNCTS[op]
                elif op == 'JR':
                    rs = reg_num(instr.operands[0])
                    word = (0 << 26) | (rs << 21) | (0 << 16) | (0 << 11) | (0 << 6) | FUNCTS[op]
                elif op == 'JALR':
                    # JALR rd, rs OR JALR rs
                    if len(instr.operands) == 2:
                        rd = reg_num(instr.operands[0])
                        rs = reg_num(instr.operands[1])
                    else:
                        rs = reg_num(instr.operands[0])
                        rd = 31
                    word = (0 << 26) | (rs << 21) | (0 << 16) | (rd << 11) | (0 << 6) | FUNCTS[op]
                else:
                    # general R-type: ADD rd, rs, rt
                    rd = reg_num(instr.operands[0])
                    rs = reg_num(instr.operands[1])
                    rt = reg_num(instr.operands[2])
                    word = (0 << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (0 << 6) | FUNCTS[op]
                machine.append(word & 0xFFFFFFFF)

            elif op in OPCODES:
                opcode = OPCODES[op]
                if op in ('J','JAL'):
                    # J target (label)
                    label = instr.operands[0]
                    if label not in self.labels:
                        raise ValueError(f"Undefined label: {label}")
                    address = self.labels[label]
                    word = (opcode << 26) | (address & 0x3FFFFFF)
                    machine.append(word)
                elif op in ('BEQ','BNE'):
                    # BEQ/BNE rs, rt, label
                    rs = reg_num(instr.operands[0])
                    rt = reg_num(instr.operands[1])
                    label = instr.operands[2]
                    if label not in self.labels:
                        raise ValueError(f"Undefined label: {label}")
                    imm = self.labels[label] - (idx + 1)
                    imm &= 0xFFFF
                    word = (opcode << 26) | (rs << 21) | (rt << 16) | imm
                    machine.append(word)
                elif op in ('BLT', 'BGE', 'BLE', 'BGT'):
                    # BLT/BGE/BLE/BGT rs, rt, label
                    rs = reg_num(instr.operands[0])
                    rt = reg_num(instr.operands[1])
                    label = instr.operands[2]
                    if label not in self.labels:
                        raise ValueError(f"Undefined label: {label}")
                    imm = self.labels[label] - (idx + 1)
                    imm &= 0xFFFF
                    word = (opcode << 26) | (rs << 21) | (rt << 16) | imm
                    machine.append(word)
                elif op in ('BLEZ', 'BGTZ'):
                    # BLEZ/BGTZ rs, label
                    rs = reg_num(instr.operands[0])
                    label = instr.operands[1]
                    if label not in self.labels:
                        raise ValueError(f"Undefined label: {label}")
                    imm = self.labels[label] - (idx + 1)
                    imm &= 0xFFFF
                    word = (opcode << 26) | (rs << 21) | (0 << 16) | imm
                    machine.append(word)
                elif op in ('LW','SW','LB','LBU','LH','LHU','SB','SH'):
                    # syntax: LW rt, imm(rs)
                    rt = reg_num(instr.operands[0])
                    # operands may be ['imm','(','$rs',')'] or ['imm','(','rs',')']
                    if '(' in instr.operands:
                        p = instr.operands
                        # find '(' index
                        i = p.index('(')
                        imm_str = p[i-1]
                        rs = reg_num(p[i+1])
                    else:
                        # fallback: rt, rs, imm
                        imm_str = instr.operands[1]
                        rs = reg_num(instr.operands[2])
                    imm = parse_imm(imm_str) & 0xFFFF
                    word = (opcode << 26) | (rs << 21) | (rt << 16) | imm
                    machine.append(word)
                else:
                    # I-type arithmetic: ADDI rt, rs, imm
                    rt = reg_num(instr.operands[0])
                    rs = reg_num(instr.operands[1])
                    imm = parse_imm(instr.operands[2]) & 0xFFFF
                    word = (opcode << 26) | (rs << 21) | (rt << 16) | imm
                    machine.append(word)
            else:
                raise ValueError(f'Unsupported mnemonic {op}')
        return machine