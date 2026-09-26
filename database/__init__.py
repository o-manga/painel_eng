"""Conexões por requisição e migrações incrementais sem apagar dados."""
import sqlite3
from pathlib import Path
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db = get_db()
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > 1:
            raise RuntimeError("Banco de versão mais recente. Utilize a versão compatível do sistema.")
        if version == 0:
            schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
            db.executescript("BEGIN IMMEDIATE;\n" + schema + "\nPRAGMA user_version = 1;\nCOMMIT;")
