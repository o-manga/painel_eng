from datetime import date
import re
import sqlite3
from core.navigation import STATUS
from . import repository

STATES = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
LIMITS = {"nome": 160, "codigo": 40, "endereco": 250, "cidade": 120, "estado": 2, "cliente": 160, "responsavel": 160, "observacoes": 5000}


def validate(form):
    data = {field: form.get(field, "").strip() for field in repository.FIELDS}
    data["codigo"] = data["codigo"].upper()
    data["estado"] = data["estado"].upper()
    errors = {}
    for field in ["nome", "codigo"]:
        if not data[field]:
            errors[field] = "Campo obrigatório."
    for field, limit in LIMITS.items():
        if len(data[field]) > limit:
            errors[field] = f"Use no máximo {limit} caracteres."
    if data["estado"] and data["estado"] not in STATES:
        errors["estado"] = "Selecione uma UF válida."
    if data["status"] not in STATUS:
        errors["status"] = "Selecione um status válido."
    for field in ["data_inicio", "previsao_termino"]:
        if data[field]:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data[field]):
                    raise ValueError
                date.fromisoformat(data[field])
            except ValueError:
                errors[field] = "Informe uma data válida."
    if not errors and data["data_inicio"] and data["previsao_termino"] and data["previsao_termino"] < data["data_inicio"]:
        errors["previsao_termino"] = "O término não pode ser anterior ao início."
    return data, errors


def save(form, obra_id=None):
    data, errors = validate(form)
    if errors:
        return None, data, errors
    try:
        return repository.save(data, obra_id), data, {}
    except sqlite3.IntegrityError:
        return None, data, {"codigo": "Este código já está cadastrado. Use outro código."}
