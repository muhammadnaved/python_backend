#!D:\naved_personal\OCS\new_design\backend\backend\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'knox==0.0.22','console_scripts','knox'
__requires__ = 'knox==0.0.22'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('knox==0.0.22', 'console_scripts', 'knox')()
    )
