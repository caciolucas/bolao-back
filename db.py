from urllib.parse import urlparse

import mysql.connector
import os


CLEARDB_DATABASE_URL = os.environ.get('CLEARDB_DATABASE_URL', 'mysql://root:localhost@localhost:3306/bolao')

mydb = mysql.connector



def parse_mysql_url(url):
    database_connection = {}

    parsed = urlparse(url)

    netloc = parsed.netloc
    username, password = netloc.split("@")[0].split(":")  # Split username and password

    host_port = netloc.split("@")[1].split(":")  # Split host and port
    if len(host_port) == 1:  # If no port is specified, use default port 3306
        host, port = host_port[0], 3306
    else:
        host, port = host_port  # Otherwise, use host and port

    database_connection['username'] = username
    database_connection['password'] = password
    database_connection['host'] = host
    database_connection['port'] = port
    database_connection['database'] = parsed.path[1:]  # Skip the leading '/'

    return database_connection
def connectdb():
    db = mydb.connect(
        **parse_mysql_url(CLEARDB_DATABASE_URL)
    )
    cursor = db.cursor(buffered=True)
    return db, cursor


def closedb(db):
    db.close()
