
from classes import *
from vars   import *

from pathlib import Path
import sys


if __name__ == "__main__":
    try:
        FILEPATH    = str(Path(sys.argv[1]).absolute())
    except IndexError:
        SRNError(1, "Missing file name.", pos=None)
        sys.exit(1)

    else:
        if not Path(FILEPATH).exists():
            SRNError(2, f"The file '{FILEPATH}' doesn't exist in the current directory.", pos=None)
    
    
    SRNI(*Lexer(FILEPATH).lex()).interpret()