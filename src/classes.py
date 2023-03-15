from typing import Any
from vars import *

from functools      import reduce
from rich.console   import Console

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

    def __init__(self, lex: list[list[str]], pos: Position) -> None:
        self.lex    = lex
        self.pos    = pos

    def __call__(self) -> Any:

        if self.COMV in KEYWORD['COMPUTE']:
            expr = self.expr()
            RESULTS.append(expr)
            return F_EXPR, expr
        
        elif self.COMV in KEYWORD['EXECUTE']:   
            return F_STAT, self.stmt(REQUIREMENTS[self.COM_TYPE])
        
        else:
            SRNError(9, f"Invalid command type <{self.COM_TYPE}>.", self.pos)
    
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

        for line in self.lex:
            if line == []: continue

            self.COM_TYPE,                        \
            self.COMV    ,                         \
            self.ARG_TYPE,                          \
            self.ARGV,                               \
            =                                    \
            getType(line[0],  0),                 \
            getType(line[0], -1),                  \
           [getType(arg, 0) for arg in line[1:]],   \
           [getType(arg,-1) for arg in line[1:]]
            
            for a, t in zip(self.ARGV, self.ARG_TYPE):
                if t is T_IDENTIFIER:
                    if a in MEMORY:
                        self.ARGV[self.ARGV.index(a)] = MEMORY[a]
                    else: SRNError(10, f"${a} is NOT in the program's memory.", self.pos)

            codeType, value = self()

            value = reduce(lambda a, kv: a.replace(*kv), TEMPL.items(), value)

            if SETTINGS['showDebugInfo']:
                c.log(f"{self.COMV} {self.ARGV} -> {value}")
            
            if   codeType is F_STAT:
                exec(value)

                if SETTINGS['showDebugInfo']:
                    c.line()
                    c.log(f'{value=}')
                    c.log(f'{MEMORY=}')
                    c.log(f'{self.ARGV=}')
                
            elif codeType is F_EXPR:
                eval(value)

                if SETTINGS['showDebugInfo']:
                    c.log(f'{RESULTS=}')

    ########## CODE TYPES ##########

    def expr(self):
        if self.COMV in KEYWORD["COMPUTE"]:
            return KEYWORD["COMPUTE"][self.COMV][1]
        else:
            SRNError(7, "Invalid command name [expression].", self.pos)

    def stmt(self, arg):
        if self.isAssignable(arg):
            if self.COMV in KEYWORD["EXECUTE"]:
                return KEYWORD["EXECUTE"][self.COMV][1]
            else:
                SRNError(8, "Invalid command name [statement].", self.pos)
    
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

            if line != []:
                for j, token in enumerate(line):
                    
                    self.pos.tk += 1

                    if  all([char in DIGITS for char in token]):
                        if token.count('.') <= 1:
                            lex[i][j] = repr(Token(T_FLOAT, token))

                        lex[i][j] = repr(Token(T_INTEGER, token))

                    else:
                        if token in LITERALS:
                            lex[i][j] = repr(Token(LITERALS[token], token))

                        elif token in KEYWORD["EXECUTE"]:
                            lex[i][j] = repr(Token(KEYWORD["EXECUTE"][token][0], token))
                        
                        elif token in KEYWORD["COMPUTE"]:
                            lex[i][j] = repr(Token(KEYWORD["COMPUTE"][token][0], token))

                        elif re.search(pattern=r'\$[A-Za-z_][\w@!-]*+', string=token):
                            if token[1:] in BUILTIN_VARS:
                                tokenInstType = type(BUILTIN_VARS[token[1:]])

                                if tokenInstType == str:
                                    lex[i][j] = repr(Token(T_STRING, BUILTIN_VARS[token[1:]]))

                                elif tokenInstType == int:
                                    lex[i][j] = repr(Token(T_INTEGER, BUILTIN_VARS[token[1:]]))

                                elif tokenInstType == float:
                                    lex[i][j] = repr(Token(T_FLOAT, BUILTIN_VARS[token[1:]]))
                                
                                continue
                            
                            elif token[1:] in MEMORY:
                                tokenInstType = type(MEMORY[token[1:]])

                                if tokenInstType == str:
                                    lex[i][j] = repr(Token(T_STRING, MEMORY[token[1:]]))

                                elif tokenInstType == int:
                                    lex[i][j] = repr(Token(T_INTEGER, MEMORY[token[1:]]))

                                elif tokenInstType == float:
                                    lex[i][j] = repr(Token(T_FLOAT, MEMORY[token[1:]]))

                            lex[i][j] = repr(Token(T_IDENTIFIER, token[1:]))

                        elif re.search(pattern=r'[\'"].+[\'"]', string=token, flags=re.DOTALL):
                            lex[i][j] = repr(Token(T_STRING, eval(token)))

                        #elif re.search(pattern=r'\d', string=token): pass

                        else:
                            SRNError(3, f"Invalid token: <{token}>", self.pos)

            self.pos.ln += 1

        return lex, self.pos
    
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

