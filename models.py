from typing import Optional

from pydantic import BaseModel, constr, Field


class LoginModel(BaseModel):
    email: str = Field(...)
    senha: str = Field(...)


class UserModel(BaseModel):
    email: constr(max_length=45) = Field(...)
    nome: constr(max_length=45) = Field(...)
    sobrenome: constr(max_length=45) = Field(...)
    telefone: constr(max_length=15) = Field(...)
    senha: str


class BolaoWOId(BaseModel):
    nome: constr(max_length=45) = Field(...)
    privacidade: constr(max_length=45) = Field(...)
    status: int = Field(...)
    aposta_minima: float = Field(...)
    campeonato_id: int = Field(...)
    adminstrador_email: Optional[constr(max_length=45)] = None
    adminstrador_token: Optional[str] = None
    placar_certo: int = Field(...)
    gols_time_vencedor: int = Field(...)
    gols_time_perdedor: int = Field(...)
    saldo_gols: int = Field(...)
    acerto_vencedor: int = Field(...)
    acerto_empate: int = Field(...)

class Bolao(BolaoWOId):
    id: int = Field(...)
