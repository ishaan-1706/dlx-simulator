# Program 4: nested_branch.asm
# Tests: Nested branches - one NOT taken, one taken
#
# Logic:
#   $1 = 10
#   $2 = 5
#   if $1 < $2? (10 < 5 = false, branch NOT taken)
#   (continue to next instruction)
#   $3 = 1
#   $4 = 2
#   Jump to 'end' (unconditional, taken - flushes pipeline)
#   $5 = 999 (should NOT execute - jump flushes pipeline)
# end:
#   $6 = 42 (should execute)
#
# Expected Final State:
#   $1 = 10, $2 = 5, $3 = 1, $4 = 2, $6 = 42
#   $5 should remain 0 (never assigned)

ADDI $1, $0, 10
ADDI $2, $0, 5
BLT $1, $2, end
ADDI $3, $0, 1
ADDI $4, $0, 2
J end
ADDI $5, $0, 999
end:
ADDI $6, $0, 42
HALT
