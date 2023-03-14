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

class Interpreter:

    """
    Interpreter <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """

    def __init__(self, lex: list[list[str]], pos: Position) -> None:
        self.lex    = lex
        self.pos    = pos
    
    def __call__(self) -> None:
        getType = lambda x, idx: x.split(':')[idx]

        for line in self.lex:

            COM_TYPE,                        \
            COMV    ,                         \
            ARG_TYPE,                          \
            ARGV,                               \
            =                                    \
            getType(line[0],  0),                 \
            getType(line[0], -1),                  \
           [getType(arg, 0) for arg in line[1:]],   \
           [getType(arg,-1) for arg in line[1:]]
            
            for a in ARGV:
                if a in MEMORY:
                    ARGV[ARGV.index(a)] = MEMORY[a]

            codeType, value = Builtin(ARGV, ARG_TYPE, COMV, COM_TYPE, self.pos)()

            value = reduce(lambda a, kv: a.replace(*kv), TEMPL.items(), value)
            
            if SETTINGS['showDebugInfo']:
                c.log(f"{' '.join([COMV]+ARGV)} -> {value}")
            
            if   codeType is F_STAT:
                exec(value)

                if SETTINGS['showDebugInfo']:
                    c.log(f'{value=}   #')
                    c.log(f'{MEMORY=}  ##')
                    c.log(f'{ARGV=}   ###')
                
            elif codeType is F_EXPR:
                eval(value)

class Builtin:

    """

    Parameters:
        args                            <list[str]>:
            Arguments to process
        argsType                        <list[str]>:
            Arguments' token types
        com                             <str>:
            Command to execute
        comType                         <str>:
            Command's token type

    Builtin <class> for the SRNFTPLBWN language.
    Use this class to "Pythonize" SRNFTPLBWN code.
    Last edited: 11:38 8/3/2023
    """

    def __init__(self, args, argsType, com, comType, pos: Position) -> None:
        
        self.argsType   = argsType
        self.com        = com
        self.comType    = comType
        self.pos        = pos
        
        self.args = [int(a) if t in T_INTEGER else a for a, t in zip(args, argsType)]
            
    def isAssignable(self, idx):
        
        """
        Parameters:
            idx <int>: argument position
        """

        if self.argsType[idx] is T_IDENTIFIER:
            if self.args[idx] not in MEMORY:
                SRNError(6, f"${self.args[idx]} is not defined.", self.pos)
                sys.exit(1)

                # TODO: Make an error system!
            return True
        
        elif self.argsType[idx] in BUILTIN_TYPES: return True
        else:
            SRNError(5, f"Can't assign ${self.args[0]} to the value '{self.args[1]}'.", self.pos)
            sys.exit(1)

    ########## EXPRESSION ##########

    def expr(self):
        if self.comType in COMPUTE:
            return COMPUTE[self.comType]
        else:
            SRNError(7, "Invalid command name <expression>.", self.pos)
            sys.exit(1)

    def stmt(self, idx):
        if idx == 'all':
            isAssignable = all([self.isAssignable(i) for i, _ in enumerate(self.args)])
        else:
            isAssignable = self.isAssignable(idx)

        if isAssignable:
            if self.comType in EXECUTE:
                return EXECUTE[self.comType]
            else:
                SRNError(8, "Invalid command name <statement>.", self.pos)
                sys.exit(1)

    def __call__(self):
        if   self.comType in COMPUTE:
            expr =self.expr()
            RESULTS.append(expr)
            return F_EXPR, expr
        elif self.comType in EXECUTE:
            return F_STAT, eval(f"self.{self.com}()")
        else:
            SRNError(9, "Invalid command type.", self.pos)
            sys.exit(1)
    
    ########## STATEMENT ##########

    def prnLn(self):
        return self.stmt(0)

    def prn(self):
        return self.stmt('all')

    def var(self):
        return self.stmt(1)

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

                    if  all([char in DIGITS for char in token[1:]]):
                        lex[i][j] = repr(Token(T_INTEGER, token))

                    else:
                        if token in LITERALS:
                            lex[i][j] = repr(Token(LITERALS[token], token))

                        elif token in KEYWORD:
                            lex[i][j] = repr(Token(KEYWORD[token], token))

                        elif re.search(pattern=r'\$[A-Za-z_][\w@!-]*+', string=token):
                            if token[1:] in BUILTIN_VARS:
                                tokenInstType = type(BUILTIN_VARS[token[1:]])

                                if tokenInstType == str:
                                    lex[i][j] = repr(Token(T_STRING, BUILTIN_VARS[token[1:]]))

                                elif tokenInstType == int:
                                    lex[i][j] = repr(Token(T_INTEGER, BUILTIN_VARS[token[1:]]))
                                
                                continue

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

