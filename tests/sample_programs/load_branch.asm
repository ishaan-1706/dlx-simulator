# Program 3: load_branch.asm
# Tests: Load-use stall before branch condition
#
# Logic:
#   Store 0 at memory address 0x0
#   Load from memory address 0x0 into $1
#   (1-cycle stall due to load-use dependency on BEQ)
#   if $1 == 0 (will be true), branch to 'skip'
#   $2 = 999 (should NOT execute)
# skip:
#   $2 = 100 (should execute)
#
# Expected Final State:
#   $1 = 0 (loaded from memory)
#   $2 = 100 (branch taken, 999 skipped)
#   mem[0x0] = 0

ADDI $1, $0, 0
SW $1, 0($0)
LW $1, 0($0)
BEQ $1, $0, skip
ADDI $2, $0, 999
skip:
ADDI $2, $0, 100
HALT
