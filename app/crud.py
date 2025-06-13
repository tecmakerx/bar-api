from io import BytesIO
import qrcode
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
import random
import string
from typing import List
import base64
from io import BytesIO



# -------- MESAS --------

def generate_qrcode_base64(identificador: str) -> str:
    """Gera QR Code como string Base64"""
    url = f"https://seuapp.com/welcome/{identificador}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')


'''
def create_mesa(db: Session, mesa: schemas.MesaCreate):
    url = f"https://seuapp.com/welcome/{mesa.identificador}"
    qrcode_base64 = generate_qrcode_base64(url)
    
    nova_mesa = models.Mesa(
        identificador=mesa.identificador,
        qrcode=qrcode_base64  # Armazena direto como string
    )
    db.add(nova_mesa)
    db.commit()
    return nova_mesa
'''


def create_mesas_lote(db: Session, quantidade: int, prefixo: str = "MESA") -> List[models.Mesa]:
    mesas_criadas = []
    ultimo_numero = 0
    
    # Encontra o último número usado
    ultima_mesa = db.query(models.Mesa).filter(
        models.Mesa.identificador.startswith(f"{prefixo}-")
    ).order_by(models.Mesa.identificador.desc()).first()
    
    if ultima_mesa:
        try:
            ultimo_numero = int(ultima_mesa.identificador.split("-")[1])
        except (IndexError, ValueError):
            pass
    


    # Cria as mesas em lote
    for i in range(1, quantidade + 1):
        identificador = f"{prefixo}-{ultimo_numero + i}"
        qrcode_base64 = generate_qrcode_base64(identificador)
        
        nova_mesa = models.Mesa(
            identificador=identificador,
            qrcode=qrcode_base64
        )
        db.add(nova_mesa)
        mesas_criadas.append(nova_mesa)
    
    db.commit()
    return mesas_criadas



def get_mesas(db: Session) -> List[models.Mesa]:
    return db.query(models.Mesa).all()

def get_mesa_by_identificador(db: Session, identificador: str) -> models.Mesa:
    mesa = db.query(models.Mesa).filter(
        models.Mesa.identificador == identificador
    ).first()
    
    if not mesa:
        raise ValueError(f"Mesa com identificador '{identificador}' não encontrada")
    return mesa



def get_mesa_by_identificador(db: Session, identificador: str) -> models.Mesa | None:
    return db.query(models.Mesa).filter(models.Mesa.identificador == identificador).first()






# -------- CLIENTE --------

def create_cliente(db: Session, mesa_identificador: str) -> models.Cliente:
    mesa = get_mesa_by_identificador(db, mesa_identificador)
    if not mesa:
        raise ValueError(f"Mesa com identificador '{mesa_identificador}' não existe")

    cliente = models.Cliente(mesa_id=mesa.id)
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
        forma_pagamento=pedido.forma_pagamento.upper(),
        status="PENDENTE",
        created_at=datetime.utcnow()
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)

    for item in pedido.itens:
        produto = get_produto(db, item.produto_id)
        if not produto:
            continue

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

    pedido.status = status.upper()
    db.commit()
    db.refresh(pedido)
    return pedido

