#!/usr/bin/env python3
"""Regression tests for curriculum placeholder detection."""

from __future__ import annotations

from validate_curriculum_safe import contains_template_placeholder


def assert_placeholder(text: str) -> None:
    if not contains_template_placeholder(text):
        raise SystemExit(f"expected placeholder was accepted: {text!r}")


def assert_legitimate(text: str) -> None:
    if contains_template_placeholder(text):
        raise SystemExit(f"legitimate teaching prose was rejected: {text!r}")


def main() -> None:
    assert_placeholder("# TOPIC-000 — Replace me")
    assert_placeholder(
        "Descreva exatamente o que deve ser produzido e como vincular ou transcrever a evidência no formulário de avaliação. "
        "Quando o entregável estiver em Google Drive ou outro workspace externo, preserve um link seguro e deixe claro que o resultado oficial da avaliação permanece no GitHub."
    )

    assert_legitimate("Descreva o impacto de um julgamento precipitado sobre a decisão seguinte.")
    assert_legitimate("Inclua exercícios adicionais somente quando ajudarem a comparar duas interpretações.")
    assert_legitimate("Apresente ao menos uma objeção real antes de formular sua resposta.")
    assert_legitimate("O estudante deve descrever o próprio raciocínio sem copiar definições.")

    print("Curriculum placeholder regression tests passed.")


if __name__ == "__main__":
    main()
