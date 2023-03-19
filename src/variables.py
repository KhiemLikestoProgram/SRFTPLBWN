
from pathlib import Path
import json, os, re, time
import platform as pl

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
F_CONST = 0x14 	# Constant flag for constants in this language.
F_VAR	= 0x15	# Variable flag for variables in this language.

### TOKEN TYPES ###
T_COMMENT		= 'CMT'
T_FLOAT			= 'FLOAT'
T_IDENTIFIER	= 'IDEN'	
T_INTEGER 		= 'INT'
T_STRING		= 'STR'

BUILTIN_VARS	= {
	"_AUTH":  	"NTGKhiem74",
	"_USR":  	os.getlogin(),
	"_CWD":		str(Path.cwd()),
	"_HW!":	 	"Hello world!",
	"_OS": 	   	f"{pl.system()} {pl.version()}",
	"_THISPL":  "SRNFTPLBWN",
	"_UNIXTIME":time.time(),
	"_VER":	 	repr(Version('alpha', 0, 1, 1)),
	"~":		str(Path.home()),
}
BUILTIN_TYPES   = [ globals()[var] for var in dir() if re.match(r'T_', var) ]

### KEYWORDS ###
KEYWORDS = {
	#	Token	    Type	  Function to call   #
	"COMMENT": {
		"cmt":	  (T_COMMENT, "comment",	None),
		"#":	  (T_COMMENT, "comment",	None),
	},
	"STMT": {
		"ask":	  ("INPUT",  "inp", 	("all", BUILTIN_TYPES)),
		"askLn":  ("INPLN",  "inpLn", 	("all", BUILTIN_TYPES)),
		"wrt":    ("PRINT",	 "prn", 	("all", BUILTIN_TYPES)),
		"wrtLn":  ("PRNLN",	 "prnLn", 	("all", BUILTIN_TYPES)),
		"set":    ("SET",	 "var", 	(1, 	BUILTIN_TYPES)),
		"def":    ("DEF",	 "const", 	(1, 	BUILTIN_TYPES)),
	},
	"EXPR": {
		"sub":	  ("SUB",	 "sub", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"add":	  ("ADD",	 "add", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"mul":	  ("MUL",	 "mul", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"div":	  ("DIV",	 "div", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"fdiv":	  ("FDIV",	 "floor_div", ("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"mod":	  ("MOD",	 "mod", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"log":	  ("LOG",	 "log", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"pow":	  ("POW",	 "pow", 	("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
		"sum":    ("SUM", 	 "add",		("all", (T_IDENTIFIER, T_INTEGER, T_FLOAT))),
	},
}

STPATH = r"D:\srnftplbwn\settings"

with open(f"{STPATH}/settings.json", 'r') as setting:
	SETTINGS = json.loads(setting.read())

with open(f"{STPATH}/config.json", 'r') as config:
	CONFIGS = json.loads(config.read())

# Not constants!
MEMORY  = {}
STACK  	= []
RESULTS = []