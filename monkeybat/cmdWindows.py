import os
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE, PIPE
import sys
import time

#A12-Comparator
#    mediator
#    mediator-cli
#    (...)
#    script.py

code = """import sys
for line in sys.stdin: # poor man's `cat`
    sys.stdout.write(line)
    sys.stdout.flush()
"""


def create_console():
    return Popen([sys.executable, "-c", code],
                  stdin=PIPE, bufsize=1, universal_newlines=True,
                  creationflags=CREATE_NEW_CONSOLE)

def println():
    print("\n\n")

#supplier_count = eval(input("Number of suppliers to run (at least 2). Option: "))
compiling_console = create_console()

def windows(CMD):
    print("Compiling security module...")
    security_process = Popen(['cmd', '/k', 'start', CMD], shell=True, cwd=".", stdout=compiling_console.stdin)
windows('log')
windows('cmd')
println()

'''
print("Compiling supplier-ws module...")
supplier_ws_comp = Popen(['start', 'cmd'], shell=True, cwd=".", stdout=compiling_console.stdin)
supplier_ws_comp.wait()

'''