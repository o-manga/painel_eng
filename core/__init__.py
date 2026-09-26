from importlib import import_module
import sqlite3
from flask import Flask, render_template
from config import ROOT, VERSION, settings
from core.navigation import MODULES, STATUS
from core.security import csrf_token, protect_csrf
from database import init_app


def create_app(test_config=None):
    app = Flask(__name__, template_folder=str(ROOT / "templates"), static_folder=str(ROOT / "static"))
    app.config.update(settings())
    if test_config:
        app.config.update(test_config)
    init_app(app)
    app.before_request(protect_csrf)
    app.jinja_env.globals.update(csrf_token=csrf_token, modules=MODULES, statuses=STATUS, version=VERSION)
    app.jinja_env.filters["date_br"] = lambda value: "/".join(value.split("-")[::-1]) if value else "Não informada"
    for name in ["dashboard", "obras"] + [name for name, _ in MODULES]:
        app.register_blueprint(import_module(f"modules.{name}.routes").bp)

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        return response

    for code in [400, 404, 405, 413, 500]:
        app.register_error_handler(code, lambda error: (render_template("error.html", code=error.code, message=error.description), error.code))

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        app.logger.error("Falha operacional no banco: %s", type(error).__name__)
        return render_template("error.html", code=503, message="Banco indisponível ou ocupado. Tente novamente. Se persistir, confira as permissões da pasta instance."), 503

    return app
