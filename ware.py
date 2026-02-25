#!/usr/bin/env python3
"""
Ware - A programming language interpreter
Blocks end with a period (.) instead of 'end'
"""

import re
import sys

TOKEN_PATTERNS = [
    ("COMMENT",  r"//[^\n]*"),
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("STRING",   r'"[^"]*"'),
    ("BOOL",     r"\b(true|false)\b"),
    ("KW",       r"\b(while|during|if|else|function|which|has|read|show|add|to|break|continue|range|and|or|not|is|bigger|smaller|than|return)\b"),
    ("IDENT",    r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("DOT",      r"\."),
    ("OP",       r"[+\-*/\(\)\[\]]"),
    ("COMMA",    r","),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
]

def tokenize(code):
    tokens = []
    pos = 0
    while pos < len(code):
        matched = False
        for kind, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                val = m.group(0)
                pos += len(val)
                if kind not in ("SKIP", "COMMENT"):
                    tokens.append((kind, val))
                matched = True
                break
        if not matched:
            raise SyntaxError(f"Unknown character: {code[pos]!r}")
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] != "NEWLINE"]
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        if i < len(self.tokens):
            return self.tokens[i]
        return ("EOF", "")

    def consume(self, kind=None, val=None):
        tok = self.peek()
        if kind and tok[0] != kind:
            raise SyntaxError(f"Expected {kind!r} but got {tok}")
        if val and tok[1] != val:
            raise SyntaxError(f"Expected '{val}' but got '{tok[1]}'")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek()[0] != "EOF":
            stmts.append(self.parse_stmt())
        return stmts

    def parse_block(self):
        stmts = []
        while self.peek()[0] not in ("DOT", "EOF") and self.peek()[1] != "else":
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        tok = self.peek()

        if tok == ("KW", "while"):
            self.consume()
            cond = self.parse_expr()
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("DOT")
            return ("while", cond, body)

        if tok == ("KW", "during"):
            self.consume()
            var = self.consume("IDENT")[1]
            self.consume("COMMA")
            self.consume("KW", "range")
            self.consume("OP", "(")
            count = self.parse_expr()
            self.consume("OP", ")")
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("DOT")
            return ("during", var, count, body)

        if tok == ("KW", "if"):
            self.consume()
            cond = self.parse_expr()
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            else_body = []
            if self.peek() == ("KW", "else"):
                self.consume()
                if self.peek()[0] == "COMMA": self.consume()
                else_body = self.parse_block()
            self.consume("DOT")
            return ("if", cond, body, else_body)

        if tok == ("KW", "function"):
            self.consume()
            name = self.consume("IDENT")[1]
            self.consume("KW", "which")
            self.consume("KW", "has")
            params = [self.consume("IDENT")[1]]
            while self.peek()[0] == "COMMA" and self.peek(1)[0] == "IDENT":
                self.consume()
                params.append(self.consume("IDENT")[1])
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("DOT")
            return ("function", name, params, body)

        if tok == ("KW", "show"):
            self.consume()
            return ("show", self.parse_expr())

        if tok == ("KW", "read"):
            self.consume()
            return ("read", self.consume("IDENT")[1])

        if tok == ("KW", "add"):
            self.consume()
            self.consume("KW", "to")
            var = self.consume("IDENT")[1]
            self.consume("COMMA")
            return ("add", var, self.parse_expr())

        if tok == ("KW", "return"):
            self.consume()
            return ("return", self.parse_expr())

        if tok == ("KW", "break"):
            self.consume(); return ("break",)
        if tok == ("KW", "continue"):
            self.consume(); return ("continue",)

        if tok[0] == "IDENT" and self.peek(1) == ("KW", "is") and self.peek(2)[1] not in ("bigger", "smaller", "not"):
            name = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("assign", name, self.parse_expr())

        return ("expr", self.parse_expr())

    def parse_expr(self): return self.parse_or()

    def parse_or(self):
        left = self.parse_and_expr()
        while self.peek() == ("KW", "or"):
            self.consume()
            left = ("or", left, self.parse_and_expr())
        return left

    def parse_and_expr(self):
        left = self.parse_not()
        while self.peek() == ("KW", "and"):
            self.consume()
            left = ("and", left, self.parse_not())
        return left

    def parse_not(self):
        if self.peek() == ("KW", "not"):
            self.consume()
            return ("not", self.parse_comparison())
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_add()
        if self.peek() == ("KW", "is"):
            self.consume()
            if self.peek() == ("KW", "not"):
                self.consume()
                return ("!=", left, self.parse_add())
            elif self.peek() == ("KW", "bigger"):
                self.consume(); self.consume("KW", "than")
                return (">", left, self.parse_add())
            elif self.peek() == ("KW", "smaller"):
                self.consume(); self.consume("KW", "than")
                return ("<", left, self.parse_add())
            else:
                return ("==", left, self.parse_add())
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[1] in ("+", "-"):
            op = self.consume()[1]
            left = (op, left, self.parse_mul())
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[1] in ("*", "/"):
            op = self.consume()[1]
            left = (op, left, self.parse_unary())
        return left

    def parse_unary(self):
        if self.peek()[1] == "-":
            self.consume()
            return ("neg", self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()

        if tok[0] == "NUMBER":
            self.consume()
            v = tok[1]
            return ("num", float(v) if "." in v else int(v))

        if tok[0] == "STRING":
            self.consume()
            return ("str", tok[1][1:-1])

        if tok[0] == "BOOL":
            self.consume()
            return ("bool", tok[1] == "true")

        if tok[0] == "IDENT":
            self.consume()
            name = tok[1]
            if self.peek() == ("OP", "("):
                self.consume()
                args = []
                if self.peek() != ("OP", ")"):
                    args.append(self.parse_expr())
                    while self.peek()[0] == "COMMA":
                        self.consume()
                        args.append(self.parse_expr())
                self.consume("OP", ")")
                node = ("call", name, args)
            else:
                node = ("var", name)
            while self.peek() == ("OP", "["):
                self.consume()
                idx = self.parse_expr()
                self.consume("OP", "]")
                node = ("index", node, idx)
            return node

        if tok == ("OP", "("):
            self.consume()
            expr = self.parse_expr()
            self.consume("OP", ")")
            return expr

        raise SyntaxError(f"Unexpected token: {tok}")


class ReturnSignal(Exception):
    def __init__(self, v): self.value = v
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class Interpreter:
    def __init__(self):
        self.env = {}

    def run(self, stmts):
        for s in stmts: self.exec(s)

    def fmt(self, val):
        if isinstance(val, bool): return "true" if val else "false"
        if isinstance(val, list): return "[" + ", ".join(self.fmt(v) for v in val) + "]"
        if isinstance(val, float) and val == int(val): return str(int(val))
        return str(val)

    def exec(self, stmt):
        k = stmt[0]
        if k == "assign":
            self.env[stmt[1]] = self.eval(stmt[2])
        elif k == "show":
            print(self.fmt(self.eval(stmt[1])))
        elif k == "read":
            self.env[stmt[1]] = input()
        elif k == "add":
            lst = self.env.get(stmt[1])
            if not isinstance(lst, list): raise RuntimeError(f"'{stmt[1]}' is not a list")
            lst.append(self.eval(stmt[2]))
        elif k == "while":
            while self.eval(stmt[1]):
                try:
                    for s in stmt[2]: self.exec(s)
                except BreakSignal: break
                except ContinueSignal: continue
        elif k == "during":
            count = int(self.eval(stmt[2]))
            for i in range(1, count + 1):
                self.env[stmt[1]] = i
                try:
                    for s in stmt[3]: self.exec(s)
                except BreakSignal: break
                except ContinueSignal: continue
        elif k == "if":
            body = stmt[2] if self.eval(stmt[1]) else stmt[3]
            for s in body: self.exec(s)
        elif k == "function":
            self.env[stmt[1]] = ("__func__", stmt[2], stmt[3], dict(self.env))
        elif k == "return":
            raise ReturnSignal(self.eval(stmt[1]))
        elif k == "break": raise BreakSignal()
        elif k == "continue": raise ContinueSignal()
        elif k == "expr": self.eval(stmt[1])

    def eval(self, node):
        k = node[0]
        if k == "num": return node[1]
        if k == "str": return node[1]
        if k == "bool": return node[1]
        if k == "var":
            if node[1] not in self.env: raise RuntimeError(f"Undefined variable: '{node[1]}'")
            return self.env[node[1]]
        if k == "index":
            obj = self.eval(node[1])
            if not isinstance(obj, list): raise RuntimeError("Cannot index a non-list")
            return obj[int(self.eval(node[2])) - 1]
        if k == "call":
            args = [self.eval(a) for a in node[2]]
            func = self.env.get(node[1])
            if func is None: raise RuntimeError(f"Undefined function: '{node[1]}'")
            if not (isinstance(func, tuple) and func[0] == "__func__"):
                raise RuntimeError(f"'{node[1]}' is not a function")
            _, params, body, closure = func
            saved = self.env
            self.env = {**closure, **dict(zip(params, args))}
            result = None
            try:
                for s in body: self.exec(s)
            except ReturnSignal as r: result = r.value
            finally: self.env = saved
            return result
        if k == "and":
            lv, rv = self.eval(node[1]), self.eval(node[2])
            if isinstance(lv, bool) and isinstance(rv, bool): return lv and rv
            if isinstance(lv, list): return lv + ([rv] if not isinstance(rv, list) else rv)
            if isinstance(rv, list): return [lv] + rv
            return [lv, rv]
        if k == "or":
            return self.eval(node[1]) or self.eval(node[2])
        if k == "not": return not self.eval(node[1])
        if k == "neg": return -self.eval(node[1])
        if k == "==": return self.eval(node[1]) == self.eval(node[2])
        if k == "!=": return self.eval(node[1]) != self.eval(node[2])
        if k == ">":  return self.eval(node[1]) >  self.eval(node[2])
        if k == "<":  return self.eval(node[1]) <  self.eval(node[2])
        if k == "+":  return self.eval(node[1]) +  self.eval(node[2])
        if k == "-":  return self.eval(node[1]) -  self.eval(node[2])
        if k == "*":  return self.eval(node[1]) *  self.eval(node[2])
        if k == "/":  return self.eval(node[1]) /  self.eval(node[2])
        raise RuntimeError(f"Unknown node: {node}")


def run_file(path):
    with open(path) as f: code = f.read()
    tokens = tokenize(code)
    ast = Parser(tokens).parse()
    Interpreter().run(ast)

def repl():
    print("Ware 1.0 — type 'exit' to quit")
    interp = Interpreter()
    while True:
        try:
            line = input(">> ")
            if line.strip() == "exit": break
            tokens = tokenize(line)
            ast = Parser(tokens).parse()
            interp.run(ast)
        except (SyntaxError, RuntimeError) as e:
            print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
