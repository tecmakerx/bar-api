from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Enums nomeados ajudam na leitura e uso futuro
StatusPedidoEnum = ("PENDENTE", "APROVADO", "RECUSADO")
FormaPagamentoEnum = ("PIX", "DEBITO", "CREDITO")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pedidos = relationship("Pedido", back_populates="cliente")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True, nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)  # 10 dígitos no total, 2 decimais


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    status = Column(Enum(*StatusPedidoEnum, name="status_pedido"), default="PENDENTE", nullable=False)
    forma_pagamento = Column(Enum(*FormaPagamentoEnum, name="forma_pagamento"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")


class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")
