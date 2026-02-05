# pipeline/pipeline.py
from pipeline.pipeline_regs import IF_ID, ID_EX, EX_MEM, MEM_WB
from pipeline.pipeline_stages import IF, ID, EX, MEM, WB
from pipeline.hazards import forwarding, detect_raw, detect_load_use_hazard, detect_branch_taken

class Pipeline:
    """5-stage pipeline controller with stall and flush logic.

    This controller manages the pipeline registers and detects/handles hazards:
    - Stall on load-use hazards (prevent IF/ID and ID/EX advancement)
    - Flush on demand (clear pipeline registers on mispredicted branches)
    """
    def __init__(self):
        # current pipeline register state
        self.if_id = IF_ID()
        self.id_ex = ID_EX()
        self.ex_mem = EX_MEM()
        self.mem_wb = MEM_WB()

        # next pipeline register state container (created each cycle)
        self.next_if_id = IF_ID()
        self.next_id_ex = ID_EX()
        self.next_ex_mem = EX_MEM()
        self.next_mem_wb = MEM_WB()
        
        # cycle counter for debugging
        self.cycle = 0

    def step(self, cpu):
        """Perform one pipeline cycle with hazard detection and control.
        
        1. Check for load-use hazard; if detected, stall IF/ID and ID/EX (and insert NOP in EX)
        2. Run stages (WB, MEM, EX, ID, IF) appropriately based on stall/flush
        3. Check for branch taken in next_ex_mem (just computed by EX); if taken, flush pipeline and redirect PC
        4. Apply forwarding
        5. Commit pipeline registers
        """
        self.cycle += 1
        
        # Check for load-use hazard between current ID/EX and current EX/MEM
        stall_requested = detect_load_use_hazard(self.id_ex, self.ex_mem)
        
        # WRITEBACK stage (always runs)
        WB(cpu, self.mem_wb)

        # MEM stage (always runs)
        MEM(cpu, self.ex_mem, self.next_mem_wb)

        # EX stage: if stalling, insert NOP (clear); otherwise execute current ID/EX
        if stall_requested:
            # Stall: insert a NOP into the pipeline (clear EX/MEM)
            self.next_ex_mem.clear()
        else:
            # Normal: execute current ID/EX
            EX(self.id_ex, self.next_ex_mem)

        # Check for branch taken in next_ex_mem (the result of EX stage this cycle)
        branch_taken, branch_target = detect_branch_taken(self.next_ex_mem)

        # ID stage: if stalling, hold ID/EX; otherwise decode next instruction
        if stall_requested:
            # Stall: restore instruction info but clear operand values so forwarding refills them
            self.next_id_ex.pc = self.id_ex.pc
            self.next_id_ex.op = self.id_ex.op
            self.next_id_ex.rs = self.id_ex.rs
            self.next_id_ex.rt = self.id_ex.rt
            self.next_id_ex.rd = self.id_ex.rd
            self.next_id_ex.imm = self.id_ex.imm
            self.next_id_ex.shamt = self.id_ex.shamt
            # Clear operand values so they can be re-forwarded from updated pipeline state
            # But preserve values for register $0 (always 0, no forwarding needed)
            self.next_id_ex.rs_val = None if self.id_ex.rs != 0 else self.id_ex.rs_val
            self.next_id_ex.rt_val = None if self.id_ex.rt != 0 else self.id_ex.rt_val
        else:
            # Normal: decode next instruction
            ID(cpu, self.if_id, self.next_id_ex)

        # Apply forwarding (even during stall, as values may have become available)
        forwarding(self.next_id_ex, self.ex_mem, self.mem_wb)
        forwarding(self.next_id_ex, self.next_ex_mem, self.next_mem_wb)

        # IF stage: if stalling, hold IF/ID; otherwise fetch next instruction
        if stall_requested:
            # Stall: copy current IF/ID to next (no new fetch, don't advance PC)
            self.next_if_id.pc = self.if_id.pc
            self.next_if_id.instr = self.if_id.instr
        else:
            # Normal: fetch next instruction
            IF(cpu, self.next_if_id)

        # Handle branch taken: flush pipeline and redirect PC
        # This must happen BEFORE commit so the flushed state is used next cycle
        if branch_taken and branch_target is not None:
            # Flush the next IF/ID (clear fetched instruction that came after branch)
            self.next_if_id.clear()
            # Flush the next ID/EX (clear decoded instruction that came after branch)
            self.next_id_ex.clear()
            # Redirect PC to branch target for next cycle
            cpu.pc = branch_target

        # Commit: advance register snapshots
        self.if_id = self.next_if_id
        self.id_ex = self.next_id_ex
        self.ex_mem = self.next_ex_mem
        self.mem_wb = self.next_mem_wb

        # Allocate fresh next-stage containers for the next cycle
        self.next_if_id = IF_ID()
        self.next_id_ex = ID_EX()
        self.next_ex_mem = EX_MEM()
        self.next_mem_wb = MEM_WB()

    def flush(self):
        """Flush all pipeline registers (e.g., after a taken branch)."""
        self.if_id.clear()
        self.id_ex.clear()
        self.ex_mem.clear()
        self.mem_wb.clear()
