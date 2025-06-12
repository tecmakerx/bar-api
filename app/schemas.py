from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal


# -------- PRODUTOS --------

class ProdutoBase(BaseModel):
    id: int
    nome: str
    preco: Decimal  # Usa Decimal para refletir o Numeric do SQLAlchemy

    class Config:
        from_attributes = True

class ProdutoCreate(BaseModel):
    nome: str = Field(..., example="Cerveja Artesanal")
    preco: Decimal = Field(..., gt=0, example=12.50)


# -------- PEDIDO --------

class PedidoItemCreate(BaseModel):
    produto_id: int = Field(..., example=1)
    quantidade: int = Field(..., gt=0, example=2)

class PedidoCreate(BaseModel):
    cliente_id: int = Field(..., example=1)
    forma_pagamento: str = Field(..., example="PIX")  # PIX, DEBITO, CREDITO
    itens: List[PedidoItemCreate]


# -------- RESPOSTAS --------

class PedidoItemResponse(BaseModel):
    produto: ProdutoBase
    quantidade: int
    valor_unitario: Decimal

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    status: str
    forma_pagamento: str
    itens: List[PedidoItemResponse]

    class Config:
        from_attributes = True


# -------- CLIENTE WELCOME --------

class ClienteProdutosResponse(BaseModel):
    mesa_id: str
    cliente_id: int
    produtos: List[ProdutoBase]

