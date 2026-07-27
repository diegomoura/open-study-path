#!/usr/bin/env python3
"""Run curriculum validation with structural placeholder detection.

The underlying validator historically matched broad Portuguese phrases such as
"descreva o", which can occur naturally in legitimate teaching content. This
wrapper narrows placeholder detection to template tokens and exact instructional
lines inherited unchanged from templates/module.md.
"""

from __future__ import annotations

import re

import validate_curriculum as validator

PLACEHOLDER_TOKEN = re.compile(
    r"(?:\breplace me\b|\bTOPIC-000\b|\bstudy the core concept\b|\bsubstitua por\b)",
    re.IGNORECASE,
)

PLACEHOLDER_LINES = {
    "Explique a sequência de estudo, o tempo sugerido e o que o estudante deverá produzir. Este arquivo deve ser uma aula autocontida, não apenas uma lista de tarefas.",
    "Divida a experiência em três a sete ações pequenas e verificáveis. Cada ação deve normalmente durar entre 10 e 25 minutos. Evite uma única linha que misture leitura, exercício, entrega e avaliação.",
    "Inclua duas ou três perguntas curtas ou tarefas de recuperação ativa. Dê orientação para revisar o tópico anterior quando necessário.",
    "Ensine efetivamente o conteúdo em linguagem adequada ao nível configurado. Inclua definições, relações entre conceitos, limites, nuances e raciocínio. Não use placeholders como “estude o conceito”.",
    "Introduza o que o diagrama representa e por que ele ajuda a compreender este tópico. Todo módulo materializado deve conter ao menos um diagrama Mermaid útil e explicado. Temas complexos podem usar vários diagramas separados.",
    "Apresente ao menos dois exemplos resolvidos passo a passo, incluindo um caso simples e um caso com ambiguidade ou erro comum.",
    "Liste equívocos prováveis, explique por que estão errados e mostre como reformular o raciocínio.",
    "Inclua exercícios com pistas graduais. Não revele imediatamente a resposta completa; mostre critérios para o estudante conferir o próprio raciocínio.",
    "Inclua tarefas que exijam transferência para um caso novo e produção do entregável definido no tópico.",
    "Inclua perguntas que possam ser respondidas sem consultar o texto e uma breve orientação de revisão espaçada.",
    "Descreva exatamente o que deve ser produzido e como vincular ou transcrever a evidência no formulário de avaliação. Quando o entregável estiver em Google Drive ou outro workspace externo, preserve um link seguro e deixe claro que o resultado oficial da avaliação permanece no GitHub.",
    "Liste fontes primárias ou oficiais com localizador canônico. Para pesquisa acadêmica descoberta com Consensus ou outro provedor, registre a fonte verificável; não cite apenas a resposta do plugin. Para cursos externos, identifique seção ou aula, acesso e alternativa gratuita quando aplicável.",
}


def contains_template_placeholder(body: str) -> bool:
    """Return true only for durable template residue, not ordinary prose."""
    if PLACEHOLDER_TOKEN.search(body):
        return True
    normalized_lines = {line.strip() for line in body.splitlines() if line.strip()}
    return bool(normalized_lines.intersection(PLACEHOLDER_LINES))


class StructuralPlaceholderPattern:
    """Provide the minimal search interface expected by validate_curriculum."""

    @staticmethod
    def search(body: str) -> object | None:
        return object() if contains_template_placeholder(body) else None


def main() -> None:
    validator.PLACEHOLDER_CONTENT = StructuralPlaceholderPattern()
    validator.main()


if __name__ == "__main__":
    main()
