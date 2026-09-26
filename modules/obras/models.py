from dataclasses import dataclass


@dataclass(frozen=True)
class Obra:
    id: int
    nome: str
    codigo: str
    endereco: str
    cidade: str
    estado: str
    cliente: str
    responsavel: str
    data_inicio: str
    previsao_termino: str
    status: str
    observacoes: str
    criado_em: str
    atualizado_em: str
