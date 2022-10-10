#!C:\Users\eclec\AppData\Local\Microsoft\WindowsApps\python3.exe

import os, re, sys, codecs, cgi

lcount = tcount = 0
kwrd_flag = 0
word_flag = False
adjt_flag = False


def wrall(fl, s) :
    fl.write(s)
    print(s)
    
    
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


def print_token(s, reqs, self, fl) :
    global tcount, kwrd_flag, word_flag

    comment_flag = (s.find('@') >= 0)

    s = s.lstrip('~*@#')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')   

    if s[0:1].isalpha() and s[2:].isdigit() :
        s = '<b style="color: grey">' + s + '</b>'

    if s[0] == '|':  
        return

    if s[0] == '+':
        s = '<b>[K] </b>' + s[1:].replace('"', '') 

    if s[0] == '[' :
        s = s.replace('%', '/')
        if s.find('http') >= 0:
            s = '<a href="' + s[1:-1] + '">' + s[1:-1] +'</a>'
    
    if s[0] == '{' :
        s = '<u>' + s[1:].replace('}', '') + '</u>'

    
    words = s.split()
    for i in range(len(words)) :
        for req in reqs :
            if req_found(req.lower(), words[i].lower(), kwrd_flag, word_flag) != [] :
                tcount += 1
                words[i] = '<span style="background: yellow">' + words[i] + '</span>'
    s = ' '.join(words)
    if comment_flag and self :
        s = '<i>' + s + '</i>'
    list = s.split('\\')
    for t in list :
        wrall(fl, t + '<br>')


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

    
def print_line(l, reqs, fl) :

    self = (l.find('~') >=0)

    l = protect_html(l)
    tokens = l.rsplit('/')
    wrall(fl, '<p>')
    for token in tokens :
        print_token(token, reqs, self, fl)
    i = l.find('|')
    if i >= 0:
        s = '<img src="/images/' + l[0:6] +'.' + l[i+1:i+4] + '">'
        wrall(fl, s)
       

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


def html_head(fl) :
    wrall(fl, '<!DOCTYPE HTML>')
    wrall(fl, '<html>')
    wrall(fl, ' <head>')
    wrall(fl, ' <meta charset="utf-8">')
    wrall(fl, ' <title>Facts found</title>')
    wrall(fl, ' <style type="text/css">')
    wrall(fl, ' p {font-family: Arial, Helvetica, sans-serif;}')
    wrall(fl, ' </style>')
    wrall(fl, ' </head>')
    wrall(fl, '<body>') 


def html_tail(fl) :
    wrall(fl, '</body>')
    wrall(fl, '</html>')


#
# Main program
#

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
print("Content-Type: text/html")
print()


form = cgi.FieldStorage()
wanted = form.getfirst("wanted", "")
reqs = wanted.split()
key_k = form.getfirst("key_k", "")
key_b = form.getfirst("key_b", "")
key_w = form.getfirst("key_w", "")
key_a = form.getfirst("key_a", "")
cpath = 'D:\\Users\\sklyankin\\Factorium'

result = []

p = reqs.copy()
for i in range(len(p)) :
    p.insert(2*i+1, r'\w*?\W')
pattern = re.compile(''.join(p), re.IGNORECASE)


if key_k == "1":
    kwrd_flag = 1
elif key_w == "3":
    word_flag = True
elif key_a == "4":
    adjt_flag = True
elif key_b == "2":
    reqs.append('+"')

with os.scandir(cpath + '\\facts\\') as it:
    for entry in it:
        if entry.name.endswith('.fact') :
            result.extend(process_file(cpath + '\\Facts\\' + entry.name, reqs))

if kwrd_flag == 1: 
    kwrd_flag = 2

html_file = open(cpath + '\\hist\\result.html', 'w', encoding='utf-8')
html_head(html_file)

if adjt_flag :
    lcount = 0
    for line in result :
        if pattern.search(line) != None :
            lcount += 1
            print_line(line, reqs, html_file)
else :
    for line in result :
        print_line(line, reqs, html_file)

html_tail(html_file)
html_file.close






