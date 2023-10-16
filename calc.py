from typing import List, Tuple, Iterator
import enum


class Token_Kind(enum.Enum):
    INT = enum.auto(),
    PLUS = enum.auto(),
    MINUS = enum.auto(),
    ASTERISK = enum.auto(),
    SLASH = enum.auto(),
    LPAREN = enum.auto(),
    RPAREN = enum.auto(),


Token_Type = Tuple[Token_Kind, str]

def match_sequence_in_range(s:str,rs:Iterator[Iterator])->Tuple[str,str]:
    out = ""
    while s and any(ord(s[0]) in r for r in rs):
        c, *s = s
        out += c
    return out,s

def match_range(s:str,rs:Iterator[Iterator]):
    c = ""
    if s and any(ord(s[0]) in r for r in rs):
        c, *s = s
    return c,s



def match_digits(s:str):
    DIGITS = [range(ord("0"),ord("9")+1)]
    return match_sequence_in_range(s,DIGITS)

def match_whitespace(s:str):
    WHITES = [[ord(c) for c in [" ", "\t"]]]
    return match_sequence_in_range(s,WHITES)

def tokenize(s: str) -> List[Token_Type]:
    tokens = []
    while s:
        # skip whitespace

        if s[0] == "+":
            c,*s = s
            tokens.append((Token_Kind.PLUS,c))
            _,s = match_whitespace(s)
            continue
        elif s[0] == "-":
            c,*s = s
            tokens.append((Token_Kind.MINUS,c))
            _,s = match_whitespace(s)
            continue
        elif s[0] == "*":
            c,*s = s
            tokens.append((Token_Kind.ASTERISK,c))
            _,s = match_whitespace(s)
            continue
        elif s[0] == "/":
            c,*s = s
            tokens.append((Token_Kind.SLASH,c))
            _,s = match_whitespace(s)
            continue
        elif s[0] == "(":
            c,*s = s
            tokens.append((Token_Kind.LPAREN,c))
            _,s = match_whitespace(s)
            continue
        elif s[0] == ")":
            c,*s = s
            tokens.append((Token_Kind.RPAREN,c))
            _,s = match_whitespace(s)
            continue


        xl_int,s = match_digits(s)
        if xl_int:
            tokens.append((Token_Kind.INT,int(xl_int)))
            _,s = match_whitespace(s)
            continue
        
        raise NotImplementedError(f"Unknown token: '{s[0]}'")

    return tokens

op_prec = {
    Token_Kind.PLUS: 1,
    Token_Kind.MINUS: 1,
    Token_Kind.ASTERISK: 2,
    Token_Kind.SLASH:2,
}


def parse(tokens:List[Token_Type])->List[Token_Type]:
    ops = []
    out = []

    for token in tokens:
        if token[0] == Token_Kind.INT:
            out.append(token)
        elif token[0] in [Token_Kind.PLUS, Token_Kind.MINUS, Token_Kind.ASTERISK, Token_Kind.SLASH]:
            if len(ops) == 0:
                ops.append(token)
            else:
                if ops[-1][0] == Token_Kind.LPAREN:
                    ops.append(token)
                elif op_prec[ops[-1][0]] < op_prec[token[0]]: # see mult was add
                    ops.append(token)
                else: # see add was mult
                    while ops and ops[-1][0] != Token_Kind.LPAREN and not op_prec[ops[-1][0]] < op_prec[token[0]]:#...
                        out.append(ops.pop())
                    ops.append(token)
        elif token[0] == Token_Kind.LPAREN:
            ops.append(token)
        elif token[0] == Token_Kind.RPAREN:
            while ops and ops[-1][0] != Token_Kind.LPAREN:
                out.append(ops.pop())
            lp = ops.pop()
    
    while ops:
        out.append(ops.pop())
    return out


tokens = tokenize("1    +3*9*((7) + 3) ")
instr = parse(tokens)
for token in tokens:
    print(token)

print()
for token in instr:
    print(token)