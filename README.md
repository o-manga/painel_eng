# Sistema de Gerenciamento de Obras — v0.1.0

Aplicação local em Python, Flask e SQLite. Dashboard e cadastro de obras funcionais; os demais módulos estão preparados para evolução incremental.

## Instalação no Windows

1. Instale Python **3.11 ou superior** pelo [site oficial](https://www.python.org/downloads/windows/). No instalador, habilite a opção de adicionar Python ao PATH. Abra um novo PowerShell após a instalação.
2. Abra a pasta `sistema_engenharia` no terminal. Todos os comandos seguintes devem ser executados nela.
3. Crie um ambiente virtual isolado:

```powershell
py -m venv .venv
```

4. Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, **não é necessário alterar a política do Windows**. Use diretamente o executável do ambiente, como nos comandos abaixo.

5. Instale as dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Flask fornece a aplicação e os templates; python-dotenv carrega configurações locais opcionais; Waitress executa o servidor HTTP no Windows. HTML, CSS e JavaScript são locais: a interface não depende de CDN nem de acesso à internet.

6. Inicie:

```powershell
.\.venv\Scripts\python.exe app.py
```

7. Abra **http://127.0.0.1:5000** no navegador.
8. Para parar, pressione **Ctrl+C** no terminal. Para iniciar novamente, repita o comando do passo 6. Os dados permanecem salvos.

O servidor escuta apenas no próprio computador. Não há login nesta versão. Antes de disponibilizar em rede ou nuvem, será necessário implementar autenticação, autorização, HTTPS, backups e configurar a implantação. Não altere o endereço de escuta para expor esta versão diretamente.

## Configuração opcional

Copie `.env.example` para `.env` somente se desejar personalizar. O exemplo contém apenas nomes de variáveis, sem segredos. Valores vazios utilizam os padrões seguros:

- `SECRET_KEY`: segredo aleatório local usado nas sessões. Se não definido, é gerado em memória a cada início; formulários abertos antes da reinicialização precisam ser recarregados. Para manter sessões entre reinicializações, configure um valor aleatório privado no `.env`.
- `DATABASE_PATH`: caminho do SQLite. Padrão: `instance/engenharia.sqlite3`. Caminhos relativos partem da raiz do projeto.
- `PORT`: porta local. Padrão: `5000`. Use outra se já estiver ocupada.

Nunca publique `.env`, banco de dados, backups ou credenciais. `.gitignore` exclui esses arquivos e o ambiente virtual.

## Uso

1. Clique em **Nova obra** e preencha nome e código, obrigatórios.
2. Os demais campos podem ser preenchidos depois. Código é único, sem diferenciar maiúsculas e minúsculas.
3. Informe datas válidas; previsão de término não pode anteceder o início.
4. Consulte e edite pela central da obra. A conclusão é registrada escolhendo **Concluída** na edição.
5. Pesquise por nome, código, cliente ou cidade e combine com o filtro de status. SQLite oferece busca parcial; equivalência de acentos não é normalizada nesta versão.
6. **Arquivar** preserva os dados. **Reativar** define o status como Ativa, inclusive para uma obra concluída.
7. **Excluir** abre uma confirmação e exige digitar o código. Exclusão é permanente; prefira arquivar quando precisar manter histórico.
8. Os atalhos da central levam aos módulos com `obra_id`, preservando o vínculo. Nenhuma regra financeira ou de medições foi implementada nesta etapa.

## Banco e backups

O banco é criado no primeiro início, sem dados fictícios. O caminho independe da pasta de onde o programa é iniciado. Reabrir a aplicação não apaga ou recria registros.

Antes de atualizar ou migrar, pare o programa e copie a pasta `instance` para um local privado de backup. Para restaurar, pare o programa e preserve uma cópia do banco atual antes de substituir pelo backup compatível. Git versiona o **código**, não os seus cadastros.

O esquema inicial usa `PRAGMA user_version = 1`. Próximas alterações devem adicionar migrações incrementais transacionais, sem remover os dados existentes. Uma versão antiga do aplicativo recusa um banco com versão de esquema mais recente.

## Estrutura

```text
app.py                  Entrada do servidor local
config/                 Configurações e caminhos
core/                   Fábrica da aplicação, segurança e navegação
database/               Conexão SQLite e esquema versionado
modules/dashboard/      Rotas e template dos indicadores
modules/obras/           Modelo, repositório, serviços, rotas e templates
modules/medicoes/       Estrutura reservada ao próximo módulo
modules/compras/         Estrutura reservada
modules/planejamento/    Estrutura reservada
modules/custos/          Estrutura reservada
modules/empreiteiros/    Estrutura reservada
modules/documentos/      Estrutura reservada
modules/relatorios/      Estrutura reservada
templates/              Layout, macros e páginas compartilhadas
static/css/             Estilos responsivos
static/js/              Comportamento do menu móvel
tests/                  Testes isolados com banco temporário
instance/               Dados privados gerados localmente (fora do Git)
```

Cada módulo tem Blueprint próprio e templates com namespace. SQL fica no repositório; validações nos serviços; rotas coordenam os fluxos. A função `create_app()` aceita configurações de teste. A futura migração para outro banco exige adaptar a camada de persistência e as migrações, preservando a interface dos serviços.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam arquivos temporários e **não alteram o banco de uso real**. Cobrem cadastro, edição, filtros, status, exclusão confirmada, duplicidade, validação de datas, persistência após recriação da aplicação, CSRF, escape HTML, pesquisa parametrizada, links e módulos vinculados. Consulte `VALIDACAO.md` para a conferência adicional no navegador e o teste de reinício real.

Conferência manual: cadastre uma obra de teste, edite os dados, conclua, arquive, reative e confira os indicadores. Pare e reinicie o programa; confirme que ela continua listada. Abra todos os atalhos internos. Teste a janela estreita e o menu móvel. Por último, exclua apenas o cadastro de teste digitando o código na confirmação.

## Atualização e versionamento

Para reinstalar as versões aprovadas das dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

As dependências estão fixadas. Para adotar versões mais novas, atualize `requirements.txt` em uma branch específica, teste e registre uma nova versão. Não atualize bibliotecas às cegas no ambiente em uso.

A branch `main` deve conter entregas testadas. A tag `v0.1.0` identifica esta entrega. Evoluções devem partir da versão estável, usar commits claros, executar regressão e adicionar tags sem substituir as anteriores. Consulte `CHANGELOG.md`. Repositório definido: https://github.com/o-manga/painel_eng.

Próxima etapa sugerida: **v0.2.0 — Medições**, somente após definir suas regras e campos. Compras, Planejamento, Custos, Empreiteiros, Documentos e Relatórios permanecem para etapas posteriores.

## Problemas comuns

- **Python não encontrado:** instale o Python e reabra o terminal; use `py` para criar o ambiente.
- **Módulo não encontrado:** instale os requisitos com o Python da `.venv`.
- **Porta ocupada:** configure `PORT` em `.env` e acesse a nova porta.
- **Formulário expirado:** recarregue a página e preencha novamente.
- **Banco indisponível:** confirme permissão de escrita em `instance`, espaço livre e ausência de outra ferramenta mantendo uma transação aberta.
- **Código duplicado:** cada obra deve ter um código diferente, inclusive obras arquivadas.
- **Grandes volumes:** esta versão lista resultados sem paginação e foi projetada para o uso local inicial; paginação pode ser acrescentada ao repositório e às telas conforme o volume crescer.
