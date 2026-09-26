from dataclasses import asdict
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from core.navigation import STATUS
from . import repository, services

bp = Blueprint("obras", __name__, url_prefix="/obras", template_folder="templates")


def get_obra(obra_id):
    obra = repository.find(obra_id)
    if obra is None:
        abort(404, description="Obra não encontrada.")
    return obra


@bp.get("/")
def index():
    query = request.args.get("q", "").strip()[:200]
    status = request.args.get("status", "")
    if status and status not in STATUS:
        abort(400, description="Filtro de status inválido.")
    return render_template("obras/index.html", obras=repository.search(query, status), query=query, selected_status=status)


@bp.route("/nova", methods=["GET", "POST"])
def create():
    data, errors = {"status": "ativa"}, {}
    if request.method == "POST":
        obra_id, data, errors = services.save(request.form)
        if obra_id:
            flash("Obra cadastrada com sucesso.", "success")
            return redirect(url_for("obras.detail", obra_id=obra_id))
    return render_template("obras/form.html", data=data, errors=errors, obra=None, states=services.STATES), 422 if errors else 200


@bp.get("/<int:obra_id>")
def detail(obra_id):
    return render_template("obras/detail.html", obra=get_obra(obra_id))


@bp.route("/<int:obra_id>/editar", methods=["GET", "POST"])
def edit(obra_id):
    obra = get_obra(obra_id)
    data, errors = asdict(obra), {}
    if request.method == "POST":
        saved, data, errors = services.save(request.form, obra_id)
        if saved:
            flash("Dados da obra atualizados.", "success")
            return redirect(url_for("obras.detail", obra_id=obra_id))
    return render_template("obras/form.html", data=data, errors=errors, obra=obra, states=services.STATES), 422 if errors else 200


@bp.post("/<int:obra_id>/arquivar")
def archive(obra_id):
    get_obra(obra_id)
    repository.change_status(obra_id, "arquivada")
    flash("Obra arquivada. Seus dados foram preservados.", "success")
    return redirect(url_for("obras.detail", obra_id=obra_id))


@bp.post("/<int:obra_id>/reativar")
def reactivate(obra_id):
    get_obra(obra_id)
    repository.change_status(obra_id, "ativa")
    flash("Obra reativada.", "success")
    return redirect(url_for("obras.detail", obra_id=obra_id))


@bp.route("/<int:obra_id>/excluir", methods=["GET", "POST"])
def delete(obra_id):
    obra = get_obra(obra_id)
    if request.method == "POST":
        if request.form.get("confirmacao", "").strip() != obra.codigo:
            flash("Digite o código exatamente como exibido para confirmar a exclusão.", "error")
            return render_template("obras/delete.html", obra=obra), 422
        repository.delete(obra_id)
        flash("Obra excluída.", "success")
        return redirect(url_for("obras.index"))
    return render_template("obras/delete.html", obra=obra)
