# app/models.py
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class UserDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class CirurgiaDB(Base):
    __tablename__ = "cirurgias"
    codigo_cirurgia = Column(Integer, primary_key=True, index=True)
    codigo_estabelecimento = Column(Integer)
    sala = Column(String)
    data = Column(Date)
    horario_inicio = Column(Time)
    status_codigo = Column(String)
    status_descricao = Column(String)
    paciente_codigo = Column(Integer)
    paciente_nome = Column(String)
    carater_atendimento = Column(String)
    medico_codigo = Column(Integer)
    medico_nome = Column(String)
    medico_conselho = Column(String)
    procedimento_descricao = Column(Text)
    
    equipe = relationship("EquipeDB", back_populates="cirurgia", cascade="all, delete-orphan")

class EquipeDB(Base):
    __tablename__ = "equipe_cirurgica"
    id = Column(Integer, primary_key=True, index=True)
    nome_profissional = Column(String)
    conselho_profissional = Column(String)
    funcao = Column(String)
    cirurgia_id = Column(Integer, ForeignKey("cirurgias.codigo_cirurgia"))

    cirurgia = relationship("CirurgiaDB", back_populates="equipe")