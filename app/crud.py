from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime


# -------- CLIENTE --------

def create_cliente(db: Session, mesa_id: str) -> models.Cliente:
    cliente = models.Cliente(mesa_id=mesa_id)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


# -------- PRODUTOS --------

def get_produtos(db: Session) -> list[models.Produto]:
    return db.query(models.Produto).all()

def get_produto(db: Session, produto_id: int) -> models.Produto | None:
    return db.query(models.Produto).filter(models.Produto.id == produto_id).first()

def create_produto(db: Session, produto: schemas.ProdutoCreate) -> models.Produto:
    novo_produto = models.Produto(nome=produto.nome, preco=produto.preco)
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


# -------- PEDIDOS --------

def create_pedido(db: Session, pedido: schemas.PedidoCreate) -> models.Pedido:
    db_pedido = models.Pedido(
        cliente_id=pedido.cliente_id,
        forma_pagamento=pedido.forma_pagamento.upper(),  # Garante compatibilidade com o Enum
        status="PENDENTE",
        created_at=datetime.utcnow()
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)

    for item in pedido.itens:
        produto = get_produto(db, item.produto_id)
        if not produto:
            continue  # Ignora produtos inválidos

        pedido_item = models.PedidoItem(
            pedido_id=db_pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            valor_unitario=produto.preco
        )
        db.add(pedido_item)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def get_pedidos(db: Session) -> list[models.Pedido]:
    return db.query(models.Pedido).all()

def update_pedido_status(db: Session, pedido_id: int, status: str) -> models.Pedido | None:
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        return None

    pedido.status = status.upper()  # Garante compatibilidade com Enum
    db.commit()
    db.refresh(pedido)
    return pedido
