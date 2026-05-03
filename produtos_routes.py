from fastapi import APIRouter, Depends
from schemas import ProdutoSchema
from models import Usuario, Produto
from sqlalchemy.orm import Session
from dependencies import verificar_usuario, pegar_sessao


produtos_router = APIRouter(prefix='/produtos', tags=['produtos'])

@produtos_router.post('/criar_produto')
async def criar_produto(produto_schema: ProdutoSchema, usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = Produto(nome=produto_schema.nome,
                      descricao=produto_schema.descricao,
                      preco=produto_schema.preco,
                      estoque=produto_schema.estoque,
                      vendedor_id=usuario.id)
    session.add(produto)
    session.commit()
    session.refresh(produto)
    return {
        'detail': 'produto criado com sucesso',
        'produto': produto
    }
