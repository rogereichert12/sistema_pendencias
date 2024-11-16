from flask import Blueprint, jsonify, make_response
from app.helpers import get_db_connection, close_db_connection
from app.config import Config
import pandas as pd
from io import BytesIO
from fpdf import FPDF

export_blueprint = Blueprint("export", __name__)

@export_blueprint.route("/csv", methods=["GET"])
def export_csv():
    """Exporta clientes para CSV."""
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()
        df = pd.DataFrame(clients)
        csv_data = df.to_csv(index=False, encoding="utf-8")
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = "attachment; filename=clientes.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    finally:
        cursor.close()
        close_db_connection(conn)
