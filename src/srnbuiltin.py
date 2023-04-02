import sys
import numpy as np
import readchar

from variables import *

class Statement:
    commands = {
        "ask":	  SimpleNamespace(type="ASK",	 fn="ask", 		req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
        "askLn":  SimpleNamespace(type="ASKLN",	 fn="askLn", 	req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
        "askChr": SimpleNamespace(type="ASKCHR",  fn="askChr", 	req=(    0, tuple([T_PARAMETER.type]) )),
        "mode":	  SimpleNamespace(type="MODE",	 fn="mode", 	req=(    0, tuple([T_PARAMETER.type]) )),
        "prn":	  SimpleNamespace(type="PRINT",	 fn="prn", 		req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
        "prnLn":  SimpleNamespace(type="PRNLN",	 fn="prnLn", 	req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
        "stack":  SimpleNamespace(type="STACK",	 fn="stack", 	req=((1, None), tuple(t.type for t in BUILTIN_TYPES) )),
        "set":	  SimpleNamespace(type="SET",	 fn="var", 		req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
        "def":    SimpleNamespace(type="DEF", 	 fn="const",	req=("all", tuple(t.type for t in BUILTIN_TYPES) )),
    }

    def __init__(self, pos, com, args, argsType) -> None:
        self.pos = pos
        self.com = com
        self.args = args
        self.argsType = argsType

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
                    SRNError(ERRORS['SCE'], f"Invalid value for command: 'mode'.")
            case '-?' | '?': Param.help()
            case _:
                SRNError(ERRORS['SCE'], f"Invalid parameter: '{self.args[0]}'.", self.pos)

    def prn(self):
        sys.stdout.write(''.join([str(a) for a in self.args]))
        sys.stdout.flush()
    
    def prnLn(self):
        sys.stdout.write(''.join([str(a) for a in self.args])+'\n')
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
                    if (self.argsType[1], self.argsType[2]) != (T_INTEGER.type, T_INTEGER.type):
                        SRNError(ERRORS['SCE'], "The indexes to switch must be integers.", self.pos)

                    if self.args[1] >= len(STACK) or self.args[2] >= len(STACK):
                        SRNError(ERRORS['SCE'], "The indexes to switch must be smaller than the length of the stack.", self.pos)

                    STACK[self.args[1]], STACK[self.args[2]] = STACK[self.args[2]], STACK[self.args[1]]

            case 'ldup' | 'rdup':
                pos = 0 if self.args[0] == 'ldup' else 1
                STACK.insert(self.args[1]+pos, STACK[self.args[1]])
            case _:
                SRNError(ERRORS['SCE'], "Invalid stack operation.", self.pos)
        
        MEMORY["_STACK"] = SimpleNamespace(tok=T_OTHER, val=' '.join([str(s) for s in STACK]), type=F_VAR)
    
    def var(self):
        if (self.args[0] not in MEMORY) or (self.args[0] in MEMORY and MEMORY[self.args[0]].type == F_VAR):
            MEMORY[self.args[0]] = \
            SimpleNamespace(tok=self.argsType[1], val=self.args[1], type=F_VAR)
        else:
            SRNError(ERRORS['SCE'], "Can't change the value of a constant.", self.pos)

    def const(self):
        if self.args[0] in MEMORY and MEMORY[self.args[0]].type == F_CONST:
            SRNError(ERRORS['SCE'], "Can't change the value of a constant.", self.pos)
        elif self.args[0] not in MEMORY:
            MEMORY[self.args[0]] = \
            SimpleNamespace(tok=self.argsType[1], val=self.args[1], type=F_VAR)

class Expression:
    commands = {
        "add":	  SimpleNamespace(type="ADD",	 fn="add", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "sub":	  SimpleNamespace(type="SUB",	 fn="sub", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "pow":	  SimpleNamespace(type="POW",	 fn="pow", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "mul":	  SimpleNamespace(type="MUL",	 fn="mul", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "div":	  SimpleNamespace(type="DIV",	 fn="div", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "fdiv":   SimpleNamespace(type="FDIV",   fn="floor_div",    req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "mod":	  SimpleNamespace(type="MOD",	 fn="mod", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "log":	  SimpleNamespace(type="LOG",	 fn="log", 			req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
        "sum":    SimpleNamespace(type="SUM",    fn="sum",		    req=("all", 	(T_IDENTIFIER.type, T_INTEGER.type, T_FLOAT.type))),
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
    def debug(val=True): SETTINGS['show-debug-info'] = val

    @staticmethod
    def help():
        accentColor = COLORS["accent"]
        versionColor = COLORS["version"]
        c.print(f"Welcome to [{accentColor} bold italic]{BUILTIN_VARS['_THISPL']} [{versionColor}]{BUILTIN_VARS['_VER']}[reset]!")
        c.print("Here's the list of available commands:")
        c.print('\n'.join([f'{k:5s} -> {v[1]}' for k, v in RT_PARAMETERS.items()]))
        sys.exit(0)

KEYWORDS = SimpleNamespace(
	CMT = {
		"cmt":	  SimpleNamespace(type=T_COMMENT.type, fn=None, req=(None, None)),
		"#":	  SimpleNamespace(type=T_COMMENT.type, fn=None, req=(None, None)),
	},
	STMT = Statement.commands,
	EXPR = Expression.commands,
)

FORBID_CONVERT = (KEYWORDS.STMT['prn'].type, KEYWORDS.STMT['prnLn'].type,
				  KEYWORDS.STMT['ask'].type, KEYWORDS.STMT['askLn'].type)
