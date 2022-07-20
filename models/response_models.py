from typing import List, Dict
from pydantic import BaseModel, Field
from models.database_models import Bolao, Campeonato


class BaseResponse(BaseModel):
    success: bool = Field(...)


class MessageResponse(BaseResponse):
    message: str = Field(...)


class LoginSuccessResponse(BaseResponse):
    token: str = Field(...)


class RegisterResponse(BaseResponse):
    ...


class BolaoResponse(Bolao):
    administrador: dict = Field(...)
    campeonato: dict = Field(...)
    participantes: dict = Field(...)


class CampeonatoResponse(Campeonato):
    ...


class PartidaPalpiteResponse(BaseResponse):
    palpites: Dict = Field(...)


BolaoListResponse = List[BolaoResponse]
CampeonatoListResponse = List[CampeonatoResponse]
DEFAULT_ERROR_RESPONSES = {401: {"description": "Unauthorized", "model": MessageResponse},
                           500: {"description": "Internal Server Error", "model": MessageResponse}}
