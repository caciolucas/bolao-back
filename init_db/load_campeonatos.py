import requests
from db import connectdb, closedb

API_URL = "http://api.football-data.org/v4/competitions"
AVAILABLE_CHAMPIONSHIPS_CODES = ["WC", "CL", "BL1", "DED", "BSA", "PD", "FL1", "ELC", "PPL", "EC", "SA", "PL", "CLI"]


def get_campeonatos():
    response = requests.get(API_URL)
    return response.json()


def load_campeonatos(campeonatos):
    insert_query = "INSERT INTO bolao.campeonato (idcampeonato, nome, emblema) VALUES(%s, %s, %s);"
    for campeonato in campeonatos:
        db, cursor = connectdb()
        codigo = campeonato.get('code')
        if codigo in AVAILABLE_CHAMPIONSHIPS_CODES:
            cursor.execute(insert_query, (campeonato['id'], campeonato['name'], campeonato['emblem']))
        db.commit()
        closedb(db)


if __name__ == "__main__":
    campeonatos = get_campeonatos()['competitions']
    print("Loading {} campeonatos".format(len(campeonatos)))
    load_campeonatos(campeonatos)
