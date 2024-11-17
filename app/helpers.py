from flask import g
import mysql.connector
from app.config import Config

def get_db_connection(db_config=None):
    """
    Cria e retorna uma conexão com o banco de dados.
    """
    if db_config is None:
        from app.config import Config

        db_config = Config.DB_CONFIG  # Use o DB_CONFIG padrão da configuração

    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
    )

def close_db_connection(e=None):
    db_conn = g.pop("db_conn", None)
    if db_conn is not None and db_conn.is_connected():
        db_conn.close()
