from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_admin
from models import Produto, Usuario, ItensPedido, Pedido

analitycs_router = APIRouter(prefix='/analitycs', tags=['analitycs'])

@analitycs_router.get('/total_produtos')
async def total_de_produtos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    total_produtos = session.query(func.count(Produto.id)).scalar()
    return {
        'total_produtos': total_produtos
    }

@analitycs_router.get('/produto_mais_caro')
async def produto_mais_caro(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto).order_by(Produto.preco.desc()).first()
    return {
        'produto_mais_caro': produto
    }


@analitycs_router.get('/produto_mais_barato')
async def produto_mais_barato(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto).order_by(Produto.preco.asc()).first()
    return {
        'produto_mais_barato': produto
    }

@analitycs_router.get('/media_precos')
async def media_dos_precos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    media_preco = session.query(func.avg(Produto.preco)).scalar()
    return {
        'media_precos': media_preco
    }

@analitycs_router.get('/soma_total_estoque')
async def soma_total_do_estoque(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    total = session.query(func.sum(Produto.estoque)).scalar()
    return {
        'total_estoque': total
    }

@analitycs_router.get('/produtos_sem_estoque')
async def produtos_sem_etoque(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produtos = session.query(Produto).filter(Produto.estoque<=0).all()
    return {
        'produtos_sem_estoque': produtos
    }

@analitycs_router.get('/buscar_produtos_nome/{nome_produto}')
async def buscar_produto_por_nome(nome_produto: str, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto).filter(Produto.nome.ilike(f'%{nome_produto}%')).first()
    if not produto:
        raise HTTPException(status_code=404, detail='produto não encontrado')
    return {
        'produto': produto
    }

@analitycs_router.get('/user_mais_pedidos')
async def usuario_com_mais_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    usuario = session.query(Usuario.nome, func.count(Pedido.id).label('total_pedidos')).join(Pedido, Pedido.comprador_id == Usuario.id).group_by(Usuario.nome).order_by(func.count(Pedido.id).desc()).first()
    return {
        'usuario': usuario.nome,
        'total': usuario.total_pedidos
    }

@analitycs_router.get('/produto_mais_pedido')
async def produto_com_mais_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto.nome, func.count(ItensPedido.id).label('total_pedidos')).join(ItensPedido, Produto.id == ItensPedido.produto_id).group_by(Produto.nome).order_by(func.count(ItensPedido.id).desc()).first()
    return {
        'produto': produto.nome,
        'total_pedidos': produto.total_pedidos
    }

@analitycs_router.get('/produto_menos_estoque')
async def produto_com_menos_estoque(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto.nome, Produto.estoque).filter(Produto.estoque != 0).order_by(Produto.estoque.asc()).first()
    return {
        'produto': produto.nome,
        'estoque': produto.estoque
    }

@analitycs_router.get('/media_itens_pedido')
async def media_de_itens_por_pedido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    quantidade_pedidos = session.query(Pedido).count()
    quantidade_itens = session.query(func.sum(ItensPedido.quantidade)).scalar()
    media = float(quantidade_itens / quantidade_pedidos)
    return {
        'media': media.__round__(2)
    }

@analitycs_router.get('usuario_mais_gastou')
async def usuario_que_mais_gastou(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    usuario = session.query(Usuario.nome, func.sum(ItensPedido.total).label('total_gasto')).join(Pedido, Pedido.comprador_id == Usuario.id).join(ItensPedido, ItensPedido.pedido_id == Pedido.id).group_by(Usuario.nome).order_by(func.sum(ItensPedido.total).desc()).first()
    return {
        'usuario': usuario.nome,
        'total_gasto': usuario.total_gasto
    }

@analitycs_router.get('/produtos_nunca_comprado')
async def produtos_nunca_comprado(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produtos = session.query(Produto).outerjoin(ItensPedido, ItensPedido.produto_id == Produto.id).filter(ItensPedido.id == None).all()
    return {
        'produtos': produtos
    }

@analitycs_router.get('/quantidade_itens_vendido')
async def quantidade_total_de_itens_vendidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    quantidade = session.query(func.sum(ItensPedido.quantidade)).scalar()
    return {
        'quantidade_total': quantidade
    }

@analitycs_router.get('/produto_mais_vendido')
async def produto_mais_vendido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_admin)):
    produto = session.query(Produto.nome, func.sum(ItensPedido.quantidade).label('quantidade')).join(ItensPedido, Produto.id == ItensPedido.produto_id).group_by(Produto.nome).order_by(func.sum(ItensPedido.quantidade).desc()).first()
    return {
        'produto': produto.nome,
        'quantidade_vendas': produto.quantidade
    }
