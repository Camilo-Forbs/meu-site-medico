# AGENTS.md — meu-site-medico

Site Quarto publicado pelo GitHub Pages a partir de `main` → `/docs`.
Qualquer merge em `main` publica. Nada vai para `main` sem autorização explícita do Camilo.

## Caminhos
- Site (este repositório): `/Users/forbs/Downloads/Website/meu-site-medico-teste`
- Pasta original (não mexer, não fazer `pull`): `/Users/forbs/Downloads/Website/meu-site-medico`
- Fonte dos erros: `/Users/forbs/Downloads/estrategia-med/state/materials/<id>.json` (somente leitura)
- Quarto: `/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto` (não está no PATH)

## Seção "Lembrar para a prova"
- Erros: `lembrar/<area>/<materia>/<id>.md`, gerados pelo importador. Não editar à mão.
- Especialidade → pasta: `lembrar/_mapa.json`. Especialidade nova = nova entrada no mapa
  + página da matéria (copiar `lembrar/clinica-medica/hematologia.qmd`) + card em `lembrar-para-a-prova.qmd`.
- Estilos da seção: `lembrar/lembrar.css` (cores em `styles.css`).

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
- `about.qmd` tem um bloco R: o render completo precisa do R instalado.
- Commit, push, PR, merge e publicação só com autorização.
- Pendente (tarefa separada): tirar `.quarto/` e `.Rproj.user/` do controle de versão.
