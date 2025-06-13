from pydantic import BaseModel, Field, field_serializer, model_validator
from typing import List, Optional
from decimal import Decimal
import base64




# -------- MESAS --------

class MesaBase(BaseModel):
    id: int
    identificador: str
    qrcode: str | None  # Já será uma string Base64

    class Config:
        from_attributes = True

class MesaResponse(BaseModel):
    id: int
    identificador: str
    qrcode: Optional[str] = None  # String Base64 ou None
    
    class Config:
        from_attributes = True

'''
class MesaCreate(BaseModel):
    identificador: str = Field(..., example="MESA-1")
'''
    

class MesasCreateLote(BaseModel):
    quantidade: int = Field(..., gt=0, le=50, example=1)

    prefixo: str = Field("M", example="MESA")







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
    mesa_identificador: str  # Agora mostra o identificador real da mesa (ex: "MESA-1")
    cliente_id: int
    produtos: List[ProdutoBase]


