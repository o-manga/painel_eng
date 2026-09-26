from flask import Blueprint, abort, render_template, request
from modules.obras.routes import get_obra


def create_future_blueprint(name, title, import_name):
    bp = Blueprint(name, import_name, url_prefix=f"/{name}", template_folder="templates")

    @bp.get("/")
    def index():
        obra = None
        if "obra_id" in request.args:
            obra_id = request.args.get("obra_id", type=int)
            if obra_id is None:
                abort(400, description="Identificador de obra inválido.")
            obra = get_obra(obra_id)
        return render_template(f"{name}/index.html", title=title, obra=obra)

    return bp
