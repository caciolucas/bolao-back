import mysql.connector

mydb = mysql.connector


def connectdb():
    db = mydb.connect(
        host="localhost",
        user="root",
        password="localhost"
    )
    cursor = db.cursor()
    cursor.execute("USE bolao")
    return db, cursor


def closedb(db):
    db.close()
