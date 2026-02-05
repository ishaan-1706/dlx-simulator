# Program 5: memory_branch.asm
# Tests: Load/store operations + branch interaction
#
# Logic:
#   $1 = 0x1000 (memory address, but we'll use 0 as base)
#   $2 = 42 (value to store)
#   Store $2 to memory at address 0
#   Load from memory address 0 into $3
#   (1-cycle stall on LW, then another cycle before BEQ can use it)
#   if $2 == $3 (both should be 42, branch taken)
#   $4 = 999 (should NOT execute)
# success:
#   $4 = 1 (should execute)
#
# Expected Final State:
#   $2 = 42, $3 = 42, $4 = 1
#   mem[0x0000] = 42

ADDI $2, $0, 42
SW $2, 0($0)
LW $3, 0($0)
BEQ $2, $3, success
ADDI $4, $0, 999
success:
ADDI $4, $0, 1
HALT
