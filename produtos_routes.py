from fastapi import APIRouter, Depends, HTTPException
from schemas import ProdutoSchema
from models import Usuario, Produto, Pedido, ItensPedido
from sqlalchemy import and_
from sqlalchemy.orm import Session
from dependencies import verificar_usuario, pegar_sessao
from datetime import datetime


produtos_router = APIRouter(prefix='/produtos', tags=['produtos'])

def fazer_pedido(id_usuario, session):
    data_agora = datetime.utcnow()
    pedido = Pedido(id_usuario, data_agora)
    session.add(pedido)
    session.flush()
    return pedido

def editar_produto(produto: Produto, produto_editado: ProdutoSchema, session: Session):
    produto.nome = produto_editado.nome
    produto.descricao = produto_editado.descricao
    produto.estoque = produto_editado.estoque
    produto.preco = produto_editado.preco
    session.commit()
    return True

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
async def seus_produto(usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto.nome.label('nome_produto'), Produto.preco, Produto.descricao, Produto.estoque, Usuario.nome.label('nome_usuario')).join(Usuario, Produto.vendedor_id == Usuario.id).filter(Produto.vendedor_id == usuario.id).all()
    if not produto:
        raise HTTPException(status_code=404, detail='Você ainda não possui produtos')
    produto = [formatar_produtos(x) for x in produto]
    return {'produtos': produto}


@produtos_router.put('/produtos/{id_produto}')
async def editar_seu_produto(produto_schema: ProdutoSchema, id_produto: int, usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto).filter(and_(Produto.vendedor_id == usuario.id, Produto.id == id_produto)).first()
    if not produto:
        raise HTTPException(status_code=403, detail='Esse produto não pertence a você')
    editar_produto(produto, produto_schema, session)
    return {
        'detail': 'Produto editado com sucesso'
    }

@produtos_router.delete('/produtos/{id_produto}')
async def deletar_produto_por_id(id_produto: int, usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    if not usuario.admin:
        produto = session.query(Produto).filter(and_(Produto.vendedor_id == usuario.id, Produto.id == id_produto)).first()
        if not produto:
            raise HTTPException(status_code=403, detail='Você não pode deletar um produto que não é seu')
        
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
            raise HTTPException(status_code=404, detail='id de produto não encontrado')
    session.delete(produto)
    session.commit()
    return {
        'detail': 'produto deletado com sucesso',
        'produto': produto
    }

@produtos_router.post('/comprar/{id_produto}/{quantidade}')
async def comprar_produto_por_id(quantidade: int, id_produto: int, usuario: Usuario = Depends(verificar_usuario), session: Session = Depends(pegar_sessao)):
    produto = session.query(Produto).filter(Produto.id==id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail='produto não encontrado')
    if produto.estoque <= 0 or produto.estoque < quantidade:
        raise HTTPException(status_code=400, detail='Estoque insuficiente')
    if usuario.saldo < produto.preco * quantidade:
        raise HTTPException(status_code=400, detail='Saldo insuficiente')
    if usuario.id == produto.vendedor_id:
        raise HTTPException(status_code=403, detail='Você não pode comprar seu proprio produto')
    pedido = fazer_pedido(id_usuario = usuario.id, session = session)
    total = produto.preco * quantidade
    itens_pedido = ItensPedido(pedido.id, produto.id, quantidade, total)
    session.add(itens_pedido)
    produto.estoque -= quantidade
    vendedor = session.query(Usuario).filter(Usuario.id == produto.vendedor_id).first()
    vendedor.saldo += total
    usuario.saldo -= total
    session.commit()
    return {
        'detail': 'compra realizada com sucesso'
    }



