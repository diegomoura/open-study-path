# Agent pilot: Etapa 4b — desenho para `diagnostic` (decisão fechada, implementação pendente)

Status: **decisão de arquitetura fechada. Nenhum código implementado.**
Este documento existe para desbloquear a Etapa 5 sem deixar `diagnostic`
como uma pendência vaga — a pergunta "que formato ele vai ter" está
respondida; construir o harness é trabalho futuro, do tamanho de uma etapa
própria, não um ajuste incremental sobre `intake`/`publish`.

## 1. Por que `diagnostic` não cabe no harness atual

`instructions/20-diagnostic.md` é explícito: "Ask exactly one short
question or practical task at a time... Do not present the entire
questionnaire at once... Ask the next question directly when no
clarification is required." Isso é uma sessão real, com um humano
respondendo turno a turno -- não um "author isolado escreve arquivo,
reviewer confere diff" de disparo único.

O harness atual (`scripts/agent_runtime.py`, `run_agent()`) é fechado: uma
chamada de API, um conjunto de tool calls, termina em `finish_phase()`. Não
existe "aluno respondendo no meio do loop". Rodar isso sem humano
significaria o agente simulando as próprias respostas do aluno -- o que não
testa nem produz nada real.

## 2. Resolução: gatilho por `issue_comment`, não `workflow_dispatch`

As outras fases usam `workflow_dispatch`: um humano aperta "Run workflow",
o job roda do início ao fim sem interrupção. `diagnostic` precisa de um
gatilho que aconteça **a cada resposta do aluno**, não uma vez só. GitHub
Actions já tem esse gatilho: `issue_comment: [created]`.

Desenho:

1. Ao final de `intake`, uma issue é criada (ou reaproveitada) representando
   a sessão de diagnóstico, com uma label própria (`diagnostic:in-progress`).
2. O aluno responde a cada pergunta como **comentário** nessa issue -- não
   em chat, não em outro canal. A thread de comentários *é* a sessão.
3. Um novo comentário do aluno na issue dispara o workflow, filtrado pela
   label (`if: contains(github.event.issue.labels.*.name,
   'diagnostic:in-progress')`).
4. Cada disparo é uma chamada de author **isolada**, sem memória de sessão
   -- ela reconstrói o estado inteiro lendo a thread de comentários da
   issue (`list_issue_comments`), a mesma disciplina que já vale para
   `intake`/`publish`: contexto vem de artefatos, nunca de "lembrança".
   Isso é mais consistente com a filosofia do resto da proposta do que
   pareceria à primeira vista -- só muda o evento que dispara, não o
   princípio de isolamento de contexto.
5. A cada turno, o author decide, com base na thread reconstruída e no
   contrato de `instructions/20-diagnostic.md` (orçamento de perguntas,
   regra de parada):
   - evidência insuficiente → posta a próxima pergunta como comentário
     novo na issue (tool `post_issue_comment`, escopo restrito a essa
     issue e a essa label, mesmo princípio do `label_github_issue`
     restrito a uma única label em `intake`);
   - evidência suficiente → executa a operação de repositório de verdade
     (escreve `state/diagnostic-summary.json`, atualiza
     `.open-study-path/instance.yml`, abre PR) e posta a resposta de
     conclusão como comentário final.
6. O reviewer isolado (`diagnostic` profile, já existente em
   `scripts/review_framework.py`) roda **só no turno final** -- quando o
   author decide que a evidência é suficiente e abre PR -- não a cada
   pergunta. Isso evita custo de API a cada troca e mantém o padrão
   "reviewer nunca vê o raciocínio do author, só o resultado final".

## 3. Por que isso não é um ajuste incremental

Comparado a estender `intake`/`publish`, isso muda:

- o **evento de gatilho** (`issue_comment` em vez de `workflow_dispatch`) --
  workflow YAML novo, não uma opção a mais no existente;
- a necessidade de **tooling de comentário** (`list_issue_comments`,
  `post_issue_comment`), não coberto pelo tool set de GitHub Issues já
  existente (que só lê/rotula issues, nunca posta comentário);
- uma lógica de **orçamento de perguntas persistido entre turnos** (contar
  quantas perguntas já foram feitas, checar `owner_requested_comprehensive`,
  aplicar a regra de parada de `instructions/20-diagnostic.md`) que precisa
  ser reconstruída da thread a cada chamada -- não existe hoje um padrão no
  harness para "estado que persiste implicitamente numa conversa pública do
  GitHub" como este;
- validação real exigiria simular várias trocas de comentário reais
  (dispatches múltiplos por sessão de teste), não um único dispatch como
  bastou para `intake`/`publish`.

Isso é dimensionalmente parecido com o trabalho que intake+publish já
levaram juntos -- por isso fica registrado como sua própria etapa
("Etapa 4b"), não como algo que bloqueia ou precisa terminar antes da
Etapa 5.

## 4. Decisão registrada

- Formato: **turn-based via `issue_comment`**, não multi-turn dentro de uma
  única chamada de API, não `workflow_dispatch` de disparo único.
- Escopo de implementação: **fora desta sessão de trabalho**. Fica
  documentado como próximo passo elegível a qualquer momento, sem bloquear
  `generate` (Etapa 5, proposta seção 7 passo 5).
- `docs/claude-agent-pilot.md` §Scope aponta para este documento em vez de
  descrever `diagnostic` como "pendente de decisão" -- a decisão já foi
  tomada.
