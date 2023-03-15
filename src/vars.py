
from pathlib import Path
import json, os, re, time
import platform as pl

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

F_STAT  = 0x11  # Statement flag.
F_EXPR  = 0x12  # Expression flag.
F_LOCKED = 0x13 # Locked flag for constants in this language.

LITERALS = {
	"==":   "EQEQ"
}

KEYWORD	 = {
	"EXECUTE": {
		"prn":    ("PRINT",  "sys.stdout.write($arg)"),
		"prnLn":  ("PRNLN",  "sys.stdout.write($arg+'\\n')"),
		"var":    ("VAR",	 "MEMORY.update({$0: $1})"),
		"const":  ("CONST",  "MEMORY.update({$0: ($1, F_LOCKED)}"),
	},
	"COMPUTE": {
		"add":	  ("ADD",  "np.add($0, $1)"),
		"sub":	  ("SUB",  "np.subtract($0, $1)"),
		"mul":	  ("MUL",  "np.multiply($0, $1)"),
		"div":	  ("DIV",  "np.divide($0, $1)"),
		"fdiv":	  ("FDIV", "np.divmod($0, $1)"),
		"mod":	  ("MOD",  "np.mod($0, $1)"),
		"log":	  ("LOG",  "np.emath.logn($0, $1)"),
		"pow":	  ("POW",  "np.power($0, $1)"),
	},
}

REQUIREMENTS = {
	"VAR": 		0,
	"CONST": 	0,
	"PRINT": 	"all",
	"PRNLN": 	"all",
}

TEMPL = {
	"$0": "self.ARGV[0]",
	"$1": "self.ARGV[1]",
	"$arg": "' '.join(self.ARGV)"
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
	"_VER":	 	repr(Version('alpha', 1, 0, 0)),
	"~":		str(Path.home()),
}
BUILTIN_TYPES   = [ globals()[var] for var in dir() if re.search(r'T_', var) ]

STPATH = os.environ.get("SRNFTPL_SETTINGS_PATH")

with open(f"{STPATH}/settings.json", 'r') as stFile:
	SETTINGS = json.loads(stFile.read())

with open(f"{STPATH}/config.json", 'r') as cfFile:
	CONFIGS = json.loads(cfFile.read())

# Not constants!
MEMORY  = {}
STACK  	= []
RESULTS = []