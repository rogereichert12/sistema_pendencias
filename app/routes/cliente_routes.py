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

# Blueprint para as rotas de clientes
cliente_blueprint = Blueprint("clientes", __name__, url_prefix="/clientes")

# ========================
# ROTA: Renderizar Página de Clientes
# ========================
@cliente_blueprint.route("/", methods=["GET"])
def clientes_page():
    """
    Renderiza a página HTML de clientes.

    Requisitos:
    - O usuário deve estar autenticado (checar a sessão 'user').

    Redireciona para a página de login caso a sessão esteja vazia.
    """
    if "user" in session:
        return render_template("clientes.html")
    return redirect(url_for("auth.login"))

# ========================
# ROTA: Listar Clientes
# ========================
@cliente_blueprint.route("/list", methods=["GET"])
def clientes_list():
    """
    Retorna a lista de clientes como JSON.

    A lista inclui:
    - ID
    - Nome do aluno
    - Nome do responsável
    - Telefone
    - CPF
    - Status (Ativo/Inativo)

    Método:
    - SELECT na tabela 'clientes'.
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, aluno, responsavel, telefone, cpf, status FROM clientes"
        )
        clients = cursor.fetchall()
        return jsonify({"clients": clients})
    finally:
        cursor.close()
        close_db_connection(conn)

# ========================
# ROTA: Adicionar Cliente
# ========================
@cliente_blueprint.route("/add", methods=["POST"])
def clientes_add():
    """
    Adiciona um novo cliente no banco de dados.

    Dados esperados no JSON:
    - aluno: Nome do aluno
    - responsavel: Nome do responsável
    - telefone: Número de telefone
    - cpf: CPF do cliente

    Padrão:
    - O status inicial do cliente será "Ativo".

    Retorna:
    - Sucesso (201) ou erro (500).
    """
    data = request.json
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clientes (aluno, responsavel, telefone, cpf, status) VALUES (%s, %s, %s, %s, %s)",
            (
                data["aluno"],
                data["responsavel"],
                data["telefone"],
                data["cpf"],
                "Ativo",
            ),
        )
        conn.commit()
        return (
            jsonify({"success": True, "message": "Cliente adicionado com sucesso!"}),
            201,
        )
    finally:
        cursor.close()
        close_db_connection(conn)

# ========================
# ROTA: Buscar Cliente Específico
# ========================
@cliente_blueprint.route("/get/<int:id>", methods=["GET"])
def clientes_get(id):
    """
    Retorna os dados de um cliente específico pelo ID.

    Parâmetro:
    - id: ID do cliente (int).

    Retorna:
    - JSON com os dados do cliente ou erro (404/500).
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        client = cursor.fetchone()
        if client:
            return jsonify({"client": client}), 200
        else:
            return jsonify({"error": "Cliente não encontrado"}), 404
    except Exception as err:
        return jsonify({"error": f"Erro ao buscar cliente: {err}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)

# ========================
# ROTA: Editar Cliente
# ========================
@cliente_blueprint.route("/edit/<int:id>", methods=["PUT"])
def clientes_edit(id):
    """
    Atualiza as informações de um cliente existente pelo ID.

    Dados esperados no JSON:
    - aluno: Nome do aluno
    - responsavel: Nome do responsável
    - telefone: Número de telefone
    - cpf: CPF do cliente
    - status (opcional): Status do cliente (Ativo/Inativo)

    Retorna:
    - Sucesso (200) ou erro (500).
    """
    data = request.json
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        query = """
            UPDATE clientes
            SET aluno = %s, responsavel = %s, telefone = %s, cpf = %s, status = %s
            WHERE id = %s
        """
        cursor.execute(
            query,
            (
                data.get("aluno"),
                data.get("responsavel"),
                data.get("telefone"),
                data.get("cpf"),
                data.get(
                    "status", "Ativo"
                ),  # Caso não tenha status, define como "Ativo"
                id,
            ),
        )
        conn.commit()
        return (
            jsonify({"success": True, "message": "Cliente atualizado com sucesso!"}),
            200,
        )
    except Exception as err:
        return (
            jsonify({"success": False, "message": f"Erro ao atualizar cliente: {err}"}),
            500,
        )
    finally:
        cursor.close()
        close_db_connection(conn)

# ========================
# ROTA: Excluir Cliente
# ========================
@cliente_blueprint.route("/delete/<int:id>", methods=["DELETE"])
def clientes_delete(id):
    """
    Remove um cliente do banco de dados pelo ID.

    Parâmetro:
    - id: ID do cliente (int).

    Retorna:
    - Sucesso (204 - Sem Conteúdo) ou erro (500).
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
        conn.commit()
        return "", 204  # Retorna status HTTP 204 (Sem Conteúdo)
    except Exception as err:
        return jsonify({"error": f"Erro ao excluir cliente: {err}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)
