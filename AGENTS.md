# AGENTS.md — meu-site-medico

Site Quarto publicado pelo GitHub Pages a partir de `main` → `/docs`.
Qualquer merge em `main` publica. Nada vai para `main` sem autorização explícita do Camilo.

## Caminhos
- Site (pasta de trabalho, este repositório): `/Users/forbs/Downloads/Website/meu-site-medico`
- Cópia de teste (só histórico; não usar para novos trabalhos): `/Users/forbs/Downloads/Website/meu-site-medico-teste`
- Backups (não apagar sem autorização): `meu-site-medico-backup-20261120` e `meu-site-medico-backup-20261120-pre-publicacao`, ao lado da pasta do site
- `git stash list`: `stash@{0}` guarda as versões locais anteriores à sincronização de 20/11/2026. Não descartar.
- Fonte dos erros: `/Users/forbs/Downloads/estrategia-med/state/materials/<id>.json` (somente leitura)
- Quarto: `/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto` (não está no PATH)

## Estrutura (uma pasta por pilar)
- `index.qmd`, `about.qmd` na raiz. Menu em `_quarto.yml` (Residência é submenu).
- `residencia/`: `index.qmd`, `questoes/` (questões comentadas) e `lembrar/` (Lembrar para a prova).
- `internato/`: `index.qmd` e `casos/`. `fisiopatologia/`: `index.qmd`.
- Mover ou renomear página publicada: adicionar `aliases:` com o caminho antigo no cabeçalho
  (cria um redirecionamento). As URLs da estrutura antiga, de antes de 21/11/2026, já têm aliases.

## Seção "Lembrar para a prova" (`residencia/lembrar/`)
- Erros: `residencia/lembrar/<area>/<materia>/<id>.md`, gerados pelo importador. Não editar à mão.
- Especialidade → pasta: `residencia/lembrar/_mapa.json`. Especialidade nova = nova entrada no mapa
  + página da matéria (copiar `residencia/lembrar/clinica-medica/hematologia.qmd`) + card em `residencia/lembrar/index.qmd`.
- `ids_dir_antigo` no mapa: os 7 erros publicados antes da mudança de pasta (recebem aliases). Não acrescentar IDs novos.
- Estilos da seção: `residencia/lembrar/lembrar.css` (cores em `styles.css` e `_brand.yml`).

## Casos clínicos e questões comentadas (listagens automáticas)
- Caso novo: criar `internato/casos/<nome>.qmd` com `numero`, `chamada` e `resumo` no cabeçalho. Aparece sozinho em `internato/index.qmd`.
- Questão nova: criar `residencia/questoes/<especialidade>/questao-NNN.qmd` com `numero`, `chamada`, `tema` (opcional) e `resumo`.
  Aparece sozinha na página da especialidade (ex.: `residencia/questoes/hepatologia.qmd`). Não editar as páginas-índice à mão.
- Modelos das listagens: `_listagens/casos.ejs` e `_listagens/questoes.ejs`. Ordem pelo campo `numero`.
- Especialidade nova: página como `residencia/questoes/hepatologia.qmd` (mudando `contents`) + entrada em `residencia/questoes/index.qmd`.

## Comandos
```bash
python3 scripts/importar_erros.py --simular          # relatório, não grava
python3 scripts/importar_erros.py                    # cria só os <id>.md novos
python3 scripts/importar_erros.py --atualizar <id>   # regrava um registro de propósito
/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto render   # gera docs/
```
Para testar sem tocar em `docs/` e `.quarto/`, copie o projeto para uma pasta temporária e use `render --output-dir <tmp>`.

## Regras
- Conversão JSON → Markdown é feita só pelo importador. Não usar IA para isso nem ler os JSONs à mão.
- CONFLITO no relatório: investigar antes de usar `--atualizar`. Nunca apagar `<id>.md` para "resolver".
- Sempre `render` do projeto inteiro (o menu fica igual em todas as páginas). Não editar `docs/` à mão.
- O site não depende do R para renderizar; não adicionar blocos de código R sem necessidade.
- Commit, push, PR, merge e publicação só com autorização. Nunca usar force push.
- Antes de trabalhar: `git fetch` e conferir `git status -sb`. Se `main` estiver atrás, só avançar com `git merge --ff-only`.
