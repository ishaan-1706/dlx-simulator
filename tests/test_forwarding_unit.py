# tests/test_forwarding_unit.py
"""Unit test for forwarding logic."""
from pipeline.pipeline_regs import ID_EX, EX_MEM, MEM_WB
from pipeline.hazards import forwarding


def test_forwarding_from_mem_wb():
    """Test that forwarding works from MEM/WB."""
    id_ex = ID_EX()
    id_ex.rs = 1
    id_ex.rs_val = None  # Cleared, needs forwarding

    print(f"Before forwarding: id_ex.rs_val = {id_ex.rs_val}, type = {type(id_ex.rs_val)}")

    ex_mem = EX_MEM()
    ex_mem.mem_op = "LW"
    ex_mem.rd = 1
    ex_mem.alu_result = 0  # Address computed

    mem_wb = MEM_WB()
    mem_wb.mem_data = 42
    mem_wb.alu_result = None
    mem_wb.rd = 1

    print(f"mem_wb: rd={mem_wb.rd}, mem_data={mem_wb.mem_data}, alu_result={mem_wb.alu_result}")
    print(f"Calling forwarding...")

    # Apply forwarding
    forwarding(id_ex, ex_mem, mem_wb)

    print(f"After forwarding: id_ex.rs_val = {id_ex.rs_val}, type = {type(id_ex.rs_val)}")
    assert id_ex.rs_val == 42, f"Expected forwarding to fill rs_val with 42, got {id_ex.rs_val}"


if __name__ == "__main__":
    test_forwarding_from_mem_wb()
    print("Forwarding unit test passed!")
