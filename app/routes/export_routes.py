from flask import Blueprint, jsonify, make_response
from app.helpers import get_db_connection, close_db_connection
from app.config import Config
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Blueprint para rotas de exportação
export_blueprint = Blueprint("export", __name__, url_prefix="/export")


# ========================
# ROTA: Exportar CSV
# ========================
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


# ========================
# ROTA: Exportar Excel
# ========================
@export_blueprint.route("/excel", methods=["GET"])
def export_excel():
    """Exporta clientes para Excel."""
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()
        df = pd.DataFrame(clients)

        # Gerar o arquivo Excel na memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Clientes")
        output.seek(0)

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=clientes.xlsx"
        response.headers[
            "Content-Type"
        ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    finally:
        cursor.close()
        close_db_connection(conn)


# ========================
# ROTA: Exportar PDF
# ========================
@export_blueprint.route("/pdf", methods=["GET"])
def export_pdf():
    """Exporta clientes para PDF."""
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()

        # Criar o arquivo PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)

        # Cabeçalho do PDF
        pdf.cell(200, 10, "Relatório de Clientes", ln=True, align="C")
        pdf.ln(10)

        # Conteúdo do PDF
        pdf.set_font("Arial", size=10)
        for client in clients:
            pdf.cell(
                0,
                10,
                f"ID: {client['id']}, Aluno: {client['aluno']}, Responsável: {client['responsavel']}, Telefone: {client['telefone']}, CPF: {client['cpf']}",
                ln=True,
            )

        response = make_response(pdf.output(dest="S").encode("latin1"))
        response.headers["Content-Disposition"] = "attachment; filename=clientes.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    finally:
        cursor.close()
        close_db_connection(conn)
