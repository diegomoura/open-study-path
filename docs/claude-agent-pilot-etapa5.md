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
