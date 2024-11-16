from flask import Blueprint, render_template, session, redirect, url_for

dashboard_blueprint = Blueprint("dashboard", __name__)

@dashboard_blueprint.route("/dashboard", methods=["GET"])
def dashboard():
    """Exibe o dashboard principal."""
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("auth.login"))
