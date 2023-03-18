
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

KEYWORDS = {
	"STMT": {
	#	Token	    Type	  Function to call   #
		"inp":	  ("INPUT",  "inp"),
		"inpLn":  ("INPLN",  "inpLn"),
		"prn":    ("PRINT",	 "prn"),
		"prnLn":  ("PRNLN",	 "prnLn"),
		"set":    ("SET",	 "var"),
		"def":    ("DEF",	 "const"),
	},
	"EXPR": {
		"sub":	  ("SUB",	 "sub"),
		"add":	  ("ADD",	 "add"),
		"mul":	  ("MUL",	 "mul"),
		"div":	  ("DIV",	 "div"),
		"fdiv":	  ("FDIV",	 "floor_div"),
		"mod":	  ("MOD",	 "mod"),
		"log":	  ("LOG",	 "log"),
		"pow":	  ("POW",	 "pow"),
	},
}

REQUIREMENTS = {
	"SET": 		0,
	"DEF": 		0,
	"PRINT": 	"all",
	"PRNLN": 	"all",
	"INPUT":	"all",
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