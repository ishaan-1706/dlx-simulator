# tests/test_pipeline_basic.py
from tests.util import assemble
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline


def test_pipeline_simple_add_sequence():
    # Program: $1=5; $2=10; $3 = $1+$2
    src = 'ADDI $1, $0, 5\nADDI $2, $0, 10\nADD $3, $1, $2'
    machine = assemble(src)

    cpu = CPUstate()
    # load machine code into memory at 0,4,8
    for i, word in enumerate(machine):
        cpu.memory.store_word(i * 4, word)

    pipeline = Pipeline()

    # Run enough cycles for the three-instruction program to write back $3
    # A conservative upper bound: pipeline depth (5) + number of instructions
    cycles = 5 + len(machine) + 1
    for _ in range(cycles):
        pipeline.step(cpu)

    assert cpu.registers.read(3) == 15
