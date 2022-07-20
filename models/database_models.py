import datetime
import hashlib
from typing import Optional, Dict, List

from pydantic import BaseModel, constr, Field

from db import connectdb, closedb
from models.request_models import BolaoCreate
from utils import cursor_result_to_dict, crypt_password


class Usuario(BaseModel):
    email: constr(max_length=45) = Field(...)
    nome: constr(max_length=45) = Field(...)
    sobrenome: constr(max_length=45) = Field(...)
    telefone: constr(max_length=15) = Field(...)
    senha: str

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}):
        select_query = f"SELECT * FROM usuario"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def join_bolao(self, bolao_id: int):
        Bolao.retrieve_from_db(single=True, filters={"idbolao": bolao_id}).add_user_participation(self.email)

    def check_password(self, senha):
        user = self.retrieve_from_db(single=True, filters={"email": self.email})
        if crypt_password(senha) == user.senha:
            return True
        return False

    @classmethod
    def insert_in_db(cls, dict_user):
        insert_query = "INSERT INTO usuario (email, nome, sobrenome, telefone, senha) VALUES(%s, %s, %s, %s, %s);"
        dict_user["senha"] = crypt_password(dict_user["senha"])
        db, cursor = connectdb()
        cursor.execute(insert_query, (
            dict_user['email'], dict_user['nome'], dict_user['sobrenome'], dict_user['telefone'], dict_user['senha']))
        db.commit()
        closedb(db)

    def clean_dict(self):
        r = self.dict()
        r.pop("senha")
        return r


class Campeonato(BaseModel):
    idcampeonato: int = Field(...)
    nome: constr(max_length=45) = Field(...)
    emblema: constr(max_length=100) = Field(...)

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}):
        select_query = f"SELECT * FROM campeonato"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def serialize(self):
        object_dict = self.dict()
        return object_dict


class Bolao(BolaoCreate):
    idbolao: int = Field(...)
    administrador_email: constr(max_length=45) = Field(...)

    @classmethod
    def insert_in_db(cls, dict_bolao):
        insert_query = "INSERT INTO bolao " \
                       "(nome, privacidade, status, aposta_minima, Campeonato_id, Administrador_email, placar_certo," \
                       " gols_time_vencedor, gols_time_perdedor, saldo_gols, acerto_vencedor, acerto_empate) " \
                       "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db, cursor = connectdb()
        cursor.execute(insert_query, (dict_bolao['nome'], dict_bolao['privacidade'], dict_bolao['status'],
                                      dict_bolao['aposta_minima'], dict_bolao['campeonato_id'],
                                      dict_bolao['administrador_email'], dict_bolao['placar_certo'],
                                      dict_bolao['gols_time_vencedor'], dict_bolao['gols_time_perdedor'],
                                      dict_bolao['saldo_gols'], dict_bolao['acerto_vencedor'],
                                      dict_bolao['acerto_empate']))
        db.commit()
        closedb(db)

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}):
        select_query = f"SELECT * FROM bolao"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    @classmethod
    def search_on_database(cls, search, single=False):
        search_query = "SELECT b.idbolao,b.nome,b.privacidade,b.status,b.aposta_minima,b.campeonato_id," \
                       "b.administrador_email,b.placar_certo,b.gols_time_vencedor,b.gols_time_perdedor,b.saldo_gols," \
                       "b.acerto_vencedor,b.acerto_empate  " \
                       "FROM bolao.bolao b INNER JOIN bolao.campeonato c ON c.idcampeonato = b.Campeonato_id " \
                       "WHERE b.nome LIKE %s or c.nome LIKE %s "
        db, cursor = connectdb()
        cursor.execute(search_query, (f"%{search}%", f"%{search}%"))
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def serialize(self):
        object_dict = self.dict()
        object_dict["campeonato"] = Campeonato.retrieve_from_db(single=True,
                                                                filters={"idcampeonato": self.campeonato_id}).dict()
        object_dict["administrador"] = Usuario.retrieve_from_db(single=True,
                                                                filters={"email": self.administrador_email}
                                                                ).clean_dict()
        object_dict["participantes"] = self.get_user_participations()
        object_dict["primeira_partida"] = self.get_match()
        object_dict["ultima_partida"] = self.get_match(True)
        return object_dict

    def add_user_participation(self, user_email):
        status = 1 if self.privacidade == "publico" else 0
        insert_query = "INSERT INTO participa (Apostador_email, Bolao_id, valor_apostado, status) VALUES(%s, %s, %s, %s)"
        db, cursor = connectdb()
        cursor.execute(insert_query, (user_email, self.idbolao, self.aposta_minima, status))
        db.commit()
        closedb(db)

    def get_user_participations(self):
        participacoes = Participacao.retrieve_from_db(single=False, filters={"Bolao_id": self.idbolao})
        return [participacao.clean_dict() for participacao in participacoes]

    def get_match(self, last=False):
        direction = "DESC" if last else "ASC"
        partida = Partida.retrieve_from_db(single=True, filters={"Campeonato_id": self.campeonato_id},
                                           order_by=["data " + direction, "horario " + direction])
        return partida.serialize()


class Participacao(BaseModel):
    Apostador_email: constr(max_length=45) = Field(...)
    status: int = Field(...)
    Bolao_id: int = Field(...)
    valor_apostado: int = Field(...)

    def clean_dict(self):
        object_dict = self.dict()
        object_dict.pop("Bolao_id")
        object_dict.pop("valor_apostado")
        return object_dict

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}):
        select_query = f"SELECT * FROM participa"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def update_on_db(self, dict_participacao):
        update_query = "UPDATE participa SET status = %s WHERE Apostador_email = %s AND Bolao_id = %s"
        db, cursor = connectdb()
        cursor.execute(update_query, (dict_participacao['status'], self.Apostador_email,
                                      self.Bolao_id))
        db.commit()
        closedb(db)


class Partida(BaseModel):
    idpartida: int = Field(...)
    data: datetime.date = Field(...)
    horario: datetime.timedelta = Field(...)
    id_time_casa: int = Field(...)
    id_time_fora: int = Field(...)
    num_gols_casa: Optional[int] = Field(...)
    num_gols_fora: Optional[int] = Field(...)
    Campeonato_id: int = Field(...)

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}, order_by: List[str] = ""):
        select_query = f"SELECT * FROM partida"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        if order_by:
            select_query += f" ORDER BY {','.join(order_by)}"

        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def serialize(self):
        object_dict = self.dict()
        object_dict['data'] = datetime.datetime(self.data.year, self.data.month, self.data.day) + object_dict.pop(
            'horario')
        object_dict['data'] = str(object_dict['data'])
        object_dict['time_casa'] = Time.retrieve_from_db(single=True, filters={"idtime": self.id_time_casa}).serialize()
        object_dict['time_fora'] = Time.retrieve_from_db(single=True, filters={"idtime": self.id_time_fora}).serialize()

        return object_dict


class Time(BaseModel):
    idtime: int = Field(...)
    nome: str = Field(...)
    escudo: str = Field(...)

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}, order_by: List[str] = ""):
        select_query = f"SELECT * FROM time"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        if order_by:
            select_query += f" ORDER BY {','.join(order_by)}"

        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    def serialize(self):
        object_dict = self.dict()
        return object_dict


class Aposta(BaseModel):
    Apostador_email: constr(max_length=45) = Field(...)
    Partida_id: int = Field(...)
    gols_time_visitante: int = Field(...)
    gols_time_casa: int = Field(...)
    data: datetime.date = Field(...)
    horario: datetime.timedelta = Field(...)

    @classmethod
    def retrieve_from_db(cls, single=False, filters: Dict[str, any] = {}, order_by: List[str] = ""):
        select_query = f"SELECT * FROM aposta"
        if filters:
            filters = " AND ".join(f"{k} LIKE '{v}'" for k, v in filters.items())
            select_query += f" WHERE {filters}"
        if order_by:
            select_query += f" ORDER BY {','.join(order_by)}"

        db, cursor = connectdb()
        cursor.execute(select_query)
        response = cursor_result_to_dict(cursor, single)
        closedb(db)
        if single:
            return cls(**response) if response else None
        else:
            return [cls(**r) for r in response]

    @classmethod
    def get_for_apostador(cls, apostador_email, campeonato_id):
        select_query = f"SELECT * FROM aposta a right join partida p ON p.idpartida = a.Partida_id WHERE (a.Apostador_email = '{apostador_email}' OR a.Apostador_email IS NULL)"
        if campeonato_id:
            select_query += f" AND p.Campeonato_id = {campeonato_id}"
        db, cursor = connectdb()
        cursor.execute(select_query)
        closedb(db)
        apostas = cursor_result_to_dict(cursor, False)
        palpites = {
            aposta['idpartida']: {'fora': aposta['gols_time_visitante'], 'casa': aposta['gols_time_casa'], }
            for aposta in apostas
        }
        return palpites

    @classmethod
    def insert_in_db(cls, aposta):
        insert_query = "INSERT INTO aposta (Apostador_email, Partida_id, gols_time_visitante, gols_time_casa, data," \
                       "horario) VALUES (%s, %s, %s, %s, %s, %s)"
        data = datetime.date.today()
        horario = datetime.datetime.now().time()
        db, cursor = connectdb()
        cursor.execute(insert_query, (aposta['Apostador_email'], aposta['Partida_id'], aposta['gols_time_visitante'],
                                      aposta['gols_time_casa'], data, horario))
        db.commit()
        closedb(db)

    def update_in_db(cls, gols_time_visitante, gols_time_casa):
        data = datetime.date.today()
        horario = datetime.datetime.now().time()
        update_query = "UPDATE aposta SET gols_time_visitante = %s, gols_time_casa = %s, `data` = %s, horario = %s " \
                       "WHERE Partida_id = %s and Apostador_email = %s"
        db, cursor = connectdb()
        cursor.execute(update_query,
                       (gols_time_visitante, gols_time_casa, data, horario, cls.Partida_id, cls.Apostador_email))
        db.commit()
        closedb(db)
