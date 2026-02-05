# pipeline/pipeline_regs.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IF_ID:
    pc: int = 0
    instr: Optional[int] = None

    def clear(self):
        self.pc = 0
        self.instr = None


@dataclass
class ID_EX:
    pc: int = 0
    rs: Optional[int] = None  # register number
    rt: Optional[int] = None  # register number
    rs_val: Optional[int] = None
    rt_val: Optional[int] = None
    rd: Optional[int] = None
    imm: Optional[int] = None
    op: Optional[str] = None
    shamt: Optional[int] = None  # shift amount for shift operations
    branch_target: Optional[int] = None  # target address for branches/jumps

    def clear(self):
        self.pc = 0
        self.rs = None
        self.rt = None
        self.rs_val = None
        self.rt_val = None
        self.rd = None
        self.imm = None
        self.op = None
        self.shamt = None
        self.branch_target = None


@dataclass
class EX_MEM:
    pc: int = 0
    op: Optional[str] = None  # operation (for branch detection)
    alu_result: Optional[int] = None
    rt_val: Optional[int] = None
    rs_val: Optional[int] = None  # rs_val needed for branch evaluation
    rd: Optional[int] = None
    mem_op: Optional[str] = None
    branch_target: Optional[int] = None  # target address for branches

    def clear(self):
        self.pc = 0
        self.op = None
        self.alu_result = None
        self.rt_val = None
        self.rs_val = None
        self.rd = None
        self.mem_op = None
        self.branch_target = None


@dataclass
class MEM_WB:
    pc: int = 0
    mem_data: Optional[int] = None
    alu_result: Optional[int] = None
    rd: Optional[int] = None

    def clear(self):
        self.pc = 0
        self.mem_data = None
        self.alu_result = None
        self.rd = None
