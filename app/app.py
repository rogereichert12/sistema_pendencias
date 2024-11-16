from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
import pandas as pd
import mysql.connector
from io import BytesIO
from fpdf import FPDF

# Configuração do aplicativo
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Configuração do banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "3364",
    "database": "controle_financeiro"
}

# ========================
# SEÇÃO: ROTAS DE AUTENTICAÇÃO
# ========================

@app.route("/")
def home():
    """
    Rota inicial que redireciona para o login se o usuário não estiver autenticado.
    Caso contrário, redireciona para o dashboard.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Rota de login para autenticação de usuários.
    Método GET: Renderiza a página de login.
    Método POST: Processa as credenciais enviadas e autentica o usuário.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()

            if user:
                session["user"] = user["nome"]
                return jsonify({"success": True, "message": f"Bem-vindo, {user['nome']}!"}), 200
            else:
                return jsonify({"success": False, "message": "E-mail ou senha incorretos."}), 401
        except mysql.connector.Error as err:
            return jsonify({"success": False, "message": f"Erro no banco de dados: {err}"}), 500
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Rota de logout. Remove a sessão do usuário e redireciona para o login.
    """
    session.pop("user", None)
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for("login"))

# ========================
# SEÇÃO: ROTAS DO DASHBOARD
# ========================

@app.route("/dashboard")
def dashboard():
    """
    Rota do dashboard principal. Exibe informações gerais e links para funcionalidades.
    """
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))

# ========================
# SEÇÃO: ROTAS DE CLIENTES
# ========================

@app.route("/clientes", methods=["GET"])
def clientes():
    """
    Rota principal da página de clientes.
    Renderiza a interface para gerenciar clientes.
    """
    if "user" in session:
        return render_template("clientes.html")
    return redirect(url_for("login"))

@app.route("/clientes/list", methods=["GET"])
def clientes_list():
    """
    Retorna a lista de clientes no formato JSON.
    Permite que o frontend consuma e exiba os dados.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf, status FROM clientes")
        clients = cursor.fetchall()
        return jsonify({"clients": clients})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/add", methods=["POST"])
def clientes_add():
    """
    Adiciona um novo cliente ao banco de dados.
    Espera um corpo JSON com as informações do cliente.
    """
    data = request.json
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (aluno, responsavel, telefone, cpf, status) VALUES (%s, %s, %s, %s, %s)",
            (data["aluno"], data["responsavel"], data["telefone"], data["cpf"], "Ativo"),
        )
        conn.commit()
        return jsonify({"success": True, "message": "Cliente adicionado com sucesso!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Erro ao adicionar cliente: {err}"}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/get/<int:id>", methods=["GET"])
def clientes_get(id):
    """
    Retorna os dados de um cliente específico pelo ID.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        client = cursor.fetchone()
        if client:
            return jsonify({"client": client}), 200
        else:
            return jsonify({"error": "Cliente não encontrado"}), 404
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/edit/<int:id>", methods=["PUT"])
def clientes_edit(id):
    """
    Edita as informações de um cliente existente pelo ID.
    Espera um corpo JSON com as informações atualizadas.
    """
    data = request.json
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            UPDATE clientes 
            SET aluno = %s, responsavel = %s, telefone = %s, cpf = %s, status = %s 
            WHERE id = %s
        """
        cursor.execute(query, (
            data["aluno"], data["responsavel"], data["telefone"], data["cpf"], data.get("status", "Ativo"), id
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Cliente atualizado com sucesso!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Erro ao atualizar cliente: {err}"}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/delete/<int:id>", methods=["DELETE"])
def clientes_delete(id):
    """
    Remove um cliente do banco de dados pelo ID.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
        conn.commit()
        return "", 204
    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro ao excluir cliente: {err}"}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/update_status/<int:id>", methods=["PUT"])
def update_status(id):
    """
    Atualiza o status de um cliente (Ativo ou Inativo).
    Espera um corpo JSON com o novo status.
    """
    data = request.json
    new_status = data.get("status", "Ativo")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET status = %s WHERE id = %s", (new_status, id))
        conn.commit()
        return jsonify({"success": True, "message": "Status atualizado com sucesso!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Erro ao atualizar status: {err}"}), 500
    finally:
        if conn.is_connected():
            conn.close()

# ========================
# SEÇÃO: EXPORTAÇÕES
# ========================

@app.route("/clientes/export/csv", methods=["GET"])
def export_csv():
    """
    Exporta a lista de clientes em formato CSV.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()

        df = pd.DataFrame(clients)
        csv_data = df.to_csv(index=False, encoding="utf-8")

        response = make_response(csv_data)
        response.headers["Content-Disposition"] = "attachment; filename=clientes.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/export/excel", methods=["GET"])
def export_excel():
    """
    Exporta a lista de clientes em formato Excel.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()

        df = pd.DataFrame(clients)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Clientes")
        output.seek(0)

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=clientes.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route("/clientes/export/pdf", methods=["GET"])
def export_pdf():
    """
    Exporta a lista de clientes em formato PDF.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, aluno, responsavel, telefone, cpf FROM clientes")
        clients = cursor.fetchall()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Relatório de Clientes", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=10)
        for client in clients:
            pdf.cell(0, 10, f"ID: {client['id']}, Aluno: {client['aluno']}, Responsável: {client['responsavel']}, Telefone: {client['telefone']}, CPF: {client['cpf']}", ln=True)

        response = make_response(pdf.output(dest="S").encode("latin1"))
        response.headers["Content-Disposition"] = "attachment; filename=clientes.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            conn.close()

# ========================
# EXECUÇÃO DO APLICATIVO
# ========================
if __name__ == "__main__":
    app.run(debug=True)
