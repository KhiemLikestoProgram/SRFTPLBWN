
import os
import platform as pl
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from numpy import float64, int64
from rich.console import Console

########## CONSTANTS ##########
c = Console()

class SRNError:
    def __init__(self, errtype, errmes, pos) -> None:
        match pos:
            case None:
                posDetail = f"<noPosInfo>"
            case _:
                posDetail = f"[bold {COLORS['accent']}]{pos.fn}[/]:{pos.ln}:{pos.tk}"
        if SETTINGS["notify-error"]: c.bell()
        c.print(\
f"""\
{posDetail}
\t[bold red]{errtype}[/]: {errmes}
"""
        )
        sys.exit(1)

iden = lambda key: MEMORY[key].val

class Version:
	def __init__(self, stage, *args: int) -> None:
		self.stage 	= stage
		self.v 		= (str(i) for i in args)

	def __repr__(self) -> str:
		return str(self)
	
	def __str__(self) -> str:
		return f"v{'.'.join(self.v)}{self.stage[0]}"

F_CONST = 0x14 	# Constant flag for constants in this language.
F_VAR	= 0x15	# Variable flag for variables in this language.

### TOKEN TYPES ###
T_COMMENT		= SimpleNamespace(type='CMT', cls=None)
T_OTHER			= SimpleNamespace(type='OTHER', cls=None)
T_FLOAT			= SimpleNamespace(type='FLOAT', cls=float64)
T_IDENTIFIER	= SimpleNamespace(type='IDEN', cls=iden)
T_INTEGER 		= SimpleNamespace(type='INT', cls=int64)
T_STRING		= SimpleNamespace(type='STR', cls=str)
T_PARAMETER		= SimpleNamespace(type='PARAM', cls=None)

## VARIABLES ##
STACK  	= []
RESULTS = []
MEMORY  = {
	"_RES":		SimpleNamespace(tok=T_STRING.type, val=', '.join(RESULTS), type=F_VAR),
	"_STACK":	SimpleNamespace(tok=T_STRING.type, val=', '.join(STACK),	 type=F_VAR)
}

# BUILT-IN STUFF
BUILTIN_VARS	= {
	"_AUTH":  	"NTGKhiem74",
	"_CWD":		str(Path.cwd()),
	"_HW!":	 	"Hello world!",
	"_OS": 	   	f"{pl.system()} {pl.release()}",
	"_THISPL":  "SRNFTPLBWN",
	"_UTS":		float64(time.time()), # Unix time stamp
	"_USR":  	os.getlogin(),
	"_VER":	 	repr(Version('alpha', 0, 1, 1)),
	"~":		Path.home().as_posix(),
}
BUILTIN_TYPES   = [ globals()[var] for var in dir() if re.match(r'T_', var) ]

# Customizable
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
	"CFE": "ConfigurationError"
}


