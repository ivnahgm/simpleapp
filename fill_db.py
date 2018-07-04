#!/usr/bin/python

import random
import psycopg2
import psycopg2.extras
from settings import *


db_settings = {
        "user": DBUSER,
        "password": DBPASS,
        "dbname": DBNAME,
        "host": DBHOST
        }

def getListFromFile (fileName):
    listFromFile = []

    for line in open(fileName, 'r'):
        listFromFile.append(line.rstrip('\n'))
    
    return listFromFile

def getRandomFromList (List):
    return List[random.randint(0, len(List)-1)]

def getRandomCellPhone ():
    cellPhone = "+79"
    
    for i in range(9):
        cellPhone += str(random.randint(0,9))
    
    return cellPhone


if __name__ == '__main__':

    cities = getListFromFile(CITIES)
    names = [
        {
            'names': getListFromFile(MALENAMES),
            'surnames': getListFromFile(MALESURNAMES)
        },
        {
            'names': getListFromFile(FEMALENAMES),
            'surnames': getListFromFile(FEMALESURNAMES)
        }
    ]


    connection = psycopg2.connect(**db_settings)
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    for city in cities:
        cur.execute("""INSERT INTO cities (name) VALUES (%s);""", (city,))    
        connection.commit()

    for i in range(10000):
        randomGender = random.randint(0,1)

        cur.execute("""SELECT id FROM cities ORDER BY random() LIMIT 1;""")
        randomCity = cur.fetchone()
        cur.execute("""
        INSERT INTO phones (name, surname, phone_number, citie_id)
        VALUES (%s, %s, %s, %s)
        """, (
        getRandomFromList(names[randomGender]['names']),
        getRandomFromList(names[randomGender]['surnames']),
        getRandomCellPhone(),
        randomCity[0]))

        connection.commit()