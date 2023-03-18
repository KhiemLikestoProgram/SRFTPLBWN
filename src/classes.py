from variables import *

from rich.console   import Console
from rich.panel     import Panel

import srnbuiltin as srnbi
import re
import sys

c = Console()

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

class SRNError:
    def __init__(self, errno: int, errmes, pos: Position | None) -> None:
        match pos:
            case None:
                posDetail = f"<noPosInfo>"
            case _:
                posDetail = f"[File {pos.fn}, Ln {pos.ln}, Tok {pos.tk}]"
        c.log(\
f"""\
Error [{errno}]: {errmes}
{posDetail}
"""
        )
        sys.exit(errno)    

class SRNI:

    """
    S.R.N. Interpreter <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """

    def __init__(self, lex: list[list[str]], fn) -> None:
        self.lex    = lex
        self.pos    = Position(-1, 1, fn)
        
    def isAssignable(self, idx):
        
        """
        Parameters:
            arg    <Any>: argument value
            idx    <int | str>: argument position | 'all'
        """
        if idx == 'all':
            arg = self.ARGV
        elif isinstance(idx, int): 
            arg = self.ARGV[idx]
        else: c.log('DEADEND #1'); sys.exit(1313)

        if arg == T_IDENTIFIER:
            if arg not in MEMORY:
                SRNError(6, f"${arg} is not defined.", self.pos)
            return True
        
        elif all([t in BUILTIN_TYPES for t in self.ARG_TYPE]): return True
        else:
            SRNError(5, f"{arg} is not assignable.", self.pos)

    def interpret(self) -> None:
        getType = lambda x, idx: x.split(':')[idx]
        py_to_srn = lambda mem: {str: T_STRING, int: T_INTEGER, float: T_FLOAT}[type(mem)]

        for i, line in enumerate(self.lex):

            if line == []: self.pos.ln += 1; continue

            self.COM_TYPE,                        \
            self.COMV    ,                         \
            self.ARG_TYPE,                          \
            self.ARGV,                               \
            =                                         \
            getType(line[0],  0),                      \
            getType(line[0],  1),                       \
           [getType(arg, 0) for arg in line[1:]],        \
           [getType(arg, 1) for arg in line[1:]]
            
            # Replaces every argument Token object (value and type) with a builtin Token object.
            self.pos.tk += 1
            
            for (i, a), t in zip(enumerate(self.ARGV), self.ARG_TYPE):
                
                self.pos.tk += 1

                if  t == T_IDENTIFIER \
                and self.COM_TYPE not in [KEYWORDS["STMT"]['set'][0], KEYWORDS["STMT"]['def'][0]]:
                    if a in MEMORY:
                        self.ARG_TYPE[i]    = py_to_srn(MEMORY[a][0]) # Find a better solution later
                        self.ARGV[i]        = MEMORY[a][0]
                    else: SRNError(10, f"${a} is NOT in the program's memory.", self.pos)

                elif t == T_INTEGER \
                and self.COM_TYPE in [val[0] for val in KEYWORDS["EXPR"]["NUM"].values()]:
                    self.ARGV[i] = int(a)
                
                elif t == T_FLOAT \
                and self.COM_TYPE in [val[0] for val in KEYWORDS["EXPR"]["NUM"].values()]:
                    self.ARGV[i] = float(a)

            if self.COMV in KEYWORDS["EXPR"]:
                self.expr()
            elif self.COMV in KEYWORDS["STMT"]:
                self.stmt(REQUIREMENTS[self.COM_TYPE])
            else:
                SRNError(9, f"Invalid command type <{self.COM_TYPE}>.", self.pos)
            
            if SETTINGS['showDebugInfo']:
                panel = Panel(cont, title=f'Line <{self.pos.ln}>')
                c.print(panel)

            self.pos.ln += 1

    ########## CODE TYPES ##########

    def expr(self):
        KEYWORDS["EXPR"][self.COMV][1](self.ARGV)

        if SETTINGS['showDebugInfo']:
            global cont
            cont = f'{RESULTS=}'

    def stmt(self, req):
        if self.isAssignable(req):
            stmt = srnbi.Statement(SRNError, self.pos, self.ARGV)
            getattr(stmt, KEYWORDS["STMT"][self.COMV][1])()
            
        if SETTINGS['showDebugInfo']:
            global cont
            cont = f'{RESULTS=}\n{MEMORY=}\n{self.ARGV=}'
    
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
        with open(fileName, 'r') as file:
            self.txt    = file.read().splitlines()
            self.pos    = Position(-1, 1, fileName)

    def lex(self):
        lex = [self.tokenize(line) for line in self.txt]
        for i, line in enumerate(lex):
            if line == []: self.pos.ln += 1; continue

            for j, token in enumerate(line):
                self.pos.tk += 1

                if  all([char in DIGITS for char in token]):
                    if token.count('.') <= 1:
                        lex[i][j] = repr(Token(T_FLOAT, token))
                    lex[i][j] = repr(Token(T_INTEGER, token))
                else:
                    if token in LITERALS:
                        lex[i][j] = repr(Token(LITERALS[token], token))

                    elif token in KEYWORDS["STMT"]:
                        lex[i][j] = repr(Token(KEYWORDS["STMT"][token][0], token))
                    
                    elif token in KEYWORDS["EXPR"]:
                        lex[i][j] = repr(Token(KEYWORDS["EXPR"]["NUM"][token][0], token))
                    
                    elif re.match(pattern=r'\$[A-Za-z_][\w@!-]*+', string=token):
                        if token[1:] in BUILTIN_VARS:
                            tokenInstType = type(BUILTIN_VARS[token[1:]])

                            if tokenInstType == str:
                                lex[i][j] = repr(Token(T_STRING, BUILTIN_VARS[token[1:]]))

                            elif tokenInstType == int:
                                lex[i][j] = repr(Token(T_INTEGER, BUILTIN_VARS[token[1:]]))

                            elif tokenInstType == float:
                                lex[i][j] = repr(Token(T_FLOAT, BUILTIN_VARS[token[1:]]))

                        lex[i][j] = repr(Token(T_IDENTIFIER, token[1:]))

                    elif re.match(pattern=r'[\'"].*[\'"]', string=token, flags=re.DOTALL):
                        lex[i][j] = repr(Token(T_STRING, eval(token)))

                    #elif re.search(pattern=r'\d', string=token): pass

                    else:
                        SRNError(3, f"Invalid token: <{token}>", self.pos)

            self.pos.ln += 1

        return lex, self.pos.fn
    
    def tokenize(self, line) -> list[str]:
        tokens = [];    tok = ''
        isString = 0

        for char in line:
            if char == '"':
                isString ^= True
                
            if char == ' ' and not isString:
                tokens.append(tok)
                tok = ''
                continue
            tok += char

        tokens.append(tok)

        tokens = [tok for tok in tokens if tok != '']

        return tokens

