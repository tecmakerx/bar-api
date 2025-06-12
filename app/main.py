from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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

# ---------------------- ROTAS ----------------------

@app.post("/produtos/", response_model=schemas.ProdutoBase, status_code=status.HTTP_201_CREATED)    #Cria novos produtos
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    return crud.create_produto(db, produto)


@app.get("/produtos/", response_model=List[schemas.ProdutoBase])   #Lista Produtos no banco de dados
def listar_produtos(db: Session = Depends(get_db)):
    return crud.get_produtos(db)


@app.get("/welcome/{mesa_id}", response_model=schemas.ClienteProdutosResponse)  # Bem Vindo
def welcome(mesa_id: str, db: Session = Depends(get_db)):
    cliente = crud.create_cliente(db, mesa_id)
    produtos = crud.get_produtos(db)
    if not produtos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum produto cadastrado"
        )
    return {
        "mesa_id" : mesa_id,
        "cliente_id": cliente.id,
        "produtos": produtos
    }


@app.post("/pedidos/", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED)  # Criar Pedidos
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    # Validação: verifica se os produtos existem
    for item in pedido.itens:
        produto = crud.get_produto(db, item.produto_id)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.produto_id} não encontrado"
            )

    db_pedido = crud.create_pedido(db, pedido)
    return db_pedido


@app.get("/pedidos/", response_model=List[schemas.PedidoResponse])   # Listar Pedidos
def listar_pedidos(db: Session = Depends(get_db)):
    return crud.get_pedidos(db)

