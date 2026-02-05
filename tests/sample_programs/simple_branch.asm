# Program 1: simple_branch.asm
# Tests: BEQ with forwarding
# 
# Logic:
#   $1 = 5
#   $2 = 5
#   if $1 == $2, jump to 'equal'
#   $3 = 999 (should NOT execute - branch taken)
# equal:
#   $3 = 1 (should execute)
#
# Expected Final State:
#   $1 = 5, $2 = 5, $3 = 1
#   The instruction at 'equal' should execute, skipping the 999 assignment

ADDI $1, $0, 5
ADDI $2, $0, 5
BEQ $1, $2, equal
ADDI $3, $0, 999
equal:
ADDI $3, $0, 1
HALT
