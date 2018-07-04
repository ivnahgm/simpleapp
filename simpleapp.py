#!/usr/bin/python

from flask import abort, Flask, render_template, request
import psycopg2
import psycopg2.extras
import os
import re
from settings import *


psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
simpleapp = Flask(__name__)

db_settings = {
        "user": DBUSER,
        "password": DBPASS,
        "dbname": DBNAME,
        "host": DBHOST
        }
only_int = re.compile('^\d+$')


@simpleapp.route('/')
@simpleapp.route('/phones')
def phones():
    ''' show page with all enities in database
    '''
    listname = "All phones list"

    try:
        connection = psycopg2.connect(**db_settings)
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT phones.name,phones.surname,phones.phone_number,cities.name as city
                       FROM phones INNER JOIN cities ON
                       (phones.city_id=cities.id) ORDER BY surname;""")

        phones = cur.fetchall()
    except:
        abort(500)
    finally: 
        connection.commit()
    
    return render_template("phonespage.html",
            listname=listname,
            phones=phones
            )

if __name__ == "__main__":
#    simpleapp.debug = True
#    simpleapp.run(host='0.0.0.0')
    simpleapp.run()