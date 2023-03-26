
from variables import *
import numpy as np
import readchar
import sys

class Statement:
    commands = {
    #   Token     Type       Function to call   Requirements (see `isType` function)
        "ask":	  ("ASK",	 "ask", 			("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
        "askLn":  ("ASKLN",	 "askLn", 			("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
        "askChr": ("ASKCHR", "askChr", 			(    0, 	     (T_PARAMETER[0]) )),
        "mode":	  ("MODE",	 "mode", 			(    0, 	     (T_PARAMETER[0]) )),
        "prn":	  ("PRINT",	 "prn", 			("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
        "prnLn":  ("PRNLN",	 "prnLn", 	        ("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
        "stack":  ("STACK",	 "stack", 			((1, None), tuple(t[0] for t in BUILTIN_TYPES) )),
        "set":	  ("SET",	 "var", 			("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
        "def":    ("DEF", 	 "const",			("all", 	tuple(t[0] for t in BUILTIN_TYPES) )),
    }

    def __init__(self, pos, com, args, argsType) -> None:
        self.pos = pos
        self.com = com
        self.args, self.argsType = args, argsType

    def ask(self):
        self.prn()
        input = sys.stdin.readline().strip('\n')
        RESULTS.append(input)

    def askLn(self):
        self.prnLn()
        input = sys.stdin.readline().strip('\n')
        RESULTS.append(input)
    
    def askChr(self):
        match self.args[0]:
            case '-sb' | '-hb': 
                input = bytes(readchar.readchar(), 'utf-8')
                if self.args[0] == '-sb': sys.stdout.write(input.decode('utf-8')) 
            case '-sc' | '-hc':
                input = readchar.readchar()
                if self.args[0] == '-sc': sys.stdout.write(input)
            case _:
                SRNError(ERRORS['SCE'], f"Invalid parameter: '{self.args[0]}'.", self.pos)
        RESULTS.append(input)

    def mode(self):
        match self.args[0]:
            case '-d':
                if len(self.args) < 2:
                    SRNError(ERRORS['SCE'], f"Not enough arguments for command: 'mode'", self.pos)
                try:
                    Param.debug(bool(self.args[1]))
                except ValueError:
                    SRNError(ERRORS['SCE'], f"Invalid value for {SETTINGS=}.")
            case '-?' | '?': Param.help()
            case _:
                SRNError(ERRORS['SCE'], f"Invalid parameter: '{self.args[0]}'.", self.pos)

    def prn(self):
        sys.stdout.write(''.join(self.args))
        sys.stdout.flush()
    
    def prnLn(self):
        sys.stdout.write(''.join(self.args)+'\n')
        sys.stdout.flush()

    def stack(self):
        match self.args[0]:
            case 'add':
                for a, t in zip(self.args[1:], self.argsType[1:]): STACK.append((t, a))

            case 'idx':
                [RESULTS.append(i) for i, val in enumerate(STACK) if val == self.args[1]]

            case 'del': STACK.pop(self.args[1])

            case 'ins' | 'switch':
                if len(self.args[1:]) < 2:
                    SRNError(ERRORS['SCE'], "Not enough arguments.", self.pos)
                
                if self.args[0] == 'ins':
                    if self.argsType[1] != T_INTEGER[0]:
                        SRNError(ERRORS['SCE'], "The index to insert must be an integer.", self.pos)
                
                    if self.args[1] >= len(STACK):
                        SRNError(ERRORS['SCE'], "The index to insert must be smaller than the length of the stack.", self.pos)

                    STACK.insert(self.args[1], (self.argsType[2], self.args[2]))

                elif self.args[0] == 'switch':
                    if (self.argsType[1], self.argsType[2]) != (T_INTEGER[0], T_INTEGER[0]):
                        SRNError(ERRORS['SCE'], "The indexes to switch must be integers.", self.pos)

                    if self.args[1] >= len(STACK) or self.args[2] >= len(STACK):
                        SRNError(ERRORS['SCE'], "The indexes to switch must be smaller than the length of the stack.", self.pos)

                    STACK[self.args[1]], STACK[self.args[2]] = STACK[self.args[2]], STACK[self.args[1]]

            case 'ldup' | 'rdup':
                pos = 0 if self.args[0] == 'ldup' else 1
                STACK.insert(self.args[1]+pos, STACK[self.args[1]])
            case _:
                SRNError(ERRORS['SCE'], "Invalid stack operation.", self.pos)
    
    def var(self):
        if (self.args[0] not in MEMORY) or (self.args[1] in MEMORY and MEMORY[self.args[0]][1] == F_VAR):
            MEMORY.update({self.args[0]: (self.argsType[1], self.args[1], F_VAR)})
        else:
            SRNError(ERRORS['SCE'], "Can't change the value of a constant.", self.pos)

    def const(self):
        if self.args[0] in MEMORY and MEMORY[self.args[0]][1] == F_CONST:
            SRNError(ERRORS['SCE'], "Can't change the value of a constant.", self.pos)
        elif self.args[0] not in MEMORY:
            MEMORY.update({self.args[0]: (self.argsType[1], self.args[1], F_CONST)})

class Expression:
    commands = {
    #   Token     Type       Function to call   Requirements (see `isType` function)
        "add":	  ("ADD",	 "add", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "sub":	  ("SUB",	 "sub", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "pow":	  ("POW",	 "pow", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "mul":	  ("MUL",	 "mul", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "div":	  ("DIV",	 "div", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "fdiv":   ("FDIV",	 "floor_div", 	    ("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "mod":	  ("MOD",	 "mod", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "log":	  ("LOG",	 "log", 			("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
        "sum":    ("SUM", 	 "sum",				("all", 	(T_IDENTIFIER[0], T_INTEGER[0], T_FLOAT[0]))),
    }
    
    def __init__(self, args, argsType) -> None:
        self.argsType = argsType
        self.args     = args

    add = lambda self: np.add(self.args[0], self.args[1])
    sub = lambda self: np.subtract(self.args[0], self.args[1])
    mul = lambda self: np.multiply(self.args[0], self.args[1])
    div = lambda self: np.divide(self.args[0], self.args[1])
    floor_div = \
          lambda self: np.floor_divide(self.args[0], self.args[1])
    mod = lambda self: np.mod(self.args[0], self.args[1])
    log = lambda self: np.emath.logn(self.args[0], self.args[1])
    pow = lambda self: np.power(self.args[0], self.args[1])
    
    sum = lambda self: np.sum(np.array(self.args))

class Param:
    
    @staticmethod
    def debug(boolean=True): SETTINGS['show-debug-info'] = boolean

    @staticmethod
    def help():
        accentColor = COLORS["accent"]
        versionColor = COLORS["version"]
        c.print(f"Welcome to [{accentColor} bold italic]{BUILTIN_VARS['_THISPL']} [{versionColor}]{BUILTIN_VARS['_VER']}[reset]!")
        c.print("Here's the list of available commands:")
        c.print('\n'.join([f'{k:5s} -> {v[1]}' for k, v in RT_PARAMETERS.items()]))
        sys.exit(0)

KEYWORDS = {
	#   Token     Type        Function to call  Requirements (see `isType` function)
	"COMMENT": {
		"cmt":	  (T_COMMENT, None,				(None,		None)),
		"#":	  (T_COMMENT, None,				(None,		None)),
	},
	"STMT": Statement.commands,
	"EXPR": Expression.commands,
}