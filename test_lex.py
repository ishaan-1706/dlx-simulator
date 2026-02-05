from parser.lexer import Lexer

code = """
ADDI $1, $31, 1
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
print("Tokens:")
for tok in tokens:
    print(f"  {tok}")
