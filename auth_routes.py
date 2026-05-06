from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_usuario, verificar_admin
from schemas import UsuarioSchema, LoginSchema
from models import Usuario
from security import criar_hash, autenticar, criar_token
from datetime import timedelta

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.post('/cadastrar')
async def criar_usuario(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail='Já existe um usuario com esse email')
    usuario = Usuario(nome=usuario_schema.nome,
                      email=usuario_schema.email,
                      senha=criar_hash(usuario_schema.senha),
                      saldo=usuario_schema.saldo,
                      admin=usuario_schema.admin)
    session.add(usuario)
    session.commit()
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    return {'detail': 'usuario criado com sucesso',
            'usuario': usuario
            }

@auth_router.post('/login')
async def login(login: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar(email=login.email,
                         senha=login.senha,
                         session=session)
    if not usuario:
        raise HTTPException(status_code=404, detail='email ou senha incorretos')
    access_token = criar_token(login.email)
    refresh_token = criar_token(login.email, timedelta(days=7), refresh=True)
    return {
        'detail': 'logado com sucesso',
        'access_token': access_token,
        'refresh_token': refresh_token
    }

@auth_router.post('/login-form')
async def login(login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar(email=login.username,
                         senha=login.password,
                         session=session)
    if not usuario:
        raise HTTPException(status_code=404, detail='email ou senha incorretos')
    access_token = criar_token(login.username)
    refresh_token = criar_token(login.username, timedelta(days=7), refresh=True)
    return {
        'detail': 'logado com sucesso',
        'access_token': access_token,
        'refresh_token': refresh_token
    }

@auth_router.get('/usuario')
async def perfil_usuario(usuario: Usuario = Depends(verificar_usuario)):
    return {
        'usuario': usuario
    }
    

