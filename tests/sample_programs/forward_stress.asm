# Program 6: forward_stress.asm
# Tests: Multi-stage forwarding through multiple dependent instructions
#
# Logic:
#   $1 = 10
#   $2 = $1 + 5  (forward $1 from EX stage to next ALU)
#   $3 = $2 + $1 (forward $2 from MEM stage, $1 already in WB)
#   $4 = $3 - $2 (forward $3 from MEM stage, $2 from WB)
#   if $4 == $1? ($4 = 10, $1 = 10? yes, branch taken)
#   $5 = 999 (should NOT execute - branch taken)
# end:
#   $5 = 0 (should execute)
#
# Expected Final State:
#   $1 = 10, $2 = 15, $3 = 25, $4 = 10, $5 = 0
#   Tests forwarding: ALU->ALU, MEM->ALU, WB->ALU chains

ADDI $1, $0, 10
ADDI $2, $1, 5
ADD $3, $2, $1
SUB $4, $3, $2
BEQ $4, $1, end
ADDI $5, $0, 999
end:
ADDI $5, $0, 0
HALT
