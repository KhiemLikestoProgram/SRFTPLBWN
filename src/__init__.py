"""
Author: NTGKhiem74
File name (original name): __init__.py
Last edited: 19/3/2023

This program has a <DEBUG> mode that will only work if you don't use `wrt` command to write, since it
doesn't print the newlines out.
"""
from classes import *
from srnbuiltin import Param

from pathlib import Path
import sys

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        SRNError(1.1, "Missing file name.", pos=None)
        sys.exit(1)
    else:
        FILEPATH    = Path(sys.argv[1]).absolute()
        if not FILEPATH.exists():
            SRNError(2, f"The file '{FILEPATH}' doesn't exist in the current directory.", pos=None)

    if len(sys.argv) == 3:
        PARAM       = sys.argv[2]
    
    if PARAM in PARAMETERS:
        getattr(Param, PARAMETERS[PARAM][0])()
    
    SRNFTPLBWNI(*Lexer(FILEPATH).lex()).interpret()