#parser/lexer.py
import re
from typing import List, NamedTuple

class Token(NamedTuple):
    type: str
    value: str
    line: int

class Lexer:
    # Recognized mnemonics (expandable)
    MNEMONICS = (
        'ADD','ADDU','SUB','SUBU','AND','OR','XOR','NOR',
        'SLT','SLTU','SLL','SRL','SRA','JR','JALR',
        'ADDI','ADDIU','SLTI','SLTIU','ANDI','ORI','XORI',
        'LW','SW','LB','LBU','LH','LHU','SB','SH',
        'BEQ','BNE','BLEZ','BGTZ','BLT','BGE','BLE','BGT',
        'J','JAL','HALT'
    )

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        lines = self.source.split('\n')
        for lineno, line in enumerate(lines, start=1):
            # strip comments (# or ;)
            line = re.split(r"[#;]", line)[0].strip()
            if not line:
                continue
            self._tokenize_line(line, lineno)
        return self.tokens

    def _tokenize_line(self, line: str, lineno: int):
        # Split into words and punctuation while keeping parentheses & commas
        # Examples: ADD $1, $2, $3    LW $4, 8($5)   label:  J label
        pos = 0
        patterns = [
            (r"^([A-Za-z_][A-Za-z0-9_]*)\:", 'LABEL_DEF'),
            (r"^([A-Za-z_][A-Za-z0-9_]*)", 'IDENT'),
            (r"^\$(3[0-1]|[1-2][0-9]|[0-9])", 'REGISTER'),
            (r"^(-?0x[0-9A-Fa-f]+)", 'IMMEDIATE'),
            (r"^(-?\d+)", 'IMMEDIATE'),
            (r"^,", 'COMMA'),
            (r"^\(", 'LPAREN'),
            (r"^\)", 'RPAREN'),
            (r"^\s+", 'WS'),
        ]
        while pos < len(line):
            substring = line[pos:]
            matched = False
            for regex, ttype in patterns:
                m = re.match(regex, substring)
                if not m:
                    continue
                val = m.group(1) if ttype in ('LABEL_DEF','IDENT','REGISTER','IMMEDIATE') else m.group(0)
                pos += m.end()
                matched = True
                if ttype == 'WS':
                    break
                # Distinguish mnemonics (IDENT -> MNEMONIC) or identifiers
                if ttype == 'IDENT':
                    if val.upper() in self.MNEMONICS:
                        self.tokens.append(Token('MNEMONIC', val.upper(), lineno))
                    else:
                        self.tokens.append(Token('IDENTIFIER', val, lineno))
                elif ttype == 'LABEL_DEF':
                    self.tokens.append(Token('LABEL_DEF', val, lineno))
                elif ttype == 'REGISTER':
                    # Restore dollar sign in register token (e.g., '$1')
                    self.tokens.append(Token('REGISTER', f'${val}', lineno))
                elif ttype == 'IMMEDIATE':
                    self.tokens.append(Token('IMMEDIATE', val, lineno))
                else:
                    self.tokens.append(Token(ttype, val, lineno))
                break
            if not matched:
                # Unknown char -> treat as single char token
                ch = line[pos]
                self.tokens.append(Token('CHAR', ch, lineno))
                pos += 1