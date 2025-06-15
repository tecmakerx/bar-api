from io import BytesIO
from fastapi import HTTPException
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

def create_produtos(db: Session, produtos: list[schemas.ProdutoCreate]) -> list[models.Produto]:
    produtos_criados = []
    for produto in produtos:
        novo_produto = models.Produto(
            nome=produto.nome,
            preco=produto.preco
        )
        db.add(novo_produto)
        produtos_criados.append(novo_produto)

    db.commit()

    for produto in produtos_criados:
        db.refresh(produto)

    return produtos_criados





# -------- PEDIDOS --------

def create_pedido(db: Session, pedido: schemas.PedidoCreate) -> models.Pedido:
    db_pedido = models.Pedido(
        cliente_id=pedido.cliente_id,
        forma_pagamento=pedido.forma_pagamento.upper(),
        status="PENDENTE",
        created_at=datetime.utcnow()
    )
    db.add(db_pedido)
    db.flush()  # Garante que o ID do pedido é gerado antes de criar os itens

    itens = []
    for item in pedido.itens:
        produto = get_produto(db, item.produto_id)
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com ID {item.produto_id} não encontrado"
            )

        pedido_item = models.PedidoItem(
            pedido_id=db_pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            valor_unitario=produto.preco
        )
        itens.append(pedido_item)

    db.add_all(itens)  # ⚠️ Isso garante que todos os itens sejam salvos corretamente
    db.commit()
    db.refresh(db_pedido)
    return db_pedido



def get_pedidos(db: Session):
    pedidos = db.query(models.Pedido).all()

    response = []
    for pedido in pedidos:
        response.append({
            "id": pedido.id,
            "cliente_id": pedido.cliente_id,
            '''"cliente_nome": pedido.cliente.nome,  # Se você fez o relacionamento correto'''
            "status": pedido.status,
            "forma_pagamento": pedido.forma_pagamento,
            "itens": [
                {
                    "produto": {
                        "id": item.produto.id,
                        "nome": item.produto.nome,
                        "preco": item.valor_unitario
                    },
                    "quantidade": item.quantidade,
                    "valor_unitario": item.valor_unitario
                }
                for item in pedido.itens
            ]
        })

    return response





def update_pedido_status(db: Session, pedido_id: int, status: str) -> models.Pedido | None:
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        return None

    pedido.status = status.upper()
    db.commit()
    db.refresh(pedido)
    return pedido



def listar_clientes_mesas_valor_total(db: Session) -> list[dict]:
    clientes = db.query(models.Cliente).all()

    response = []
    for cliente in clientes:
        pedidos = (
            db.query(models.Pedido)
            .filter(models.Pedido.cliente_id == cliente.id)
            .all()
        )

        total = 0
        for pedido in pedidos:
            for item in pedido.itens:
                total += float(item.valor_unitario) * item.quantidade

        response.append({
            "cliente_id": cliente.id,
            "mesa_id": cliente.mesa_id,
            "valor_total_pedidos": total
        })

    return response
