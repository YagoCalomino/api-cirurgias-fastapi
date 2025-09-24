# app/tests/test_main.py

import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Importações Relativas Corrigidas ---
# '..' significa "do diretório pai" (a pasta 'app')
from ..main import app
from ..database import get_db, Base
from .. import models

# --- Configuração do Banco de Dados de Teste ---
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/cirurgias_db_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Substituição da Dependência (Override) ---
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- Fixture do Pytest ---
@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

# --- Funções de Teste ---
def test_criar_usuario_e_fazer_login(client):
    from ..security import pwd_context
    from ..models import UserDB
    
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("testpassword")
    test_user = UserDB(username="testuser", hashed_password=hashed_password)
    db.add(test_user)
    db.commit()
    db.close()

    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_fluxo_completo_cirurgia(client):
    from ..security import pwd_context
    from ..models import UserDB
    from ..schemas import CirurgiaCreateSchema, EquipeSchema

    db = TestingSessionLocal()
    if not db.query(UserDB).filter(UserDB.username == "testuser").first():
        hashed_password = pwd_context.hash("testpassword")
        test_user = UserDB(username="testuser", hashed_password=hashed_password)
        db.add(test_user)
        db.commit()
    db.close()
    
    login_response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cirurgia_schema = CirurgiaCreateSchema(
        codigo_cirurgia=999, codigo_estabelecimento=1, sala="Sala Teste",
        data="2025-10-10", horario_inicio="10:00:00", status_codigo="TEST",
        status_descricao="Em Teste", paciente_codigo=1, paciente_nome="Paciente Teste",
        carater_atendimento="Eletiva", medico_codigo=1, medico_nome="Dr. Teste",
        medico_conselho="CRM/TEST 123", procedimento_descricao="Procedimento de Teste",
        equipe=[EquipeSchema(nome_profissional="Enf. Teste", conselho_profissional="COREN/TEST 123", funcao="Auxiliar")]
    )
    
    create_response = client.post("/api/v1/cirurgias/", headers=headers, json=cirurgia_schema.model_dump(mode="json"))
    
    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["paciente_nome"] == "Paciente Teste"

    read_response = client.get(f"/api/v1/cirurgias/{created_data['codigo_cirurgia']}", headers=headers)
    
    assert read_response.status_code == 200

    unauthorized_response = client.get(f"/api/v1/cirurgias/{created_data['codigo_cirurgia']}")
    assert unauthorized_response.status_code == 401