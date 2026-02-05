# Program: nested_branch_again.asm
# Tests: Nested branches - first taken, second NOT taken
#
# Logic:
#   $1 = 5
#   $2 = 10
#   if $1 < $2? (5 < 10 = true, branch TAKEN)
#   (skip to 'skip' label)
#   $3 = 999 (should NOT execute - branch taken)
# skip:
#   $4 = 1
#   $5 = 5
#   if $4 == $5? (1 == 5 = false, branch NOT taken)
#   (continue to next instruction)
#   $6 = 42 (should execute - branch not taken)
# end:
#   $7 = 100 (should execute)
#
# Expected Final State:
#   $1 = 5, $2 = 10, $3 = 0 (never set)
#   $4 = 1, $5 = 5, $6 = 42, $7 = 100

ADDI $1, $0, 5
ADDI $2, $0, 10
BLT $1, $2, skip
ADDI $3, $0, 999
skip:
ADDI $4, $0, 1
ADDI $5, $0, 5
BEQ $4, $5, end
ADDI $6, $0, 42
end:
ADDI $7, $0, 100
HALT
