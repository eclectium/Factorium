import subprocess
import colorama
from colorama import Fore, Back, Style
import sys

fact_prompt = "\n" + Fore.CYAN + Back.BLACK + "fct > " + Style.RESET_ALL
sqlt_prompt = "\n" + Fore.CYAN + Back.BLACK + "sql > " + Style.RESET_ALL
fact_applic = "search_fact.py"
sqlt_applic = "search_sqlt.py"
prompt = fact_prompt
applic = fact_applic

while True:
    line = input(prompt)

    if line.startswith('.') :
        if line.startswith('.x') :
            exit(0)
        if line.startswith('.f') : 
            prompt = fact_prompt
            applic = fact_applic
        elif line.startswith('.q') : 
            prompt = sqlt_prompt
            applic = sqlt_applic
        else :
            print('Illegal command')
        continue     
    
    cmd_line = line.split()
    s = 'd = subprocess.run([sys.executable, applic, '
    for cmd in cmd_line:
        s = s + '"' + cmd + '" ,'
    exec_line = s[:-1] + '])'    
    exec(exec_line)
    
  