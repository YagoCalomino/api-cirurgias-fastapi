# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas, security
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Cirurgias Refatorada")

origins = ["http://localhost", "http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================================
#                                       ENDPOINTS
# =====================================================================================

# --- Endpoint de Autenticação ---
@app.post("/token", response_model=schemas.Token, tags=["Autenticação"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ... (código de login sem alteração)
    user = security.get_user(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoints de Cirurgias (Protegidos) ---
# ... (Todos os 5 endpoints de cirurgias continuam aqui, sem alteração por enquanto)
@app.get("/api/v1/cirurgias/", response_model=List[schemas.CirurgiaSchema], tags=["Cirurgias"])
def consultar_todas_as_cirurgias(data: Optional[date] = None, medico_nome: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    # ... código ...
    query = db.query(models.CirurgiaDB)
    if data:
        query = query.filter(models.CirurgiaDB.data == data)
    if medico_nome:
        query = query.filter(models.CirurgiaDB.medico_nome.ilike(f"%{medico_nome}%"))
    return query.offset(skip).limit(limit).all()

# ... (GET por ID, POST, PUT, DELETE de cirurgias aqui)

# --- NOVOS ENDPOINTS PARA GERENCIAR PROFISSIONAIS ---

@app.post("/api/v1/profissionais/", response_model=schemas.ProfissionalSchema, status_code=status.HTTP_201_CREATED, tags=["Profissionais"])
def criar_profissional(profissional: schemas.ProfissionalCreate, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    """
    Cadastra um novo profissional no sistema.
    """
    db_profissional = models.ProfissionalDB(**profissional.model_dump())
    db.add(db_profissional)
    db.commit()
    db.refresh(db_profissional)
    return db_profissional

@app.get("/api/v1/profissionais/", response_model=List[schemas.ProfissionalSchema], tags=["Profissionais"])
def listar_profissionais(db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    """
    Lista todos os profissionais cadastrados.
    """
    return db.query(models.ProfissionalDB).all()

@app.get("/api/v1/profissionais/{profissional_id}", response_model=schemas.ProfissionalSchema, tags=["Profissionais"])
def buscar_profissional(profissional_id: int, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    """
    Busca um profissional específico pelo seu ID.
    """
    db_profissional = db.query(models.ProfissionalDB).filter(models.ProfissionalDB.id == profissional_id).first()
    if db_profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return db_profissional

@app.put("/api/v1/profissionais/{profissional_id}", response_model=schemas.ProfissionalSchema, tags=["Profissionais"])
def atualizar_profissional(profissional_id: int, profissional: schemas.ProfissionalCreate, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    """
    Atualiza os dados de um profissional.
    """
    db_profissional = db.query(models.ProfissionalDB).filter(models.ProfissionalDB.id == profissional_id).first()
    if db_profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    for key, value in profissional.model_dump().items():
        setattr(db_profissional, key, value)
        
    db.commit()
    db.refresh(db_profissional)
    return db_profissional

@app.delete("/api/v1/profissionais/{profissional_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Profissionais"])
def deletar_profissional(profissional_id: int, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    """
    Deleta um profissional do cadastro.
    """
    db_profissional = db.query(models.ProfissionalDB).filter(models.ProfissionalDB.id == profissional_id).first()
    if db_profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
        
    db.delete(db_profissional)
    db.commit()
    return