import time

import requests
from db import connectdb, closedb

AVAILABLE_CHAMPIONSHIPS_CODES = ["WC", "CL", "BL1", "DED", "BSA", "PD", "FL1", "ELC", "PPL", "EC", "SA", "PL", "CLI"]
API_URL = "http://api.football-data.org/v4/competitions/{}/teams"
TOKENS = [ '09b0cdafa7d74d19b4df8eb5687220d0', 'bd19a4f9fdae4040b6716369077f05b2']
TOKEN_INDEX = 0
def get_times(campeonato):
    response = requests.get(API_URL.format(campeonato), headers={'X-Auth-Token': TOKENS[TOKEN_INDEX]})
    return response.json()


def load_times(times):
    insert_query = "INSERT INTO bolao.`time` (idtime, nome, escudo) VALUES(%s, %s, %s);"
    for time in times:
        db, cursor = connectdb()
        cursor.execute(insert_query, (time['id'], time['name'], time['crest']))
        db.commit()
        closedb(db)

def deduplicate_times(times):
    deduplicate_times_list = []
    deduplicate_times_ids_list = []
    for time in times:
        if time['id'] not in deduplicate_times_ids_list:
            deduplicate_times_list.append(time)
            deduplicate_times_ids_list.append(time['id'])

    return deduplicate_times_list


if __name__ == "__main__":
    times = []
    for campeonato in AVAILABLE_CHAMPIONSHIPS_CODES:
        response = get_times(campeonato)
        times.extend(response['teams'])
        print("Received {} times from {}".format(len(response['teams']), campeonato))
        print("Waiting for API token timeout...")
        TOKEN_INDEX = (TOKEN_INDEX + 1) % len(TOKENS)
        time.sleep(3)

    load_times(deduplicate_times(times))