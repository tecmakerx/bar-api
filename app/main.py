from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import qrcode
from fastapi.responses import StreamingResponse
from io import BytesIO
import base64




models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bar API",
    description="API para gerenciamento de pedidos",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# ---------------------- PRODUTOS ----------------------

@app.post("/produtos/", response_model=List[schemas.ProdutoBase], status_code=status.HTTP_201_CREATED)
def criar_produtos(produtos: List[schemas.ProdutoCreate], db: Session = Depends(get_db)):
    return crud.create_produtos(db, produtos)

@app.get("/produtos/", response_model=List[schemas.ProdutoBase])
def listar_produtos(db: Session = Depends(get_db)):
    return crud.get_produtos(db)




# ---------------------- MESAS ----------------------

'''
@app.post("/mesas/", response_model=schemas.MesaBase, status_code=status.HTTP_201_CREATED)
def criar_mesa(mesa: schemas.MesaCreate, db: Session = Depends(get_db)):
    # Esta função agora automaticamente gera e salva o QR code
    return crud.create_mesa(db, mesa)
'''
    

@app.post("/mesas/lote/", response_model=List[schemas.MesaBase])
def criar_mesas_lote(
    lote: schemas.MesasCreateLote, 
    db: Session = Depends(get_db)
):
    try:
        mesas = crud.create_mesas_lote(
            db, 
            quantidade=lote.quantidade,
            prefixo=lote.prefixo
        )
        return mesas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar mesas: {str(e)}"
        )



@app.get("/mesas/", response_model=List[schemas.MesaBase])
def listar_mesas(db: Session = Depends(get_db)):
    try:
        mesas = crud.get_mesas(db)
        return mesas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar mesas: {str(e)}"
        )

@app.get("/mesas/identificador/{identificador}", response_model=schemas.MesaResponse)
def visualizar_mesa_por_identificador(
    identificador: str,  # Agora recebe o identificador como parâmetro
    db: Session = Depends(get_db)
):
    try:
        mesa = crud.get_mesa_by_identificador(db, identificador)
        return mesa
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/mesas/{identificador}/qrcode")
def gerar_qrcode(identificador: str, db: Session = Depends(get_db)):
    """
    Endpoint para gerar QR Code da mesa. Agora com armazenamento no banco de dados.
    
    Fluxo:
    1. Verifica se a mesa existe
    2. Se já tem QR code no banco, retorna ele
    3. Se não tem, gera um novo, salva no banco e retorna
    """
    mesa = crud.get_mesa_by_identificador(db, identificador)
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    # Se já existe QR code armazenado, retorna ele
    if mesa.qrcode:
        return StreamingResponse(BytesIO(mesa.qrcode), media_type="image/png")

    # Se não existe, gera um novo
    url = f"https://seuapp.com/welcome/{identificador}"  # Substitua pelo seu domínio real
    
    try:
        # Gera o QR code
        img = qrcode.make(url)
        buf = BytesIO()
        img.save(buf, format="PNG")
        qrcode_bytes = buf.getvalue()
        
        # Salva no banco de dados
        mesa.qrcode = qrcode_bytes
        db.commit()
        db.refresh(mesa)
        
        # Retorna o QR code
        return StreamingResponse(BytesIO(qrcode_bytes), media_type="image/png")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar QR code: {str(e)}"
        )



# ---------------------- CLIENTE - WELCOME ----------------------

@app.post("/welcome", response_model=schemas.ClienteProdutosResponse)
def welcome_via_qrcode(
    qrcode_base64: str,  # Recebe o QR Code em Base64 diretamente
    db: Session = Depends(get_db)
):
    try:
        # 1. Busca a mesa com o QR Code correspondente
        mesa = db.query(models.Mesa).filter(
            models.Mesa.qrcode == qrcode_base64
        ).first()

        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code inválido ou mesa não encontrada"
            )

        # 2. Cria o cliente associado (mantendo seu código original)
        cliente = crud.create_cliente(db, mesa.identificador)

        # 3. Retorna os produtos (mantendo seu código original)
        produtos = crud.get_produtos(db)
        if not produtos:
            raise HTTPException(status_code=404, detail="Nenhum produto cadastrado")

        return {
            "mesa_identificador": mesa.identificador,
            "cliente_id": cliente.id,
            "produtos": produtos
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))




# ---------------------- PEDIDOS ----------------------

@app.post("/pedidos/", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    for item in pedido.itens:
        produto = crud.get_produto(db, item.produto_id)
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com ID {item.produto_id} não encontrado"
            )

    return crud.create_pedido(db, pedido)

@app.get("/pedidos/", response_model=List[schemas.PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).all()

    resposta = []
    for pedido in pedidos:
        resposta.append({
            "id": pedido.id,
            "cliente_id": pedido.cliente_id,
            "mesa_identificador": pedido.cliente.mesa.identificador,  # <-- Aqui puxa o identificador da mesa
            "status": pedido.status,
            "forma_pagamento": pedido.forma_pagamento,
            "itens": [
                {
                    "produto": {
                        "id": item.produto.id,
                        "nome": item.produto.nome,
                        "preco": item.produto.preco
                    },
                    "quantidade": item.quantidade,
                    "valor_unitario": item.valor_unitario
                } for item in pedido.itens
            ]
        })

    return resposta



@app.get("/clientes-mesas-valor-total/", response_model=List[schemas.ClienteMesaValorTotalResponse])
def listar_clientes_mesas_valor_total(db: Session = Depends(get_db)):
    return crud.listar_clientes_mesas_valor_total(db)


