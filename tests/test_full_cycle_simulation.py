#tests/test_full_cycle_simulation.py
from decoder.decoder import decode
from execute.alu import alu
from execute.load_store_unit import load_store


from tests.util import assemble, make_cpu, assert_registers, assert_memory_word, require_field


# `execute_decoded` is now provided by `tests.util`. Import the shared helper instead.
from tests.util import execute_decoded, run_program



def test_full_cycle_store_and_load():
    src = 'ADDI $1, $0, 8\nSW $1, 0($0)\nLW $2, 0($0)'
    # Use `run_program` to assemble and execute the straight-line program
    cpu = run_program(src)
    assert_registers(cpu, {2: 8})
    # memory at 0 should contain 8 (word)
    assert_memory_word(cpu.memory, 0, 8)