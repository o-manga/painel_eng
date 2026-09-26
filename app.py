"""Entrada local: python app.py."""
from waitress import serve
from core import create_app
from config import VERSION

app = create_app()

if __name__ == "__main__":
    print(f"Sistema de Engenharia v{VERSION} — http://127.0.0.1:{app.config['PORT']}", flush=True)
    serve(app, host="127.0.0.1", port=app.config["PORT"])
