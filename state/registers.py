#state/registers.py
class Registers:
    def __init__(self):

        self.regs = [0] * 32  # Initialize 32 registers to 0

    def read(self, idx: int) -> int:
        return self.regs[idx]
    
    def write(self, idx: int, value: int):
        if idx == 0:  # Register 0 is always 0
            self.regs[idx] = 0
        else:
            self.regs[idx] = value

    def dump(self):

        for i, val in enumerate(self.regs):
            print(f"R{i}: {val}")
        