from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from app.config import Config
from app.helpers import get_db_connection, close_db_connection

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/", methods=["GET"])
def home():
    """Redireciona para o dashboard ou login."""
    if "user" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Rota de autenticação."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection(Config.DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            if user:
                session["user"] = user["nome"]
                return jsonify({"success": True, "message": f"Bem-vindo, {user['nome']}!"}), 200
            else:
                return jsonify({"success": False, "message": "E-mail ou senha incorretos."}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro: {e}"}), 500
        finally:
            cursor.close()
            close_db_connection(conn)

    return render_template("login.html")

@auth_blueprint.route("/logout")
def logout():
    """Rota de logout."""
    session.pop("user", None)
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for("auth.login"))
