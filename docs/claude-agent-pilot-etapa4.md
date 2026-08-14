# Agent pilot: Etapa 4 — extensão para `intake`

Status: **fechada para o caso `github_issue`.** Dois dispatches reais contra
o repositório de teste descartável
(`diegomoura/open-study-path-agent-test-20260814152628`) validaram o caso
`unique` (hashes conferidos na mão, batem) e o caso `ambiguous` (sem write de
domínio, sem label aplicada, reviewer isolado bloqueia por conta própria um
resultado imperfeito). Ver seção 5 para os números reais e uma pendência não
bloqueante encontrada no caminho `ambiguous`.

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

## 5. Validação real (Etapa 4 fechada para o caso `github_issue`)

Status: **fechada**, dois dispatches reais contra o repositório de teste
descartável (`diegomoura/open-study-path-agent-test-20260814152628`).

### 5.1 Caso `unique` — issue #7 ("Aprender Go do zero")

PR de teste #8 (`agent-pilot/intake-20260814210341`). Os 3 hashes conferidos
na mão contra os bytes reais baixados via API bateram exatamente:

| Arquivo | sha256 real | sha256 no review | Bate? |
|---|---|---|---|
| `.open-study-path/instance.yml` | `39c68737...0c40d756` | idêntico | sim |
| `study.config.yml` | `e004a2af...59fe395c4` | idêntico | sim |
| `state/intake-summary.json` | `f9bdea2b...0bce570b8` | idêntico | sim |

Os 5 checks do profile `intake` (`request_fidelity`, `preference_preservation`,
`ambiguity_resolution`, `data_minimization`, `next_phase_consistency`) todos
`passed`, `status: approved`. `path.learning_request` preservado verbatim,
`path.subject` é um rótulo derivado sem substituir a resposta original,
`path.name` igual ao título da issue sem reescrita. A label
`intake:imported` foi aplicada só na issue #7 — confirmado consultando
`GET /repos/.../issues?labels=intake:imported` depois do run: nenhuma outra
issue foi tocada. Custo real: 350.991 tokens combinados, **$0.1225**.

### 5.2 Caso `ambiguous` — issues #9 e #10 (duas candidatas válidas)

PR de teste #11 (`agent-pilot/intake-20260814210946`). Resultado central:
**nenhum arquivo de domínio foi escrito** (`study.config.yml` e
`.open-study-path/instance.yml` ficaram intocados) e **nenhuma label foi
aplicada** a #9 ou #10 — só #7 (da rodada anterior) continua marcada. O
author nunca decidiu sozinho qual candidata importar.

Achado real (não hipotético) que vale registrar: o author escreveu em
`state/intake-summary.json` um objeto de status ad hoc
(`classification_state`, `ambiguous_candidates`, `action_required`) fora do
schema real desse arquivo, em vez de não escrever nada e só usar
`finish_phase` para reportar a ambiguidade. **O reviewer isolado pegou isso
sozinho**: `status: action_required`, com blocking finding explícito
("operation changed state/intake-summary.json but did not create an
approved review artifact with all required checks... passed"). Três dos
cinco checks (`request_fidelity`, `preference_preservation`,
`next_phase_consistency`) ficaram `pending`, só `ambiguity_resolution` e
`data_minimization` foram marcados `passed`. O workflow não faz auto-merge
de qualquer forma, mas isso confirma que o reviewer bloquearia mesmo se
houvesse merge automático configurado.

Nenhum efeito colateral externo aconteceu, mas o prompt de `intake` (Etapa 4)
tinha um ponto a apertar: a instrução não deixava claro onde/como reportar um
estado `ambiguous` sem escrever num caminho de schema fixo. **Corrigido**:
`AUTHOR_INTAKE_TOOL_NOTE` agora instrui explicitamente a não escrever nenhum
arquivo de domínio em `none`/`ambiguous`, e — mais importante — `write_file`
em `agent_runtime.py` agora **recusa estruturalmente** escrever
`state/intake-summary.json` na fase `intake` a menos que
`resolve_intake_candidates` tenha retornado `state="unique"` na mesma
execução. Isso segue o mesmo princípio que já valia para o allowlist de
caminho: falhar numa fronteira de código, não só confiar na instrução do
prompt. Teste de regressão:
`test_intake_summary_write_blocked_without_a_unique_resolution`.

Custo real: 188.740 tokens combinados, **$0.0765**.

### 5.3 Critério de validação — fechado

Os 4 passos listados originalmente nesta seção foram cumpridos:

1. Dispatch real contra o repo de teste — feito, 2 execuções.
2. Hashes conferidos na mão — batem exatamente (caso `unique`).
3. Caso `ambiguous` testado — author não escreve domínio nem aplica label;
   reviewer bloqueia por conta própria o resultado imperfeito que o author
   produziu.
4. Custo registrado em `state/agent-pilot-usage.jsonl` de ambos os runs no
   repo de teste — $0.0765–$0.1225 por execução em Haiku 4.5, faixa
   compatível com `bootstrap_instance`/`configure_intake` da Etapa 3.

Pendência resolvida nesta mesma etapa: apertado o prompt e, mais
estruturalmente, adicionado um guard de código em `write_file` que recusa
`state/intake-summary.json` fora do estado `unique` -- não depende só do
prompt se comportar bem.

### 5.4 Confirmação fim-a-fim do fix (PR #83)

Terceiro dispatch, mesmas issues #9/#10 (ainda livres, sem `intake:imported`
na época do teste). Resultado: `git status --porcelain` vazio -- o author
não escreveu **nada**, nem `state/intake-summary.json`. O step `Fail if the
author produced no diff` disparou de propósito, o mesmo comportamento que já
existia para qualquer fase antes de `intake` existir. Custo real:
**$0.0293** (bem mais barato que o run anterior de `ambiguous`, $0.0765 --
o modelo não tentou mais escrever e recuar). Confirma o fix fim-a-fim, não
só a lógica testada offline.

Achado secundário, não corrigido ainda: o resumo do author (`finish_phase`'s
`summary`/`next_action`, que explicaria qual é a ambiguidade e pediria a
decisão do dono) é extraído para `/tmp/author-summary.txt` no step "Extract
author summary for the reviewer" -- **antes** do step "Fail if the author
produced no diff". Mas "Upload author artifacts" (que tornaria esse resumo
visível) vem depois do step que falha, então é pulado. Um dono da instância
vendo esse run só enxerga "author agent finished without writing any allowed
file" no log bruto do Actions, sem a explicação de qual issue escolher.
Correção sugerida para uma iteração futura: mover (ou duplicar) o upload do
resumo do author para antes do check de diff vazio, ou imprimir
`next_action` diretamente no job summary (`$GITHUB_STEP_SUMMARY`)
independente do resultado do diff.

**Corrigido nesta mesma etapa.** Novo step "Publish author result to the job
summary" (`scripts/publish_author_summary.py`) roda logo após "Extract
author summary for the reviewer" e antes de "Fail if the author produced no
diff" -- imprime `summary`/`next_action` no `$GITHUB_STEP_SUMMARY` e no log
puro, incondicionalmente. "Upload author artifacts" ganhou `if: always()`
pelo mesmo motivo: o JSON bruto do author fica disponível mesmo quando o job
falha de propósito por diff vazio. Seguindo a mesma convenção de
`scripts/format_pr_body.py`, a lógica ficou num script Python próprio, não
inline no YAML. Teste offline novo:
`scripts/test_publish_author_summary.py` (2 casos).
