
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
		return str(self)
	
	def __str__(self) -> str:
		return f"v{'.'.join(self.v)}{self.stage[0]}"

F_STAT  = 0x11  # Statement flag.
F_EXPR  = 0x12  # Expression flag.
F_CONST = 0x13 	# Constant flag for constants in this language.
F_VAR	= 0x14	# Variable flag for variables in this language.

LITERALS = {
	"==":   "EQEQ"
}

KEYWORD	 = {
	"STMT": {
		"prn":    ("PRINT",	 "sys.stdout.write(' '.join(self.ARGV))"),
		"prnLn":  ("PRNLN",	 "sys.stdout.write(' '.join(self.ARGV)+'\\n')"),
		"set":    ("SET",	 
"""\
if ($0 not in MEMORY) or ($0 in MEMORY and MEMORY[$0][1] == F_VAR):
	MEMORY.update({' '.join(self.ARGV)[0]: (' '.join(self.ARGV)[1], F_VAR)})
else:
	SRNError(11, "Can't change value of a constant.", self.pos)
"""),
		"def":    ("DEF",	 
"""\
if $0 in MEMORY and MEMORY[$0][1] == F_CONST:
	SRNError(11, "Can't change value of a constant.", self.pos)
elif $0 not in MEMORY:
  	MEMORY.update({' '.join(self.ARGV)[0]: (' '.join(self.ARGV)[1], F_CONST)})
"""),
	},
	"EXPR": {
		"add":	  ("ADD",	 "np.add( 		self.ARGV[0], self.ARGV[1]"),
		"sub":	  ("SUB",	 "np.subtract(	self.ARGV[0], self.ARGV[1]"),
		"mul":	  ("MUL",	 "np.multiply(	self.ARGV[0], self.ARGV[1]"),
		"div":	  ("DIV",	 "np.divide(	self.ARGV[0], self.ARGV[1]"),
		"fdiv":	  ("FDIV"	 "np.divmod(	self.ARGV[0], self.ARGV[1]"),
		"mod":	  ("MOD",	 "np.mod(		self.ARGV[0], self.ARGV[1]"),
		"log":	  ("LOG",	 "np.emath.logn(self.ARGV[0], self.ARGV[1]"),
		"pow":	  ("POW",	 "np.power(		self.ARGV[0], self.ARGV[1]"),
	},
}

REQUIREMENTS = {
	"SET": 		0,
	"DEF": 		0,
	"PRINT": 	"all",
	"PRNLN": 	"all",
}

### TOKEN TYPES ###
T_FLOAT			= 'FLOAT'
T_IDENTIFIER	= 'IDEN'	
T_INTEGER 		= 'INT'
T_STRING		= 'STR'

DIGITS = '0123456789ABCDEF'

BUILTIN_VARS	= {
	"_AUTH":  "NTGKhiem74",
	"_USR":  os.getlogin(),
	"_CWD":	str(Path.cwd()),
	"_HW!":	 	"Hello world!",
	"_OS": 	   f"{pl.system()} {pl.version()}",
	"_THISPL":  "SRNFTPLBWN",
	"_UNIXTIME": time.time(),
	"_VER":	 	repr(Version('alpha', 0, 1, 1)),
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