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
def listar_bolao(search: str ):
    db, cursor = connectdb()
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

        cursor.execute("SELECT * from bolao.partida p WHERe idpartida in (SELECT p.idpartida FROM bolao b INNER JOIN campeonato c ON c.idcampeonato = b.Campeonato_id INNER JOIN partida p ON p.Campeonato_id = c.idcampeonato ORDER BY DATA, horario)")
        primeira_partida = cursor.fetchone()
        primeira_partida = dict(zip(cursor.column_names, primeira_partida))
        bolao['primeira_partida'] = primeira_partida

    closedb(db)
    return boloes


@app.get('/api/bolao/campeonatos', )
def campeonatos():
    db, cursor = connectdb()
    cursor.execute("SELECT * FROM campeonato")
    campeonatos = cursor.fetchall()
    columns = cursor.column_names
    campeonatos = [dict(zip(columns, campeonato)) for campeonato in campeonatos]
    closedb(db)
    return campeonatos
