# Agent pilot: Etapa 4 — extensão para `intake`

Status: **design implementado, aguardando validação real.** Nenhum
`workflow_dispatch` foi disparado ainda para este código — o critério da
Etapa 3 (`docs/claude-agent-pilot-etapa3.md`, "rodar de verdade + conferir
hash na mão") ainda não foi aplicado a `intake`. Este documento registra o
desenho e o que falta para fechar a validação, não um resultado medido.

## 1. Escopo desta etapa

Proposta (seção 7, etapa 4): estender o piloto para `intake`, `diagnostic`,
`publish`. Esta etapa cobre **só `intake`**, e só o provider `github_issue`
(mesma restrição que `configure_intake` já tinha). `diagnostic` e `publish`
foram conscientemente adiados:

- `diagnostic` exige sessão interativa real com o aluno
  (`instructions/20-diagnostic.md`, "ask exactly one short question at a
  time") — não cabe no formato `run_agent()` de disparo único que o harness
  atual implementa. Decisão de formato pendente, registrada em
  `docs/claude-agent-pilot.md` §Scope.
- `publish` precisa de credencial de provider externo (Trello, Todoist,
  Notion, Calendar, Gmail) que a seção 6 da proposta original nunca cobriu.
  Quando for retomado, o piloto começa restrito a `task manager: GitHub
  Issues` (reaproveita o `GITHUB_TOKEN` já usado aqui), com os outros
  providers como incrementos futuros e explícitos.

## 2. O que muda no harness

`scripts/agent_runtime.py` e `scripts/build_agent_prompt.py` eram
implicitamente moldados nos dois fluxos de setup (`bootstrap_instance`,
`configure_intake`), que compartilham o mesmo contrato de escrita
(`instructions/02-setup-execution.md`, "Allowed setup diff"). `intake` tem um
contrato de saída diferente e, mais importante, precisa de um recurso que os
dois anteriores nunca precisaram: **acesso de leitura (e uma escrita pontual
de label) ao GitHub Issues da própria instância**, não só ao checkout local.

### 2.1 Allowlist de escrita local (`INTAKE_ALLOWED_EXACT_PATHS`)

Direto de `instructions/10-intake.md`, seção "Pull request and merge":

```
.open-study-path/instance.yml
study.config.yml
state/intake-summary.json
```

O quarto item citado na instrução (um artefato de revisão em
`state/reviews/`) fica de fora do allowlist do author pela mesma razão que já
valia para `bootstrap_instance`/`configure_intake`: só o reviewer isolado
escreve ali, via `submit_review`, nunca o author via `write_file`.

### 2.2 Tool novo: GitHub Issues, escopado só a `intake`

`RepoTools` ganhou um segundo grupo de tools, habilitado só quando
`phase in PHASES_WITH_GITHUB_ISSUES` (hoje, só `{"intake"}`):

| Tool | Author | Reviewer | O que faz |
|---|---|---|---|
| `list_intake_issues` | sim | sim | Lista issues abertas, não-PR, com a label `study-request` — só resumo (número, título, labels, autor), sem corpo |
| `read_github_issue(number)` | sim | sim | Corpo completo renderizado de uma issue |
| `resolve_intake_candidates(...)` | sim | não | Roda o algoritmo determinístico real de `scripts/intake_resolution.py` — **não** deixa o modelo classificar candidatos por conta própria |
| `label_github_issue(number, label)` | sim (só `intake:imported`) | não | Único write externo; recusa qualquer outra label na camada de código, não só via prompt |

Dois pontos de desenho que valem registrar:

1. **O repositório-alvo do GitHub Issues nunca vem de `target_repo` (input do
   `workflow_dispatch`)** — vem de `GITHUB_REPOSITORY`, variável que o
   próprio GitHub Actions define automaticamente para o repositório onde o
   workflow está rodando. Isso segue a mesma lógica de segurança que já
   protegia `target_repo`/`extra_context` contra interpolação em shell
   (comentário original do workflow): um input controlado por quem dispara o
   workflow não deve poder apontar o tool de Issues para um repositório
   arbitrário. `instructions/10-intake.md` já pede isso em prosa ("Search
   only the instance repository"); agora é estrutural.
2. **A classificação de candidatos não é uma decisão do modelo.**
   `instructions/10-intake.md` é explícito: "Apply the algorithm in
   scripts/intake_resolution.py; do not replace it with similarity or
   newest-issue heuristics." Em vez de confiar que o prompt sozinho garante
   isso, `resolve_intake_candidates` roda `scripts/intake_resolution.py`
   dentro do harness, em Python, sobre dados que o modelo não edita
   (`allowed_authors` e `imported_references` são resolvidos pelo harness a
   partir de `.open-study-path/instance.yml` e
   `state/intake-summary.json`, nunca fornecidos pelo modelo). O modelo só
   fornece o que precisa ler do contrato do formulário
   (`expected_headings`, `required_response_headings`, `consent_heading`),
   que já é este exigido pela instrução ("current repository form contract,
   not a hidden comment").

### 2.3 Prompts (`build_agent_prompt.py`)

Antes, `AUTHOR_SHARED_FILES` incluía `instructions/02-setup-execution.md`
incondicionalmente — correto para os dois fluxos de setup, errado para
`intake`. Foi dividido em:

- `AUTHOR_CORE_SHARED_FILES` / `REVIEWER_CORE_SHARED_FILES`: sempre incluídos
  (`AGENTS.md`, `instructions/phase-completion.md` para o author;
  `AGENTS.md` + o contrato genérico de revisão para o reviewer).
- `PHASE_EXTRA_AUTHOR_FILES` / `PHASE_EXTRA_REVIEWER_FILES`: específico por
  fase. `intake` lê `instructions/11-intake-completion-recovery.md` e
  `intake/field-mapping.yml`, não `02-setup-execution.md`.
- `PHASE_REVIEW_PROFILE`: `intake` usa o profile `intake` (não `setup`) —
  isso muda quais checks o `docs/review-framework.md`/
  `instructions/11-intake-completion-recovery.md` exige (`request_fidelity`,
  `preference_preservation`, `ambiguity_resolution`, `data_minimization`,
  `next_phase_consistency`).

Um `AUTHOR_INTAKE_TOOL_NOTE`/`REVIEWER_INTAKE_TOOL_NOTE` foi adicionado só
para a fase `intake`, documentando os quatro tools novos e reforçando
explicitamente para o author "não decida qual issue é a certa sozinho antes
de chamar `resolve_intake_candidates` — é exatamente a heurística que a
instrução proíbe".

## 3. Risco conhecido: label é write imediato, não gated por merge do PR

`label_github_issue` aplica `intake:imported` na issue real assim que o
author chama o tool — isso acontece **antes** do PR ser aberto, revisado ou
mergeado. Se o reviewer isolado rejeitar (`action_required`) ou um humano
decidir não mergear o PR, a issue já estará marcada como importada mesmo que
`study.config.yml`/`state/intake-summary.json` nunca cheguem à `main`.

Isso não é um bug novo introduzido aqui — é a mesma tensão que já existe no
fluxo manual de hoje (`instructions/10-intake.md`: "After import, persist the
exact source reference, apply `intake:imported`... for auditability" já
descreve a label como parte do próprio ato de importar, não do merge). Mas
vale registrar como limitação conhecida, não resolvida nesta etapa: um PR
rejeitado deixa a issue com a label aplicada e nenhum estado correspondente
mergeado. Mitigação futura possível: um passo de "unlabel" quando o job do
reviewer retorna `action_required` — fora do escopo desta etapa por ora.

## 4. Testes offline

`scripts/test_agent_runtime.py` ganhou 5 casos novos (total 20, todos
passando sem rede/token):

- `test_intake_allowlist_matches_pull_request_and_merge_contract`
- `test_github_issues_tools_are_gated_to_the_intake_phase`
- `test_resolve_intake_candidates_uses_real_algorithm_not_model_judgment`
- `test_label_github_issue_refuses_any_label_other_than_imported`
- `test_reviewer_cannot_label_github_issues`

Como antes, não há teste end-to-end automatizado contra a API real — custaria
tokens em todo run de CI.

## 5. O que falta para "validado" (critério da Etapa 3)

1. Rodar `workflow_dispatch` de verdade, fase `intake`, contra o repositório
   de teste descartável, com pelo menos uma issue real de exemplo já criada
   com a label `study-request` e o formulário atual.
2. Conferir manualmente: os 3 hashes dos arquivos de saída batem com os
   bytes reais; a label `intake:imported` foi aplicada só na issue correta;
   o reviewer isolado recomputou o hash (não copiou do author, replicando o
   achado da Etapa 3 sobre `configure_intake` pré-`#76`).
3. Rodar pelo menos um caso de `state: ambiguous` (duas issues válidas) e
   confirmar que o author não escreve nada e não aplica a label — só
   `finish_phase` com um resumo pedindo decisão humana.
4. Registrar custo real em `state/agent-pilot-usage.jsonl`, mesmo padrão da
   Etapa 3.

Nenhum desses 4 passos foi executado ainda. Não disparar o workflow sem
confirmação explícita, já que tem custo de API real.
