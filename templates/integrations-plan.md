---
version: 1
status: proposed
generated_at: null
source_of_truth: github
---

# Plano de integrações da trilha

Este plano é gerado depois do intake e do diagnóstico. Ele recomenda somente capacidades úteis para a trilha aprovada. Nenhuma integração opcional bloqueia geração, estudo, avaliação, recuperação ou progresso.

## Princípios invariáveis

- GitHub é a única fonte de verdade para currículo, conteúdo, avaliações, domínio e progresso verificado.
- Apenas um backend de tarefas mantém o estado operacional autoritativo.
- Todoist pode funcionar como backend principal ou como lembrete auxiliar, nunca como segundo estado concorrente.
- Mermaid é a representação visual canônica. Ferramentas externas apenas complementam.
- Airtable é uma projeção analítica unidirecional derivada do GitHub.
- Checklist, hábito, sessão ou pontuação formativa não comprovam domínio.
- Recursos pagos nunca são obrigatórios sem alternativa gratuita.
- Uma integração opcional indisponível usa o fallback e não bloqueia a fase.

## Resumo recomendado

| Capacidade | Provedor recomendado | Estado | Obrigatório | Motivo resumido | Fallback |
| --- | --- | --- | --- | --- | --- |
| Fonte de verdade | GitHub | selecionado | sim | conteúdo e evidência duráveis | nenhum |
| Pesquisa acadêmica | substituir | recomendado/dispensado | não | substituir | fontes primárias e web |
| Prática formativa | substituir | recomendado/dispensado | não | substituir | flashcards em Markdown/TSV |
| Tarefas | substituir | recomendado | não | substituir | Markdown |
| Lembretes | substituir | recomendado/dispensado | não | substituir | calendário ou chat |
| Agenda | substituir | recomendado/dispensado | não | substituir | calendário fixo ou nenhum |
| Hábitos | substituir | recomendado/dispensado | não | substituir | acompanhamento manual |
| Diagramas externos | substituir | recomendado/dispensado | não | substituir | Mermaid |
| Entregáveis | substituir | recomendado/dispensado | não | substituir | arquivos no GitHub |
| Analytics | substituir | recomendado/dispensado | não | substituir | `state/progress.json` |
| Descoberta de cursos | substituir | recomendado/dispensado | não | substituir | fontes públicas/oficiais |

## Cartões explicativos

Crie um cartão para cada capacidade recomendada ou explicitamente solicitada. Não liste ferramentas irrelevantes apenas porque estão disponíveis.

### <Capacidade> — <Provedor>

- **O que é:** descrição simples para alguém que não conhece a ferramenta.
- **Por que foi recomendado:** sinais concretos do objetivo, diagnóstico, formato, duração ou tipo de conteúdo.
- **Como será usado:** operações específicas dentro desta trilha.
- **Quando será ativado:** fase ou condição objetiva.
- **Acesso e custo:** plano gratuito esperado, limitações conhecidas e proibição de exigir recurso pago.
- **Dados utilizados:** tipos mínimos de dados enviados ou lidos; nunca credenciais ou submissões brutas desnecessárias.
- **Autoridade:** o que a ferramenta pode registrar e o que não pode decidir.
- **Fallback:** caminho sem esse provedor.
- **Preflight:** `required_for_selected_publication`, `optional_probe` ou `not_enabled`.
- **Decisão:** `selected`, `recommended`, `declined` ou `unavailable`.

## Regras por capacidade

### Pesquisa acadêmica

Prefira Consensus quando o módulo contém afirmações empíricas, ciência, saúde, psicologia, educação ou comparação de evidências. Para programação, nuvem e produtos, fontes oficiais e documentação primária geralmente têm prioridade. Registre referências verificáveis no módulo; o provedor de pesquisa não altera o currículo aprovado.

### Prática formativa

Prefira Quizlet para definições, termos, comandos, fórmulas, classificações, comparações e erros comuns. Ace Quiz Maker pode oferecer checagem rápida. Gere fallback durável em `study/flashcards/` quando flashcards forem pedagogicamente úteis. Resultados formativos nunca determinam domínio.

### Tarefas e lembretes

Prefira Trello para trilhas ricas com módulos, links, checklists, recuperação e visão do roadmap. Considere Todoist como backend principal em trilhas simples ou como lembrete recorrente auxiliar. Quando auxiliar, um item concluído no Todoist não conclui o cartão ou tópico principal.

### Agenda

Prefira Reclaim quando a disponibilidade varia e a pessoa deseja proteção e reagendamento de foco. Use Google Calendar ou Outlook Calendar para blocos fixos. Respeite `free_tier_only`; não presuma capacidades pagas.

### Hábitos

Use Habitify somente para consistência, normalmente com no máximo três hábitos: sessão de estudo, recuperação ativa e revisão espaçada. Hábito realizado não equivale a conteúdo dominado.

### Visualização externa

Mermaid sempre existe no repositório. Considere Whimsical para mapas editáveis, colaboração ou exploração espacial. Mantenha uma representação Mermaid equivalente ou simplificada e registre a versão do conteúdo sincronizada.

### Entregáveis

Considere Google Drive para Docs, Sheets e Slides. Notion, SharePoint ou Dropbox podem ser alternativas conforme o ambiente. O link do artefato é evidência; o conteúdo aprovado e o resultado da avaliação permanecem no GitHub.

### Analytics

Airtable pode receber cursos, tópicos, tentativas, sessões e recursos externos para dashboards. A sincronização é `github_to_airtable`. Airtable não promove domínio, não reescreve pontuações e não substitui arquivos de estado do repositório.

### Descoberta de cursos

Coursera, edX, Udemy e Khan Academy são fontes de recursos. Selecione capítulos, aulas ou exercícios específicos, com objetivo, estimativa e evidência. Nunca transforme um curso inteiro em uma tarefa vaga. Recursos pagos exigem alternativa gratuita ou oficial.

## Estado e idempotência

Cada recurso externo persistido em `state/integrations.json` deve registrar:

- `capability`;
- `provider`;
- `external_type`;
- `external_id` seguro;
- `external_url`;
- `topic_id` quando aplicável;
- `content_version`;
- `authority`;
- `sync_status`;
- `last_sync_at`.

Antes de criar, procure o identificador salvo e um recurso exato no provedor. Reutilize ou atualize; não duplique.
