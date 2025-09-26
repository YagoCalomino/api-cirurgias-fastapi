# app/models.py
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

# Base para os modelos SQLAlchemy
Base = declarative_base()

#  tabela de associação para a equipe cirúrgica.
# abelas 'cirurgias' e 'profissionais'.
equipe_cirurgica_association = Table('equipe_cirurgica', Base.metadata,
    Column('cirurgia_id', Integer, ForeignKey('cirurgias.codigo_cirurgia', ondelete="CASCADE"), primary_key=True),
    Column('profissional_id', Integer, ForeignKey('profissionais.id', ondelete="CASCADE"), primary_key=True),
    Column('funcao', String)
)

class UserDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

#  novo modelo para Profissionais
class ProfissionalDB(Base):
    __tablename__ = "profissionais"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    conselho_profissional = Column(String)
    
    # relação para ver em quais cirurgias este profissional participou
    cirurgias = relationship("CirurgiaDB", secondary=equipe_cirurgica_association, back_populates="equipe")

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
    
    # relação muitos-para-muitos usando a tabela de associação 'secondary'
    equipe = relationship("ProfissionalDB", secondary=equipe_cirurgica_association, back_populates="cirurgias")