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

class ProfissionalBase(BaseModel):
    nome: str
    conselho_profissional: Optional[str] = None

class ProfissionalCreate(ProfissionalBase):
    pass

class ProfissionalSchema(ProfissionalBase):
    id: int
    model_config = {"from_attributes": True}


# dados da equipe apareçam dentro de uma cirurgia
class MembroEquipeInfo(BaseModel):
    funcao: str
    profissional: ProfissionalSchema
    model_config = {"from_attributes": True}

# API deve retornar quando peço uma cirurgia
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
    # A equipe será uma lista contendo os dados completos dos profissionais
    equipe: List[ProfissionalSchema] = []

# dados necessários para criar uma nova cirurgia
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
    # Para criar, lista de IDs dos profissionais e suas funções
    equipe: List[int] = [] # Por enquanto, vamos enviar só os IDs.