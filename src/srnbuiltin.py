
from variables import *

import numpy as np
import sys

class Statement:

    def __init__(self, err, pos, args) -> None:
        self.err = err
        self.pos = pos
        self.args = args

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
            MEMORY.update({self.args[0]: (self.args[1], F_VAR)})
        else:
            self.err(11, "Can't change the value of a constant.", self.pos)

    def const(self):
        if self.args[0] in MEMORY and MEMORY[self.args[0]][1] == F_CONST:
            self.err(11, "Can't change the value of a constant.", self.pos)
        elif self.args[0] not in MEMORY:
            MEMORY.update({self.args[0]: (self.args[1], F_CONST)})

class Expression:

    @staticmethod
    def add(args):
        RESULTS.append(np.add(args[0], args[1]))
        
    @staticmethod
    def sub(args): 
        RESULTS.append(np.subtract(args[0], args[1]))

    @staticmethod
    def mul(args): 
        RESULTS.append(np.multiply(args[0], args[1]))

    @staticmethod
    def div(args): 
        RESULTS.append(np.divide(args[0], args[1]))

    @staticmethod
    def floor_div(args):
        RESULTS.append(np.floor_divide(args[0], args[1]))

    @staticmethod
    def mod(args):
        RESULTS.append(np.mod(args[0], args[1]))
    
    @staticmethod
    def log(args):
        RESULTS.append(np.emath.logn(args[0], args[1]))

    @staticmethod
    def pow(args):
        RESULTS.append(np.power(args[0], args[1]))