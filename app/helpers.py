import mysql.connector

def get_db_connection(config):
    """
    Retorna uma conexão ao banco de dados com base na configuração.
    """
    return mysql.connector.connect(**config)

def close_db_connection(conn):
    """
    Fecha a conexão com o banco de dados, se estiver ativa.
    """
    if conn.is_connected():
        conn.close()
