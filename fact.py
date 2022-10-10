import sys
import re
import os
import colorama
from colorama import Fore, Style

rec_tag = ''
rec_entry = ''
rec_comment = ''
rec_keylist = ''
rec_bookfl = False
rec_persfl = False
rec_selffl = False
rec_age = ''
rec_locus = ''
rec_link = ''
rec_quote = ''
rec_image = ''
rec_figure = ''

lcount = 0
ecount = 0
ycount = 0
entry = []
entries = []
group_entries = []
group_flag = False
group_tags = ''
tag_lead = ''
all_tag_nums = []


#
def process_error(e_w, tag_involved, diag) :
  global ecount

  ecount += 1

  if tag_involved :
    e.write(F'{rec_tag}: ' + diag + '\n')
  else :
    e.write(F'Line {lcount}: ' + diag + '\n')

  if e_w == 'e' :
    print(lcount, "lines processed.", ecount, "error(s) found. Abnormal termination.")
    e.write(F"{lcount} lines processed. {ecount} error(s) found.\n")  
    exit(1)

  return

#
def check_max_length(s, max_len) :
  if len(s) > max_len :
    process_error('w', True, 'The line will be truncated: ' + s[0:max_len+1] + '...')  

#
def parse_token(s) :
  global entry, entries, group_flag, group_tags, rec_link, rec_age, \
         rec_locus, rec_figure, rec_image, rec_selffl

  t = s.strip()

  if t.replace(' ', '') == '' :
    process_error('e', True, 'Blank token found (//).')

  if t[0] == '~' :
    rec_selffl = True
    if len(t) > 1:  t = t[1:]

  if t[0] == '*' :
    entry.append('*')
    u = (t.lstrip(t[0])).rsplit(':')
    entry.append(u)
  
  elif t[0] == '+' :
    entry.append('+')
    u = (t.lstrip(t[0])).rsplit(':')
    entry.append(u)
  
  elif t[0] == '@' :
    entry.append('@')
    t1 = t.lstrip(t[0])
    entry.append(t1)

  elif t[0] == '[' :
    if group_tags.find('[') < 0 : 
      rec_link = t.strip('[]')
      check_max_length(rec_link, 100)
  
  elif t[0] == '{' :
    if group_tags.find('{') < 0 :   
      rec_age = t.strip('{}')
      check_max_length(rec_age, 10)

  elif t[0] == '<' :
    if group_tags.find('<') < 0 :   
      rec_locus = t.strip('<>')
      check_max_length(rec_locus, 20)

  elif t[0] == '#' :
    if group_tags.find('#') < 0 :   
      rec_figure = t.strip('#')
      check_max_length(rec_figure, 30)

  elif t[0] == '|' :
    if group_tags.find('|') < 0 :   
      rec_image = t.strip('|')
      check_max_length(rec_image, 5)
        
  else :
    entry.append(' ')
    u = t.rsplit(':')
    entry.append(u)

  if t[0] not in '[{#<|' :
    entries.append(entry)
  
  return

#
def key_enumerate(l) :
  global key_list
  key_list = []
  for i, v in enumerate(l):
    if v[0] not in '@[{#<|' :
      key_list.append(v[1])
  
  return    

# 
def parse_string(s, group_line) :
  global entry, entries, group_entries, group_flag, group_tags, rec_tag, rec_link, rec_age, \
         rec_locus, rec_figure, rec_image, rec_selffl, tag_lead
  
  #rec_selffl = 0

  if group_tags.find('[') < 0 : rec_link = ''
  if group_tags.find('{') < 0 : 
    rec_age = ''
    rec_selffl = False # handle ~{date} in group line, useful for diaries
  if group_tags.find('<') < 0 : rec_locus = ''
  if group_tags.find('#') < 0 : rec_figure = ''
  if group_tags.find('|') < 0 : rec_image = ''

  if not group_line :
    rec_tag = s[0:6]

    try :
      i = int(s[2:6])

    except :
      process_error('e', False, 'Invalid tag found: ' + rec_tag)
      
    if i in all_tag_nums :
      process_error('e', False, 'Duplicate tag found: ' + rec_tag)
            
    all_tag_nums.append(i)
    if not rec_tag[0:2].isalpha() or not rec_tag[2:6].isdigit() :
      process_error('e', False, 'Invalid tag found: ' + rec_tag) 

    if tag_lead == '' :
      tag_lead = rec_tag[0:2]
    else :
      if rec_tag[0:2] != tag_lead :
        process_error('w', True, 'Tag lead is different from initially assigned: ' + tag_lead)

    s = s[7:]
  
  else :
    s = s[1:]  
  
  tokens = s.rsplit('/')
  entries = []
  for t in tokens :
    parse_token(t)
    entry = []
  
  if group_line :
    group_entries = entries 
    group_tags = ''
    
    if rec_link != '' : group_tags = group_tags + '['
    if rec_age != '' : group_tags = group_tags + '{'
    if rec_locus != '' : group_tags = group_tags + '<'
    if rec_figure != '' : group_tags = group_tags + '#'
    if rec_image != '' : group_tags = group_tags +'|'

    group_flag = True
  else :
    if group_flag :
      entries = entries + group_entries
     
  key_enumerate(entries)
 
  return


#
def preformat_string(s) :
  t = s
  if t[0] == ' ' :
    return ';;'
    
  for c in ['«', '»', '“', '”', "'"] :
    t = t.replace(c, '"')

  regex = re.compile('\[.*\]') 
  u = regex.search(t)
  if u != None :
    v = u.group(0)
    t = regex.sub(v.replace('/', '%'), t)
    
  return t

#
def check_for_mess(s) :
  if s.find('[') > 0 or s.find('{') > 0 or s.find('#') > 0 or s.find('<') > 0 or s.find('>') > 0 :
     process_error('w', True, 'Possible special tag capture: ' + s)

  return

#
def generate_delete_rec(g, tag_lead) :
  g.write(F"DELETE FROM MAIN WHERE substr(TAG, 1, 2) = '{tag_lead}';\n")
  g.write(F"DELETE FROM QUOTES WHERE substr(TAG, 1, 2) = '{tag_lead}';\n")
  g.write(F"DELETE FROM IMAGES WHERE substr(TAG, 1, 2) = '{tag_lead}';\n") 
  g.write('\n') 

#
def generate_records(g) :
  global entry, entries, rec_tag, rec_entry, rec_comment, rec_keylist, rec_bookfl, rec_persfl, \
         rec_selffl, rec_age, rec_locus, rec_link, rec_figure, rec_image, rec_quote, key_list, ycount

  if rec_image != '' :
    check_for_mess(rec_image)
    insert_image = F"INSERT INTO IMAGES VALUES ('{rec_tag}', '{rec_image}');"
    g.write(insert_image + '\n')
  
  for el in entries :
    if el[0] == '@' :
      rec_quote = el[1]
      check_for_mess(rec_quote)
      insert_quote = F"INSERT INTO QUOTES VALUES ('{rec_tag}', '{rec_quote}');"
      g.write(insert_quote + '\n')
       
    else :  
      ycount += 1
      rec_entry = el[1][0]
      rec_entry = rec_entry.strip()
      rec_entry = rec_entry.strip('"')
      check_for_mess(rec_entry)
      check_max_length(rec_entry, 64)
      
      rec_comment = ''
      if len(el[1]) > 1 :
        rec_comment = el[1][1]
        rec_comment = rec_comment.strip()
        check_for_mess(rec_comment)
        check_max_length(rec_comment, 200)

      rec_bookfl = False
      if el[0] == '+' :
        rec_bookfl = True
      rec_persfl = False
      if el[0] == '*' :
        rec_persfl = True
      
      rec_keylist = ''  
      for em in key_list :
        if em[0] != el[1][0] :
          rec_keylist = rec_keylist + '/' + em[0]

      rec_link = rec_link.replace('%', '/')   
      
      insert_entry = F"INSERT INTO MAIN VALUES ('{rec_tag}', '{rec_entry}', '{rec_comment}', '{rec_keylist}', {rec_bookfl}, {rec_persfl}, {rec_selffl}, '{rec_age}', '{rec_locus}', '{rec_link}', '{rec_figure}');"
      if rec_entry != '~':  # protect from orphan '~' insertion
        g.write(insert_entry + '\n')
    
  
  return


#
# Main program
#
if len(sys.argv) == 1 :
    print("No file name to convert.")
    sys.exit(1)

fpath = ''
if os.path.isdir('Facts') :
   fpath = 'Facts\\'

if sys.argv[1].endswith('.fact') :  
   fnamext = fpath + sys.argv[1]
   fname = fnamext[:-5]

else :
   fname = fpath + sys.argv[1]
   fnamext = fname + '.fact' 

e = open(fname + '.log', 'w', encoding='utf-8')
g = open(fname + '.sql', 'w', encoding='utf-8')

generate_delete_rec(g, fname[-2:])
colorama.init()

with open(fnamext, encoding='utf-8') as f:

 for line in f:

   lcount += 1
   
   if len(line) < 2 :
     continue
    
   line = preformat_string(line)

   if line[0] != ";" :
     parse_string(line, False)
     generate_records(g)

   else :
     group_tags = ''
     if line[1] != ';' :
       parse_string(line, True)
     else :
       group_flag = False
       rec_selffl = False
       if line.rstrip() != ';;' :  
          print(Fore.BLUE + line)
          print(Style.RESET_ALL)


if ecount == 0 :
  print(lcount, "lines processed. No errors found.")
  e.write(F"{lcount} lines processed. No errors found.\n")
else:
  print(lcount, "lines processed.", ecount, "error(s) found.")
  e.write(F"{lcount} lines processed. {ecount} error(s) found.\n")

print(ycount, "entries generated.")
e.write(F"{ycount} entries generated.")

e.close
g.close