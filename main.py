import datetime

from fastapi import FastAPI, Body, Response
import jwt
import hashlib

from starlette.responses import JSONResponse

from db import connectdb, closedb
from models import LoginModel, UserModel, Bolao, BolaoWOId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login", )
def login(data: LoginModel):
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM usuario WHERE email = %s", (data.email,))
    user = cursor.fetchone()
    if user:
        columns = cursor.column_names
        user = dict(zip(columns, user))
        if hashlib.sha256(data.senha.encode('utf-8')).hexdigest() == user['senha']:
            return {
                "token": jwt.encode({'user_email': user['email']}, "secret", algorithm="HS256", )
                # "message": "Login successful",
            }
    closedb(db)
    return JSONResponse(content={"message": "Usuário ou senha inválidos"}, status_code=401)


@app.post('/api/auth/register', )
def register(data: UserModel):
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM usuario WHERE email = %s", (data.email,))
    same_email_user = cursor.fetchone()
    if same_email_user:
        closedb(db)
        return JSONResponse(content={"message": "Email já cadastrado"}, status_code=400)

    senha = hashlib.sha256(data.senha.encode()).hexdigest()
    cursor.execute("INSERT INTO usuario (email, nome, sobrenome, telefone, senha) VALUES (%s, %s, %s, %s, %s)",
                   (data.email, data.nome, data.sobrenome, data.telefone, senha))
    db.commit()
    closedb(db)
    return {"email": data.email, "nome": data.nome, "sobrenome": data.sobrenome, "telefone": data.telefone,
            "senha": data.senha}


@app.post('/api/bolao/bolao', )
def novo_bolao(data: BolaoWOId, response: Response):
    db, cursor = connectdb()
    bearer_token = data.adminstrador_token
    administrador_email = jwt.decode(bearer_token, 'secret', algorithms=['HS256'])['user_email']
    cursor.execute(
        "INSERT INTO bolao.bolao (nome, privacidade, status, aposta_minima, Campeonato_id, Administrador_email, placar_certo, gols_time_vencedor, gols_time_perdedor, saldo_gols, acerto_vencedor, acerto_empate) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (data.nome, data.privacidade, data.status, data.aposta_minima, data.campeonato_id, administrador_email,
         data.placar_certo, data.gols_time_vencedor, data.gols_time_perdedor, data.saldo_gols, data.acerto_vencedor,
         data.acerto_empate))
    db.commit()
    closedb(db)
    return {"nome": data.nome, "privacidade": data.privacidade, "status": data.status,
            "aposta_minima": data.aposta_minima, "campeonato_id": data.campeonato_id,
            "adminstrador_email": administrador_email, "placar_certo": data.placar_certo,
            "gols_time_vencedor": data.gols_time_vencedor, "gols_time_perdedor": data.gols_time_perdedor,
            "saldo_gols": data.saldo_gols, "acerto_vencedor": data.acerto_vencedor, "acerto_empate": data.acerto_empate}


@app.get('/api/bolao/bolao', )
def listar_bolao(search: str = None):
    db, cursor = connectdb()
    if search:
        cursor.execute(
            "SELECT b.idbolao,b.nome,b.privacidade,b.status,b.aposta_minima,b.campeonato_id,b.administrador_email,b.placar_certo,b.gols_time_vencedor,b.gols_time_perdedor,b.saldo_gols,b.acerto_vencedor,b.acerto_empate  FROM bolao.bolao b INNER JOIN bolao.campeonato c ON c.idcampeonato = b.Campeonato_id WHERE b.nome LIKE %s or c.nome  LIKE %s ",
            (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM bolao.bolao")
    boloes = cursor.fetchall()
    boloes = [dict(zip(cursor.column_names, bolao)) for bolao in boloes]

    for bolao in boloes:
        cursor.execute("SELECT * FROM bolao.campeonato WHERE idcampeonato = %s", (bolao['campeonato_id'],))
        campeonato = cursor.fetchone()
        campeonato = dict(zip(cursor.column_names, campeonato))
        bolao['campeonato'] = campeonato

        cursor.execute("SELECT * FROM bolao.usuario WHERE email = %s", (bolao['administrador_email'],))
        administrador = cursor.fetchone()
        administrador = dict(zip(cursor.column_names, administrador))
        administrador.pop('senha')
        bolao['administrador'] = administrador

        cursor.execute("SELECT * FROM bolao.participa WHERE Bolao_id = %s", (bolao['idbolao'],))
        participacoes = cursor.fetchall()
        participacoes = [dict(zip(cursor.column_names, participacao)) for participacao in participacoes]
        bolao['participacoes'] = participacoes

        cursor.execute(
            "SELECT * from bolao.partida p WHERe idpartida in (SELECT p.idpartida FROM bolao b INNER JOIN campeonato c ON c.idcampeonato = b.Campeonato_id INNER JOIN partida p ON p.Campeonato_id = c.idcampeonato ORDER BY DATA, horario)")
        primeira_partida = cursor.fetchone()
        primeira_partida = dict(zip(cursor.column_names, primeira_partida))
        bolao['primeira_partida'] = primeira_partida

    closedb(db)
    return boloes


@app.get('/api/bolao/bolao/{idbolao}', )
def recuperar_bolao(idbolao: int):
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM bolao.bolao WHERE idbolao = %s", (idbolao,))
    bolao = cursor.fetchone()
    bolao = dict(zip(cursor.column_names, bolao))

    cursor.execute("SELECT * FROM bolao.campeonato WHERE idcampeonato = %s", (bolao['campeonato_id'],))
    campeonato = cursor.fetchone()
    campeonato = dict(zip(cursor.column_names, campeonato))
    bolao['campeonato'] = campeonato

    cursor.execute("SELECT * FROM bolao.usuario WHERE email = %s", (bolao['administrador_email'],))
    administrador = cursor.fetchone()
    administrador = dict(zip(cursor.column_names, administrador))
    administrador.pop('senha')
    bolao['administrador'] = administrador

    cursor.execute("SELECT * FROM bolao.participa WHERE Bolao_id = %s", (bolao['idbolao'],))
    participacoes = cursor.fetchall()
    participacoes = [dict(zip(cursor.column_names, participacao)) for participacao in participacoes]
    bolao['participacoes'] = participacoes

    return bolao


@app.post('/api/bolao/bolao/{idbolao}/participar', )
def participar_bolar(idbolao: int, token: str = Body(...), valor: float = Body()):
    db, cursor = connectdb()
    bearer_token = token
    usuario_email = jwt.decode(bearer_token, 'secret', algorithms=['HS256'])['user_email']
    cursor.execute(
        "INSERT INTO bolao.participa (Apostador_email, Bolao_id, valor_apostado, status) VALUES(%s, %s, %s, %s);",
        (usuario_email, idbolao, valor, '1'))
    db.commit()
    closedb(db)
    return {"status": "ok"}


@app.post('/api/bolao/bolao/{idbolao}/partidas/{idpartida}/palpitar', )
def palpitar(idbolao: int, idpartida: int, token: str = Body(...), gols_casa: int = Body(),
                     gols_fora: int = Body()):
    db, cursor = connectdb()
    bearer_token = token
    usuario_email = jwt.decode(bearer_token, 'secret', algorithms=['HS256'])['user_email']
    data = datetime.datetime.now()
    horario = datetime.datetime.now().time()
    data = data.strftime("%Y-%m-%d")
    cursor.execute("select * from bolao.aposta where Partida_id = %s and Apostador_email = %s", (idpartida, usuario_email))
    aposta = cursor.fetchone()
    if not aposta:
        cursor.execute(
            "INSERT INTO bolao.aposta (Apostador_email, Partida_id, gols_time_visitante, gols_time_casa, `data`, horario) VALUES(%s, %s, %s, %s, %s, %s);",
            (usuario_email, idpartida, gols_casa, gols_fora, data, horario))
    else:
        cursor.execute(
            "UPDATE bolao.aposta SET gols_time_visitante = %s, gols_time_casa = %s, `data` = %s, horario = %s WHERE Partida_id = %s and Apostador_email = %s",
            (gols_casa, gols_fora, data, horario, idpartida, usuario_email))
    db.commit()
    closedb(db)
    return {"status": "ok"}


@app.get('/api/bolao/campeonatos', )
def campeonatos():
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM campeonato")
    campeonatos = cursor.fetchall()
    columns = cursor.column_names
    campeonatos = [dict(zip(columns, campeonato)) for campeonato in campeonatos]
    closedb(db)
    return campeonatos

@app.post('/api/bolao/campeonatos/palpites', )
def get_palpites(data = Body(...)):
    db, cursor = connectdb()
    bearer_token = data['token']
    usuario_email = jwt.decode(bearer_token, 'secret', algorithms=['HS256'])['user_email']
    cursor.execute("SELECT * FROM bolao.aposta WHERE Apostador_email = %s", (usuario_email,))
    palpites = cursor.fetchall()
    columns = cursor.column_names
    palpites = [dict(zip(columns, palpite)) for palpite in palpites]
    cursor.execute("SELECT * FROM bolao.partida")
    partidas = cursor.fetchall()
    columns = cursor.column_names
    partidas = [dict(zip(columns, partida)) for partida in partidas]

    todos_palpites = {}
    for partida in partidas:
        for palpite in palpites:
            if partida['idpartida'] == palpite['Partida_id']:
                todos_palpites[partida['idpartida']] = {'fora': palpite['gols_time_visitante'],'casa': palpite['gols_time_casa']}
        if partida['idpartida'] not in todos_palpites:
            todos_palpites[partida['idpartida']] = {'fora': None,'casa': None}


    closedb(db)
    return todos_palpites

@app.get('/api/bolao/campeonatos/{id}/partidas', )
def partidas_campeonato(id: int):
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM partida WHERE Campeonato_id = %s ORDER BY DATA, HORARIO DESC", (id,))
    partidas = cursor.fetchall()
    columns = cursor.column_names
    partidas = [dict(zip(columns, partida)) for partida in partidas]

    for partida in partidas:
        if partida['id_time_casa']:
            cursor.execute("SELECT * FROM bolao.time WHERE idtime = %s", (partida['id_time_casa'],))
            time_casa = cursor.fetchone()
            time_casa = dict(zip(cursor.column_names, time_casa))
            partida['time_casa'] = time_casa
        if partida['id_time_fora']:
            cursor.execute("SELECT * FROM bolao.time WHERE idtime = %s", (partida['id_time_fora'],))
            time_fora = cursor.fetchone()
            time_fora = dict(zip(cursor.column_names, time_fora))
            partida['time_fora'] = time_fora

    closedb(db)
    return partidas
