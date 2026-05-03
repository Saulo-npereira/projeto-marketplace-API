from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from models import db, Usuario
from security import oauth2_schema, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_usuario(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    '''
    pega o token do oauth2 e e retorna o usuario do token(se existir)
    '''
    try:
        usuario = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = usuario.get('sub')
        if not email:
            raise HTTPException(
                status_code=401,
                detail='token inválido'
            )
        usuario = session.query(Usuario).filter(Usuario.email==email).first()
        if not usuario:
            raise HTTPException(status_code=404, detail='usuário não encontrado')
        return usuario

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='token inválido'
        )
    
def verificar_admin(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    '''
    pega o token do oauth2 e e retorna o usuario do token(se existir)
    '''
    try:
        usuario = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = usuario.get('sub')
        if not email:
            raise HTTPException(
                status_code=401,
                detail='token inválido'
            )
        usuario = session.query(Usuario).filter(Usuario.email==email).first()
        if not usuario:
            raise HTTPException(status_code=404, detail='usuário não encontrado')
        if not usuario.admin:
            raise HTTPException(status_code=404, detail='usuário não é admin')
        return usuario

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='token inválido'
        )