from typing import List, Tuple, Iterator, Union, Callable
import enum

import dataclasses

## TODO: add floating point support
class Token_Kind(enum.Enum):
    INT = enum.auto(),
    FLOAT = enum.auto(),
    STRING = enum.auto(),
    PLUS = enum.auto(),
    MINUS = enum.auto(),
    ASTERISK = enum.auto(),
    SLASH = enum.auto(),
    LPAREN = enum.auto(),
    RPAREN = enum.auto(),
    FUNC = enum.auto(),
    COMMA = enum.auto(),


@dataclasses.dataclass
class Token:
    kind: Token_Kind
    value: Union[int, str]

    def __str__(self):
        return f"Token(kind={self.kind:20}, value={self.value})"


def match_sequence_in_range(s: str, rs: Iterator[Iterator]) -> Tuple[str, str]:
    out = ""
    while s and any(ord(s[0]) in r for r in rs):
        c, s = s[:1], s[1:]
        out += c
    return out, s


def match_range(s: str, rs: Iterator[Iterator]):
    c = ""
    if s and any(ord(s[0]) in r for r in rs):
        c, s = s[:1], s[1:]
    return c, s


def match_digits(s: str)-> Tuple[str,str]:
    DIGITS = [range(ord("0"), ord("9")+1)]
    return match_sequence_in_range(s, DIGITS)

def match_float(s:str) -> Tuple[str,str]:
    start = s
    flt_int, s = match_digits(s)
    if not flt_int:
        return "", start
    
    if not (s and s[0] == "."):
        return "",start

    _, s = s[:1], s[1:]


    flt_frac, s = match_digits(s) # this can be empty, as in 1.


    flt_str = f"{flt_int}.{flt_frac}"
    return flt_str, s


def match_whitespace(s: str):
    WHITES = [[ord(c) for c in [" ", "\t"]]]
    return match_sequence_in_range(s, WHITES)

def match_escape_sequence(s:str):
    start = s
    if not (s and s[0] == "\\"):
        return "",start
    _, s = s[:1], s[1,]
    c, s = s[:1], s[1,]
    if c == "\\":
        return "\\",s
    elif c == "n":
        return "\n",s
    elif c == "t":
        return "\t",s
    elif c =="\"":
        return "\""
    elif c == "\'":
        return "\'"
    else:
        assert False, f"undefined escape sequence: '\{c}'"


def match_string(s:str):
    str_seps = ["\"", "'"]

    start = s
    if not (s and s[0] in str_seps):
        return None,start

    str_sep,s = s[:1], s[1:]

    str_text = ""
    while True:
        if len(s) == 0:
            return None,start
        elif s[0] == str_sep:
            _,s = s[:1], s[1:]
            return str_text,s
        elif s[0] == "\\":
            esc,s = match_escape_sequence(s)
            str_text += esc
            continue
        else:
            c,s = s[:1], s[1:]
            str_text += c


def match_funcs(s: str):
    FUNCS = ["sq", "if","type"]
    s_low = s.lower()
    for func in FUNCS:
        if s_low.startswith(func):
            func_len = len(func)
            return s[:func_len], s[func_len:]
    return "", s


def tokenize(s: str) -> List[Token]:
    assert s, "Empty Input"
    start = s
    tokens = []
    while s:
        if s[0] == "+":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.PLUS, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == "-":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.MINUS, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == "*":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.ASTERISK, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == "/":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.SLASH, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == "(":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.LPAREN, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == ")":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.RPAREN, c))
            _, s = match_whitespace(s)
            continue
        elif s[0] == ",":
            c, s = s[:1], s[1:]
            tokens.append(Token(Token_Kind.COMMA, c))
            _, s = match_whitespace(s)

        str_str, s = match_string(s)
        if str_str is not None:
            tokens.append(Token(Token_Kind.STRING,str_str))
            _,s = match_whitespace(s)
            continue

        fun_str, s = match_funcs(s)
        if fun_str:
            tokens.append(Token(Token_Kind.FUNC, fun_str))
            _, s = match_whitespace(s)
            continue

        flt_str, s = match_float(s)
        if flt_str:
            tokens.append(Token(Token_Kind.FLOAT, float(flt_str)))
            _, s = match_whitespace(s)
            continue

        int_str, s = match_digits(s)
        if int_str:
            tokens.append(Token(Token_Kind.INT, int(int_str)))
            _, s = match_whitespace(s)
            continue

        err_pos = len(start) - len(s)
        raise NotImplementedError(
            f"Unknown sequence at row {err_pos}:\n"
            f"{start}\n"
            f"{' '*err_pos}^"
        )

    return tokens

# TODO: Once input is tokenized, validate against grammar
# eg 6 ( * 8) is valid and returns 48.
def validate(tokens: List[Token]):
    def test_all(tests:List[Callable]):
        for test in tests:
            if not test:
                return False
        return True


    def validate_scopes(tokens: List[Token]):
        depth = 0
        for token in tokens:
            if token.kind == Token_Kind.LPAREN:
                depth += 1
            elif token.kind == Token_Kind.RPAREN:
                depth -= 1
            
            if depth < 0:
                print("Unmatched right parenthesis")
                return False
        
        if depth != 0:
            print("Unmatched left parenthesis")
            return False
        return True


    return test_all([validate_scopes(tokens)])
    

LIT_KINDS = [
    Token_Kind.INT,
    Token_Kind.FLOAT,
    Token_Kind.STRING,
]

# higher = more precise
LIT_PREC = {
    Token_Kind.INT:0,
    Token_Kind.FLOAT:1,
}

OP_PREC = {
    Token_Kind.COMMA: 0, # TODO: compare this to precedence 4
    Token_Kind.PLUS: 1,
    Token_Kind.MINUS: 1,
    Token_Kind.ASTERISK: 2,
    Token_Kind.SLASH: 2,
    Token_Kind.FUNC: 3,
    Token_Kind.LPAREN: 4,
}

OP_KINDS = [
    Token_Kind.PLUS,
    Token_Kind.MINUS,
    Token_Kind.ASTERISK,
    Token_Kind.SLASH,
    Token_Kind.COMMA,
    Token_Kind.FUNC,
    Token_Kind.LPAREN,
]


def parse(tokens: List[Token]) -> List[Token]:
    '''Translate infix notation to postfix notation.'''

    def peek(stack):
        assert stack, "Peek from empty stack."
        return stack[-1]


    ops: List[Token] = []
    out: List[Token] = []

    for token in tokens:
        if token.kind in LIT_KINDS:
            out.append(token)
        elif token.kind in OP_KINDS:
            while ops and peek(ops).kind not in [Token_Kind.LPAREN, Token_Kind.COMMA] and not OP_PREC[peek(ops).kind] < OP_PREC[token.kind]:
                out.append(ops.pop())
            ops.append(token)
        elif token.kind == Token_Kind.RPAREN:
            while ops and peek(ops).kind != Token_Kind.LPAREN:
                if peek(ops).kind == Token_Kind.COMMA:
                    _ = ops.pop()
                else:
                    out.append(ops.pop())
            if ops and peek(ops).kind == Token_Kind.FUNC:
                out.append(ops.pop())
            assert ops.pop().kind == Token_Kind.LPAREN
        else:
            raise NotImplementedError(f"Unparsable token: {token}")

    while ops:
        out.append(ops.pop())
    return out


def make_token(a:Union[int,float])-> Token:
    if isinstance(a, int):
        return Token(Token_Kind.INT,a)
    elif isinstance(a, float):
        return Token(Token_Kind.FLOAT,a)
    else:
        assert False, f"Unknown type '{type(a)}' of value '{a}'"


def evaluate(tokens: List[Token]):
    stack: List[Token] = []
    for token in tokens:
        if token.kind in LIT_KINDS:
            stack.append(token)
        elif token.kind == Token_Kind.PLUS:
            b = stack.pop().value
            a = stack.pop().value
            c = a+b
            stack.append(make_token(c))
        elif token.kind == Token_Kind.MINUS:
            b = stack.pop().value
            a = stack.pop().value
            c = a-b
            stack.append(make_token(c))
        elif token.kind == Token_Kind.ASTERISK:
            b = stack.pop().value
            a = stack.pop().value
            c = a*b
            stack.append(make_token(c))
        elif token.kind == Token_Kind.SLASH:
            b = stack.pop().value
            a = stack.pop().value
            c = a/b    
            stack.append(make_token(c))
        elif token.kind == Token_Kind.FUNC:
            if token.value == "sq":
                assert not len(stack) < 1, "Not enough arguments for sq function"
                a = stack.pop().value
                b = a*a
                stack.append(make_token(b))
            elif token.value == "if":
                assert not len(stack) < 3, "Not enough arguments for if function"
                false_val = stack.pop().value
                true_val = stack.pop().value
                condition = stack.pop().value
                if condition:
                    stack.append(make_token(true_val))
                else:
                    stack.append(make_token(false_val))
            elif token.value == "type":
                assert not len(stack) < 1, "Not enough arguments for type function"
                a = stack.pop().kind
                stack.append(Token(Token_Kind.STRING,a))
            else:
                raise NotImplementedError(
                    f"Cannot evaluate unknown function: {token}")
        else:
            raise NotImplementedError(
                f"Cannot evaluate unknown token: {token}")
    assert len(stack) == 1
    return stack.pop()


def calculate(s: str):
    tokens = tokenize(s)
    if not validate(tokens): return None
    instructions = parse(tokens)
    result = evaluate(instructions)
    return result.value


def print_tokens(tokens:List[Token]):
    print(" ".join(str(token.value) for token in tokens))

def terminal():
    while True:
        r = calculate(input("> "))
        if r is not None:
            print(r)

if __name__ == "__main__":
    terminal()
    # source = "1    +3*9*((7) + 3) "
    # source = "sq(sq(2))"
    # source = "sq(if(1,10*1/1+1-1,20))"
    # tokens = tokenize(source)  # 271
    # tokens = tokenize("1 + sq(2)")
    # tokens = tokenize("1    +3*9*sq((7) + 3) ") # 2701
    # tokens = tokenize("10+if(1,sq(if(1,1000,5)),10)") # 1000010
    # tokens = tokenize("if(1,if(if(0,0,1),2,3),4)") # =2

    # print_tokens(tokens)
    # # for token in tokens:
    # #     print(token)

    # instr = parse(tokens)
    # print()
    # print_tokens(instr)

    # result = evaluate(instr).value
    # print(f"{result=}")

    # print(calculate(source))
