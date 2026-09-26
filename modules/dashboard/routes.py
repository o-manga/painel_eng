from flask import Blueprint, render_template
from modules.obras.repository import counts, search

bp = Blueprint("dashboard", __name__, template_folder="templates")


@bp.get("/")
def index():
    return render_template("dashboard/index.html", counts=counts(), obras=search()[:5])
