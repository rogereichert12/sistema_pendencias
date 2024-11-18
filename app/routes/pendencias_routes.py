from flask import Blueprint, jsonify, request, render_template
from app.helpers import get_db_connection, close_db_connection
from app.config import Config
from datetime import datetime

pendencias_blueprint = Blueprint("pendencias", __name__, url_prefix="/pendencias")


@pendencias_blueprint.route("/", methods=["GET"])
def pendencias_page():
    """Renderiza a página de pendências"""
    return render_template(
        "pendencias.html"
    )  # Certifique-se de que pendencias.html existe na pasta templates


@pendencias_blueprint.route("/relatorio/<int:cliente_id>", methods=["GET"])
def gerar_relatorio(cliente_id):
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        # Obter as pendências do cliente com status 'Pendente'
        cursor.execute(
            """
            SELECT 
                p.id AS pendencia_id, 
                p.data, 
                pp.produto_id, 
                pp.quantidade, 
                prod.descricao, 
                prod.preco AS preco_unitario, -- Renomeado para deixar claro
                (pp.quantidade * prod.preco) AS subtotal
            FROM pendencias AS p
            INNER JOIN pendencias_produtos AS pp ON p.id = pp.pendencia_id
            INNER JOIN produtos AS prod ON pp.produto_id = prod.id
            WHERE p.cliente_id = %s AND p.status = 'Pendente'
            """,
            (cliente_id,),
        )
        pendencias = cursor.fetchall()

        if not pendencias:
            return (
                jsonify({"error": "Nenhuma pendência encontrada para o cliente."}),
                404,
            )

        # Retornar os dados em JSON para o frontend processar ou gerar PDF
        return jsonify({"success": True, "pendencias": pendencias})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_db_connection(conn)



@pendencias_blueprint.route("/clientes/pendentes", methods=["GET"])
def listar_clientes_com_pendencias():
    """
    Rota para listar os clientes que possuem pendências
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        # Consulta para buscar clientes que possuem pendências
        cursor.execute(
            """
            SELECT DISTINCT c.id, c.aluno AS nome
            FROM clientes c
            INNER JOIN pendencias p ON c.id = p.cliente_id
            WHERE p.valor > 0
        """
        )
        clientes = cursor.fetchall()

        # Se não houver clientes com pendências, retornar uma mensagem
        if not clientes:
            return (
                jsonify(
                    {
                        "clients": [],
                        "message": "Nenhum cliente com pendências encontrado.",
                    }
                ),
                200,
            )

        return jsonify({"clients": clientes}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar clientes com pendências: {e}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)


@pendencias_blueprint.route("/list", methods=["GET"])
def listar_pendencias():
    """
    Rota para listar pendências
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.id, p.cliente_id, p.data, p.valor, c.aluno AS cliente
            FROM pendencias p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.status = 'Pendente'
            """
        )
        pendencias = cursor.fetchall()
        return jsonify({"pendencias": pendencias}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar pendências: {e}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)


@pendencias_blueprint.route("/pagar/<int:pendencia_id>", methods=["POST"])
def pagar_pendencia(pendencia_id):
    """
    Rota para marcar uma pendência como paga
    """
    conn = get_db_connection(Config.DB_CONFIG)
    cursor = conn.cursor()
    try:
        # Atualizar o status da pendência
        cursor.execute(
            """
            UPDATE pendencias
            SET status = 'pago'
            WHERE id = %s
            """,
            (pendencia_id,),
        )
        conn.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Erro ao marcar pendência como paga: {e}")
        return jsonify({"error": f"Erro ao marcar pendência como paga: {e}"}), 500
    finally:
        cursor.close()
        close_db_connection(conn)
