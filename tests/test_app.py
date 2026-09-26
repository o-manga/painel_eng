import re
import tempfile
import unittest
from pathlib import Path
from core import create_app
from core.navigation import MODULES
from database import get_db
from modules.obras.repository import counts, find


class SystemTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(Path(self.folder.name) / "test.sqlite3")}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.client.get("/obras/nova")
        with self.client.session_transaction() as session:
            self.token = session["csrf_token"]

    def tearDown(self):
        self.folder.cleanup()

    def payload(self, **changes):
        data = dict(nome="Edifício Horizonte", codigo="ENG-001", endereco="Rua das Acácias, 100", cidade="São Paulo", estado="SP", cliente="Cliente de teste", responsavel="Engenheira de teste", data_inicio="2026-01-10", previsao_termino="2026-12-20", status="ativa", observacoes="Primeira linha\nSegunda linha", csrf_token=self.token)
        data.update(changes)
        return data

    def create(self, **changes):
        response = self.client.post("/obras/nova", data=self.payload(**changes))
        self.assertEqual(response.status_code, 302)
        return response.headers["Location"]

    def test_complete_lifecycle(self):
        location = self.create()
        self.assertIn("Horizonte", self.client.get(location).text)
        response = self.client.post(location + "/editar", data=self.payload(nome="Horizonte atualizado"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("Horizonte atualizado", self.client.get("/obras/?q=atualizado").text)
        self.client.post(location + "/arquivar", data={"csrf_token": self.token})
        with self.app.app_context():
            self.assertEqual(find(1).status, "arquivada")
        self.client.post(location + "/reativar", data={"csrf_token": self.token})
        with self.app.app_context():
            self.assertEqual(find(1).status, "ativa")
        self.assertEqual(self.client.get(location + "/excluir").status_code, 200)
        self.assertEqual(self.client.post(location + "/excluir", data={"csrf_token": self.token, "confirmacao": "errado"}).status_code, 422)
        self.assertEqual(self.client.get(location).status_code, 200)
        self.assertEqual(self.client.post(location + "/excluir", data={"csrf_token": self.token, "confirmacao": "ENG-001"}).status_code, 302)
        self.assertEqual(self.client.get(location).status_code, 404)

    def test_dashboard_counts_and_filters(self):
        for i, status in enumerate(["ativa", "concluida", "arquivada"]):
            self.create(codigo=f"ENG-{i}", status=status)
        with self.app.app_context():
            self.assertEqual(counts(), {"total": 3, "ativa": 1, "concluida": 1, "arquivada": 1})
        self.assertEqual(self.client.get("/").status_code, 200)
        for status in ["ativa", "concluida", "arquivada"]:
            self.assertIn("1 obra(s)", self.client.get(f"/obras/?status={status}").text)
        self.assertEqual(self.client.get("/obras/?status=invalid").status_code, 400)

    def test_validation(self):
        cases = [{"nome": " "}, {"codigo": ""}, {"nome": "x" * 161}, {"estado": "XX"}, {"status": "invalid"}, {"data_inicio": "2026-02-30"}, {"data_inicio": "20260110"}, {"previsao_termino": "2025-01-01"}, {"observacoes": "x" * 5001}]
        for case in cases:
            with self.subTest(case=list(case)):
                self.assertEqual(self.client.post("/obras/nova", data=self.payload(**case)).status_code, 422)
        with self.app.app_context():
            self.assertEqual(counts()["total"], 0)

    def test_duplicate_code_and_own_edit(self):
        location = self.create()
        self.assertEqual(self.client.post("/obras/nova", data=self.payload(codigo="eng-001")).status_code, 422)
        self.assertEqual(self.client.post(location + "/editar", data=self.payload()).status_code, 302)
        self.create(codigo="ENG-002")
        self.assertEqual(self.client.post("/obras/2/editar", data=self.payload()).status_code, 422)
        with self.app.app_context():
            self.assertEqual(find(2).codigo, "ENG-002")

    def test_persistence_after_new_application(self):
        self.create()
        restarted = create_app(self.config)
        with restarted.app_context():
            self.assertEqual(find(1).cliente, "Cliente de teste")
            self.assertEqual(get_db().execute("PRAGMA user_version").fetchone()[0], 1)
        self.assertIn("Horizonte", restarted.test_client().get("/obras/1").text)

    def test_csrf_and_safe_methods(self):
        self.assertEqual(self.client.post("/obras/nova", data={"nome": "Teste"}).status_code, 400)
        location = self.create()
        for action in ["arquivar", "reativar", "excluir", "editar"]:
            self.assertEqual(self.client.post(location + "/" + action, data={}).status_code, 400)
        self.assertEqual(self.client.get(location + "/arquivar").status_code, 405)
        self.assertEqual(self.client.get(location + "/reativar").status_code, 405)
        with self.app.app_context():
            self.assertEqual(find(1).status, "ativa")

    def test_future_navigation_context(self):
        self.create()
        for name, _ in MODULES:
            with self.subTest(module=name):
                self.assertEqual(self.client.get(f"/{name}/").status_code, 200)
                scoped = self.client.get(f"/{name}/?obra_id=1")
                self.assertEqual(scoped.status_code, 200)
                self.assertIn("ENG-001", scoped.text)
                self.assertIn('/obras/1', scoped.text)
                self.assertEqual(self.client.get(f"/{name}/?obra_id=999").status_code, 404)
                self.assertEqual(self.client.get(f"/{name}/?obra_id=abc").status_code, 400)

    def test_escape_and_search_injection(self):
        self.create(nome='<script>alert("x")</script>')
        html = self.client.get("/obras/1").text
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertIn("&lt;script&gt;", html)
        response = self.client.get("/obras/", query_string={"q": "' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("0 obra(s)", response.text)
        self.assertIn("0 obra(s)", self.client.get("/obras/?q=%25").text)

    def test_links_assets_and_security_headers(self):
        self.create()
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        for link in re.findall(r'href="([^"]+)"', response.text):
            if link.startswith("/"):
                with self.client.get(link) as linked_response:
                    self.assertEqual(linked_response.status_code, 200, link)
        with self.client.get("/static/js/app.js") as asset_response:
            self.assertEqual(asset_response.status_code, 200)
        self.assertEqual(self.client.get("/nao-existe").status_code, 404)


if __name__ == "__main__":
    unittest.main()
