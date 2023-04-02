
########### IMPORTS ###########

from variables import *
from srnbuiltin import *
from rich.pretty import pprint
from rich.panel import Panel

import re

########### CLASSES ###########

class Position:

    """
    Position <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """
    
    def __init__(self, tok, ln, fn) -> None:
        self.tk = tok
        self.ln = ln
        self.fn = fn
    
    def advance(self, mode='token'):
        match mode:
            case 'line': self.ln += 1; self.tk = 1
            case 'token': self.tk += 1

class Interpreter:

    """
    SRNFTPLBWN Interpreter <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """

    def __init__(self, lex: list[list[str]], fn) -> None:
        self.lex    = lex
        self.pos    = Position(-1, 1, fn)
    
    def isType(self, idx, types_):
        """
        Checks if the argument of (option idx) is in the types_ provided for the command.

        Parameters:
            idx    <int | str | tuple>: argument position | 'all'
        """
        if idx == 'all':
            if all([t in types_ for t in self.ARG_TYPE]):
                return True
            else:
                SRNError(ERRORS["SCE"], 
                f"All arguments' type must be in {types_}.", self.pos)

        elif isinstance(idx, tuple):
            if all([t in types_ for t in self.ARG_TYPE[idx[0]:idx[1]]]):
                return True
            else:
                SRNError(ERRORS["SCE"], 
                f"Arguments' type span from {idx[0]} to {idx[1]} must be in \n\t{types_}, not {self.ARG_TYPE[idx]}", self.pos)

        elif isinstance(idx, int) and idx < len(self.ARGV):
            t = self.ARG_TYPE[idx]
            if t in types_: return True
            else:
                SRNError(ERRORS["SCE"],
                f"The argument no. {idx}'s type must be in \n{types_}, not {t}", self.pos)
        
        elif idx is None: return True
        else:
            SRNError(ERRORS["CFE"], f"Expect `idx` to be an integer, a tuple or literal 'all', not '{idx}'.", self.pos)

    def _loop(self) -> None:
        """
            Replaces every argument Token object (value and type) with a `iden` object, 
            if it is in the program's "memory".
            Also executes command (each line)
        """
        lnk = (KEYWORDS.STMT, KEYWORDS.EXPR, KEYWORDS.CMT)
        
        for (i, a), t in zip(enumerate(self.ARGV), self.ARG_TYPE):

            self.pos.advance()
            cls = [bit.cls for bit in BUILTIN_TYPES if t == bit.type][0]

            if  t == T_IDENTIFIER.type    \
            and self.COM_TYPE not in (KEYWORDS.STMT["set"].type, KEYWORDS.STMT["def"].type):
                if a in MEMORY:
                    if isinstance(MEMORY[a].tok, SimpleNamespace):
                        self.ARG_TYPE[i] = MEMORY[a].tok.type
                    else: # Temporary if-else statement here
                        self.ARG_TYPE[i] = MEMORY[a].tok
                    self.ARGV[i]     = cls(a)
                else:
                    SRNError(ERRORS["SCE"], f"${a} is NOT in the program's memory.", self.pos)

            elif t in (T_INTEGER.type, T_FLOAT.type)    \
            and self.COM_TYPE not in FORBID_CONVERT:
                self.ARGV[i] = cls(a)
            
            elif i == 1 \
            and t == T_IDENTIFIER.type \
            and self.COM_TYPE in (KEYWORDS.STMT["set"].type, KEYWORDS.STMT["def"].type):
                match self.ARGV[i]:
                    case '.':      self.ARGV[i] = RESULTS[-1] if RESULTS else ''
                    case _:        self.ARGV[i] = iden(self.ARGV[i])

        # Real execution
        if   self.COMV in lnk[0]:
            self.stmt(lnk[0][self.COMV].req)
        elif self.COMV in lnk[1]:
            self.expr(lnk[1][self.COMV].req)
        elif self.COMV in lnk[2]:
            self.cmt()
        else: SRNError(ERRORS["SCE"], f"Invalid command type <{self.COMV}>.", self.pos)
        
        if SETTINGS['show-debug-info']:
            panel = Panel(
                cont,
                title="At line <[%s]%i[/]>" % (COLORS["accent"], self.pos.ln),
                title_align='left', highlight=True
            )
            c.print(panel)

        self.pos.advance('line')

    def run(self) -> None:
        for line in self.lex:
            if line == []: self.pos.advance('line'); continue

            self.COM_TYPE, self.COMV,                           \
            self.ARG_TYPE, self.ARGV                            \
            =                                                   \
            line[0].split(':')[0],                              \
            line[0].split(':')[1],                              \
           [         arg.split(':')[0]   for arg in line[1:]],  \
           [':'.join(arg.split(':')[1:]) for arg in line[1:]]
            
            self._loop()

    ########## KW TYPES ##########

    def expr(self, req):
        if self.isType(*req):
            expr = Expression(self.ARGV, self.ARG_TYPE)
            RESULTS.append(getattr(expr, KEYWORDS.EXPR[self.COMV].fn)())
        MEMORY["_RES"] = SimpleNamespace(tok=T_IDENTIFIER.type, val=' '.join(str(r) for r in RESULTS), type=F_VAR)
        
        if SETTINGS['show-debug-info']:
            global cont
            cont = f'{RESULTS=}'

    def stmt(self, req):
        if self.isType(*req):
            stmt = Statement(self.pos, self.COMV, self.ARGV, self.ARG_TYPE)
            getattr(stmt, KEYWORDS.STMT[self.COMV].fn)()
            
        if SETTINGS['show-debug-info']:
            global cont
            cont = f'{RESULTS=}\n{MEMORY=}\n{STACK=}\n{self.ARGV=}'
    
    def cmt(self):
        if SETTINGS['show-debug-info']:
            global cont
            cont = ' '.join(self.ARGV)
    
class Token:

    """
    Token <class> for the SRNFTPLBWN language.
    Last edited: 11:46 7/3/2023
    """

    def __init__(self, type_: str, value: str) -> None:
        self.value = value
        self.type  = type_

    def __repr__(self) -> str:
        return '%s:%s' % (self.type, self.value)

class Lexer:

    """
    Lexer <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """

    def __init__(self, fileName) -> None:
        with open(fileName, 'r', encoding='utf-8') as file:
            self.txt    = file.read().splitlines()
            self.pos    = Position(-1, 1, fileName)

    def lex(self):
        lex = [self.tokenize(line) for line in self.txt]

        isComment = False

        for i, line in enumerate(lex):
            if line == []: self.pos.advance('line'); continue

            for j, token in enumerate(line):
                self.pos.advance('tok')
                
                if isComment:
                    lex[i][j] = repr(Token(T_COMMENT.type, token))
                    if len(line) - j == 1: isComment = False
                    continue

                if  re.match(r'^[+-]?(\d*\.)?\d+$', token):
                    if '.' in token:
                        lex[i][j] = repr(Token(T_FLOAT.type, token))
                    else:
                        lex[i][j] = repr(Token(T_INTEGER.type, token))
                else:
                    if re.match(r'-?[A-z]\w*', token) and j >= 1:
                        lex[i][j] = repr(Token(T_PARAMETER.type, token))

                    elif token in KEYWORDS.STMT:
                        if j != 0: SRNError(ERRORS['SCE'], "Command name must be the first token.", self.pos)
                        lex[i][j] = repr(Token(KEYWORDS.STMT[token].type, token))

                    elif token in KEYWORDS.EXPR:
                        if j != 0: SRNError(ERRORS['SCE'], "Command name must be the first token.", self.pos)
                        lex[i][j] = repr(Token(KEYWORDS.EXPR[token].type, token))
                    
                    elif re.match(r'(cmt|#)', token):
                        lex[i][j] = repr(Token(T_COMMENT.type, token))
                        isComment = True
                                                
                    elif re.match(r'\$[^ \t\n\r0-9].*', token):
                        if token[1:] in BUILTIN_VARS:
                            tokType = {bit.cls: bit.type for bit in BUILTIN_TYPES}[type(BUILTIN_VARS[token[1:]])]
                            lex[i][j] = repr(Token(tokType, BUILTIN_VARS[token[1:]]))
                        else: 
                            lex[i][j] = repr(Token(T_IDENTIFIER.type, token[1:]))

                    elif re.match(r'[\'"].*[\'"]', token, flags=re.DOTALL):
                        lex[i][j] = repr(Token(T_STRING.type, eval(token)))

                    else:
                        SRNError(ERRORS["SCE"], f"Invalid token: <{token}>", self.pos)
            self.pos.advance('line')

        return lex, self.pos.fn
    
    def tokenize(self, line) -> list[str]:
        tokens = [];    tok = ''
        lSQ = [False, None] # lastStringQuote
        
        for char in line:
            if char in '"\'':
                if lSQ[1] is not None and lSQ[1] == char: lSQ = [False, None]
                elif lSQ[1] is None: lSQ = [True, char]
            elif char == ' ' and not lSQ[0]:
                tokens.append(tok)
                tok = ''
                continue

            tok += char

        tokens.append(tok)
        tokens = [tok for tok in tokens if tok != '']
        return tokens

