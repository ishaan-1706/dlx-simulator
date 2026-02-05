from parser.lexer import Lexer
from parser.asm_parser import Parser
from parser.assembler import Assembler
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline

code = """
ADDI $1, $0, 5
ADDI $2, $0, 5
BEQ $1, $2, label2
ADDI $3, $0, 999
label2:
BEQ $1, $2, end
ADDI $4, $0, 999
end:
ADDI $5, $0, 42
HALT
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
instructions = parser.parse()
print("Parsed instructions:")
for i, inst in enumerate(instructions):
    print(f"  {i}: {inst.mnemonic} {inst.operands}")

assembler = Assembler(instructions)
machine_code = assembler.assemble()

print('\nMachine code length:', len(machine_code))
print('Labels found:', assembler.labels)

cpu = CPUstate()
pipeline = Pipeline()

for idx, instruction in enumerate(machine_code):
    addr = idx * 4
    cpu.memory.store_word(addr, instruction)

print(f"\nRunning for up to 50 cycles...")
cycle = 0
for cycle in range(50):
    print(f"Cycle {cycle}: PC before step={hex(cpu.pc)}")
    pipeline.step(cpu)
    print(f"Cycle {cycle}: PC after step={hex(cpu.pc)}, IF/ID.instr={hex(pipeline.if_id.instr) if pipeline.if_id.instr is not None else None}")
    if cpu.pc < 0 or cpu.pc >= len(machine_code) * 4:
        print(f"Halt at cycle {cycle}: PC={hex(cpu.pc)}, prog_len={len(machine_code)*4}")
        break

print('\nFinal registers:')
for i in [1, 2, 3, 4, 5]:
    print(f'  ${i} = {cpu.registers.read(i)}')
print('Total cycles:', cycle)
