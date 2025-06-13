import sqlalchemy

# Use a mesma URL que está no alembic.ini
DB_URL = "mysql+pymysql://u214234210_barApi:developerUnxt25@193.203.175.253/u214234210_barApi"

try:
    engine = sqlalchemy.create_engine(DB_URL)
    connection = engine.connect()
    print("✅ Conexão bem-sucedida com o banco de dados!")
    connection.close()
except Exception as e:
    print("❌ Falha na conexão com o banco de dados:")
    print(f"Erro: {e}")