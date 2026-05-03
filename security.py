from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from models import Usuario
from datetime import timedelta, datetime
from jose import jwt
from dotenv import load_dotenv
import os

pwd = CryptContext(schemes=['argon2'], deprecated='auto')
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/login-form')

def criar_hash(senha):
    return pwd.hash(senha)

def autenticar(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    verificar_senha = pwd.verify(senha, usuario.senha)
    if not verificar_senha:
        return False
    return usuario

def criar_token(email, exp: timedelta = timedelta(minutes=30), refresh = False):
    data_expiracao = datetime.utcnow() + exp
    dict_jwt = {'sub': email, 'exp': data_expiracao, 'refresh': refresh}
    return jwt.encode(dict_jwt, SECRET_KEY, algorithm=ALGORITHM)

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')