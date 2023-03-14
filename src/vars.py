
from pathlib import Path
import time
import json
import platform as pl
import os
import re

os.environ["SRNFTPL_SETTINGS_PATH"] = r"D:\srnftplbwn\settings"


########## CONSTANTS ##########
class Version:
	def __init__(self, stage, *args: int) -> None:
		self.stage 	= stage
		self.v 		= (str(i) for i in args)

	def __repr__(self) -> str:
		return f"v{'.'.join(self.v)}{self.stage[0]}"
	
	def __str__(self) -> str:
		return f"v{'.'.join(self.v)}{self.stage[0]}"

F_STAT  = 0x1001 #  Statement flag
F_EXPR  = 0x1002 # Expression flag

KEYWORD	 = {
	"var":    "VAR",
	"prn":	  "PRINT",
	"prnLn":  "PRNLN",
	"const":  "CONST",

	"add":	  "ADD",
	"sub":	  "SUB",
	"mul":	  "MUL",
	"div":	  "DIV",
	"fdiv":	  "FDIV",
	"mod":	  "MOD",
	"log":	  "LOG",
}
LITERALS = {
	"==":   "EQEQ"
}
TEMPL = {
	"$0": "ARGV[0]",
	"$1": "ARGV[1]",
	"$arg": "' '.join(ARGV)"
}
COMPUTE = {
    'ADD':   "np.add($0, $1)",
    'SUB':   "np.subtract($0, $1)",
    'MUL':   "np.multiply($0, $1)",
    'DIV':   "np.divide($0, $1)",
    'FDIV':  "np.divmod($0, $1)",
    'MOD':   "np.mod($0, $1)",
    'LOG':   "np.emath.logn($0, $1)",
}
EXECUTE = {
    'PRINT': "sys.stdout.write($arg)",
    'PRNLN': "sys.stdout.write($arg+'\\n')",
    'VAR':   "MEMORY.update({$0: $1})"
}

### TOKEN TYPES ###
T_FLOAT			= 'FLOAT'
T_IDENTIFIER	= 'IDEN'	
T_INTEGER 		= 'INT'
T_STRING		= 'STR'

DIGITS = '0123456789ABCDEF'

BUILTIN_VARS	= {
	"_AUTHOR":  "NTGKhiem74",
	"_CURUSR":  os.getlogin(),
	"_CWDIR":	str(Path.cwd()),
	"_HW!":	 	"Hello world!",
	"_OS": 	   f"{pl.system()} {pl.version()}",
	"_THISPL":  "SRNFTPLBWN",
	"_UNIXTIME": time.time(),
	"_USERS":   os.name,
	"_VER":	 	repr(Version('alpha', 1, 0, 0)),
	"~":		str(Path.home()),
}
BUILTIN_TYPES   = [ globals()[var] for var in dir() if re.search(r'T_', var)]

STPATH = os.environ.get("SRNFTPL_SETTINGS_PATH")
with open(f"{STPATH}/settings.json", 'r') as stFile:
	SETTINGS = json.loads(stFile.read())
with open(f"{STPATH}/config.json", 'r') as cfFile:
	CONFIGS = json.loads(cfFile.read())

# Not constants!
MEMORY  = {}
STACK  	= []
RESULTS = []