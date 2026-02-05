from parser.lexer import Lexer
from parser.asm_parser import Parser
from parser.assembler import Assembler
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline

code = """
ADDI $1, $0, 10
ADDI $2, $1, 5
ADDI $3, $2, 5
SW $1, 4($0)
LW $4, 4($0)
NOP
NOP
ADD $5, $4, $3
NOP
NOP
NOP
HALT
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
instructions = parser.parse()
assembler = Assembler(instructions)
machine_code = assembler.assemble()

cpu = CPUstate()
pipeline = Pipeline()

for idx, instruction in enumerate(machine_code):
    addr = idx * 4
    cpu.memory.store_word(addr, instruction)

halted = False
cycle = 0
halt_cycle = 0
for cycle in range(100):
    pipeline.step(cpu)
    
    # Track key events
    if cycle >= 4 and cycle <= 12:
        print(f"Cycle {cycle}: PC={hex(cpu.pc)}, $4={cpu.registers.read(4)}, $5={cpu.registers.read(5)}")
    
    if cpu.pc < 0 or cpu.pc >= len(machine_code) * 4:
        if not halted:
            halted = True
            halt_cycle = cycle
        elif cycle >= halt_cycle + 5:
            break

print(f'\nFinal registers:')
for i in [1, 2, 3, 4, 5]:
    print(f'  ${i} = {cpu.registers.read(i)}')
