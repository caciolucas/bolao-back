from fastapi import FastAPI, Body
import jwt

from starlette.requests import Request
from starlette.responses import JSONResponse

from db import connectdb, closedb
from fastapi.middleware.cors import CORSMiddleware

from models.database_models import Usuario, Bolao, Campeonato, Participacao, Partida, Aposta
from models.request_models import Login, BolaoCreate, RequestAnswer, RequestPalpite
from models.response_models import LoginSuccessResponse, MessageResponse, BolaoListResponse, \
    DEFAULT_ERROR_RESPONSES, BolaoResponse, CampeonatoListResponse
from utils import generate_token, check_for_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login", tags=["Autenticação"], response_model=LoginSuccessResponse,
          responses=DEFAULT_ERROR_RESPONSES)
def login(body: Login):
    try:
        user = Usuario.retrieve_from_db(filters={"email": body.email}, single=True)
        if user and user.check_password(body.senha):
            return JSONResponse(
                {"success": True, "token": generate_token(user.email)},
                status_code=200
            )

        return JSONResponse(content={
            "success": False,
            "message": "Usuário e/ou senha inválidos"
        }, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.post('/api/auth/register', tags=["Autenticação"])
def register(body: Usuario):
    try:
        user = Usuario.retrieve_from_db(filters={"email": body.email}, single=True)
        if user:
            return JSONResponse(content={
                "success": False,
                "message": "Email já cadastrado"
            }, status_code=401)

        Usuario.insert_in_db(body.dict())

        return JSONResponse(content={
            "success": True,
            "message": "Usuário cadastrado com sucesso"
        }, status_code=200)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.post('/api/bolao', response_model=MessageResponse, tags=["Bolão"], responses=DEFAULT_ERROR_RESPONSES)
def create_bolao(body: BolaoCreate, request: Request):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            bolao = body.dict()
            bolao['administrador_email'] = response.get('email')
            Bolao.insert_in_db(bolao)
            return JSONResponse(content={
                "success": True,
                "message": "Bolão cadastrado com sucesso"
            }, status_code=201)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.get('/api/bolao', response_model=BolaoListResponse, tags=["Bolão"], responses=DEFAULT_ERROR_RESPONSES)
def list_bolao(request: Request, search: str = None):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            if search:
                boloes = Bolao.search_on_database(search)
            else:
                boloes = Bolao.retrieve_from_db()
            return JSONResponse(content={
                "success": True,
                "data": [boloes.serialize() for boloes in boloes]
            }, status_code=200)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.get('/api/bolao/{idbolao}', response_model=BolaoResponse, tags=["Bolão"], responses=DEFAULT_ERROR_RESPONSES)
def retrieve_bolao(idbolao: int, request: Request):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            bolao = Bolao.retrieve_from_db(single=True, filters={"idbolao": idbolao})
            return JSONResponse(content={
                "success": True,
                "data": bolao.serialize()
            }, status_code=200)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.post('/api/bolao/{idbolao}/join', response_model=MessageResponse, tags=["Bolão"],
          responses=DEFAULT_ERROR_RESPONSES)
def join_bolao(idbolao: int, request: Request):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            user = Usuario.retrieve_from_db(filters={"email": response.get('email')}, single=True)
            user.join_bolao(idbolao)
            return JSONResponse(content={
                "success": True,
                "message": "Participação realizada com sucesso!"
            }, status_code=200)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.post('/api/bolao/{idbolao}/responder', response_model=MessageResponse, tags=["Bolão"], )
def answer_request(idbolao: int, request: Request, body: RequestAnswer):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            participacao = Participacao.retrieve_from_db(
                filters={"Bolao_id": idbolao, "Apostador_email": body.Apostador_email}, single=True)
            if participacao:
                participacao.update_on_db({'status': body.status})
                return JSONResponse(content={
                    "success": True,
                    "message": "Resposta realizada com sucesso!"
                }, status_code=200)
            return JSONResponse(content={
                "success": False,
                "message": "Participação não encontrada"
            }, status_code=404)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@app.get('/api/campeonatos/{idcampeonato}/partidas/palpites', )
def get_palpites(idcampeonato: int, apostador_email: str, request: Request):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            partidas_apostadas = Aposta.get_for_apostador(apostador_email, idcampeonato)
            return JSONResponse(content={
                "success": True,
                "data": partidas_apostadas
            }, status_code=200)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)

@app.post('/api/campeonatos/{idcampeonato}/partidas/{idpartida}/palpites', )
def palpitar(idcampeonato: int, idpartida: int, request: Request, body: RequestPalpite):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            aposta = Aposta.retrieve_from_db(
                filters={"Partida_id": idpartida, "Apostador_email": response.get('email')}, single=True)

            if aposta:
                aposta.update_in_db(**body.dict())
                return JSONResponse(content={
                    "success": True,
                    "message": "Palpite realizado com sucesso!"
                }, status_code=200)
            else:
                Aposta.insert_in_db(
                    {'Apostador_email': response.get('email'), 'Partida_id': idpartida, **body.__dict__})
                return JSONResponse(content={
                    "success": True,
                    "message": "Palpite realizado com sucesso!"
                }, status_code=200)

        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)

    db, cursor = connectdb()
    bearer_token = token
    usuario_email = jwt.decode(bearer_token, 'secret', algorithms=['HS256'])['user_email']
    data = datetime.datetime.now()
    horario = datetime.datetime.now().time()
    data = data.strftime("%Y-%m-%d")
    cursor.execute("select * from bolao.aposta where Partida_id = %s and Apostador_email = %s",
                   (idpartida, usuario_email))
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


@app.get('/api/campeonatos/{idcampeonato}/partidas', )
def partidas_campeonato(idcampeonato: int, request: Request):
    try:
        response = check_for_token(request.headers.get('Authorization', ''))
        if response.get('success'):
            partidas = Partida.retrieve_from_db(filters={"Campeonato_id": idcampeonato})
            return JSONResponse(content={
                "success": True,
                "data": [partida.serialize() for partida in partidas]
            }, status_code=200)
        return JSONResponse(content=response, status_code=401)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)
