import hmac
import secrets
from flask import abort, request, session


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def protect_csrf():
    if request.method == "POST":
        expected = session.get("csrf_token", "")
        actual = request.form.get("csrf_token", "")
        if not expected or not hmac.compare_digest(expected, actual):
            abort(400, description="Formulário expirado ou inválido. Recarregue a página e tente novamente.")
