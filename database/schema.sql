CREATE TABLE IF NOT EXISTS obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK(length(trim(nome)) BETWEEN 1 AND 160),
    codigo TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK(length(trim(codigo)) BETWEEN 1 AND 40),
    endereco TEXT NOT NULL DEFAULT '',
    cidade TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL DEFAULT '',
    cliente TEXT NOT NULL DEFAULT '',
    responsavel TEXT NOT NULL DEFAULT '',
    data_inicio TEXT NOT NULL DEFAULT '',
    previsao_termino TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'ativa' CHECK(status IN ('ativa','concluida','arquivada')),
    observacoes TEXT NOT NULL DEFAULT '',
    criado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    atualizado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_obras_status ON obras(status);
