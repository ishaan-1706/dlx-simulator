# Program 2: loop_count.asm
# Tests: Repeated BNE branch in a loop
#
# Logic:
#   $1 = 5 (counter)
#   $2 = 0 (accumulator)
#   loop: $2 = $2 + $1
#         $1 = $1 - 1
#         if $1 != 0, branch back to loop
#   (exit loop when $1 == 0)
#
# Expected Final State:
#   $1 = 0 (counter exhausted)
#   $2 = 5 + 4 + 3 + 2 + 1 = 15
#   Loop executes 5 times

ADDI $1, $0, 5
ADDI $2, $0, 0

loop:
ADD $2, $2, $1
ADDI $1, $1, -1
BNE $1, $0, loop

ADDI $3, $0, 42
HALT
