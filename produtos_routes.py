from fastapi import APIRouter, Depends, HTTPException
from schemas import ProdutoSchema
from models import Usuario, Produto
from sqlalchemy.orm import Session
from dependencies import verificar_usuario, pegar_sessao


produtos_router = APIRouter(prefix='/produtos', tags=['produtos'])

def formatar_produtos(tupla_produto):
    return {'nome_produto': tupla_produto[0],
            'preço': tupla_produto[1],
            'descrição': tupla_produto[2],
            'estoque': tupla_produto[3],
            'vendedor': tupla_produto[4]}

@produtos_router.post('/produtos')
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

@produtos_router.get('/produtos')
async def listar_produtos(usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    resultado = session.query(Produto.nome.label('nome_produto'),Produto.preco,Produto.descricao,Produto.estoque,Usuario.nome.label('nome_vendedor')).join(Usuario, Produto.vendedor_id == Usuario.id).all()
    if not resultado:
        raise HTTPException(status_code=400, detail='não existe produtos por enquanto')
    produtos = [formatar_produtos(x) for x in resultado ]
    return {'produtos': produtos}

@produtos_router.get('/produtos/{id_produto}')
async def detalhe_produto(id_produto: int, usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto.nome.label('nome_produto'), Produto.preco, Produto.descricao, Produto.estoque, Usuario.nome.label('nome_usuario')).join(Usuario, Produto.vendedor_id == Usuario.id).all()
    if not produto:
        raise HTTPException(status_code=404, detail='produto inexistente')
    produto = [formatar_produtos(x) for x in produto]
    return {'produto': produto}

@produtos_router.get('/seus_produtos')
async def detalhe_produto(usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto.nome.label('nome_produto'), Produto.preco, Produto.descricao, Produto.estoque, Usuario.nome.label('nome_usuario')).join(Usuario, Produto.vendedor_id == Usuario.id).filter(Produto.vendedor_id == usuario.id).all()
    if not produto:
        raise HTTPException(status_code=404, detail='Você ainda não possui produtos')
    produto = [formatar_produtos(x) for x in produto]
    return {'produtos': produto}

