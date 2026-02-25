#!/usr/bin/env python3
"""
Ware - A programming language interpreter
Version 2.0 - Advanced Edition
"""

import re
import sys
import os
import math
import json
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
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
    ("BOOL",     r"\b(true|false)\\b"),
    ("KW",       r"\b(while|during|if|else|try|catch|function|which|has|read|show|add|to|break|continue|range|and|or|not|is|bigger|smaller|than|return|import|constant|make|window|button|label|input|textbox|on|click|open|run|as)\b"),
    ("IDENT",    r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("DOT",      r"\."),
    ("OP",       r"[+\-*/\(\)\[\]{}%]"),
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

# ─── Parser ───────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] != "NEWLINE"]
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else ("EOF", "")

    def consume(self, kind=None, val=None):
        tok = self.peek()
        if kind and tok[0] != kind:
            raise SyntaxError(f"Expected {kind!r} but got {tok!r}")
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
        while self.peek()[0] not in ("DOT", "EOF") and self.peek()[1] not in ("else", "catch"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        tok = self.peek()

        # import "file.ware"
        if tok == ("KW", "import"):
            self.consume()
            path = self.consume("STRING")[1][1:-1]
            return ("import", path)

        # const name is expr
        if tok == ("KW", "constant"):
            self.consume()
            name = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("const", name, self.parse_expr())

        # while
        if tok == ("KW", "while"):
            self.consume()
            cond = self.parse_expr()
            if self.peek()[0] == "COMMA": self.consume()
            body = self.parse_block()
            self.consume("DOT")
            return ("while", cond, body)

        # during
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

        # if / else
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

        # try / catch
        if tok == ("KW", "try"):
            self.consume()
            if self.peek()[0] == "COMMA": self.consume()
            try_body = self.parse_block()
            err_var = None
            catch_body = []
            if self.peek() == ("KW", "catch"):
                self.consume()
                if self.peek()[0] == "IDENT":
                    err_var = self.consume("IDENT")[1]
                if self.peek()[0] == "COMMA": self.consume()
                catch_body = self.parse_block()
            self.consume("DOT")
            return ("try", try_body, err_var, catch_body)

        # function
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

        # show
        if tok == ("KW", "show"):
            self.consume()
            return ("show", self.parse_expr())

        # read
        if tok == ("KW", "read"):
            self.consume()
            return ("read", self.consume("IDENT")[1])

        # add to
        if tok == ("KW", "add"):
            self.consume()
            self.consume("KW", "to")
            var = self.consume("IDENT")[1]
            self.consume("COMMA")
            return ("add", var, self.parse_expr())

        # return (supports multiple values: return a, b)
        if tok == ("KW", "return"):
            self.consume()
            vals = [self.parse_expr()]
            while self.peek()[0] == "COMMA":
                self.consume()
                vals.append(self.parse_expr())
            return ("return", vals)

        if tok == ("KW", "break"):
            self.consume(); return ("break",)
        if tok == ("KW", "continue"):
            self.consume(); return ("continue",)

        # GUI: window "Title" size 800, 600
        if tok == ("KW", "make"):
            self.consume()
            what = self.peek()[1]

            if what == "window":
                self.consume()
                title = self.parse_expr()
                width, height = 800, 600
                if self.peek()[1] == "size":
                    self.consume()
                    width = self.eval_later(self.parse_expr())
                    self.consume("COMMA")
                    height = self.eval_later(self.parse_expr())
                return ("gui_window", title, width, height)

            if what == "label":
                self.consume()
                return ("gui_label", self.parse_expr())

            if what == "textbox":
                self.consume()
                return ("gui_textbox", self.consume("IDENT")[1])

            if what == "button":
                self.consume()
                label = self.parse_expr()
                self.consume("KW", "on")
                self.consume("KW", "click")
                if self.peek()[0] == "COMMA": self.consume()
                body = self.parse_block()
                self.consume("DOT")
                return ("gui_button", label, body)

            raise SyntaxError(f"Unknown make target: '{what}'")

        # open "file.txt"  → read file
        if tok == ("KW", "open"):
            self.consume()
            path = self.parse_expr()
            if self.peek()[1] == "as": self.consume()
            var = self.consume("IDENT")[1]
            return ("file_read", path, var)

        # multi-assign: a, b is func()
        if tok[0] == "IDENT" and self.peek(1)[0] == "COMMA":
            # peek ahead to find "is"
            i = 1
            names = [tok[1]]
            j = self.pos + 1
            while j < len(self.tokens) and self.tokens[j][0] == "COMMA":
                j += 1
                if j < len(self.tokens) and self.tokens[j][0] == "IDENT":
                    names.append(self.tokens[j][1])
                    j += 1
                else:
                    break
            if j < len(self.tokens) and self.tokens[j] == ("KW", "is"):
                # consume all the names and "is"
                self.consume("IDENT")
                for extra in names[1:]:
                    self.consume("COMMA")
                    self.consume("IDENT")
                self.consume("KW", "is")
                return ("multi_assign", names, self.parse_expr())

        # assignment or expression
        if tok[0] == "IDENT" and self.peek(1) == ("KW", "is") and self.peek(2)[1] not in ("bigger", "smaller", "not"):
            name = self.consume("IDENT")[1]
            self.consume("KW", "is")
            return ("assign", name, self.parse_expr())

        # IDENT[idx] is expr  (index assignment)
        if tok[0] == "IDENT" and self.peek(1) == ("OP", "["):
            saved = self.pos
            name = self.consume("IDENT")[1]
            self.consume("OP", "[")
            idx = self.parse_expr()
            self.consume("OP", "]")
            if self.peek() == ("KW", "is"):
                self.consume()
                val = self.parse_expr()
                return ("index_assign", name, idx, val)
            self.pos = saved

        return ("expr", self.parse_expr())

    def eval_later(self, node):
        # placeholder: return node for later eval
        return node

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
                self.consume(); return ("!=", left, self.parse_add())
            elif self.peek() == ("KW", "bigger"):
                self.consume(); self.consume("KW", "than"); return (">", left, self.parse_add())
            elif self.peek() == ("KW", "smaller"):
                self.consume(); self.consume("KW", "than"); return ("<", left, self.parse_add())
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
        while self.peek()[1] in ("*", "/", "%"):
            op = self.consume()[1]
            left = (op, left, self.parse_unary())
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

        # list literal [1, 2, 3]
        if tok == ("OP", "["):
            self.consume()
            items = []
            if self.peek() != ("OP", "]"):
                items.append(self.parse_expr())
                while self.peek()[0] == "COMMA":
                    self.consume(); items.append(self.parse_expr())
            self.consume("OP", "]")
            return ("list_literal", items)

        if tok[0] == "IDENT":
            self.consume(); name = tok[1]
            if self.peek() == ("OP", "("):
                self.consume()
                args = []
                if self.peek() != ("OP", ")"):
                    args.append(self.parse_expr())
                    while self.peek()[0] == "COMMA":
                        self.consume(); args.append(self.parse_expr())
                self.consume("OP", ")")
                node = ("call", name, args)
            else:
                node = ("var", name)
            while self.peek() == ("OP", "["):
                self.consume(); idx = self.parse_expr(); self.consume("OP", "]")
                node = ("index", node, idx)
            if self.peek() == ("DOT",) or (self.peek()[0] == "DOT" and self.peek(1)[0] == "IDENT"):
                pass  # method call handled via builtins
            return node

        if tok == ("OP", "("):
            self.consume(); expr = self.parse_expr(); self.consume("OP", ")"); return expr

        raise SyntaxError(f"Unexpected token: {tok}")


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
        # Math
        self.env["pi"]    = math.pi
        self.env["sqrt"]  = lambda args: math.sqrt(args[0])
        self.env["abs"]   = lambda args: abs(args[0])
        self.env["round"] = lambda args: round(args[0], int(args[1]) if len(args) > 1 else 0)
        self.env["floor"] = lambda args: math.floor(args[0])
        self.env["ceil"]  = lambda args: math.ceil(args[0])
        self.env["power"] = lambda args: args[0] ** args[1]
        self.env["log"]   = lambda args: math.log(args[0])
        self.env["sin"]   = lambda args: math.sin(args[0])
        self.env["cos"]   = lambda args: math.cos(args[0])
        # String
        self.env["length"]    = lambda args: len(args[0])
        self.env["upper"]     = lambda args: str(args[0]).upper()
        self.env["lower"]     = lambda args: str(args[0]).lower()
        self.env["trim"]      = lambda args: str(args[0]).strip()
        self.env["split"]     = lambda args: str(args[0]).split(args[1] if len(args) > 1 else " ")
        self.env["join"]      = lambda args: str(args[1]).join([str(x) for x in args[0]])
        self.env["replace"]   = lambda args: str(args[0]).replace(str(args[1]), str(args[2]))
        self.env["contains"]  = lambda args: str(args[1]) in str(args[0])
        self.env["starts"]    = lambda args: str(args[0]).startswith(str(args[1]))
        self.env["ends"]      = lambda args: str(args[0]).endswith(str(args[1]))
        self.env["slice"]     = lambda args: args[0][int(args[1])-1 : int(args[2])]
        self.env["number"]    = lambda args: float(args[0]) if "." in str(args[0]) else int(args[0])
        self.env["text"]      = lambda args: str(args[0])
        # List
        self.env["size"]      = lambda args: len(args[0])
        self.env["first"]     = lambda args: args[0][0]
        self.env["last"]      = lambda args: args[0][-1]
        self.env["reverse"]   = lambda args: list(reversed(args[0]))
        self.env["sort"]      = lambda args: sorted(args[0])
        self.env["remove"]    = lambda args: [x for i, x in enumerate(args[0]) if i != int(args[1]) - 1]
        self.env["has"]       = lambda args: args[1] in args[0]
        # File
        self.env["write"]     = self._builtin_write
        self.env["append"]    = self._builtin_append
        # Type check
        self.env["is_number"] = lambda args: isinstance(args[0], (int, float)) and not isinstance(args[0], bool)
        self.env["is_text"]   = lambda args: isinstance(args[0], str)
        self.env["is_list"]   = lambda args: isinstance(args[0], list)

    def _builtin_write(self, args):
        path, content = str(args[0]), str(args[1])
        with open(path, "w") as f: f.write(content)
        return None

    def _builtin_append(self, args):
        path, content = str(args[0]), str(args[1])
        with open(path, "a") as f: f.write(content + "\n")
        return None

    def run(self, stmts):
        for s in stmts: self.exec(s)

    def fmt(self, val):
        if isinstance(val, bool):  return "true" if val else "false"
        if isinstance(val, list):  return "[" + ", ".join(self.fmt(v) for v in val) + "]"
        if isinstance(val, float) and val == int(val): return str(int(val))
        if val is None: return "nothing"
        return str(val)

    def exec(self, stmt):
        k = stmt[0]

        if k == "import":
            path = os.path.join(self.source_dir, stmt[1])
            with open(path) as f: code = f.read()
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            sub = Interpreter(os.path.dirname(path))
            sub.env = self.env  # share environment
            sub.constants = self.constants
            sub.run(ast)

        elif k == "const":
            if stmt[1] in self.constants:
                raise WareError(f"Cannot reassign constant '{stmt[1]}'")
            self.env[stmt[1]] = self.eval(stmt[2])
            self.constants.add(stmt[1])

        elif k == "multi_assign":
            val = self.eval(stmt[2])
            names = stmt[1]
            if isinstance(val, tuple):
                for name, v in zip(names, val):
                    self.env[name] = v
            else:
                self.env[names[0]] = val

        elif k == "assign":
            if stmt[1] in self.constants:
                raise WareError(f"Cannot reassign constant '{stmt[1]}'")
            self.env[stmt[1]] = self.eval(stmt[2])

        elif k == "index_assign":
            lst = self.env.get(stmt[1])
            if not isinstance(lst, list): raise WareError(f"'{stmt[1]}' is not a list")
            idx = int(self.eval(stmt[2])) - 1
            lst[idx] = self.eval(stmt[3])

        elif k == "show":
            val = self.eval(stmt[1])
            if isinstance(val, tuple):  # multiple return values
                print(", ".join(self.fmt(v) for v in val))
            else:
                print(self.fmt(val))

        elif k == "read":
            raw = input()
            try:
                self.env[stmt[1]] = int(raw)
            except ValueError:
                try:
                    self.env[stmt[1]] = float(raw)
                except ValueError:
                    self.env[stmt[1]] = raw

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
            self.env[stmt[1]] = ("__func__", stmt[2], stmt[3], dict(self.env))

        elif k == "return":
            vals = [self.eval(v) for v in stmt[1]]
            raise ReturnSignal(tuple(vals) if len(vals) > 1 else vals[0])

        elif k == "break": raise BreakSignal()
        elif k == "continue": raise ContinueSignal()
        elif k == "expr": self.eval(stmt[1])

        # ── GUI ──
        elif k == "gui_window":
            self._gui_window(stmt)
        elif k == "gui_label":
            self._gui_label(stmt)
        elif k == "gui_button":
            self._gui_button(stmt)
        elif k == "gui_textbox":
            self._gui_textbox(stmt)

        # ── File ──
        elif k == "file_read":
            path = self.eval(stmt[1])
            with open(path) as f: content = f.read()
            self.env[stmt[2]] = content

    # ── GUI helpers ───────────────────────────────────────────────────────────

    def _gui_window(self, stmt):
        if not HAS_GUI: raise WareError("GUI not available: tkinter is not installed")
        title = self.eval(stmt[1])
        w = self.eval(stmt[2]) if not isinstance(stmt[2], tuple) else 800
        h = self.eval(stmt[3]) if not isinstance(stmt[3], tuple) else 600
        # evaluate width/height if they're AST nodes
        if isinstance(w, tuple): w = self.eval(w)
        if isinstance(h, tuple): h = self.eval(h)
        self.gui_root = tk.Tk()
        self.gui_root.title(str(title))
        self.gui_root.geometry(f"{int(w)}x{int(h)}")
        self.gui_root.configure(bg="#1a1a2e")

    def _gui_label(self, stmt):
        if not self.gui_root: raise WareError("No window open. Use 'window' first.")
        text = self.eval(stmt[1])
        lbl = tk.Label(self.gui_root, text=str(text),
                       bg="#1a1a2e", fg="#e0e0f0",
                       font=("Arial", 12), pady=5)
        lbl.pack()
        return lbl

    def _gui_button(self, stmt):
        if not self.gui_root: raise WareError("No window open. Use 'window' first.")
        text = self.eval(stmt[1])
        body = stmt[2]
        def on_click():
            try:
                for s in body: self.exec(s)
            except Exception as e:
                messagebox.showerror("Ware Error", str(e))
        btn = tk.Button(self.gui_root, text=str(text),
                        command=on_click,
                        bg="#3a3a5c", fg="#e0e0f0",
                        font=("Arial", 11), relief="flat",
                        padx=10, pady=5, cursor="hand2")
        btn.pack(pady=4)

    def _gui_textbox(self, stmt):
        if not self.gui_root: raise WareError("No window open. Use 'window' first.")
        name = stmt[1]
        entry = tk.Entry(self.gui_root,
                         bg="#22223a", fg="#e0e0f0",
                         font=("Arial", 11),
                         insertbackground="#a78bfa",
                         relief="flat", width=30)
        entry.pack(pady=4)
        # make the variable a live proxy
        self.gui_widgets[name] = entry
        self.env[name] = entry  # store widget; reading it returns .get()

    # ── Evaluator ─────────────────────────────────────────────────────────────

    def eval(self, node):
        k = node[0]
        if k == "num":  return node[1]
        if k == "str":  return node[1]
        if k == "bool": return node[1]

        if k == "fstr":
            # f"Hello {name}, you are {age} years old"
            template = node[1]
            def replacer(m):
                expr_src = m.group(1)
                tokens = tokenize(expr_src)
                ast = Parser(tokens).parse()
                # eval as expression
                val = self.eval(Parser(tokenize(expr_src)).parse_expr())
                return self.fmt(val)
            return re.sub(r"\{([^}]+)\}", replacer, template)

        if k == "list_literal":
            return [self.eval(item) for item in node[1]]

        if k == "var":
            name = node[1]
            if name not in self.env: raise WareError(f"Undefined variable: '{name}'")
            val = self.env[name]
            # if it's a tk.Entry widget, return its text
            if hasattr(val, 'get'): return val.get()
            return val

        if k == "index":
            obj = self.eval(node[1])
            if hasattr(obj, 'get'): obj = obj.get()
            if isinstance(obj, str):
                return obj[int(self.eval(node[2])) - 1]
            if not isinstance(obj, list): raise WareError("Cannot index a non-list")
            return obj[int(self.eval(node[2])) - 1]

        if k == "call":
            name, arg_nodes = node[1], node[2]
            args = [self.eval(a) for a in arg_nodes]
            func = self.env.get(name)
            if func is None: raise WareError(f"Undefined function: '{name}'")
            # built-in lambda
            if callable(func):
                result = func(args)
                # run gui loop if window exists and this was last statement
                return result
            # user-defined function
            if isinstance(func, tuple) and func[0] == "__func__":
                _, params, body, closure = func
                saved = self.env
                self.env = {**closure, **dict(zip(params, args))}
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
        if k == "+":   return self.eval(node[1]) +  self.eval(node[2])
        if k == "-":   return self.eval(node[1]) -  self.eval(node[2])
        if k == "*":   return self.eval(node[1]) *  self.eval(node[2])
        if k == "/":   return self.eval(node[1]) /  self.eval(node[2])
        if k == "%":   return self.eval(node[1]) %  self.eval(node[2])
        raise WareError(f"Unknown node: {node}")


# ─── Entry Point ──────────────────────────────────────────────────────────────

def run_file(path):
    with open(path) as f: code = f.read()
    tokens = tokenize(code)
    ast = Parser(tokens).parse()
    interp = Interpreter(source_dir=os.path.dirname(os.path.abspath(path)))
    interp.run(ast)
    # if a GUI window was created, start the event loop
    if interp.gui_root:
        interp.gui_root.mainloop()

def repl():
    print("Ware 2.0 — type 'exit' to quit")
    interp = Interpreter()
    while True:
        try:
            line = input(">> ")
            if line.strip() == "exit": break
            tokens = tokenize(line)
            ast = Parser(tokens).parse()
            interp.run(ast)
        except (SyntaxError, WareError, Exception) as e:
            print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
