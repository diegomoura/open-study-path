# Agent pilot: Etapa 4b — `diagnostic` (design fechado, harness implementado)

Status: **harness implementado, testado offline (38 casos em
`test_agent_runtime.py` + 2 em `test_build_diagnostic_context.py`),
aguardando validação real.** A seção 1-4 abaixo é o desenho original
(decisão de arquitetura, fechada antes de qualquer código); a seção 5
documenta o que foi de fato construído.

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

## 5. O que foi implementado

Implementação real do desenho acima, sem desvios de arquitetura.

### 5.1 Harness (`agent_runtime.py`)

- Allowlist: `.open-study-path/instance.yml`, `state/diagnostic-summary.json`
  -- direto de `instructions/20-diagnostic.md`'s "Diagnostic pull-request
  policy", cross-checado contra `scripts/review_framework.py`'s próprio
  `_allowed_domain_path` para o profile `diagnostic` (batem exatamente).
- Agente `diagnostic` (author, `sonnet` -- já cadastrado em `AGENT_CATALOG`).
- Dois tools novos, exclusivos do author (o reviewer não ganha nenhum):
  `list_issue_comments(number)` (lê a thread inteira) e
  `post_issue_comment(number, body)` (posta pergunta ou resposta de
  conclusão).
- `diagnostic` entra em `PHASES_WITH_GITHUB_ISSUES` (para ganhar
  `github_request`/`repository`), mas é explicitamente excluído do bloco
  genérico que dá tools de leitura de issue ao *reviewer* -- a instrução
  exige que o reviewer reconstrua a conclusão só a partir do resumo
  persistido, nunca da transcrição bruta.
- Guard estrutural real em `finish_phase`: recusa terminar um turno de
  `diagnostic` sem que `post_issue_comment` tenha sido chamado antes. Isso é
  deliberadamente mais fraco que os guards de `intake`/`publish` (que travam
  em cima de um resultado determinístico de classificação) -- aqui não
  existe sinal determinístico de "evidência suficiente", a decisão é
  julgamento do modelo. O guard garante só que nenhum turno termina em
  silêncio, não que o julgamento em si estava certo.

### 5.2 `scripts/build_diagnostic_context.py`

Novo. Busca o corpo da issue + todos os comentários via API do GitHub e
monta um texto único (`render_transcript()`) que vira o `extra_context` do
author -- é o mecanismo completo de "memória" entre turnos, já que cada
invocação é um processo novo sem estado nenhum. Testado offline (2 casos).

### 5.3 `build_agent_prompt.py`

- `--extra-context-file` novo na CLI: le o contexto de um arquivo em vez de
  um argumento de shell -- necessário porque uma transcrição de várias
  perguntas/respostas pode ter aspas e quebras de linha, inseguro como
  argumento único de shell (mesmo raciocínio que já levou `EXTRA_CONTEXT` a
  ser passado via `env:` no workflow original, agora um passo além).
- `instructions/20-diagnostic.md` + `21-diagnostic-completion-recovery.md`
  como contrato; review profile `diagnostic` (5 checks:
  `evidence_basis`, `bounded_questioning`, `adjacent_experience_separation`,
  `placement_consistency`, `privacy_and_minimization`).
- Nota de escopo do author: passo a passo explícito do turno (ler a thread
  primeiro sempre, decidir suficiência, postar pergunta OU concluir),
  adaptando o contrato -- escrito assumindo um chat ao vivo -- para o
  formato real "um processo novo por resposta do aluno".
- Nota de escopo do reviewer: reforça que não há tools de issue disponíveis
  de propósito, e que evidência fraca no resumo já é, por si, um achado
  (`placement_consistency`), não motivo para tentar investigar a conversa
  original.

### 5.4 Workflow novo (`.github/workflows/agent-pilot-diagnostic.yml`)

Não é uma opção a mais no workflow existente -- é um arquivo próprio,
porque o modelo de gatilho e a semântica de sucesso/falha são
fundamentalmente diferentes:

- Gatilho `issue_comment: [created]`, não `workflow_dispatch`.
- Guardas: só roda se (a) o comentário foi numa *issue*, não numa PR
  (`issue_comment` dispara para os dois no modelo do GitHub); (b) a issue
  tem a label `diagnostic:in-progress`; (c) quem comentou não foi o próprio
  bot -- sem isso, a pergunta/resposta que o author posta re-dispararia o
  workflow nele mesmo, um loop infinito real.
- `TARGET_REPO` é sempre `github.repository` (nunca de input) -- mesma
  fronteira de segurança de todas as outras fases.
- **Diff vazio não é falha aqui** -- é o resultado normal da maioria dos
  turnos (o author só postou a próxima pergunta). Um novo step "Check
  whether this turn completed the diagnostic" define
  `completed=true/false` como output do job; o job do reviewer só roda
  quando `completed=true` (`needs.author.outputs.completed == 'true'`).
- Ao completar (turno terminal), a label `diagnostic:in-progress` é
  removida **antes** do commit -- fecha a janela onde uma resposta
  tardia/duplicada do aluno poderia disparar um segundo turno contra uma
  sessão já resolvida.
- **Limitação conhecida, mesma categoria já documentada para
  `intake`/`publish`**: a resposta de conclusão é postada como comentário
  pelo *author*, antes do reviewer isolado confirmar. Se o reviewer
  bloquear (`action_required`), o aluno já viu a mensagem de conclusão
  mesmo assim -- efeito colateral imediato, independente do PR ser
  mergeado.

### 5.5 O que falta para "validado"

Diferente de todas as fases anteriores, validar isso de verdade exige
simular idas e vindas reais de comentário (não um único
`workflow_dispatch`): criar uma issue de sessão com a label
`diagnostic:in-progress`, postar uma resposta, conferir que o workflow
dispara e posta a próxima pergunta, repetir até a conclusão, e então
aplicar o mesmo critério de sempre (hash na mão, custo real, revisão
isolada). Pendente -- não tentado ainda nesta etapa.
