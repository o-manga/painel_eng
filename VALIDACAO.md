# Validação da v0.1.0

## Ambiente

- Windows, Python 3.12, Flask 3.1.2 e Waitress 3.0.2.
- Banco SQLite em arquivo persistente.
- Navegador Microsoft Edge em sessão isolada para testes.

## Testes automatizados

Comando: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.

Nove testes aprovados:

1. Ciclo de cadastro, edição, arquivamento, reativação e exclusão.
2. Proteção CSRF e recusa de métodos inseguros para alterações.
3. Indicadores e filtros por status.
4. Código duplicado, inclusive na edição, sem alteração indevida de dados.
5. Escape de HTML e pesquisa resistente a injeção SQL.
6. Navegação dos sete módulos futuros com validação do vínculo à obra.
7. Links, arquivos estáticos, cabeçalhos de segurança e página inexistente.
8. Persistência após criar uma nova instância da aplicação.
9. Campos obrigatórios, limites, UF, status e datas inválidas.

## Servidor e interface

O servidor foi efetivamente iniciado em `127.0.0.1:5000`. Foram exercitados pelo navegador:

- Cadastro com todos os campos, edição e conclusão.
- Arquivamento e reativação com atualização do status exibido.
- Os sete atalhos internos com o identificador da obra.
- Pesquisa e navegação pelo menu móvel.
- Renderização em 1440 × 1000 e 390 × 844 pixels.
- Ausência de erros JavaScript durante o fluxo.
- Reinicialização real do processo e confirmação dos dados persistidos.
- Tentativa de exclusão com confirmação errada (recusada) e confirmação correta (aprovada).
- Retorno 404 após exclusão e banco final sem registros de teste.

Um problema de rolagem horizontal da página no celular foi identificado e corrigido. A tabela mantém sua própria área de rolagem para preservar a legibilidade das colunas.

## Limites da entrega

Não há autenticação, anexos, regras financeiras ou módulos futuros completos nesta versão. A validação cobre o uso local inicial; não constitui teste de carga ou homologação para exposição em rede. Não há erros críticos conhecidos nos fluxos testados.
