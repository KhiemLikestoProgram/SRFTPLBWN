f"""
Author: NTGKhiem74
File name (original name): __init__.py
Last edited: 19/3/2023

This program also has a debug mode and a help message.
How to interpret the file:
1) Run `python __init__.py some-path-to-the-file.srn [-d | -?]`
2) Run `srn some-path-to-the-file.srn [-d | -?]`
3) Double click on a .srn file <will implementing soon, experimental>
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
        if sys.argv[2] in RT_PARAMETERS:
            getattr(Param, RT_PARAMETERS[sys.argv[2]][0])()
    
    Interpreter(*Lexer(FILEPATH).lex()).run()