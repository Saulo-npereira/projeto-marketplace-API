from pydantic import BaseModel

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    saldo: float
    admin: bool

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ProdutoSchema(BaseModel):
    nome: str
    descricao: str
    preco: float
    estoque: int

    class Config:
        from_attributes = True
