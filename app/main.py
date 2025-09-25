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

# Configuração do CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de Login com DEBUG ---
@app.post("/token", response_model=schemas.Token, tags=["Autenticação"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # --- INÍCIO DO CÓDIGO DE DEBUG ---
    print("--- Nova Tentativa de Login ---")
    print(f"Username recebido do formulário: '{form_data.username}'")
    print(f"Password recebido do formulário: '{form_data.password}'")
    
    user = security.get_user(db, username=form_data.username)
    
    if not user:
        print("DEBUG: Usuário NÃO encontrado no banco de dados.")
        print("--------------------------")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"DEBUG: Usuário encontrado no banco: '{user.username}'")
    print(f"DEBUG: Hash salvo no banco: {user.hashed_password}")
    
    is_password_correct = security.verify_password(form_data.password, user.hashed_password)
    print(f"DEBUG: A senha está correta? {is_password_correct}")
    print("--------------------------")
    # --- FIM DO CÓDIGO DE DEBUG ---

    if not user or not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoints de Cirurgias (Protegidos) ---
@app.get("/api/v1/cirurgias/", response_model=List[schemas.CirurgiaSchema], tags=["Cirurgias"])
def consultar_todas_as_cirurgias(
    data: Optional[date] = None,
    medico_nome: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(security.get_current_user)
):
    query = db.query(models.CirurgiaDB)
    if data:
        query = query.filter(models.CirurgiaDB.data == data)
    if medico_nome:
        query = query.filter(models.CirurgiaDB.medico_nome.ilike(f"%{medico_nome}%"))
    cirurgias = query.offset(skip).limit(limit).all()
    return cirurgias

@app.get("/api/v1/cirurgias/{id_cirurgia}", response_model=schemas.CirurgiaSchema, tags=["Cirurgias"])
def consultar_cirurgia_por_id(id_cirurgia: int, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    db_cirurgia = db.query(models.CirurgiaDB).filter(models.CirurgiaDB.codigo_cirurgia == id_cirurgia).first()
    if db_cirurgia is None:
        raise HTTPException(status_code=404, detail="Cirurgia não encontrada")
    return db_cirurgia

@app.post("/api/v1/cirurgias/", response_model=schemas.CirurgiaSchema, status_code=status.HTTP_201_CREATED, tags=["Cirurgias"])
def criar_cirurgia(cirurgia: schemas.CirurgiaCreateSchema, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    cirurgia_data = cirurgia.model_dump()
    equipe_data = cirurgia_data.pop("equipe")
    db_cirurgia = models.CirurgiaDB(**cirurgia_data)
    db.add(db_cirurgia)
    db.commit()
    db.refresh(db_cirurgia)
    for membro_data in equipe_data:
        db_membro = models.EquipeDB(**membro_data, cirurgia_id=db_cirurgia.codigo_cirurgia)
        db.add(db_membro)
    db.commit()
    db.refresh(db_cirurgia)
    return db_cirurgia

@app.put("/api/v1/cirurgias/{id_cirurgia}", response_model=schemas.CirurgiaSchema, tags=["Cirurgias"])
def atualizar_cirurgia(id_cirurgia: int, cirurgia_atualizada: schemas.CirurgiaCreateSchema, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    db_cirurgia = db.query(models.CirurgiaDB).filter(models.CirurgiaDB.codigo_cirurgia == id_cirurgia).first()
    if not db_cirurgia:
        raise HTTPException(status_code=404, detail="Cirurgia não encontrada para atualização")
    update_data = cirurgia_atualizada.model_dump()
    equipe_data = update_data.pop("equipe", [])
    for key, value in update_data.items():
        setattr(db_cirurgia, key, value)
    db.query(models.EquipeDB).filter(models.EquipeDB.cirurgia_id == id_cirurgia).delete()
    for membro_data in equipe_data:
        db.add(models.EquipeDB(**membro_data, cirurgia_id=id_cirurgia))
    db.commit()
    db.refresh(db_cirurgia)
    return db_cirurgia

@app.delete("/api/v1/cirurgias/{id_cirurgia}", status_code=status.HTTP_200_OK, tags=["Cirurgias"])
def deletar_cirurgia(id_cirurgia: int, db: Session = Depends(get_db), current_user: schemas.UserSchema = Depends(security.get_current_user)):
    db_cirurgia = db.query(models.CirurgiaDB).filter(models.CirurgiaDB.codigo_cirurgia == id_cirurgia).first()
    if not db_cirurgia:
        raise HTTPException(status_code=404, detail="Cirurgia não encontrada para deletar")
    db.delete(db_cirurgia)
    db.commit()
    return {"detail": f"Cirurgia com ID {id_cirurgia} e sua equipe foram deletadas com sucesso."}