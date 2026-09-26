"""SQL isolado: ponto de adaptação para outro banco no futuro."""
from database import get_db
from .models import Obra

FIELDS = ("nome", "codigo", "endereco", "cidade", "estado", "cliente", "responsavel", "data_inicio", "previsao_termino", "status", "observacoes")


def find(obra_id):
    row = get_db().execute("SELECT * FROM obras WHERE id = ?", (obra_id,)).fetchone()
    return Obra(**dict(row)) if row else None


def search(query="", status=""):
    clauses, params = [], []
    if query:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clauses.append("(nome LIKE ? ESCAPE '\\' OR codigo LIKE ? ESCAPE '\\' OR cliente LIKE ? ESCAPE '\\' OR cidade LIKE ? ESCAPE '\\')")
        params.extend([f"%{escaped}%"] * 4)
    if status:
        clauses.append("status = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    rows = get_db().execute("SELECT * FROM obras" + where + " ORDER BY id DESC", params).fetchall()
    return [Obra(**dict(row)) for row in rows]


def save(data, obra_id=None):
    db = get_db()
    with db:
        values = [data[field] for field in FIELDS]
        if obra_id is None:
            cursor = db.execute(f"INSERT INTO obras ({','.join(FIELDS)}) VALUES ({','.join('?' for _ in FIELDS)})", values)
            return cursor.lastrowid
        assignments = ",".join(f"{field} = ?" for field in FIELDS)
        db.execute(f"UPDATE obras SET {assignments}, atualizado_em = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id = ?", values + [obra_id])
    return obra_id


def change_status(obra_id, status):
    db = get_db()
    with db:
        db.execute("UPDATE obras SET status = ?, atualizado_em = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id = ?", (status, obra_id))


def delete(obra_id):
    db = get_db()
    with db:
        db.execute("DELETE FROM obras WHERE id = ?", (obra_id,))


def counts():
    result = {"ativa": 0, "concluida": 0, "arquivada": 0}
    result.update({row["status"]: row["total"] for row in get_db().execute("SELECT status, count(*) AS total FROM obras GROUP BY status")})
    result["total"] = sum(result.values())
    return result
