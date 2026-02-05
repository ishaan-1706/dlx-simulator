#tests/util.py
from typing import Any, Dict, List, Optional

from parser.lexer import Lexer
from parser.asm_parser import Parser
from parser.assembler import Assembler
from decoder.decoder import decode as decode_word
from state.cpu_state import CPUstate
from state.memory import Memory


def require_field(dec: Any, name: str):
    """Ensure decoded instruction `dec` has non-None attribute `name` and return it.

    Raises ValueError with a clear message when the field is missing.
    """
    val = getattr(dec, name, None)
    if val is None:
        raise ValueError(f"DecodedInstruction missing required field '{name}' for op {getattr(dec, 'op', None)}")
    return val


def require_int_field(dec: Any, name: str) -> int:
    """Require that a decoded field exists and is an int."""
    val = require_field(dec, name)
    if not isinstance(val, int):
        raise ValueError(f"DecodedInstruction field '{name}' expected int, got {type(val).__name__}")
    return val


def require_reg_field(dec: Any, name: str) -> int:
    """Require that a decoded field is a valid register number (0-31)."""
    reg = require_int_field(dec, name)
    if not (0 <= reg < 32):
        raise ValueError(f"Register field '{name}' out of range: {reg}")
    return reg


def assemble(src: str) -> List[int]:
    """Assemble a small assembly source string into machine words."""
    toks = Lexer(src).tokenize()
    instrs = Parser(toks).parse()
    return Assembler(instrs).assemble()


def assemble_and_decode(src: str, pc: int = 0):
    """Assemble source and return list of decoded instructions (pc increments by 4)."""
    words = assemble(src)
    return [decode_word(w, pc=pc + i * 4) for i, w in enumerate(words)]


def make_cpu(registers: Optional[Dict[int, int]] = None, memory_words: Optional[Dict[int, int]] = None, pc: int = 0) -> CPUstate:
    """Create a CPUstate preloaded with registers and word-aligned memory values."""
    cpu = CPUstate()
    cpu.pc = pc
    if registers:
        for r, v in registers.items():
            cpu.registers.write(r, v)
    if memory_words:
        for addr, val in memory_words.items():
            cpu.memory.store_word(addr, val)
    return cpu


def assert_registers(cpu: CPUstate, expected: Dict[int, int]):
    """Assert multiple registers equal expected values with helpful messages."""
    for r, v in expected.items():
        actual = cpu.registers.read(r)
        assert actual == v, f"Register ${r} expected {v}, found {actual}"


def assert_memory_word(memory: Memory, addr: int, expected: int):
    """Assert a memory word equals expected value."""
    actual = memory.load_word(addr)
    assert actual == expected, f"Memory at {addr:#x} expected {expected:#x}, found {actual:#x}"


# Minimal single-instruction executor used by tests. This mirrors the simple executor
# in `tests/test_full_cycle_simulation.py` and keeps tests DRY. It supports common
# R-type arithmetic, I-type immediate arithmetic/logical, and basic loads/stores.
from execute.alu import alu
from execute.load_store_unit import load_store


def execute_decoded(dec, cpu: CPUstate):
    """Execute a single decoded instruction against `cpu`.

    Note: This is intentionally small and only covers ops exercised in tests.
    """
    if dec.type == 'R':
        if dec.op in ('ADD','ADDU','SUB','SUBU','AND','OR','XOR','SLT', 'SLTU'):
            rs = require_reg_field(dec, 'rs')
            rt = require_reg_field(dec, 'rt')
            a = cpu.registers.read(rs)
            b = cpu.registers.read(rt)
            res = alu(dec.op, a, b, shamt=dec.shamt or 0)
            rd = require_reg_field(dec, 'rd')
            cpu.registers.write(rd, res)
            cpu.pc += 4
        else:
            cpu.pc += 4
    elif dec.type == 'I':
        if dec.op in ('ADDI','ADDIU'):
            rs = require_reg_field(dec, 'rs')
            imm = require_int_field(dec, 'imm')
            rt = require_reg_field(dec, 'rt')
            a = cpu.registers.read(rs)
            res = alu('ADD' if dec.op == 'ADDI' else 'ADDU', a, imm)
            cpu.registers.write(rt, res)
            cpu.pc += 4
        elif dec.op in ('SLTI','SLTIU'):
            rs = require_reg_field(dec, 'rs')
            imm = require_int_field(dec, 'imm')
            rt = require_reg_field(dec, 'rt')
            a = cpu.registers.read(rs)
            res = alu('SLT' if dec.op == 'SLTI' else 'SLTU', a, imm)
            cpu.registers.write(rt, res)
            cpu.pc += 4
        elif dec.op in ('ANDI','ORI','XORI'):
            rs = require_reg_field(dec, 'rs')
            imm = require_int_field(dec, 'imm')
            rt = require_reg_field(dec, 'rt')
            a = cpu.registers.read(rs)
            op_map = {'ANDI': 'AND', 'ORI': 'OR', 'XORI': 'XOR'}
            res = alu(op_map[dec.op], a, imm)
            cpu.registers.write(rt, res)
            cpu.pc += 4
        elif dec.op in ('LW','LB','LBU','LH','LHU'):
            rs = require_reg_field(dec, 'rs')
            imm = require_int_field(dec, 'imm')
            addr = cpu.registers.read(rs) + imm
            val = load_store(dec.op, cpu.memory, addr)
            rt = require_reg_field(dec, 'rt')
            assert val is not None
            cpu.registers.write(rt, val)
            cpu.pc += 4
        elif dec.op in ('SW','SB','SH'):
            rs = require_reg_field(dec, 'rs')
            imm = require_int_field(dec, 'imm')
            rt = require_reg_field(dec, 'rt')
            addr = cpu.registers.read(rs) + imm
            load_store(dec.op, cpu.memory, addr, cpu.registers.read(rt))
            cpu.pc += 4
        else:
            cpu.pc += 4
    else:
        cpu.pc += 4


def run_program(src: str, cpu: Optional[CPUstate] = None, start_pc: int = 0) -> CPUstate:
    """Assemble and run a straight-line program (no control-flow chasing).

    Decodes instructions with sequential PCs starting at `start_pc` and executes
    them in order with `execute_decoded`.
    """
    words = assemble(src)
    decs = [decode_word(w, pc=start_pc + i * 4) for i, w in enumerate(words)]
    if cpu is None:
        cpu = make_cpu(pc=start_pc)
    else:
        cpu.pc = start_pc
    for dec in decs:
        execute_decoded(dec, cpu)
    return cpu
