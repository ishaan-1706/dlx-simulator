#parser/asm_parser.py
from typing import List, Dict
from .lexer import Token

class Instruction:
    def __init__(self, mnemonic: str, operands: List[str], label: str | None = None):
        self.mnemonic = mnemonic
        self.operands = operands
        self.label = label

    def __repr__(self):
        return f"Instruction({self.mnemonic}, {self.operands}, label={self.label})"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.instructions: List[Instruction] = []
        self.labels: Dict[str, int] = {}

    def parse(self) -> List[Instruction]:
        while self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            if tok.type == 'LABEL_DEF':
                label = tok.value
                self.pos += 1
                # next token should be a mnemonic
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'MNEMONIC':
                    mnemonic = self.tokens[self.pos].value
                    self.pos += 1
                    operands = self._collect_operands()
                    instr = Instruction(mnemonic, operands, label)
                    self.labels[label] = len(self.instructions)
                    self.instructions.append(instr)
                else:
                    # Label alone on line
                    self.labels[label] = len(self.instructions)
            elif tok.type == 'MNEMONIC':
                mnemonic = tok.value
                self.pos += 1
                operands = self._collect_operands()
                instr = Instruction(mnemonic, operands)
                self.instructions.append(instr)
            else:
                # Skip unexpected tokens (commas, parentheses cleaned in assembler)
                self.pos += 1
        return self.instructions

    def _collect_operands(self) -> List[str]:
        ops: List[str] = []
        while self.pos < len(self.tokens) and self.tokens[self.pos].type not in ('MNEMONIC','LABEL_DEF'):
            tok = self.tokens[self.pos]
            if tok.type in ('REGISTER','IMMEDIATE','IDENTIFIER'):
                ops.append(tok.value)
                self.pos += 1
            elif tok.type == 'COMMA':
                self.pos += 1
            elif tok.type in ('LPAREN','RPAREN'):
                ops.append(tok.value)
                self.pos += 1
            else:
                # ignore other tokens
                self.pos += 1
        return ops