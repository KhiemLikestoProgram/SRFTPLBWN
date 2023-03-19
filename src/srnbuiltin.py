
from variables import *

import numpy as np
import sys

class Statement:

    def __init__(self, err, pos, args, argsType) -> None:
        self.err = err
        self.pos = pos
        self.args = args
        self.argsType = argsType

    def inp(self):
        sys.stdout.write(' '.join(self.args))
        RESULTS.append(sys.stdin.readline().rstrip())

    def inpLn(self):
        sys.stdout.write(' '.join(self.args))
        RESULTS.append(sys.stdin.readline().rstrip())
    
    def prn(self):
        sys.stdout.write(' '.join(self.args))
    
    def prnLn(self):
        sys.stdout.write(' '.join(self.args)+'\n')
    
    def var(self):
        if (self.args[0] not in MEMORY) or (self.args[1] in MEMORY and MEMORY[self.args[0]][1] == F_VAR):
            MEMORY.update({self.args[0]: (self.argsType[1], self.args[1], F_VAR)})
        else:
            self.err(11, "Can't change the value of a constant.", self.pos)

    def const(self):
        if self.args[0] in MEMORY and MEMORY[self.args[0]][1] == F_CONST:
            self.err(11, "Can't change the value of a constant.", self.pos)
        elif self.args[0] not in MEMORY:
            MEMORY.update({self.args[0]: (self.argsType[1], self.args[1], F_CONST)})

class Expression:

    def __init__(self, args, argsType) -> None:
        self.argsType = argsType
        self.args     = args

    add = lambda self: RESULTS.append(np.add(self.args[0], self.args[1]))
    sub = lambda self: RESULTS.append(np.subtract(self.args[0], self.args[1]))
    mul = lambda self: RESULTS.append(np.multiply(self.args[0], self.args[1]))
    div = lambda self: RESULTS.append(np.divide(self.args[0], self.args[1]))
    floor_div \
        = lambda self: RESULTS.append(np.floor_divide(self.args[0], self.args[1]))
    mod = lambda self: RESULTS.append(np.mod(self.args[0], self.args[1]))
    log = lambda self: RESULTS.append(np.emath.logn(self.args[0], self.args[1]))
    pow = lambda self: RESULTS.append(np.power(self.args[0], self.args[1]))
    
    sum = lambda self: RESULTS.append(np.sum(np.array(self.args)))