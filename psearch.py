import os, re, sys, getopt, colorama, psycopg2
from psycopg2 import Error
from colorama import Fore, Style

#
def create_selects(opts, reqs) :
    result = ''
    result = "select distinct entry, entrycom, locus, quote from main, quotes where "
            + "(entry like '{keyword}' or entrycom like '{keyword}' or locus like '{keyword}' or quote like '{keyword}') and main.tag = quotes.tag "
             
    return result
    


#
# Main program
#
# Process options
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

# Connect to database
print("Connecting to factorium database... ", end = ' ')

try:
    connection = psycopg2.connect(user="postgres",
                                  password="Fringilla_2020",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres")
    
    print("Connected.\n")
    
    cursor = connection.cursor()
    selects = create_selects(opts, reqs)
    for select_str in selects :
        cursor.execute(select_str)
        selection = cursor.fetchall()
           

except (Exception, Error) as error:
    print("\nError detected: ", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("\nConnection closed.")