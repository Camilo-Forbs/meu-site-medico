#!/usr/bin/env python3
"""Importa erros do estrategia-med para a seção "Lembrar para a prova".

Fonte de verdade: estrategia-med/state/materials/<id>.json
Saída: residencia/lembrar/<area>/<materia>/<id>.md (um arquivo por questão)

Conversão determinística, sem IA e só com a biblioteca padrão.
- Cria apenas arquivos que ainda não existem.
- Arquivo existente e idêntico ao que seria gerado: ignorado.
- Arquivo existente e diferente: conflito (não sobrescreve).
  Para regravar de propósito: --atualizar <id>.
- Especialidade fora de residencia/lembrar/_mapa.json: reportada, nunca adivinhada.
- IDs listados em "ids_dir_antigo" no mapa ganham "aliases" (redirecionamento da URL
  antiga, de antes da mudança para residencia/lembrar/).
- Complementos (somente leitura, se existirem) acrescentados DEPOIS do resumo original:
  estrategia-med/caderno/entradas.json (por que errei, para fixar, armadilha, conduta),
  estrategia-med/caderno/padroes.json (padrões e erros relacionados) e os flashcards do material.

Uso:
  python3 scripts/importar_erros.py [--materiais DIR] [--caderno DIR] [--atualizar ID ...] [--simular]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SECAO = RAIZ / "residencia" / "lembrar"
MAPA = SECAO / "_mapa.json"
MATERIAIS_PADRAO = Path("/Users/forbs/Downloads/estrategia-med/state/materials")
CADERNO_PADRAO = Path("/Users/forbs/Downloads/estrategia-med/caderno")

# Primeira linha de resumo_md: "### <título> — <id> · você: <X> · gabarito: <Y>"
CABECALHO = re.compile(
    r"^### (?P<titulo>.+) — (?P<id>\d+) · você: (?P<voce>\S+) · gabarito: (?P<gabarito>\S+)$"
)


def q(valor):
    """String YAML entre aspas duplas (JSON é YAML válido)."""
    return json.dumps(str(valor), ensure_ascii=False)


def br(data):
    """2026-11-21 -> 21/11/2026 (mantém o texto se não for data ISO)."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(data))
    return f"{m[3]}/{m[2]}/{m[1]}" if m else str(data)


def literal(texto):
    """Impede que "1) …" ou "- …" no início de uma linha do flashcard vire lista Markdown."""
    return re.sub(r"(^|<br>|\n)(\s*)(\d+)([.)])", r"\1\2\3\\\4", str(texto)).replace("\n", "<br>")


def complementos(qid, material, entrada, padroes, onde, titulos, pasta):
    """Seções extras em Markdown, só com dados que existem nas fontes."""
    out = []
    if entrada:
        if entrada.get("por_que_errei"):
            out += ["## Por que errei", "", entrada["por_que_errei"], ""]
        if entrada.get("fixar"):
            out += ["## Para fixar", ""] + [f"- {x}" for x in entrada["fixar"]] + [""]
        if entrada.get("armadilha"):
            out += ["## Armadilha", "", entrada["armadilha"], ""]
        if entrada.get("conduta"):
            out += ["## Conduta", "", entrada["conduta"], ""]
        if entrada.get("observacao"):
            out += ["## Observação", "", entrada["observacao"], ""]
    relacionados = [p for grupo, lista in padroes.items() if isinstance(lista, list)
                    for p in lista if isinstance(p, dict) and qid in p.get("ids", [])]
    if relacionados:
        out += ["## Padrões relacionados", ""]
        for p in relacionados:
            out += [f"### {p.get('titulo', 'Padrão')}", ""]
            if p.get("regra"):
                out += [p["regra"], ""]
            outros = [i for i in p.get("ids", []) if i != qid]
            if outros:
                out += ["Outras questões com este padrão:", ""]
                for i in outros:
                    nome = titulos.get(i, f"questão {i}")
                    if i in onde:
                        out.append(f"- [{nome}]({os.path.relpath(onde[i], pasta)})")
                    else:
                        out.append(f"- {nome} (questão {i}, ainda não publicada no site)")
                out.append("")
    if entrada and len(entrada.get("ocorrencias") or []) > 1:
        out += ["## Histórico", ""] + [f"- {br(o.get('data', ''))}: {o.get('tipo', '')}" for o in entrada["ocorrencias"]] + [""]
    cards = [c for c in (material.get("cards") or []) if c.get("front") and c.get("back")]
    if cards:
        out += ['::: {.callout-tip collapse="true"}', f"## Flashcards ({len(cards)})", ""]
        for c in cards:
            out += [f"**{literal(c['front'])}**", "", literal(c["back"]), ""]
        out += [":::", ""]
    origem = (entrada or {}).get("origem") or {}
    if origem.get("descricao"):
        out += [f"*Contexto do estudo: {origem['descricao']}.*", ""]
    return ("\n".join(out).rstrip() + "\n") if out else ""


def gerar(material, destino, extra=""):
    """Devolve (conteúdo do .md, None) ou (None, motivo do erro)."""
    qid = str(material.get("id", ""))
    resumo = material.get("resumo_md")
    reg = material.get("registro")
    if not isinstance(resumo, str) or not resumo.strip():
        return None, "resumo_md ausente ou vazio"
    if not isinstance(reg, dict):
        return None, "registro ausente"
    primeira, _, corpo = resumo.partition("\n")
    m = CABECALHO.match(primeira)
    if not m:
        return None, "primeira linha de resumo_md fora do formato esperado"
    if m["id"] != qid:
        return None, f"ID do cabeçalho ({m['id']}) difere do ID do material"
    for campo, achado in (("minha_resposta", m["voce"]), ("gabarito", m["gabarito"])):
        if reg.get(campo) and reg[campo] != achado:
            return None, f"{campo} do cabeçalho ({achado}) difere do registro ({reg[campo]})"

    v = lambda k: str(reg.get(k, "")).strip()
    partes = [v("fonte"), v("ano")]
    if v("minha_resposta"):
        partes.append(f"você: {v('minha_resposta')}")
    if v("gabarito"):
        partes.append(f"gabarito: {v('gabarito')}")
    if v("acerto_geral_pct"):
        partes.append(f"acerto geral: {v('acerto_geral_pct')}%")
    descricao = " · ".join(p for p in partes if p)

    campos = [
        ("id", qid),
        ("title", m["titulo"]),
        ("subtitle", v("tema")),
        ("description", descricao),
        ("date", v("data_resposta")),
        ("banca", v("fonte")),
        ("ano", v("ano")),
        ("especialidade", v("especialidade")),
        ("area", destino["area"]),
        ("materia", destino["materia"]),
        ("tema", v("tema")),
        ("minha_resposta", v("minha_resposta")),
        ("gabarito", v("gabarito")),
        ("acerto_geral_pct", v("acerto_geral_pct")),
        ("tem_comentario", v("tem_comentario")),
        ("origem", f"estrategia-med/state/materials/{qid}.json"),
    ]
    linhas = ["---", "# Gerado por scripts/importar_erros.py. Não editar à mão: use --atualizar <id>."]
    linhas += [f"{k}: {q(val)}" for k, val in campos if val]
    if qid in destino.get("ids_dir_antigo", []):
        antigo = os.path.relpath(RAIZ / destino["dir_antigo"] / f"{qid}.html", RAIZ / destino["dir"])
        linhas += ["aliases:", f"  - {q(antigo)}"]
    linhas.append("---")
    texto = "\n".join(linhas) + "\n" + corpo
    if not texto.endswith("\n"):
        texto += "\n"
    if extra:
        texto += "\n" + extra
    return texto, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--materiais", type=Path, default=MATERIAIS_PADRAO,
                    help=f"pasta com <id>.json (padrão: {MATERIAIS_PADRAO})")
    ap.add_argument("--caderno", type=Path, default=CADERNO_PADRAO,
                    help=f"pasta com entradas.json e padroes.json (padrão: {CADERNO_PADRAO}); opcional")
    ap.add_argument("--atualizar", nargs="+", default=[], metavar="ID",
                    help="regrava estes IDs mesmo que o .md exista e esteja diferente")
    ap.add_argument("--simular", action="store_true", help="não grava nada; só relata")
    args = ap.parse_args(argv)

    if not args.materiais.is_dir():
        print(f"ERRO: pasta de materiais não encontrada: {args.materiais}")
        return 2
    mapa = json.loads(MAPA.read_text(encoding="utf-8"))
    entradas, padroes = {}, {}
    if (args.caderno / "entradas.json").is_file():
        entradas = {str(e.get("id")): e for e in json.loads((args.caderno / "entradas.json").read_text(encoding="utf-8"))}
    if (args.caderno / "padroes.json").is_file():
        padroes = json.loads((args.caderno / "padroes.json").read_text(encoding="utf-8"))
    # Onde cada questão está (ou estará) no site e com que título, para ligar erros relacionados.
    onde = {p.stem: p for p in SECAO.rglob("*.md") if p.stem.isdigit()}
    titulos = {i: e.get("subassunto") for i, e in entradas.items() if e.get("subassunto")}
    for arq in args.materiais.glob("*.json"):
        try:
            m0 = json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        d0 = mapa.get(str(m0.get("registro", {}).get("especialidade", "")).strip())
        c0 = CABECALHO.match(str(m0.get("resumo_md", "")).partition("\n")[0])
        if d0 and str(m0.get("id")) == arq.stem:
            onde[arq.stem] = RAIZ / d0["dir"] / f"{arq.stem}.md"
            if c0:
                titulos[arq.stem] = c0["titulo"]
    atualizar = set(args.atualizar)
    vistos = set()
    res = {"novo": [], "atualizado": [], "ignorado": [], "conflito": [], "sem_mapa": [], "invalido": []}

    for arq in sorted(args.materiais.glob("*.json")):
        try:
            material = json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            res["invalido"].append((arq.stem, f"JSON ilegível: {e}"))
            continue
        qid = str(material.get("id", ""))
        if qid != arq.stem or not qid.isdigit():
            res["invalido"].append((arq.stem, f"ID interno '{qid}' difere do nome do arquivo"))
            continue
        vistos.add(qid)
        esp = str(material.get("registro", {}).get("especialidade", "")).strip()
        destino = mapa.get(esp)
        if destino is None:
            res["sem_mapa"].append((qid, esp or "(sem especialidade)"))
            continue
        extra = complementos(qid, material, entradas.get(qid), padroes, onde, titulos, RAIZ / destino["dir"])
        texto, erro = gerar(material, destino, extra)
        if erro:
            res["invalido"].append((qid, erro))
            continue

        alvo = RAIZ / destino["dir"] / f"{qid}.md"
        outros = [p for p in SECAO.rglob(f"{qid}.md") if p != alvo]
        if outros:
            res["conflito"].append((qid, f"já existe em {outros[0].relative_to(RAIZ)}"))
            continue
        if alvo.exists():
            if alvo.read_text(encoding="utf-8") == texto:
                res["ignorado"].append((qid, "já existe, idêntico"))
                continue
            if qid not in atualizar:
                res["conflito"].append((qid, f"{alvo.relative_to(RAIZ)} difere; use --atualizar {qid}"))
                continue
            if not args.simular:
                tmp = alvo.with_suffix(".md.tmp")
                tmp.write_text(texto, encoding="utf-8")
                tmp.replace(alvo)
            res["atualizado"].append((qid, str(alvo.relative_to(RAIZ))))
            continue
        if not args.simular:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            with open(alvo, "x", encoding="utf-8") as f:  # "x": falha se o arquivo surgir no meio
                f.write(texto)
        res["novo"].append((qid, str(alvo.relative_to(RAIZ))))

    for qid in sorted(atualizar - vistos):
        res["invalido"].append((qid, "--atualizar: ID não encontrado nos materiais"))

    rotulos = {"novo": "NOVO", "atualizado": "ATUALIZADO", "conflito": "CONFLITO",
               "sem_mapa": "SEM MAPA", "invalido": "INVÁLIDO"}
    for chave, rotulo in rotulos.items():
        for qid, info in res[chave]:
            print(f"{rotulo:<10} {qid}  {info}")
    prefixo = "[simulação] " if args.simular else ""
    nomes = {"novo": "novos", "atualizado": "atualizados", "ignorado": "ignorados",
             "conflito": "conflitos", "sem_mapa": "sem mapa", "invalido": "inválidos"}
    print(prefixo + " · ".join(f"{nomes[k]}: {len(v)}" for k, v in res.items()))
    return 1 if res["conflito"] or res["invalido"] else 0


if __name__ == "__main__":
    sys.exit(main())
