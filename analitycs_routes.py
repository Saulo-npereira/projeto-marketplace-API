from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from models import Produto, Usuario, ItensPedido, Pedido

analitycs_router = APIRouter(prefix='/analitycs', tags=['analitycs'])

@analitycs_router.get('/total_produtos')
async def total_de_produtos(session: Session = Depends(pegar_sessao)):
    total_produtos = session.query(func.count(Produto.id)).scalar()
    return {
        'total_produtos': total_produtos
    }

@analitycs_router.get('/produto_mais_caro')
async def produto_mais_caro(session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto).order_by(Produto.preco.desc()).first()
    return {
        'produto_mais_caro': produto
    }


@analitycs_router.get('/produto_mais_barato')
async def produto_mais_barato(session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto).order_by(Produto.preco.asc()).first()
    return {
        'produto_mais_barato': produto
    }

@analitycs_router.get('/media_precos')
async def media_dos_precos(session: Session = Depends(pegar_sessao)):
    media_preco = session.query(func.avg(Produto.preco)).scalar()
    return {
        'media_precos': media_preco
    }

@analitycs_router.get('/soma_total_estoque')
async def soma_total_do_estoque(session: Session = Depends(pegar_sessao)):
    total = session.query(func.sum(Produto.estoque)).scalar()
    return {
        'total_estoque': total
    }

@analitycs_router.get('/produtos_sem_estoque')
async def produtos_sem_etoque(session: Session = Depends(pegar_sessao)):
    produtos = session.query(Produto).filter(Produto.estoque<=0).all()
    return {
        'produtos_sem_estoque': produtos
    }

@analitycs_router.get('/buscar_produtos_nome/{nome_produto}')
async def buscar_produto_por_nome(nome_produto: str, session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto).filter(Produto.nome.ilike(f'%{nome_produto}%')).first()
    if not produto:
        raise HTTPException(status_code=404, detail='produto não encontrado')
    return {
        'produto': produto
    }

@analitycs_router.get('/user_mais_pedidos')
async def usuario_com_mais_pedidos(session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario.nome, func.count(Pedido.id).label('total_pedidos')).join(Pedido, Pedido.comprador_id == Usuario.id).group_by(Usuario.nome).order_by(func.count(Pedido.id).desc()).first()
    return {
        'usuario': usuario.nome,
        'total': usuario.total_pedidos
    }
