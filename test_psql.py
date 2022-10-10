import psycopg2
import colorama
from psycopg2 import Error
from colorama import Fore, Style

print("Connecting to factorium database... ", end = ' ')

try:
    connection = psycopg2.connect(user="postgres",
                                  # пароль, который указали при установке PostgreSQL
                                  password="Fringilla_2020",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres")
    
    print("Connected\n")

    
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM MAIN;")
    record = cursor.fetchone()
    print("Total count of facts = ", record[0], "\n")

    while True:
        keyword = input("Enter keyword: ")
        if keyword[0] == '/':
            break
        else:
            cursor.execute(F"select distinct entry, entrycom, quote from main, quotes where (entry = '{keyword}'" +
                           F"and main.tag = quotes.tag) or (quote like ('%{keyword}%') and main.tag = quotes.tag) order by entry;")
            selection = cursor.fetchall()
            count = 0

            for line in selection :
                print(Fore.BLUE + line[0] + ": " + Style.RESET_ALL + line[1])
                print(line[2])
                print("\n")
                count += 1

            print(count, "facts found.\n")

            

except (Exception, Error) as error:
    print("\nError detected: ", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("\nConnection closed.")