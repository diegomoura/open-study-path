# Agent pilot: Etapa 5a — extensão para `generate_proposal`

Status: **design implementado, testado offline, aguardando validação
real.** Primeira fatia da Etapa 5 (proposta, seção 7, passo 5: "estender
para `generate` — currículo, conteúdo, slides — a parte mais cara e mais
sensível a qualidade").

## 1. Por que fatiar `generate` em duas suboperações

`instructions/manifest.yml`'s fase `generate` já se divide em duas
suboperações reais, com `completion_check_sets` distintos:

- `proposal` (`instructions/28-propose-path.md`): só `study/roadmap.md` --
  o grafo de tópicos, pré-requisitos, esforço. Nenhum conteúdo detalhado.
- `detailed_generation` (`instructions/30-generate-path.md`): materializa,
  por tópico, contrato, módulo completo (18 elementos obrigatórios),
  rubrica, GitHub Issue Form e **um deck de slides renderizado de verdade**
  (Mermaid → SVG → HTML → PDF via `scripts/render_study_slides.mjs`, que é
  Node.js, não Python).

Essa segunda parte tem uma dependência de infraestrutura que as fases
anteriores nunca precisaram (Node.js/npm no runner do Actions, renderização
de PDF) e um volume de conteúdo pedagógico real por tópico que não é
redutível a um motor determinístico como aconteceu com `publish`. Por isso
esta etapa cobre só `proposal` -- a fatia menor, comparável em tamanho a
`intake`, que usa só Opus para uma decisão estrutural sem tocar
infraestrutura nova.

## 2. Por que isso não é "reaproveitar um motor" como `publish`

Os scripts já existentes relacionados a currículo/conteúdo/slides
(`scripts/curriculum_state.py`, `scripts/course_content_review.py`,
`scripts/study_slides.py`, os `validate_*.py`, ~2170 linhas ao todo) são
**validadores**, não geradores -- eles checam se o que o modelo escreveu
está estruturalmente correto (schema, cobertura de outcome, ciclos no grafo
de pré-requisitos), mas não escrevem o roadmap nem a aula. Isso é trabalho
de julgamento pedagógico real, que só o modelo pode fazer.

Uma vantagem prática, porém: esses validadores **já rodam automaticamente
no CI existente do repositório**, independente do workflow deste piloto --
o mesmo CI que já valida currículo hoje para o fluxo manual (ChatGPT
Project) roda em qualquer push, inclusive nos branches que este harness cria.
Não foi necessário construir nenhuma verificação nova para esta etapa.

## 3. O que foi implementado

Como `generate_proposal` só escreve arquivos de repositório (nenhuma
integração com GitHub Issues, nenhum tool novo), a extensão foi puramente
de configuração -- o mesmo formato de `bootstrap_instance`/
`configure_intake`, não o de `intake`/`publish`:

- **Allowlist** (`agent_runtime.py`): `study/roadmap.md`,
  `.open-study-path/instance.yml` -- direto da seção "Outputs" de
  `instructions/28-propose-path.md`. Nenhum outro caminho (`study/topics/`,
  `study/modules/`, `study/slides/`, `study/assessments/`,
  `.github/ISSUE_TEMPLATE/assessment-topic-*.yml`) é aceito -- esses
  pertencem à suboperação `detailed_generation`, que não existe neste
  harness ainda.
- **Agente**: `curriculum_architect` (author) / `curriculum_reviewer`
  (reviewer), ambos já cadastrados em `AGENT_CATALOG` como tier `opus`
  (`claude-opus-4-8`). O campo `phase` de `AGENT_CATALOG` para esses ids é a
  string `"generate"` (igual ao `manifest.yml`, que não separa `proposal`/
  `detailed_generation` em ids distintos) -- isso é só descritivo;
  `resolve_effective_models()` busca por id de agente, nunca pela chave de
  fase do harness, então usar uma chave própria (`generate_proposal`)
  aqui não quebra a resolução de modelo.
- **Review profile**: `curriculum` (`docs/review-framework.md`), com 7
  checks obrigatórios. Dois deles (`content_review_complete`,
  `assessment_alignment`) são sobre conteúdo materializado, que esta
  suboperação nunca cria -- o prompt do reviewer instrui explicitamente a
  marcá-los `passed` com uma nota de que não há conteúdo materializado no
  escopo desta operação, em vez de deixá-los `pending` (o que pareceria
  revisão incompleta) ou inventar achados que não se aplicam.
- **Nota de escopo no prompt do author**: como
  `instructions/30-generate-path.md` (a suboperação de materialização) está
  na mesma pasta `instructions/` e é facilmente alcançável por leitura, o
  prompt reforça explicitamente que só `study/roadmap.md` e
  `.open-study-path/instance.yml` podem ser escritos nesta execução -- o
  `write_file` recusa qualquer outro caminho independente do que o modelo
  tentar, mas a instrução deixa isso explícito também no prompt.

## 4. Testes offline

`scripts/test_agent_runtime.py` ganhou 2 casos novos (27 no total):
allowlist bate exatamente com a seção "Outputs" da instrução (incluindo a
confirmação de que os caminhos de `detailed_generation` são recusados), e a
fase não ganha nenhum tool de GitHub Issues (mesmo shape de tools que
`bootstrap_instance`/`configure_intake`).

## 5. O que falta para "validado"

Nenhum dispatch real ainda. Diferente de `intake`/`publish`, esta
suboperação não teve nenhuma dependência anterior faltando (não precisa de
fixture sintética -- `study.config.yml`/`state/intake-summary.json`/
`state/diagnostic-summary.json` já existem no repositório de teste de
rodadas anteriores, ou podem ser criados de forma mínima e realista antes
do dispatch). Fica pendente: rodar de verdade, conferir o roadmap gerado
contra os critérios de "Proposal quality" de `instructions/28-propose-
path.md`, e confirmar que o CI existente do repositório (não construído por
este piloto) valida a estrutura do currículo corretamente.

## 6. Validação real (dispatch único, fechada)

Status: **fechada.** Um dispatch real contra o repositório de teste
descartável.

### 6.1 Estado de entrada precisou ser reconstruído

Nenhuma PR anterior do repositório de teste tinha sido mergeada (todas
`bootstrap_instance`/`configure_intake`/`intake` ficaram como PR aberta,
por desenho -- o workflow nunca faz merge automático). `main` nunca teve
estado real. Além disso, **o `instance.yml` que essas PRs antigas
produziram não batia com o template canônico**
(`templates/instance.yml`): usavam `curriculum_status.diagnostic_status`
em vez de `status.diagnostic_complete`, sem os blocos `review_framework`/
`content_generation`/`study_slides` inteiros. Confirmado com
`scripts/curriculum_state.py`, que lê exatamente `status.curriculum_*` --
por isso o fixture desta validação foi reconstruído do template canônico
do zero, não copiado das PRs antigas. Como nenhuma delas foi mergeada,
não há inconsistência real em nenhum `main`, só nos branches de teste
descartados.

Fixture final commitado direto em `main` do repo de teste: `instance.yml`
no formato canônico, `study.config.yml`/`state/intake-summary.json`
reaproveitados do conteúdo real já validado na Etapa 4 (PR #8),
`state/diagnostic-summary.json` sintético, validado contra
`schemas/diagnostic-summary.schema.json`, claramente rotulado como
fixture no próprio campo `learner_context.notes` (diagnostic nunca foi
implementado neste harness).

### 6.2 Achado real: bug na tabela de preços, corrigido nesta mesma etapa

`state/agent-pilot-usage.jsonl` voltou com `estimated_cost_usd: null` para
author e reviewer. Causa raiz: `MODEL_PRICING_USD_PER_MTOK` em
`agent_runtime.py` tinha a chave `"claude-opus-5"`, mas
`agent_model_resolution.MODEL_CATALOG` resolve o tier `opus` para
`"claude-opus-4-8"` -- um mismatch silencioso de string que fazia todo
run em tier Opus reportar custo `null` em vez de errar alto. Verifiquei a
tarifa real (`$5/$25/$6.25/$0.50` por MTok, já confirmada por múltiplas
fontes independentes de pricing de Opus 4.8) -- os *valores* já estavam
certos, só a *chave* estava errada. Corrigido, e um teste de regressão
novo (`test_pricing_table_covers_every_resolvable_model`) garante que
todo modelo resolvível em `MODEL_CATALOG` tem entrada correspondente na
tabela de preço -- esse bug não pode mais passar despercebido para um
tier novo no futuro.

Custo real recomputado com a tabela corrigida: **$1.9829** (author
$1.6462 + reviewer $0.3367), 689.423 tokens combinados. Consideravelmente
mais caro que qualquer fase em Haiku, como esperado para Opus.

### 6.3 Resultado da geração

Roadmap real gerado para "Aprender Go do zero" (7 aulas, grafo com dois
ramos paralelos -- concorrência e testes -- convergindo no serviço HTTP
final), personalizado de forma consistente com o fixture de diagnóstico
(trata experiência em Python/JS como acelerador de sintaxe, mas tipagem
estática/concorrência como genuinamente novas, batendo exatamente com
`material_caveats`/`knowledge_gaps` do fixture). Vocabulário técnico
explicado na primeira ocorrência, sem terminologia interna vazando pro
texto do aluno, esforço total honesto (~8-9h) sem prazo forçado.

`instance.yml` atualizado corretamente: `curriculum_proposed: true`,
`curriculum_approved: true`, `curriculum_generated: false`, todo o resto
do estado preservado.

Reviewer isolado: `status: approved`, todos os 7 checks do profile
`curriculum` `passed` -- incluindo os dois sobre conteúdo materializado
(`content_review_complete`, `assessment_alignment`), corretamente
marcados `passed` com nota de escopo em vez de `pending`, exatamente como
o prompt instruiu. Os 2 hashes registrados no artefato de revisão
conferidos na mão, batem exatamente.

Nenhum achado negativo desta vez -- diferente de `intake`/`publish`, este
dispatch não revelou nenhum comportamento incorreto do harness, só o bug
pré-existente da tabela de preços (não relacionado à lógica de
`generate_proposal` em si).
