from pydantic import BaseModel, Field, constr


class Login(BaseModel):
    email: str = Field(...)
    senha: str = Field(...)


class RequestAnswer(BaseModel):
    status: int = Field(...)
    Apostador_email: str = Field(...)


class BolaoCreate(BaseModel):
    nome: constr(max_length=45) = Field(...)
    privacidade: constr(max_length=45) = Field(...)
    status: int = Field(...)
    aposta_minima: float = Field(...)
    campeonato_id: int = Field(...)
    placar_certo: int = Field(...)
    gols_time_vencedor: int = Field(...)
    gols_time_perdedor: int = Field(...)
    saldo_gols: int = Field(...)
    acerto_vencedor: int = Field(...)
    acerto_empate: int = Field(...)

class RequestPalpite(BaseModel):
    gols_time_casa: int = Field(...)
    gols_time_visitante: int = Field(...)