from flask import Blueprint, jsonify, request, render_template
from app.helpers import get_db_connection, close_db_connection
from app.config import Config

# Definição do Blueprint
produtos_blueprint = Blueprint("produtos", __name__, url_prefix="/produtos")

@produtos_blueprint.route("/list", methods=["GET"])
def listar_produtos():
    """
    Retorna a lista de produtos para o dropdown.
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, descricao, id_categoria, preco FROM produtos")
        produtos = cursor.fetchall()
        return jsonify({"produtos": produtos}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar produtos: {e}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)
