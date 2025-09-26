# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

class UserSchema(BaseModel):
    model_config = {"from_attributes": True}
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class EquipeSchema(BaseModel):
    model_config = {"from_attributes": True}
    nome_profissional: str
    conselho_profissional: str
    funcao: str

class CirurgiaSchema(BaseModel):
    model_config = {"from_attributes": True}
    codigo_cirurgia: int
    codigo_estabelecimento: int
    sala: str
    data: date
    horario_inicio: time
    status_codigo: str
    status_descricao: str
    paciente_nome: str
    medico_nome: str
    equipe: List[EquipeSchema] = []

class CirurgiaCreateSchema(BaseModel):
    codigo_cirurgia: int
    codigo_estabelecimento: int
    sala: str
    data: date
    horario_inicio: time
    status_codigo: str
    status_descricao: str
    paciente_codigo: int
    paciente_nome: str
    carater_atendimento: str
    medico_codigo: int
    medico_nome: str
    medico_conselho: str
    procedimento_descricao: str
    equipe: List[EquipeSchema]