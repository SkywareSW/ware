#!/usr/bin/env python3
"""
Ware - A programming language interpreter
Version 3.5
"""

import re, sys, os, math
try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

# ─── Signals ──────────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, v): self.value = v
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class WareError(Exception): pass

# ─── Lexer ────────────────────────────────────────────────────────────────────

TOKEN_PATTERNS = [
    ("COMMENT",  r"//[^\n]*"),
    ("FSTRING",  r'f"[^"]*"'),
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("STRING",   r'"[^"]*"'),
    ("BOOL",     r"\b(true|false)\b"),
    ("KW",       r"\b(while|during|for|each|in|if|else|try|catch|function|which|has|read|show|add|to|break|continue|range|and|or|not|is|bigger|smaller|than|return|import|constant|make|window|button|label|textbox|on|click|open|as|class|new|self|nothing|vars)\b"),
    ("IDENT",    r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("DOT",      r"\."),
    ("OP",       r"[+\-*/\(\)\[\]{}%=]"),
    ("COMMA",    r","),
    ("COLON",    r":"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
]

def tokenize(code, filename="<input>"):
    tokens = []
    pos = 0
    line = 1
    line_has_tokens = False  # track if current line already has non-whitespace tokens
    while pos < len(code):
        matched = False
        for kind, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                val = m.group(0)
                if kind == "NEWLINE":
                    line += 1
                    line_has_tokens = False
                elif kind == "DOT":
                    # standalone dot on its own line = block end
                    kind = "BLOCK_END" if not line_has_tokens else "DOT"
                    line_has_tokens = True
                elif kind not in ("SKIP", "COMMENT"):
                    line_has_tokens = True
                if kind not in ("SKIP", "COMMENT", "NEWLINE"):
                    tokens.append((kind, val, line, filename))
                pos += len(val)
                matched = True
                break
        if not matched:
            raise SyntaxError(f"[{filename}:{line}] Unknown character: {code[pos]!r}")
    return tokens

# ─── Parser ───────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] != "NEWLINE"]
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else ("EOF", "", 0, "")

    def consume(self, kind=None, val=None):
        tok = self.peek()
        if kind and tok[0] != kind:
            raise SyntaxError(f"[line {tok[2]}] Expected {kind!r} but got {tok[1]!r}")
        if val and tok[1] != val:
            raise SyntaxError(f"[line {tok[2]}] Expected '{val}' but got '{tok[1]}'")
        self.pos += 1
        return tok

    def line(self):
        return self.peek()[2]

    def parse(self):
        stmts = []
        while self.peek()[0] != "EOF":
            stmts.append(self.parse_stmt())
        return stmts

    def parse_block(self):
        stmts = []
        while self.peek()[0] not in ("BLOCK_END", "EOF") and self.peek()[1] not in ("else", "catch"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        tok = self.peek()

        # import "file.ware"
        if tok[1] == "import":
            self.consume()
            path = self.consume("STRING")[1][1:-1]
            return ("import", path)

        # constant name is expr
        if tok[1] == "constant":
            self.consume()
            name = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("const", name, self.parse_expr())

        # while
        if tok[1] == "while":
            self.consume()
            cond = self.parse_expr()
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("BLOCK_END")
            return ("while", cond, body)

        # during i, range(n)
        if tok[1] == "during":
            self.consume()
            var = self.consume("IDENT")[1]
            self.consume("COMMA")
            self.consume("KW", "range")
            self.consume("OP", "(")
            count = self.parse_expr()
            self.consume("OP", ")")
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("BLOCK_END")
            return ("during", var, count, body)

        # for each item in list
        if tok[1] == "for":
            self.consume()
            self.consume("KW", "each")
            var = self.consume("IDENT")[1]
            self.consume("KW", "in")
            iterable = self.parse_expr()
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("BLOCK_END")
            return ("foreach", var, iterable, body)

        # if / else / else if
        if tok[1] == "if":
            self.consume()
            cond = self.parse_expr()
        if self.peek()[0] == "COMMA":
            self.consume()

        body = self.parse_block()

        else_body = []

        # Support multiple else if branches
        while self.peek()[1] == "else" and self.peek(1)[1] == "if":
            self.consume()  # else
            self.consume()  # if
            elif_cond = self.parse_expr()
            if self.peek()[0] == "COMMA":
                self.consume()
            elif_body = self.parse_block()

            # Nest into else_body as another if node
            else_body = [("if", elif_cond, elif_body, else_body)]

        # Final else
        if self.peek()[1] == "else":
            self.consume()
            if self.peek()[0] == "COMMA":
                self.consume()
            else_body = self.parse_block()

        self.consume("BLOCK_END")
        return ("if", cond, body, else_body)

        # try / catch
        if tok[1] == "try":
            self.consume()
            if self.peek()[0] == "COMMA": self.consume()
            try_body = self.parse_block()
            err_var, catch_body = None, []
            if self.peek()[1] == "catch":
                self.consume()
                if self.peek()[0] == "IDENT":
                    err_var = self.consume("IDENT")[1]
                if self.peek()[0] == "COMMA": self.consume()
                catch_body = self.parse_block()
            self.consume("BLOCK_END")
            return ("try", try_body, err_var, catch_body)

        # function name which has a, b = default
        if tok[1] == "function":
            self.consume()
            name = self.consume("IDENT")[1]
            self.consume("KW", "which")
            self.consume("KW", "has")
            params = []
            # support zero-param functions: "which has,"
            if self.peek()[0] == "IDENT":
                pname = self.consume("IDENT")[1]
                default = None
                if self.peek()[1] == "=":
                    self.consume(); default = self.parse_expr()
                params.append((pname, default))
                while (self.peek()[0] == "COMMA" and self.peek(1)[0] == "IDENT"
                       and self.peek(2)[1] in ("=", ",", ".")):
                    self.consume()
                    pname = self.consume("IDENT")[1]
                    default = None
                    if self.peek()[1] == "=":
                        self.consume(); default = self.parse_expr()
                    params.append((pname, default))
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("BLOCK_END")
            return ("function", name, params, body)

        # class Name
        if tok[1] == "class":
            self.consume()
            name = self.consume("IDENT")[1]
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("BLOCK_END")
            return ("class", name, body)

        # show
        if tok[1] == "show":
            self.consume()
            return ("show", self.parse_expr())

        # read
        if tok[1] == "read":
            self.consume()
            return ("read", self.consume("IDENT")[1])

        # add to
        if tok[1] == "add":
            self.consume()
            self.consume("KW", "to")
            var = self.consume("IDENT")[1]
            self.consume("COMMA")
            return ("add", var, self.parse_expr())

        # return a, b
        if tok[1] == "return":
            self.consume()
            vals = [self.parse_expr()]
            while self.peek()[0] == "COMMA":
                self.consume(); vals.append(self.parse_expr())
            return ("return", vals)

        if tok[1] == "break":    self.consume(); return ("break",)
        if tok[1] == "continue": self.consume(); return ("continue",)

        # make window/label/textbox/button
        if tok[1] == "make":
            self.consume()
            what = self.peek()[1]
            if what == "window":
                self.consume()
                title = self.parse_expr()
                w, h = 800, 600
                if self.peek()[1] == "size":
                    self.consume()
                    w = self.parse_expr()
                    self.consume("COMMA")
                    h = self.parse_expr()
                return ("gui_window", title, w, h)
            if what == "label":
                self.consume()
                return ("gui_label", self.parse_expr())
            if what == "textbox":
                self.consume()
                return ("gui_textbox", self.consume("IDENT")[1])
            if what == "button":
                self.consume()
                lbl = self.parse_expr()
                self.consume("KW", "on")
                self.consume("KW", "click")
                if self.peek()[0] == "COMMA": self.consume()
                body = self.parse_block()
                self.consume("BLOCK_END")
                return ("gui_button", lbl, body)
            raise SyntaxError(f"Unknown make target: '{what}'")

        # open "file" as x
        if tok[1] == "open":
            self.consume()
            path = self.parse_expr()
            if self.peek()[1] == "as": self.consume()
            var = self.consume("IDENT")[1]
            return ("file_read", path, var)

        # vars  (show all variables)
        if tok[1] == "vars":
            self.consume()
            return ("vars",)

        # multi-assign: a, b is expr
        if tok[0] == "IDENT" and self.peek(1)[0] == "COMMA":
            names = [tok[1]]
            j = self.pos + 1
            while j < len(self.tokens) and self.tokens[j][0] == "COMMA":
                j += 1
                if j < len(self.tokens) and self.tokens[j][0] == "IDENT":
                    names.append(self.tokens[j][1]); j += 1
                else: break
            if j < len(self.tokens) and self.tokens[j][1] == "is":
                self.consume("IDENT")
                for _ in names[1:]:
                    self.consume("COMMA"); self.consume("IDENT")
                self.consume("KW", "is")
                return ("multi_assign", names, self.parse_expr())

        # IDENT is expr  (assignment)
        if tok[0] == "IDENT" and self.peek(1)[1] == "is" and self.peek(2)[1] not in ("bigger", "smaller", "not"):
            name = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("assign", name, self.parse_expr())

        # IDENT[idx] is expr
        if tok[0] == "IDENT" and self.peek(1)[0] == "OP" and self.peek(1)[1] == "[":
            saved = self.pos
            name = self.consume("IDENT")[1]
            self.consume("OP", "[")
            idx = self.parse_expr()
            self.consume("OP", "]")
            if self.peek()[1] == "is":
                self.consume()
                return ("index_assign", name, idx, self.parse_expr())
            self.pos = saved

        # IDENT.field is expr  or  self.field is expr  (object field assignment)
        if (tok[0] == "IDENT" or tok[1] == "self") and self.peek(1)[0] == "DOT" and self.peek(2)[0] == "IDENT" and self.peek(3)[1] == "is":
            obj = self.consume()[1]
            self.consume("DOT")
            field = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("field_assign", obj, field, self.parse_expr())

        return ("expr", self.parse_expr())

    # ── Expressions ───────────────────────────────────────────────────────────

    def parse_expr(self): return self.parse_or()

    def parse_or(self):
        left = self.parse_and_expr()
        while self.peek()[1] == "or":
            self.consume(); left = ("or", left, self.parse_and_expr())
        return left

    def parse_and_expr(self):
        left = self.parse_not()
        while self.peek()[1] == "and":
            self.consume(); left = ("and", left, self.parse_not())
        return left

    def parse_not(self):
        if self.peek()[1] == "not":
            self.consume(); return ("not", self.parse_comparison())
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_add()
        # chained comparisons: 1 is smaller than x is smaller than 10
        while self.peek()[1] == "is":
            self.consume()
            if self.peek()[1] == "not":
                self.consume(); left = ("!=", left, self.parse_add())
            elif self.peek()[1] == "bigger":
                self.consume(); self.consume("KW", "than"); left = (">", left, self.parse_add())
            elif self.peek()[1] == "smaller":
                self.consume(); self.consume("KW", "than"); left = ("<", left, self.parse_add())
            else:
                left = ("==", left, self.parse_add())
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[1] in ("+", "-"):
            op = self.consume()[1]; left = (op, left, self.parse_mul())
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[1] in ("*", "/", "%"):
            op = self.consume()[1]; left = (op, left, self.parse_unary())
        return left

    def parse_unary(self):
        if self.peek()[1] == "-":
            self.consume(); return ("neg", self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()

        if tok[0] == "NUMBER":
            self.consume(); v = tok[1]
            return ("num", float(v) if "." in v else int(v))

        if tok[0] == "STRING":
            self.consume(); return ("str", tok[1][1:-1])

        if tok[0] == "FSTRING":
            self.consume(); return ("fstr", tok[1][2:-1])

        if tok[0] == "BOOL":
            self.consume(); return ("bool", tok[1] == "true")

        if tok[1] == "nothing":
            self.consume(); return ("none",)

        # dict literal {key: val, ...}
        if tok[1] == "{":
            self.consume()
            pairs = []
            if self.peek()[1] != "}":
                k = self.parse_expr(); self.consume("COLON"); v = self.parse_expr()
                pairs.append((k, v))
                while self.peek()[0] == "COMMA":
                    self.consume()
                    k = self.parse_expr(); self.consume("COLON"); v = self.parse_expr()
                    pairs.append((k, v))
            self.consume("OP", "}")
            return ("dict_literal", pairs)

        # list literal
        if tok[1] == "[":
            self.consume()
            items = []
            if self.peek()[1] != "]":
                items.append(self.parse_expr())
                while self.peek()[0] == "COMMA":
                    self.consume(); items.append(self.parse_expr())
            self.consume("OP", "]")
            return ("list_literal", items)

        # new ClassName(args)
        if tok[1] == "new":
            self.consume()
            name = self.consume("IDENT")[1]
            args = []
            if self.peek()[1] == "(":
                self.consume()
                if self.peek()[1] != ")":
                    args.append(self.parse_expr())
                    while self.peek()[0] == "COMMA":
                        self.consume(); args.append(self.parse_expr())
                self.consume("OP", ")")
            return ("new", name, args)

        if tok[0] == "IDENT" or tok[1] == "self":
            self.consume(); name = tok[1]
            # function call
            if self.peek()[1] == "(":
                self.consume()
                args = []
                if self.peek()[1] != ")":
                    args.append(self.parse_expr())
                    while self.peek()[0] == "COMMA":
                        self.consume(); args.append(self.parse_expr())
                self.consume("OP", ")")
                node = ("call", name, args)
            else:
                node = ("var", name)
            # index / field access chaining
            while True:
                if self.peek()[1] == "[":
                    self.consume(); idx = self.parse_expr(); self.consume("OP", "]")
                    node = ("index", node, idx)
                elif self.peek()[0] == "DOT" and self.peek(1)[0] == "IDENT":
                    self.consume(); field = self.consume("IDENT")[1]
                    if self.peek()[1] == "(":
                        self.consume()
                        args = []
                        if self.peek()[1] != ")":
                            args.append(self.parse_expr())
                            while self.peek()[0] == "COMMA":
                                self.consume(); args.append(self.parse_expr())
                        self.consume("OP", ")")
                        node = ("method_call", node, field, args)
                    else:
                        node = ("field", node, field)
                else:
                    break
            return node

        if tok[1] == "(":
            self.consume(); expr = self.parse_expr(); self.consume("OP", ")"); return expr

        raise SyntaxError(f"[line {tok[2]}] Unexpected token: {tok[1]!r}")


# ─── WareClass & WareInstance ─────────────────────────────────────────────────

class WareClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods  # dict of name -> ("__func__", params, body, closure)

class WareInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __repr__(self):
        return f"<{self.klass.name} object>"


# ─── Interpreter ──────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self, source_dir="."):
        self.env = {}
        self.constants = set()
        self.source_dir = source_dir
        self.gui_root = None
        self.gui_widgets = {}
        self._setup_builtins()

    def _setup_builtins(self):
        E = self.env
        # Math
        E["pi"]       = math.pi
        E["sqrt"]     = lambda a: math.sqrt(a[0])
        E["abs"]      = lambda a: abs(a[0])
        E["round"]    = lambda a: round(a[0], int(a[1]) if len(a) > 1 else 0)
        E["floor"]    = lambda a: math.floor(a[0])
        E["ceil"]     = lambda a: math.ceil(a[0])
        E["power"]    = lambda a: a[0] ** a[1]
        E["log"]      = lambda a: math.log(a[0])
        E["sin"]      = lambda a: math.sin(a[0])
        E["cos"]      = lambda a: math.cos(a[0])
        # String
        E["length"]   = lambda a: len(a[0])
        E["upper"]    = lambda a: str(a[0]).upper()
        E["lower"]    = lambda a: str(a[0]).lower()
        E["trim"]     = lambda a: str(a[0]).strip()
        E["split"]    = lambda a: str(a[0]).split(a[1] if len(a) > 1 else " ")
        E["join"]     = lambda a: str(a[1]).join(str(x) for x in a[0])
        E["replace"]  = lambda a: str(a[0]).replace(str(a[1]), str(a[2]))
        E["contains"] = lambda a: str(a[1]) in str(a[0])
        E["starts"]   = lambda a: str(a[0]).startswith(str(a[1]))
        E["ends"]     = lambda a: str(a[0]).endswith(str(a[1]))
        E["slice"]    = lambda a: a[0][int(a[1])-1:int(a[2])]
        E["number"]   = lambda a: float(a[0]) if "." in str(a[0]) else int(a[0])
        E["text"]     = lambda a: str(a[0])
        # List
        E["size"]     = lambda a: len(a[0])
        E["first"]    = lambda a: a[0][0]
        E["last"]     = lambda a: a[0][-1]
        E["reverse"]  = lambda a: list(reversed(a[0]))
        E["sort"]     = lambda a: sorted(a[0])
        E["remove"]   = lambda a: [x for i,x in enumerate(a[0]) if i != int(a[1])-1]
        E["has"]      = lambda a: a[1] in a[0]
        E["index_of"] = lambda a: (a[0].index(a[1]) + 1) if a[1] in a[0] else 0
        # Dict
        E["keys"]     = lambda a: list(a[0].keys()) if isinstance(a[0], dict) else []
        E["values"]   = lambda a: list(a[0].values()) if isinstance(a[0], dict) else []
        E["has_key"]  = lambda a: a[1] in a[0] if isinstance(a[0], dict) else False
        # File
        E["write"]    = lambda a: open(str(a[0]),"w").write(str(a[1])) and None
        E["append"]   = lambda a: open(str(a[0]),"a").write(str(a[1])+"\n") and None
        # Type
        E["is_number"]   = lambda a: isinstance(a[0],(int,float)) and not isinstance(a[0],bool)
        E["is_text"]     = lambda a: isinstance(a[0],str)
        E["is_list"]     = lambda a: isinstance(a[0],list)
        E["is_dict"]     = lambda a: isinstance(a[0],dict)
        E["is_bool"]     = lambda a: isinstance(a[0],bool)
        E["type_of"]     = lambda a: ("number" if (isinstance(a[0],(int,float)) and not isinstance(a[0],bool)) else "text" if isinstance(a[0],str) else "list" if isinstance(a[0],list) else "dict" if isinstance(a[0],dict) else "bool" if isinstance(a[0],bool) else "object" if hasattr(a[0],"fields") else "nothing" if a[0] is None else "unknown")
        # String inspection
        E["is_empty"]    = lambda a: len(a[0]) == 0
        E["count"]       = lambda a: str(a[0]).count(str(a[1]))
        E["find"]        = lambda a: (str(a[0]).find(str(a[1])) + 1) if str(a[1]) in str(a[0]) else 0
        E["is_upper"]    = lambda a: str(a[0]).isupper()
        E["is_lower"]    = lambda a: str(a[0]).islower()
        E["is_numeric"]  = lambda a: str(a[0]).replace(".","",1).replace("-","",1).isnumeric() if str(a[0]) else False
        E["is_alpha"]    = lambda a: str(a[0]).isalpha()
        E["repeat"]      = lambda a: str(a[0]) * int(a[1])
        E["pad_left"]    = lambda a: str(a[0]).rjust(int(a[1]), str(a[2]) if len(a) > 2 else " ")
        E["pad_right"]   = lambda a: str(a[0]).ljust(int(a[1]), str(a[2]) if len(a) > 2 else " ")
        E["strip_chars"] = lambda a: str(a[0]).strip(str(a[1]))
        E["char_at"]     = lambda a: str(a[0])[int(a[1])-1]
        E["words"]       = lambda a: str(a[0]).split()
        E["lines"]       = lambda a: str(a[0]).splitlines()
        E["to_chars"]    = lambda a: list(str(a[0]))
        # List inspection
        E["is_empty"]    = lambda a: len(a[0]) == 0   # works for both strings and lists
        E["count_in"]    = lambda a: a[0].count(a[1]) if isinstance(a[0],list) else str(a[0]).count(str(a[1]))
        E["any_true"]    = lambda a: any(a[0])
        E["all_true"]    = lambda a: all(a[0])
        E["sum_list"]    = lambda a: sum(a[0])
        E["max_of"]      = lambda a: max(a[0])
        E["min_of"]      = lambda a: min(a[0])
        E["flatten"]     = lambda a: [x for sub in a[0] for x in (sub if isinstance(sub,list) else [sub])]
        E["unique"]      = lambda a: list(dict.fromkeys(a[0]))
        # Number formatting
        E["to_fixed"]    = lambda a: f"{float(a[0]):.{int(a[1])}f}"
        E["to_hex"]      = lambda a: hex(int(a[0]))[2:]
        E["to_bin"]      = lambda a: bin(int(a[0]))[2:]
        E["clamp"]       = lambda a: max(a[1], min(a[2], a[0]))
        E["random"]      = lambda a: __import__("random").random()
        E["random_int"]  = lambda a: __import__("random").randint(int(a[0]), int(a[1]))

    def _lookup(self, name):
        """Walk env chain to find variable."""
        env = self.env
        while env is not None:
            if name in env:
                return env[name]
            env = env.get("__parent__")
        raise WareError(f"Undefined variable: '{name}'")

    def _update(self, name, val):
        """Update existing variable in its scope."""
        env = self.env
        while env is not None:
            if name in env:
                env[name] = val
                return
            env = env.get("__parent__")
        # not found - create in current scope
        self.env[name] = val

    def run(self, stmts):
        for s in stmts: self.exec(s)

    def fmt(self, val):
        if val is None:                return "nothing"
        if isinstance(val, bool):      return "true" if val else "false"
        if isinstance(val, WareInstance): return repr(val)
        if isinstance(val, dict):
            pairs = ", ".join(f"{self.fmt(k)}: {self.fmt(v)}" for k,v in val.items())
            return "{" + pairs + "}"
        if isinstance(val, list):      return "[" + ", ".join(self.fmt(v) for v in val) + "]"
        if isinstance(val, float) and val == int(val): return str(int(val))
        return str(val)

    def exec(self, stmt, local_env=None):
        k = stmt[0]

        if k == "import":
            path = os.path.join(self.source_dir, stmt[1])
            with open(path) as f: code = f.read()
            tokens = tokenize(code, stmt[1])
            ast = Parser(tokens).parse()
            sub = Interpreter(os.path.dirname(os.path.abspath(path)))
            sub.env = self.env
            sub.constants = self.constants
            sub.run(ast)

        elif k == "const":
            if stmt[1] in self.constants:
                raise WareError(f"Cannot reassign constant '{stmt[1]}'")
            self.env[stmt[1]] = self.eval(stmt[2])
            self.constants.add(stmt[1])

        elif k == "assign":
            if stmt[1] in self.constants:
                raise WareError(f"Cannot reassign constant '{stmt[1]}'")
            self._update(stmt[1], self.eval(stmt[2]))

        elif k == "multi_assign":
            val = self.eval(stmt[2])
            names = stmt[1]
            if isinstance(val, tuple):
                for name, v in zip(names, val): self.env[name] = v
            else:
                self.env[names[0]] = val

        elif k == "index_assign":
            container = self.env.get(stmt[1])
            idx_val = self.eval(stmt[2])
            val = self.eval(stmt[3])
            if isinstance(container, list):
                container[int(idx_val) - 1] = val
            elif isinstance(container, dict):
                container[idx_val] = val
            else:
                raise WareError(f"'{stmt[1]}' is not a list or dict")

        elif k == "field_assign":
            obj = self.env.get(stmt[1])
            if not isinstance(obj, WareInstance):
                raise WareError(f"'{stmt[1]}' is not an object")
            obj.fields[stmt[2]] = self.eval(stmt[3])

        elif k == "show":
            val = self.eval(stmt[1])
            print(", ".join(self.fmt(v) for v in val) if isinstance(val, tuple) else self.fmt(val))

        elif k == "read":
            raw = input()
            try: self.env[stmt[1]] = int(raw)
            except ValueError:
                try: self.env[stmt[1]] = float(raw)
                except ValueError: self.env[stmt[1]] = raw

        elif k == "add":
            lst = self.env.get(stmt[1])
            if not isinstance(lst, list): raise WareError(f"'{stmt[1]}' is not a list")
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

        elif k == "foreach":
            iterable = self.eval(stmt[2])
            if isinstance(iterable, dict): iterable = list(iterable.keys())
            for item in iterable:
                self.env[stmt[1]] = item
                try:
                    for s in stmt[3]: self.exec(s)
                except BreakSignal: break
                except ContinueSignal: continue

        elif k == "if":
            body = stmt[2] if self.eval(stmt[1]) else stmt[3]
            for s in body: self.exec(s)

        elif k == "try":
            try:
                for s in stmt[1]: self.exec(s)
            except (WareError, Exception) as e:
                if stmt[2]: self.env[stmt[2]] = str(e)
                for s in stmt[3]: self.exec(s)

        elif k == "function":
            # params is list of (name, default_node_or_None)
            # Store reference to current env for proper closure support
            self.env[stmt[1]] = ("__func__", stmt[2], stmt[3], self.env)

        elif k == "class":
            methods = {}
            # parse class body: collect function definitions
            sub_interp = Interpreter(self.source_dir)
            sub_interp.env = dict(self.env)
            for s in stmt[2]:
                if s[0] == "function":
                    methods[s[1]] = ("__func__", s[2], s[3], sub_interp.env)
                # support field defaults via assign
            self.env[stmt[1]] = WareClass(stmt[1], methods)

        elif k == "return":
            vals = [self.eval(v) for v in stmt[1]]
            raise ReturnSignal(tuple(vals) if len(vals) > 1 else vals[0])

        elif k == "break": raise BreakSignal()
        elif k == "continue": raise ContinueSignal()
        elif k == "expr": self.eval(stmt[1])

        elif k == "vars":
            for name, val in sorted(self.env.items()):
                if callable(val): continue
                if isinstance(val, WareClass): continue
                if isinstance(val, tuple) and val[0] == "__func__": continue
                if name in ("pi",): continue
                print(f"  {name} = {self.fmt(val)}")

        elif k == "gui_window": self._gui_window(stmt)
        elif k == "gui_label":  self._gui_label(stmt)
        elif k == "gui_button": self._gui_button(stmt)
        elif k == "gui_textbox":self._gui_textbox(stmt)

        elif k == "file_read":
            path = self.eval(stmt[1])
            with open(path) as f: self.env[stmt[2]] = f.read()

    # ── GUI ───────────────────────────────────────────────────────────────────

    def _gui_window(self, stmt):
        if not HAS_GUI: raise WareError("GUI requires tkinter (not installed)")
        title = self.eval(stmt[1])
        w = self.eval(stmt[2]) if isinstance(stmt[2], tuple) else 800
        h = self.eval(stmt[3]) if isinstance(stmt[3], tuple) else 600
        self.gui_root = tk.Tk()
        self.gui_root.title(str(title))
        self.gui_root.geometry(f"{int(w)}x{int(h)}")
        self.gui_root.configure(bg="#1a1a2e")

    def _gui_label(self, stmt):
        if not self.gui_root: raise WareError("No window. Use 'make window' first.")
        lbl = tk.Label(self.gui_root, text=str(self.eval(stmt[1])),
                       bg="#1a1a2e", fg="#e0e0f0", font=("Arial", 12), pady=5)
        lbl.pack()

    def _gui_button(self, stmt):
        if not self.gui_root: raise WareError("No window. Use 'make window' first.")
        text, body = self.eval(stmt[1]), stmt[2]
        def on_click():
            try:
                for s in body: self.exec(s)
            except Exception as e:
                messagebox.showerror("Ware Error", str(e))
        btn = tk.Button(self.gui_root, text=str(text), command=on_click,
                        bg="#3a3a5c", fg="#e0e0f0", font=("Arial", 11),
                        relief="flat", padx=10, pady=5, cursor="hand2")
        btn.pack(pady=4)

    def _gui_textbox(self, stmt):
        if not self.gui_root: raise WareError("No window. Use 'make window' first.")
        name = stmt[1]
        entry = tk.Entry(self.gui_root, bg="#22223a", fg="#e0e0f0",
                         font=("Arial", 11), insertbackground="#a78bfa",
                         relief="flat", width=30)
        entry.pack(pady=4)
        self.gui_widgets[name] = entry
        self.env[name] = entry

    # ── Evaluator ─────────────────────────────────────────────────────────────

    def eval(self, node):
        k = node[0]
        if k == "num":  return node[1]
        if k == "str":  return node[1]
        if k == "bool": return node[1]
        if k == "none": return None

        if k == "fstr":
            def replacer(m):
                val = self.eval(Parser(tokenize(m.group(1))).parse_expr())
                return self.fmt(val)
            return re.sub(r"\{([^}]+)\}", replacer, node[1])

        if k == "list_literal": return [self.eval(i) for i in node[1]]

        if k == "dict_literal":
            return {self.eval(kk): self.eval(vv) for kk, vv in node[1]}

        if k == "var":
            name = node[1]
            val = self._lookup(name)
            if HAS_GUI and isinstance(val, tk.Entry): return val.get()
            return val

        if k == "index":
            obj = self.eval(node[1])
            if HAS_GUI and isinstance(obj, tk.Entry): obj = obj.get()
            idx = self.eval(node[2])
            if isinstance(obj, dict): return obj[idx]
            if isinstance(obj, str):  return obj[int(idx) - 1]
            if isinstance(obj, list): return obj[int(idx) - 1]
            raise WareError("Cannot index this value")

        if k == "field":
            obj = self.eval(node[1])
            if isinstance(obj, WareInstance):
                if node[2] in obj.fields: return obj.fields[node[2]]
                raise WareError(f"Object has no field '{node[2]}'")
            if isinstance(obj, dict): return obj.get(node[2])
            raise WareError(f"Cannot access field on {type(obj).__name__}")

        if k == "method_call":
            obj = self.eval(node[1])
            method_name = node[2]
            args = [self.eval(a) for a in node[3]]
            if isinstance(obj, WareInstance):
                method = obj.klass.methods.get(method_name)
                if not method: raise WareError(f"No method '{method_name}' on {obj.klass.name}")
                _, params, body, closure = method
                saved = self.env
                local = {**closure}
                local["self"] = obj
                # bind params
                for (pname, pdefault), arg in zip(params, args):
                    local[pname] = arg
                # fill defaults for missing args
                for i, (pname, pdefault) in enumerate(params):
                    if i >= len(args):
                        if pdefault is None: raise WareError(f"Missing argument '{pname}'")
                        local[pname] = self.eval(pdefault)
                self.env = local
                result = None
                try:
                    for s in body: self.exec(s)
                except ReturnSignal as r: result = r.value
                finally: self.env = saved
                return result
            raise WareError(f"Cannot call method on {type(obj).__name__}")

        if k == "new":
            klass = self.env.get(node[1])
            if not isinstance(klass, WareClass):
                raise WareError(f"'{node[1]}' is not a class")
            instance = WareInstance(klass)
            # call init if it exists
            if "init" in klass.methods:
                method = klass.methods["init"]
                _, params, body, closure = method
                args = [self.eval(a) for a in node[2]]
                saved = self.env
                local = {**closure, "self": instance}
                for (pname, pdefault), arg in zip(params, args):
                    local[pname] = arg
                for i, (pname, pdefault) in enumerate(params):
                    if i >= len(args):
                        if pdefault is None: raise WareError(f"Missing argument '{pname}'")
                        local[pname] = self.eval(pdefault)
                self.env = local
                try:
                    for s in body: self.exec(s)
                except ReturnSignal: pass
                finally: self.env = saved
            return instance

        if k == "call":
            name, arg_nodes = node[1], node[2]
            args = [self.eval(a) for a in arg_nodes]
            func = self.env.get(name)
            if func is None: raise WareError(f"Undefined function: '{name}'")
            if callable(func): return func(args)
            if isinstance(func, tuple) and func[0] == "__func__":
                _, params, body, closure = func
                saved = self.env
                # Create new scope inheriting from closure
                local = {"__parent__": closure}
                for i, (pname, pdefault) in enumerate(params):
                    if i < len(args):
                        local[pname] = args[i]
                    elif pdefault is not None:
                        local[pname] = self.eval(pdefault)
                    else:
                        raise WareError(f"Missing argument '{pname}' in call to '{name}'")
                self.env = local
                result = None
                try:
                    for s in body: self.exec(s)
                except ReturnSignal as r: result = r.value
                finally: self.env = saved
                return result
            raise WareError(f"'{name}' is not callable")

        if k == "and":
            lv, rv = self.eval(node[1]), self.eval(node[2])
            if isinstance(lv, bool) and isinstance(rv, bool): return lv and rv
            if isinstance(lv, list): return lv + ([rv] if not isinstance(rv, list) else rv)
            if isinstance(rv, list): return [lv] + rv
            return [lv, rv]
        if k == "or":  return self.eval(node[1]) or self.eval(node[2])
        if k == "not": return not self.eval(node[1])
        if k == "neg": return -self.eval(node[1])
        if k == "==":  return self.eval(node[1]) == self.eval(node[2])
        if k == "!=":  return self.eval(node[1]) != self.eval(node[2])
        if k == ">":   return self.eval(node[1]) >  self.eval(node[2])
        if k == "<":   return self.eval(node[1]) <  self.eval(node[2])
        if k == "+":
            l, r = self.eval(node[1]), self.eval(node[2])
            # string * number via +? No - handle str repeat in *
            return l + r
        if k == "-":   return self.eval(node[1]) -  self.eval(node[2])
        if k == "*":
            l, r = self.eval(node[1]), self.eval(node[2])
            # string repeat: "ha" * 3
            if isinstance(l, str) and isinstance(r, int): return l * r
            if isinstance(r, str) and isinstance(l, int): return r * l
            return l * r
        if k == "/":   return self.eval(node[1]) /  self.eval(node[2])
        if k == "%":   return self.eval(node[1]) %  self.eval(node[2])
        raise WareError(f"Unknown node: {node}")


# ─── Build Executable ─────────────────────────────────────────────────────────

def build_exe(ware_path):
    """Wrap a .ware file into a standalone Python script, then use PyInstaller if available."""
    with open(ware_path) as f:
        ware_code = f.read()

    # Embed the interpreter + the ware source into a launcher script
    interp_src = open(__file__).read()
    # Remove the __main__ block so we can replace it
    interp_src = interp_src[:interp_src.index("# ─── Build Executable")]

    launcher = interp_src + f'''
# ─── Embedded Program ────────────────────────────────────────────────────────
_WARE_SOURCE = {repr(ware_code)}
_WARE_FILE   = {repr(ware_path)}

if __name__ == "__main__":
    tokens = tokenize(_WARE_SOURCE, _WARE_FILE)
    ast = Parser(tokens).parse()
    interp = Interpreter(source_dir=os.path.dirname(os.path.abspath(_WARE_FILE)))
    interp.run(ast)
    if interp.gui_root:
        interp.gui_root.mainloop()
'''

    base = os.path.splitext(ware_path)[0]
    launcher_path = base + "_launcher.py"
    with open(launcher_path, "w") as f:
        f.write(launcher)
    print(f"Launcher script written to: {launcher_path}")

    # Try PyInstaller
    try:
        import PyInstaller
        import subprocess
        print("PyInstaller found — building executable...")
        subprocess.run([sys.executable, "-m", "PyInstaller",
                        "--onefile", "--name", os.path.basename(base),
                        launcher_path], check=True)
        print(f"Executable built in: dist/{os.path.basename(base)}")
    except ImportError:
        print("PyInstaller not installed.")
        print(f"To build an executable, run:")
        print(f"  pip install pyinstaller")
        print(f"  pyinstaller --onefile {launcher_path}")


# ─── Entry Point ──────────────────────────────────────────────────────────────

def run_file(path):
    with open(path) as f: code = f.read()
    try:
        tokens = tokenize(code, os.path.basename(path))
        ast = Parser(tokens).parse()
        interp = Interpreter(source_dir=os.path.dirname(os.path.abspath(path)))
        interp.run(ast)
        if interp.gui_root:
            interp.gui_root.mainloop()
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except WareError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def repl():
    print("Ware 3.0 — type 'exit' to quit, 'vars' to see variables")
    interp = Interpreter()
    while True:
        try:
            line = input(">> ")
            if line.strip() == "exit": break
            if not line.strip(): continue
            tokens = tokenize(line)
            ast = Parser(tokens).parse()
            interp.run(ast)
        except (SyntaxError, WareError) as e:
            print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            print(); break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build" and len(sys.argv) > 2:
            build_exe(sys.argv[2])
        else:
            run_file(sys.argv[1])
    else:
        repl()
