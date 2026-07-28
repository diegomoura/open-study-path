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
        "Explique em poucas linhas o que a pessoa vai aprender, por que isso importa para o objetivo dela, "
        "quanto tempo reservar e o que produzir ao final. Este arquivo deve ser uma aula autocontida, "
        "não apenas uma lista de tarefas."
    )

    assert_legitimate("Descreva o impacto de um julgamento precipitado sobre a decisão seguinte.")
    assert_legitimate("Inclua exercícios adicionais somente quando ajudarem a comparar duas interpretações.")
    assert_legitimate("Apresente ao menos uma objeção real antes de formular sua resposta.")
    assert_legitimate("O estudante deve descrever o próprio raciocínio sem copiar definições.")

    print("Curriculum placeholder regression tests passed.")


if __name__ == "__main__":
    main()
