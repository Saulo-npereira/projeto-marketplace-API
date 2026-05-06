from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship

db = create_engine('sqlite:///banco.db')

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nome = Column('nome', String)
    email = Column('email', String, unique=True)
    senha = Column('senha', String)
    saldo = Column('saldo', Float)
    admin = Column('admin', Boolean)


    def __init__(self, nome, email, senha, saldo, admin):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.saldo = saldo
        self.admin = admin

class Produto(Base):
    __tablename__ = 'produtos'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nome = Column('nome', String, nullable=False, unique=True)
    descricao = Column('descricao', String, nullable=False)
    preco = Column('preco', Float, nullable=False)
    estoque = Column('estoque', Integer, nullable=False)
    vendedor_id = Column('vendedor_id', ForeignKey('usuarios.id'), nullable=False)

    def __init__(self, nome, descricao, preco, estoque, vendedor_id):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.vendedor_id = vendedor_id

    vendedor = relationship('Usuario')

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    comprador_id = Column('comprador_id', ForeignKey('usuarios.id'), nullable=False)
    criado_em = Column('criado_em', DateTime, nullable=False)

    def __init__(self, comprador_id, criado_em):
        self.comprador_id = comprador_id
        self.criado_em = criado_em

    comprador = relationship('Usuario')


class ItensPedido(Base):
    __tablename__ = 'itens_pedido'

    

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    pedido_id = Column('pedido_id', ForeignKey('pedidos.id'), nullable=False)
    produto_id = Column('produto_id', ForeignKey('produtos.id'), nullable=False)
    quantidade = Column('quantidade', Integer, nullable=False)
    total = Column('total', Float, nullable=False)

    def __init__(self, pedido_id, produto_id, quantidade, total):
        self.pedido_id = pedido_id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.total = total

    produto = relationship('Produto')
    pedido = relationship('Pedido')