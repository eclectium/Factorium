import os, re, sys, getopt, colorama
from colorama import Fore, Back, Style

lcount = tcount = 0
kwrd_flag = 0
word_flag = False
adjt_flag = False

def req_found(req, line, kf, wf) :
    i = n = 0
    l = '(' + line + ')'
    occ_list = []  
    while n >=0 :  
        n = l.find(req, i)
        i += len(req)
        if kf == 1:
            if n >= 0 and l[n-1] in '~/*' and not l[n+len(req)].isalpha() : 
                occ_list.append(n-1) 
        elif kf == 2:
            if n >= 0 and not l[n+len(req)].isalpha() : 
                occ_list.append(n-1) 
        elif wf :
            if n >= 0 and not l[n-1].isalpha() and not l[n+len(req)].isalpha() :
                occ_list.append(n-1) 
              
        else :
            if n >= 0 and not l[n-1].isalpha(): 
                occ_list.append(n-1)
    return occ_list


def print_token(s, reqs) :
    global tcount, kwrd_flag, word_flag
    
    s = s.lstrip('~*@#')
    if s[0:1].isalpha() and s[2:].isdigit() :
        s = Fore.WHITE + Back.BLUE + s + Style.RESET_ALL

    if s[0] == '+':
        s = Fore.YELLOW + Back.BLACK + '[K] ' + Style.RESET_ALL + s[1:].replace('"', '')

    if s[0] == '[' :
        s = s.replace('%', '/')

    if s[0] == '{' :
        s = Fore.YELLOW + Back.BLACK + s[1:].replace('}', '') + Style.RESET_ALL

    if s[0] == '[' :
        s = Fore.BLACK + Back.WHITE + s[1:].replace(']', '') + Style.RESET_ALL

    
    words = s.split()
    for i in range(len(words)) :
        for req in reqs :
            if req_found(req.lower(), words[i].lower(), kwrd_flag, word_flag) != [] :
                tcount += 1
                words[i] = Fore.BLACK + Back.YELLOW + words[i] + Style.RESET_ALL
    s = ' '.join(words)
    list = s.split('\\')
    for t in list :
        print(t)


def protect_html(s) :
    t = s
    n1 = t.find('[')
    if n1 >= 0 :
        n2 = t.find(']')
        if n2 < 0 :
            n2 = len(t) - 1
        u = s[n1:n2].replace('/', '%')
        t = s.replace(s[n1:n2], u)    
    return t

    
def print_line(l, reqs) :
    l = protect_html(l)
    tokens = l.rsplit('/')
    for token in tokens :
        print_token(token, reqs)
    print('\n')
       

def process_file(filename, reqs) :
    global lcount, word_flag, kwrd_flag
    group_title = ''
    result_list = []
    with open(filename, encoding='utf-8') as f:
        for line in f:
            if len(line) <= 2:
                continue
            if line[0] != ';' :
                l = line[0:6] + group_title + '/' + line[7:-1]
                i = 0
                for req in reqs:
                    if req_found(req.lower(), l.lower(), kwrd_flag, word_flag) != [] :
                        i += 1
                if i == len(reqs) :
                    lcount += 1
                    result_list.append(l)
            elif line[1] == ';' :
                group_title = ''
            else :
                group_title = '/' + line[1:-1]
    return result_list


#
# Main program
#
try:
    opts, reqs = getopt.getopt(sys.argv[1:], "abkw")
except:
    print('Invalid option')
    sys.exit(1)

if len(opts) > 1 :
    print('Only single option is supported') 
    sys.exit(1)

if reqs == [] :
    print('Use the following format:\n', 
          ' factsearch kwd1 kwd2 ... for simple search\n',
          'or\n',
          ' factsearch -a kwd1 kwd2 ... to find adjacent tokens only\n', 
          'or\n',
          ' factsearch -b kwd1 kwd2 ... to find books\n',
          'or\n',
          ' factsearch -k kwd1 kwd2 ... to find in entries\n',
          'or\n',
          ' factsearch -w kwd1 kwd2 ... to find whole words\n')
    sys.exit(1)

result = []
colorama.init()

p = reqs.copy()
for i in range(len(p)) :
    p.insert(2*i+1, r'\w*?\W')
pattern = re.compile(''.join(p), re.IGNORECASE)

for o, _ in opts:
    if o == "-k":
        kwrd_flag = 1
    elif o == "-w":
        word_flag = True
    elif o == "-a":
        adjt_flag = True
        if len(reqs) == 1 :
            print('Key -a can be used only for multiple token search\n')
            sys.exit(3)
    elif o == "-b":
        reqs.append('+"')

with os.scandir('Facts\\') as it:
    for entry in it:
        if entry.name.endswith('.fact') :
            result.extend(process_file('Facts\\' + entry.name, reqs))

if kwrd_flag == 1: 
    kwrd_flag = 2

if adjt_flag :
    lcount = 0
    for line in result :
        if pattern.search(line) != None :
            lcount += 1
            print_line(line, reqs)
else :
    for line in result :
        print_line(line, reqs)

if lcount == 0 :
    print('No occurences found.')
else :
    print(lcount, 'line(s) and', tcount, 'occurence(s) found.')
