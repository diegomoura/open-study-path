# Agent pilot: Etapa 3 — medição de custo e qualidade de revisão

Status: primeira passada de medição, com dados reais puxados do repositório de
teste descartável (`diegomoura/open-study-path-agent-test-20260814152628`),
onde as 5 execuções reais do piloto (Etapa 2, PRs #74–#79) rodaram. Nenhum
desses números vivia em `docs/claude-agent-pilot.md` ou em
`state/agent-pilot-usage.jsonl` do template canônico — o template nunca roda
`bootstrap_instance` nele mesmo, então o histórico só existe no repo
descartável. Este documento consolida o que já existe e nomeia
explicitamente o que ainda falta, em vez de estimar.

## 1. Linha do tempo real das 5 execuções

| PR (repo teste) | Horário | Fase | Harness no momento | Status do reviewer |
|---|---|---|---|---|
| #1 | 15:38 | `bootstrap_instance` | pré-#75/#76 (sem `compute_sha256`, sem rastreio de custo) | `approved` |
| #2 | 15:44 | `configure_intake` | pré-#75/#76 | `approved` |
| #3 | 15:49 | `bootstrap_instance` | pré-#75/#76 — achou os bugs que #75/#76 corrigiram | `action_required` |
| #4 | 19:00 | `bootstrap_instance` | pós-#75/#76/#77 (com rastreio de custo), sem caching (#78 ainda não mergeado) | `approved` |
| #5 | 19:10 | `bootstrap_instance` | pós-#78 (com caching) | `approved` |

Ponto central: **as duas correções estruturais do harness (#75, #76) e o
rastreio de custo (#77) e o caching (#78) só foram validados de novo em
`bootstrap_instance`.** `configure_intake` rodou uma única vez, na versão
mais antiga e com bug do harness (PR #2, 15:44), e nunca mais.

## 2. Custo: o que temos e o que falta

### `bootstrap_instance` — completo, confirma `docs/claude-agent-pilot.md`

| Run | Combined tokens | Custo estimado | Caching |
|---|---|---|---|
| PR #4 (19:00) | 215.290 | $0.2404 | não |
| PR #5 (19:10) | 247.237 | $0.1083 | sim |

Números batem exatamente com os já publicados em
`docs/claude-agent-pilot.md` (seção "Token usage and cost estimates"). Nada
novo aqui além de confirmar a fonte primária (corpo do PR + commit
`state/agent-pilot-usage.jsonl` no repo de teste).

### `configure_intake` — **não temos número comparável**

A única execução real de `configure_intake` (PR #2, 15:44) é **anterior**
ao commit que adicionou rastreio de custo (`134cdaf`, PR #77) e ao commit de
caching (`c86d189`, PR #78). O corpo do PR #2 não tem bloco de "Combined
usage" porque esse recurso ainda não existia quando ele rodou —
`state/agent-pilot-usage.jsonl` nem chegou a ser criado nesse run.

Consequência prática: **não é seguro estimar o custo de `configure_intake`
extrapolando de `bootstrap_instance`.** São instruções diferentes
(`instructions/05-configure-intake.md` vs. `instructions/00-bootstrap.md`),
com contratos de tamanhos diferentes, e o próprio
`docs/claude-agent-pilot.md` já avisa que a proporção entre "tamanho do
arquivo" e "tokens realmente gastos por um loop agentic com múltiplas
idas-e-voltas" não é linear — foi exatamente essa suposição errada que gerou
o número pré-caching de $0.24 em vez do estimado inicial.

**Ação pendente, não feita neste documento:** disparar
`.github/workflows/agent-pilot-setup.yml` com `phase: configure_intake`
contra o mesmo repo de teste, agora com #75/#76/#77/#78 todos presentes, e
registrar o número real. Não fiz esse dispatch agora porque ele gasta
dinheiro de verdade da sua conta Anthropic sem confirmação explícita sua
neste chat — ver seção 5.

## 3. Qualidade de revisão: evidência real, não simulada

Isto é o achado mais importante da Etapa 3, e não estava em nenhum dos
dois documentos anteriores. As execuções pré-#76 (PRs #1, #2, #3) por
acidente **já são o experimento de qualidade que a proposta original (seção
8) pedia** — porque cada uma delas contém dois artefatos de revisão lado a
lado: o "auto-review" que o author escreveu para si mesmo (o comportamento
do fluxo manual de hoje, uma única conversa que autora *e* revisa) e a
revisão isolada de verdade. Dá para comparar os dois diretamente.

### 3.1 `bootstrap_instance`, PR #3 (15:49) — o reviewer isolado pegou uma falha real

O author escreveu `state/reviews/setup-v1.yml` com `status: approved` e seis
fingerprints SHA-256 — todos inventados. O reviewer isolado (contexto
zerado, só viu o diff final, nunca o raciocínio do author) recomputou os
seis hashes de verdade e reportou, campo a campo, o valor reivindicado vs. o
valor real:

> Review artifact state/reviews/setup-v1.yml contains fabricated SHA256
> hashes. All six artifact fingerprints are incorrect placeholder values...
> Instance file: claimed a1e3d5c... actual 70be6a1b...
> [+ 5 outros pares claimed/actual]

Resultado: `status: action_required`, PR não teria passado no gate de CI que
`docs/review-framework.md` define (fingerprint precisa bater exatamente). O
fluxo manual de hoje — uma conversa só, sem separação de contexto — é
estruturalmente o que produziu `setup-v1.yml`: nada nesse fluxo hoje força
recomputar hash em vez de gerar um valor plausível de memória.

**Isso é o resultado que #76 (`compute_sha256` como tool real) foi criado
para garantir de forma estrutural, não só via instrução de prompt** — e o
run seguinte (#4, #5) já não repete esse padrão.

### 3.2 `configure_intake`, PR #2 (15:44) — o reviewer isolado *não* pegou a mesma falha

Este é o achado que os dois documentos anteriores não tinham. No único run
de `configure_intake` que existe, o author também inventou hashes em
`state/reviews/setup-configure-intake-v1.yml`:

```
sha256: cd2db27937c5ec3919ffc1a6c97a5f48906c5c37a2e5ef5d7e6d8e8c4f5f5a1e   # 64 chars
sha256: 2f8c9d3e9c5d7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a     # 62 chars — nem o tamanho certo
```

O reviewer isolado, em `state/reviews/agent-pilot-configure_intake.yml`,
reportou os **dois valores idênticos**, incluindo o de 62 caracteres que
nem é um SHA-256 válido — e ainda assim marcou `status: approved`, sem
nenhum finding sobre isso. Ou seja: nesta execução específica, a
"independência" do reviewer falhou silenciosamente — ele reproduziu o valor
do author em vez de calcular o próprio, o oposto exato do que aconteceu no
run de `bootstrap_instance` cinco minutos depois.

Isso não é surpresa olhando a ordem dos commits: PR #2 rodou **antes** de
#76 adicionar a tool `compute_sha256` ao reviewer. O bug que #76 corrigiu
foi descoberto justamente a partir do run de `bootstrap_instance` (PR #3),
que rodou *depois* de PR #2. `configure_intake` nunca voltou a rodar para
confirmar que a correção também vale para essa fase — é uma suposição
razoável (o harness e a tool são compartilhados entre as duas fases,
`scripts/agent_runtime.py` não diferencia por fase), mas é uma suposição,
não uma medição.

### 3.3 Tabela-resumo

| Fase | Author inventou hash? | Reviewer isolado calculou de verdade? | Resultado |
|---|---|---|---|
| `bootstrap_instance`, pré-#76 (PR #3) | sim | **sim** (recomputou e comparou) | `action_required` — pegou a falha |
| `configure_intake`, pré-#76 (PR #2, único run existente) | sim | **não** (copiou o valor do author) | `approved` — não pegou |
| `bootstrap_instance`, pós-#76 (PRs #4, #5) | n/a (author não escreve mais seu review, ver `docs/claude-agent-pilot.md` §"Author self-review") | n/a | `approved`, sem findings sobre hash |

A linha 3 confirma que a correção estrutural (#77: `state/reviews/` fora da
allowlist de escrita do author) elimina a classe inteira de problema para
`bootstrap_instance` — o author não escreve mais um review fabricado, então
não há mais nada pra reviewer "aceitar por engano". Essa mesma correção
também se aplica a `configure_intake` (é a mesma allowlist,
`scripts/agent_runtime.py`), mas **isso nunca foi confirmado com uma
execução real da fase**, só inferido do código.

## 4. O que isso significa para a decisão da Etapa 4

A proposta (seção 7, etapa 4) pergunta se estende para `intake`,
`diagnostic`, `publish` depois do piloto. Com os dados reais que existem
hoje:

- **`bootstrap_instance` está validado**: custo dentro da faixa
  $0.10–$0.25 documentada, e há evidência real (não hipotética) de que o
  reviewer isolado pega uma classe de falha que o fluxo manual de hoje
  deixaria passar.
- **`configure_intake` não está validado da mesma forma.** Custo: zero dados
  pós-tracking. Qualidade: a única medição existente é *anterior* às
  correções estruturais e mostra exatamente o modo de falha que essas
  correções deveriam prevenir — sem uma execução nova, não dá pra afirmar
  que `configure_intake` está no mesmo nível de confiabilidade que
  `bootstrap_instance` hoje.

Recomendação: **não declarar a Etapa 3 completa até existir pelo menos uma
execução nova de `configure_intake` com o harness atual** (pós-#75, #76,
#77, #78). Sem isso, estender para `intake`/`diagnostic`/`publish` (Etapa 4)
herdaria a mesma lacuna sem ninguém perceber — exatamente o tipo de "escolha
silenciosa" que a seção 4 da proposta original quis evitar para troca de
modelo, e que vale igualmente para "harness nunca validado numa fase
específica".

## 5. O que não fiz agora, e por quê

Não disparei um novo `workflow_dispatch` de `configure_intake` contra o
repo de teste para fechar a lacuna da seção 2/3.2. O workflow chama a API
real da Anthropic (custo estimado $0.10–$0.25 pelo padrão de
`bootstrap_instance`, mas configure_intake é uma instrução menor, então
pode ser mais barato — não sei até rodar) usando o secret já configurado
nesse repo. Isso é uma ação com efeito colateral real e custo monetário na
sua conta, não uma leitura — por isso não executei sem confirmar com você
primeiro.
