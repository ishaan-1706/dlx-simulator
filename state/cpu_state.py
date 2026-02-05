#state/cpu_state.py
from .memory import Memory
from .registers import Registers
class CPUstate:
    def __init__(self):
        self.pc = 0  # Program Counter initialized to 0
        self.memory = Memory()
        self.registers = Registers()

    def step_pc(self, offset: int = 4):
        self.pc += offset # Increment PC by offset (default 4 for word size)