
from pathlib 		import Path
from numpy 			import int64, float64
from rich.console   import Console
from rich.panel		import Panel
import platform as pl
import re
import os, time, sys

########## CONSTANTS ##########
c = Console()

class SRNError:
    def __init__(self, errtype, errmes, pos) -> None:
        match pos:
            case None:
                posDetail = f"<noPosInfo>"
            case _:
                posDetail = f"[File [bold {COLORS['accent']}]{pos.fn}[/], line {pos.ln}, token no. {pos.tk}]"
        if SETTINGS["notify-error"]: c.bell()
        c.log(\
f"""\
[bold red]{errtype}[/]: {errmes}
{posDetail}
"""
        )
        sys.exit(1)

class iden:
	def __new__(self, key):
		return MEMORY[key][1]

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
T_COMMENT		= 'CMT', None
T_OTHER			= 'OTHER', None
T_FLOAT			= 'FLOAT', float64
T_IDENTIFIER	= 'IDEN', iden
T_INTEGER 		= 'INT', int64
T_STRING		= 'STR', str
T_PARAMETER		= 'PARAM', None

## VARIABLES ##
MEMORY  = {}
STACK  	= []
RESULTS = []

BUILTIN_VARS	= {
	"_AUTH":  	"NTGKhiem74",
	"_CWD":		str(Path.cwd()),
	"_HW!":	 	"Hello world!",
	"_OS": 	   	f"{pl.system()} {pl.release()}",
	"_THISPL":  "SRNFTPLBWN",
	"_UTS":		time.time(), # Unix time stamp
	"_USR":  	os.getlogin(),
	"_VER":	 	repr(Version('alpha', 0, 1, 1)),
	"~":		str(Path.home()),
}
BUILTIN_TYPES   = [ globals()[var] for var in dir() if re.match(r'T_', var) ]

SETTINGS = {
    "show-debug-info": False,
    "notify-error": False
}

RT_PARAMETERS = {
	"-d": ("debug", "Show the states of variables in each command, one at a time."),
	"-?": ("help",	"Show this help message."),
}
COLORS = {
	"accent": "#29dfa9",
	"version": "#107b69",
}
ERRORS = {
	"SCE": "SourceCodeError",
	"ITPTE": "InterpreterError"
}


