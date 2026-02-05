# DLX 5-Stage Pipeline Simulator

A fully-functional, production-ready simulator for the DLX (Hennessy-Patterson) 5-stage pipeline architecture with comprehensive hazard detection and resolution.

## Features

### Core Pipeline Architecture
- **5-Stage Pipeline**: IF (Instruction Fetch) → ID (Instruction Decode) → EX (Execute) → MEM (Memory) → WB (Write Back)
- **Full Instruction Set Support**:
  - R-type instructions: ADD, SUB, AND, OR, XOR, SLL, SRL, SRA
  - I-type instructions: ADDI, ANDI, ORI, XORI, LW, SW
  - J-type instructions: J, JAL, JR, JALR
  - Branch instructions: BEQ, BNE, BLEZ, BGTZ, BLT, BGE, BLE, BGT
  - Special: HALT (with 5-cycle pipeline drain)

### Advanced Hazard Handling
- **Load-Use Stall Detection**: Automatically stalls pipeline when data dependency detected between load and immediate consumer
- **Multi-Stage Forwarding**: 
  - ALU-to-ALU forwarding
  - MEM-to-ALU forwarding
  - MEM-to-MEM forwarding
  - Maximum 5-stage forwarding distance
- **Branch Flushing**: Proper pipeline flush with instruction replay when branch misprediction detected
- **Zero Register ($0) Special Handling**: Always reads as 0, writes ignored

### Production Features
- **Command-Line Interface**: Easy-to-use CLI for running assembly programs
- **Pipeline Visualization**: Cycle-by-cycle detailed pipeline state output
- **Comprehensive Testing**: 124 unit and integration tests (100% passing)
- **Assembly Language Support**: Custom lexer, parser, and assembler with label support

## Installation

### Requirements
- Python 3.10 or higher
- pytest 9.0.2 (for running tests)

### Setup

```bash
# Clone or navigate to repository
cd simulator

# Create virtual environment
python -m venv sim_dlx
source sim_dlx/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

Quick Start (recommended)
-------------------------
If you want a quick, repeatable setup that works on Windows and POSIX systems, use the helper scripts included in the repository.

Windows (PowerShell / cmd):

```powershell
# Run once to create a venv and install deps
setup.bat

# Activate and run a single sample
call sim_venv\Scripts\activate.bat
python main.py tests\sample_programs\simple_branch.asm

# Run all bundled samples sequentially
run_all_samples.bat

# Add your own .asm to your personal directory (`user_programs`):
add_program.bat C:\path\to\your_prog.asm

# Run a user script quickly (interactive or pass filename):
run_user.bat my_prog.asm

# Delete a user script permanently:
remove_program.bat my_prog.asm
# Or delete all user scripts permanently:
remove_program.bat --all
```

macOS / Linux:

```bash
# Run once to create a venv and install deps
./setup.sh

# Activate and run a single bundled sample
source sim_venv/bin/activate
python main.py tests/sample_programs/simple_branch.asm

# Run all bundled samples sequentially
./run_all_samples.sh

# Add your own .asm to your personal folder (user_programs)
./add_program.sh /full/path/to/your_prog.asm

# Run a user script interactively or by name
./run_user.sh my_prog.asm

# Delete a user script permanently:
./remove_program.sh my_prog.asm
# Or delete all user scripts permanently:
./remove_program.sh --all
```

Why these scripts?
- `setup.bat` / `setup.sh` create a virtual environment and install `requirements.txt` so users don't pollute global Python.
- `run_all_samples.*` runs every `.asm` in `tests/sample_programs` sequentially so reviewers can quickly verify behavior.
- `add_program.*` copies a user-provided assembly file into `user_programs/` so you can keep personal scripts separate from bundled tests.
- `run_user.*` runs a single user script from `user_programs/` (interactive or by filename).
- `remove_program.*` permanently deletes user scripts from `user_programs/` (use `--all` to remove all user scripts).

If you prefer manual setup, follow the instructions in the "Setup" section above.


## Usage

### Basic Execution

```bash
# Run an assembly program
python main.py <assembly_file.asm>

# Example with sample program
python main.py tests/sample_programs/simple_branch.asm
```

### Command-Line Options

```bash
python main.py <file> [OPTIONS]

Options:
  --cycles N          Maximum number of cycles to simulate (default: 1000)
  --verbose           Enable detailed pipeline visualization output
  --halt-on-zero      Halt when $0 register is written to (default: false)
  --help              Show help message

Examples:
  # Run with 50 cycle limit
  python main.py program.asm --cycles 50

  # Run with verbose output showing all pipeline stages
  python main.py program.asm --verbose

  # Run with both options
  python main.py program.asm --cycles 100 --verbose
```

## Sample Programs

Seven comprehensive sample programs demonstrating different features:

1. **simple_branch.asm** - Basic branch with forwarding
   - Tests: Branch taken condition, ALU forwarding
   - Result: $1=5, $2=5, $3=1

2. **loop_count.asm** - Loop with repeated branches
   - Tests: Backward branching, loop accumulation
   - Result: $2=15 (sum of 1+2+3+4+5)

3. **load_branch.asm** - Load-use stall followed by branch
   - Tests: Load stall handling, branch with loaded value
   - Result: $2=100 (loaded value used in condition)

4. **nested_branch.asm** - Multiple branches with flushing
   - Tests: Branch flushing priority, jump instructions
   - Result: Complex instruction interactions validated

5. **nested_branch_again.asm** - Alternating branch patterns
   - Tests: Mixed taken/not-taken branches
   - Result: Correct execution path selection

6. **memory_branch.asm** - Store/Load with branching
   - Tests: Memory forwarding, branch with memory-loaded value
   - Result: mem[0]=42, $2=$3=42

7. **forward_stress.asm** - Multi-stage forwarding chain + branch
   - Tests: 5-deep forwarding, branch with forward chain, flush timing
   - Result: $1=10, $2=15, $3=25, $4=10 (branch taken)

### Running Sample Programs

```bash
# Simple program
python main.py tests/sample_programs/simple_branch.asm

# With verbose output
python main.py tests/sample_programs/forward_stress.asm --verbose

# With cycle limit
python main.py tests/sample_programs/loop_count.asm --cycles 30
```

Developer / Debug files
-----------------------
This repository contains a few helper and debug files in the project root intended for development and troubleshooting. They are included in the repository on purpose for maintainers and advanced users:

- `debug_test.py`, `debug_forward.py`, `test_lex.py` — quick debugging scripts you can run to exercise the lexer or forwarding scenarios. These are for developers or power users; if you don't plan to tinker with the code, you can ignore them.
- Files named `*_code.txt` and `*_bundler.py` are project-specific artifacts and are ignored by `.gitignore` so they won't be accidentally committed.

If you're new, avoid editing or running the debug scripts unless you want to explore or extend the simulator — they are useful when adding new instructions or diagnosing failures.

License
-------
This project is provided under the MIT License. See the `LICENSE` file in the repository root for the full text. If you want a different license applied, update the `LICENSE` file before publishing.

## Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with summary only
pytest tests/ -q

# Run specific test file
pytest tests/test_phase1_basic_pipeline.py -v

# Run edge-case tests
pytest tests/test_edge_cases.py -v

# Run with no traceback (summary only)
pytest tests/ --tb=no
```

### Test Coverage

- **66 Core Tests** (Phases 1-4):
  - Phase 1: Basic 5-stage pipeline (13 tests)
  - Phase 2: Hazard detection (15 tests)
  - Phase 3: Forwarding (16 tests)
  - Phase 4: Branch flushing (11 tests)

- **58 Edge-Case Tests** (Phase 5 Layer 4):
  - Branch edge cases (7 tests)
  - Forwarding chains (7 tests)
  - Stalling scenarios (6 tests)
  - Flushing timing (7 tests)
  - Register handling (6 tests)
  - Memory patterns (6 tests)
  - Complex interactions (6 tests)
  - Boundary conditions (7 tests)

**Result: 124/124 tests passing ✅**

## Assembly Language Syntax

### Instruction Format

```asm
# R-type: operation rd, rs, rt
ADD $1, $2, $3          # $1 = $2 + $3
SUB $4, $5, $6          # $4 = $5 - $6

# I-type: operation rt, rs, immediate
ADDI $1, $0, 100        # $1 = 0 + 100
LW $2, 0($3)            # $2 = memory[$3 + 0]
SW $4, 4($5)            # memory[$5 + 4] = $4

# Branch: branch rs, rt, label
BEQ $1, $2, label       # if $1 == $2, jump to label
BNE $3, $4, target      # if $3 != $4, jump to target

# Jump: jump label
J loop_start             # unconditional jump to loop_start
JAL main                 # jump to main, save return address in $31

# Special
HALT                    # end program (generates pipeline flush)
NOP                     # no operation
```

### Labels

Labels must be at the start of a line and end with a colon:

```asm
loop:
    ADD $1, $1, $1
    ADDI $2, $2, -1
    BNE $2, $0, loop
    J end
end:
    HALT
```

## Output Format

### Standard Output

```
Loading assembly file: program.asm
  Read 500 characters
Assembling...
  Assembled 15 instructions
Running simulation (max 100 cycles)...

============================================================
SIMULATION COMPLETE
============================================================
Total Cycles: 23
Halt Reason: halt-complete (pipeline flushed)
Final PC:    0x0060

Registers (non-zero):
  $1         = 0x00000042 (66)
  $2         = 0x0000000f (15)

Memory (non-zero):
  [0x0000] = 0x20010005 (536936453)
  [0x0004] = 0x20020005 (537001989)

============================================================
```

### Verbose Output (--verbose flag)

Shows cycle-by-cycle pipeline state:

```
[Cycle   1] PC=0x0004
  IF:  Fetching @ 0x0004
  ID:  ADDI    $1, $0, 10
  EX:  (empty)
  MEM: (empty)
  WB:  (empty)

[Cycle   2] PC=0x0008
  IF:  Fetching @ 0x0008
  ID:  ADDI    $2, $1, 5
  EX:  ADDI    $1, $0, 0xa
  MEM: (empty)
  WB:  (empty)

[Cycle   3] PC=0x000c
  IF:  Fetching @ 0x000c
  ID:  ADD     $3, $2, $1
  EX:  ADDI    $2, $1, 0x5
  MEM: ADDI    $1, addr=0xa
  WB:  (empty)
```

## Architecture

### Project Structure

```
simulator/
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── parser/                         # Assembly parsing
│   ├── lexer.py                   # Tokenization (handles $0-$31)
│   ├── asm_parser.py              # Instruction parsing
│   └── assembler.py               # Machine code generation
│
├── state/                         # CPU state management
│   ├── registers.py               # 32-register file
│   ├── memory.py                  # Memory system (word-addressable)
│   └── cpu_state.py               # CPU state wrapper
│
├── pipeline/                      # 5-stage pipeline
│   ├── pipeline.py                # Main pipeline controller
│   ├── pipeline_stages.py         # IF/ID/EX/MEM/WB stage logic
│   ├── pipeline_regs.py           # Pipeline register definitions
│   └── hazards.py                 # Hazard detection & forwarding
│
├── utils/
│   └── logger.py                  # Pipeline visualization
│
├── tests/                         # Test suite
│   ├── test_*.py                 # 66 phase tests
│   ├── test_edge_cases.py        # 58 edge-case tests
│   └── sample_programs/          # 7 demo programs
│       ├── simple_branch.asm
│       ├── loop_count.asm
│       ├── load_branch.asm
│       ├── nested_branch.asm
│       ├── nested_branch_again.asm
│       ├── memory_branch.asm
│       └── forward_stress.asm
│
└── [User Scripts - Preserved]
    ├── *bundler*.py              # Custom bundler scripts
    ├── *directory*_code.txt      # Code storage
    └── debug files               # Debugging utilities
```

## How It Works

### Pipeline Flow

1. **IF (Instruction Fetch)**: Load instruction from memory at PC
2. **ID (Instruction Decode)**: Decode instruction, read registers, detect hazards
3. **EX (Execute)**: Compute ALU result, evaluate branch condition
4. **MEM (Memory)**: Load/store memory operations
5. **WB (Write Back)**: Write results to register file

### Hazard Resolution

**Load-Use Stall**:
- Detected when load in EX/MEM stage and next instruction in ID stage uses loaded register
- Action: Stall IF/ID and ID/EX, insert NOP in EX
- Effect: 1-cycle delay for dependent operations

**Forwarding**:
- Detected when result in MEM/WB stage needed by current EX instruction
- Action: Forward data directly from pipeline register to ALU input
- Effect: No stall required, data bypasses normal register file

**Branch Flushing**:
- Detected when branch evaluated as taken in EX stage
- Action: Clear IF/ID and ID/EX pipeline registers, redirect PC
- Effect: Misfetched instructions discarded, correct branch target fetched

## Performance Characteristics

- **Simple ALU Chain** (5 instructions): 9 cycles (5 instructions + 4 forwarding)
- **Load-Use Dependency** (2 instructions): 7 cycles (1 extra stall cycle)
- **Branch Flush**: 5+ cycles (branch + 4 in-flight instructions + 5 flush cycles)
- **Loop Execution**: O(n) cycles for n loop iterations

## Debugging

### Debug Files

Several debug scripts are included for development and testing:

- **debug_test.py**: Manual test of specific assembly programs
- **debug_forward.py**: Detailed forwarding scenario testing
- **test_lex.py**: Lexer tokenization debugging

Run with:
```bash
python debug_test.py
python debug_forward.py
python test_lex.py
```

### Verbose Mode Interpretation

In verbose output:
- `(empty)` = Pipeline stage has no instruction (stall or early pipeline)
- `(nop)` = NOP instruction (from halt flush or stall insertion)
- `ADDI $1, $2, 0xa` = Instruction being executed
- `Write $(1) = 0x0000000a` = Writeback result in WB stage
- `BEQ` = Branch evaluation result shown

## Known Limitations

- Word-addressed memory (not byte-addressed)
- No interrupts or exceptions
- No branch prediction (takes all branches as not-taken until evaluation)
- 32-bit register width
- Maximum 1000 cycles per simulation (configurable with --cycles)

## Contributing

To add new test cases:
1. Add assembly file to `tests/sample_programs/`
2. Add Python test to `tests/test_edge_cases.py` using `run_program()` helper
3. Run `pytest tests/ -v` to verify
4. Commit with descriptive message

## License

This project is for educational purposes. Use freely for learning and teaching CPU architecture.

## Authors

Developed as a comprehensive study of DLX pipeline architecture, hazard detection, and resolution mechanisms.

## References

- "Computer Architecture: A Quantitative Approach" - Hennessy & Patterson
- DLX Instruction Set Reference
- Pipeline simulation techniques and best practices
#   d l x - s i m u l a t o r  
 