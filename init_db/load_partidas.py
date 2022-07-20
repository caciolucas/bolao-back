import json
import time

import requests
from db import connectdb, closedb

AVAILABLE_CHAMPIONSHIPS_CODES = ["WC", "CL", "BL1", "DED", "BSA", "PD", "FL1", "ELC", "PPL", "EC", "SA", "PL", "CLI"]
API_URL = "http://api.football-data.org/v4/competitions/{}/matches?season=2022"
TOKENS = [ '09b0cdafa7d74d19b4df8eb5687220d0', 'bd19a4f9fdae4040b6716369077f05b2']
TOKEN_INDEX = 0

def get_partidas(campeonato):
    response = requests.get(API_URL.format(campeonato), headers={'X-Auth-Token': TOKENS[TOKEN_INDEX]})
    return response.json()


def load_partidas(partidas):
    insert_query = "INSERT INTO bolao.partida (idpartida, `data`, horario, id_time_casa, num_gols_casa, id_time_fora, num_gols_fora, Campeonato_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"
    for partida in partidas:
        db, cursor = connectdb()
        idpartida = partida['id']
        data = partida['utcDate'].split('T')[0]
        horario = partida['utcDate'].split('T')[1][:-1]
        id_time_casa = partida['homeTeam']['id']
        num_gols_casa = partida['score']['fullTime']['home']
        id_time_fora = partida['awayTeam']['id']
        num_gols_fora = partida['score']['fullTime']['away']
        Campeonato_id = partida['competition']['id']
        if not id_time_casa or not id_time_fora:
            continue
        cursor.execute(insert_query, (idpartida, data, horario, id_time_casa, num_gols_casa, id_time_fora, num_gols_fora, Campeonato_id))
        db.commit()
    closedb(db)


if __name__ == "__main__":
    partidas = []
    for campeonato in AVAILABLE_CHAMPIONSHIPS_CODES:
        response = get_partidas(campeonato)
        matches = response.get('matches')
        if not matches:
            continue
        partidas.extend(matches)
        print("Received {} matches from {}".format(len(response['matches']), campeonato))
        print("Waiting for API token timeout...")
        TOKEN_INDEX = (TOKEN_INDEX + 1) % len(TOKENS)
        time.sleep(3)

    with open('partidas.json', 'w') as f:
        json.dump(partidas, f, indent=4)

    load_partidas(partidas)
