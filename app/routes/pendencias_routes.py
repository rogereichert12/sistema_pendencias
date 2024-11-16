from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    session,
    redirect,
    url_for,
)
from app.helpers import get_db_connection, close_db_connection
from app.config import Config

# Blueprint para as rotas de pendências
pendencias_blueprint = Blueprint("pendencias", __name__, url_prefix="/pendencias")


# ========================
# ROTA: Renderizar Página de Pendências
# ========================
@pendencias_blueprint.route("/", methods=["GET"])
def pendencias_page():
    """
    Renderiza a página HTML de pendências.

    Requisitos:
    - O usuário deve estar autenticado (checar a sessão 'user').

    Redireciona para a página de login caso a sessão esteja vazia.
    """
    if "user" in session:
        return render_template("pendencias.html")
    return redirect(url_for("auth.login"))


# ========================
# ROTA: Listar Pendências
# ========================
@pendencias_blueprint.route("/list", methods=["GET"])
def pendencias_list():
    """
    Retorna a lista de pendências financeiras como JSON.

    A lista inclui:
    - ID
    - ID do cliente
    - Data
    - Descrição
    - Valor
    - Total pago
    - Status (Pago ou Pendente)
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.id, p.cliente_id, p.data, p.descricao, p.valor,
                   COALESCE(SUM(pg.valor_pago), 0) AS total_pago
            FROM pendencias p
            LEFT JOIN pagamentos pg ON p.id = pg.pendencia_id
            GROUP BY p.id
        """
        cursor.execute(query)
        pendencias = cursor.fetchall()

        # Calcula o status baseado no total pago
        for pendencia in pendencias:
            pendencia["status"] = (
                "Pago" if pendencia["total_pago"] >= pendencia["valor"] else "Pendente"
            )

        return jsonify({"pendencias": pendencias})
    finally:
        cursor.close()
        close_db_connection(conn)


# ========================
# ROTA: Adicionar Pendência
# ========================
@pendencias_blueprint.route("/add", methods=["POST"])
def pendencias_add():
    """
    Adiciona uma nova pendência no banco de dados.

    Dados esperados no JSON:
    - cliente_id: ID do cliente
    - data: Data da pendência (formato YYYY-MM-DD)
    - descricao: Descrição do item ou serviço
    - valor: Valor da pendência

    Retorna:
    - Sucesso (201) ou erro (500).
    """
    data = request.json
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pendencias (cliente_id, data, descricao, valor) VALUES (%s, %s, %s, %s)",
            (data["cliente_id"], data["data"], data["descricao"], data["valor"]),
        )
        conn.commit()
        return (
            jsonify({"success": True, "message": "Pendência adicionada com sucesso!"}),
            201,
        )
    finally:
        cursor.close()
        close_db_connection(conn)


# ========================
# ROTA: Buscar Pendência Específica
# ========================
@pendencias_blueprint.route("/get/<int:id>", methods=["GET"])
def pendencias_get(id):
    """
    Retorna os dados de uma pendência específica pelo ID.

    Parâmetro:
    - id: ID da pendência (int).

    Retorna:
    - JSON com os dados da pendência ou erro (404/500).
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.id, p.cliente_id, p.data, p.descricao, p.valor,
                   COALESCE(SUM(pg.valor_pago), 0) AS total_pago
            FROM pendencias p
            LEFT JOIN pagamentos pg ON p.id = pg.pendencia_id
            WHERE p.id = %s
            GROUP BY p.id
        """
        cursor.execute(query, (id,))
        pendencia = cursor.fetchone()

        if pendencia:
            pendencia["status"] = (
                "Pago" if pendencia["total_pago"] >= pendencia["valor"] else "Pendente"
            )
            return jsonify({"pendencia": pendencia}), 200
        else:
            return jsonify({"error": "Pendência não encontrada"}), 404
    except Exception as err:
        return jsonify({"error": f"Erro ao buscar pendência: {err}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)


# ========================
# ROTA: Editar Pendência
# ========================
@pendencias_blueprint.route("/edit/<int:id>", methods=["PUT"])
def pendencias_edit(id):
    """
    Atualiza as informações de uma pendência existente pelo ID.

    Dados esperados no JSON:
    - data: Data da pendência
    - descricao: Descrição da pendência
    - valor: Valor da pendência

    Retorna:
    - Sucesso (200) ou erro (500).
    """
    data = request.json
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE pendencias
            SET data = %s, descricao = %s, valor = %s
            WHERE id = %s
            """,
            (data["data"], data["descricao"], data["valor"], id),
        )
        conn.commit()
        return (
            jsonify({"success": True, "message": "Pendência atualizada com sucesso!"}),
            200,
        )
    except Exception as err:
        return (
            jsonify({"success": False, "message": f"Erro ao atualizar pendência: {err}"}),
            500,
        )
    finally:
        cursor.close()
        close_db_connection(conn)


# ========================
# ROTA: Excluir Pendência
# ========================
@pendencias_blueprint.route("/delete/<int:id>", methods=["DELETE"])
def pendencias_delete(id):
    """
    Remove uma pendência do banco de dados pelo ID.

    Parâmetro:
    - id: ID da pendência (int).

    Retorna:
    - Sucesso (204 - Sem Conteúdo) ou erro (500).
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pendencias WHERE id = %s", (id,))
        conn.commit()
        return "", 204
    except Exception as err:
        return jsonify({"error": f"Erro ao excluir pendência: {err}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)

