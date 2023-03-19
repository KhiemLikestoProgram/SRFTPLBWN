
########### IMPORTS ###########

from variables import *
import srnbuiltin as srnbi

import re
import sys

if SETTINGS['showDebugInfo']:
    from rich.console   import Console
    from rich.panel     import Panel
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

class SRNFTPLBWNI:

    """
    S.R.N. Interpreter <class> for the SRNFTPLBWN language.
    Last edited: 11:06 7/3/2023
    """

    def __init__(self, lex: list[list[str]], fn) -> None:
        self.lex    = lex
        self.pos    = Position(-1, 1, fn)
        
    def isType(self, idx, types_):
        """
        Parameters:
            idx    <int | str | tuple>: argument position | 'all'
        """
        if idx == 'all':
            if all([t in types_ for t in self.ARG_TYPE]):
                return True
            else:
                SRNError(5, 
                f"Failed the requirements, need all arguments to be in these types: {types_}.", self.pos)

        elif isinstance(idx, tuple):
            if all([t in types_ for t in idx]):
                return True
            else:
                SRNError(5.1, 
                f"Failed the requirements, need arguments with {idx=} to be in these types: {types_}", self.pos)

        elif isinstance(idx, int) and idx < len(self.ARGV):
            t = self.ARG_TYPE[idx]
            if t in types_:
                return True
            else:
                SRNError(5.2, f"Failed the requirements, need an argument with {idx=} to be in these types: {types_}", self.pos)
            
        else: c.log('DEADEND #1'); sys.exit(1313)
        
    def interpret(self) -> None:
        getType = lambda x, idx: x.split(':')[idx]

        for i, line in enumerate(self.lex):

            if line == []: self.pos.ln += 1; continue

            if getType(line[0], 1) in KEYWORDS['COMMENT']: self.pos.ln += 1; continue

            self.COM_TYPE, self.COMV,                   \
            self.ARG_TYPE, self.ARGV                    \
            =                                           \
            getType(line[0], 0), getType(line[0], 1),   \
           [getType(arg, 0) for arg in line[1:]],       \
           [getType(arg, 1) for arg in line[1:]]
            
            # Replaces every argument Token object (value and type) with a builtin Token object, if it is in
            # the program's "memory".
            self.pos.tk += 1
            for (i, a), t in zip(enumerate(self.ARGV), self.ARG_TYPE):
                self.pos.tk += 1

                c.log(self.COM_TYPE, t)
                if  t == T_IDENTIFIER \
                and self.COM_TYPE not in [KEYWORDS["STMT"]["set"][0], KEYWORDS["STMT"]["def"][0]]:
                    if a in MEMORY:
                        self.ARG_TYPE[i]    = MEMORY[a][0]
                        
                        if   MEMORY[a][0] == T_STRING:
                            self.ARGV[i]    = MEMORY[a][1]
                        elif MEMORY[a][0] == T_INTEGER:
                            self.ARGV[i]    = int(MEMORY[a][1])
                        elif MEMORY[a][0] == T_FLOAT:
                            self.ARGV[i]    = float(MEMORY[a][1])
                    else: SRNError(10, f"${a} is NOT in the program's memory.", self.pos)

                elif t == T_INTEGER \
                and self.COMV in KEYWORDS["EXPR"]:
                    self.ARGV[i] = int(a)
                
                elif t == T_FLOAT \
                and self.COMV in KEYWORDS["EXPR"]:
                    self.ARGV[i] = float(a)

            if self.COMV in KEYWORDS["EXPR"]:
                self.expr(KEYWORDS["EXPR"][self.COMV][2])
            elif self.COMV in KEYWORDS["STMT"]:
                self.stmt(KEYWORDS["STMT"][self.COMV][2])
            elif self.COMV in KEYWORDS["COMMENT"]:
                global cont
                cont = ' '.join(self.ARGV)
            else:
                SRNError(9, f"Invalid command value <{self.COMV}>.", self.pos)
            
            if SETTINGS['showDebugInfo']:
                panel = Panel(
                cont, title="At line <[%s]%i[/%s]>" % (SETTINGS['lineNoColor'], self.pos.ln, SETTINGS['lineNoColor']),
                title_align='left', highlight=True
                )
                c.print(panel)

            self.pos.ln += 1

    ########## CODE TYPES ##########

    def expr(self, req):
        c.log(self.ARG_TYPE)
        if self.isType(*req):
            expr = srnbi.Expression(self.ARGV, self.ARG_TYPE)
            getattr(expr, KEYWORDS["EXPR"][self.COMV][1])()
        
        if SETTINGS['showDebugInfo']:
            global cont
            cont = f'{RESULTS=}'

    def stmt(self, req):
        if self.isType(*req):
            stmt = srnbi.Statement(SRNError, self.pos, self.ARGV, self.ARG_TYPE)
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
        with open(fileName, 'r', encoding='utf-8') as file:
            self.txt    = file.read().splitlines()
            self.pos    = Position(-1, 1, fileName)

    def lex(self):
        lex = [self.tokenize(line) for line in self.txt]

        isComment = False

        for i, line in enumerate(lex):
            if line == []: self.pos.ln += 1; continue

            for j, token in enumerate(line):
                self.pos.tk += 1
                
                if isComment: 
                    isComment = False; break

                if  re.match(r'^[+-]?(\d*\.)?\d+$', token):
                    if re.search(r'\.', token):
                        lex[i][j] = repr(Token(T_FLOAT, token))
                    else:
                        lex[i][j] = repr(Token(T_INTEGER, token))
                else:

                    if token in KEYWORDS["STMT"]:
                        lex[i][j] = repr(Token(KEYWORDS["STMT"][token][0], token))
                    
                    elif token in KEYWORDS["EXPR"]:
                        lex[i][j] = repr(Token(KEYWORDS["EXPR"][token][0], token))
                    
                    elif re.match(r'(cmt|#)', token[:3]):
                        lex[i][j] = repr(Token(T_COMMENT, token))
                        isComment = True

                    elif re.match(r'\$[^ \t\n\r0-9].*', token):
                        if token[1:] in BUILTIN_VARS:
                            tokenInstType = type(BUILTIN_VARS[token[1:]])

                            if tokenInstType == str:
                                lex[i][j] = repr(Token(T_STRING, BUILTIN_VARS[token[1:]]))

                            elif tokenInstType == int:
                                lex[i][j] = repr(Token(T_INTEGER, BUILTIN_VARS[token[1:]]))

                            elif tokenInstType == float:
                                lex[i][j] = repr(Token(T_FLOAT, BUILTIN_VARS[token[1:]]))

                        lex[i][j] = repr(Token(T_IDENTIFIER, token[1:]))

                    elif re.match(r'[\'"].*[\'"]', token, flags=re.DOTALL):
                        lex[i][j] = repr(Token(T_STRING, eval(token)))

                    else:
                        SRNError(3, f"Invalid token: <{token}>", self.pos)

            self.pos.ln += 1

        return lex, self.pos.fn
    
    def tokenize(self, line) -> list[str]:
        tokens = [];    tok = ''
        isString = False

        for char in line:
            if char == '#': break
            if char == '"':
                isString ^= True
            elif char == ' ' and not isString:
                tokens.append(tok)
                tok = ''
                continue
            
            tok += char

        tokens.append(tok)
        tokens = [tok for tok in tokens if tok != '']
        return tokens

