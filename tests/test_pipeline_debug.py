# tests/test_pipeline_debug.py
"""Debug test for tracing pipeline behavior cycle by cycle."""
from tests.util import assemble
from state.cpu_state import CPUstate
from pipeline.pipeline import Pipeline


def test_pipeline_trace_load_use():
    """Trace through the load-use stall scenario step by step."""
    src = 'LW $1, 0($0)\nADD $2, $1, $0\nADDI $3, $0, 5'
    machine = assemble(src)

    cpu = CPUstate()
    cpu.memory.store_word(0, 42)
    for i, word in enumerate(machine):
        cpu.memory.store_word(4 + i * 4, word)
    cpu.pc = 4

    pipeline = Pipeline()

    for cycle in range(12):
        pipeline.step(cpu)
        print(f"Cycle {cycle}: "
              f"ID/EX(op={pipeline.id_ex.op}, rs={pipeline.id_ex.rs}, rs_val={pipeline.id_ex.rs_val}, rt={pipeline.id_ex.rt}, rt_val={pipeline.id_ex.rt_val}, rd={pipeline.id_ex.rd}), "
              f"EX/MEM(mem_op={pipeline.ex_mem.mem_op}, alu_result={pipeline.ex_mem.alu_result}, rd={pipeline.ex_mem.rd}), "
              f"MEM/WB(mem_data={pipeline.mem_wb.mem_data}, alu_result={pipeline.mem_wb.alu_result}, rd={pipeline.mem_wb.rd}), "
              f"Regs[$1,2,3]=[{cpu.registers.read(1)}, {cpu.registers.read(2)}, {cpu.registers.read(3)}]")

    print(f"\nFinal: $1={cpu.registers.read(1)}, $2={cpu.registers.read(2)}, $3={cpu.registers.read(3)}")

