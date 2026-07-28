---
version: 1
status: proposed
generated_at: null
source_of_truth: github
---

# Ferramentas que podem ajudar nesta trilha

Este plano mostra somente ferramentas que têm uma utilidade concreta para o curso. Tudo continua funcionando com os materiais do GitHub quando uma ferramenta opcional não é conectada.

## Visão rápida

| Para quê | Ferramenta | Por que pode ajudar | É necessária? | Alternativa |
| --- | --- | --- | --- | --- |
| Acompanhar as etapas | substituir | substituir | sim/não | substituir |
| Praticar flashcards | substituir | substituir | não | flashcards no GitHub |
| Reservar tempo | substituir | substituir | não | projeção semanal e agenda manual |
| Receber lembretes | substituir | substituir | não | chat |

Não mostre nesta tabela termos internos como `selected`, `optional_probe`, `required_for_selected_publication`, `not_enabled`, `authority` ou `sync_status`.

## Como cada ferramenta será usada

Crie uma seção somente para cada ferramenta selecionada ou recomendada. Não liste serviços irrelevantes apenas porque estão disponíveis.

### <Ferramenta> — <benefício principal>

- **Por que faz sentido para você:** use sinais concretos do objetivo, diagnóstico, duração, rotina ou formato de aprendizagem.
- **Como será usada:** descreva a operação real nesta trilha.
- **Quando entra em cena:** diga em que momento a pessoa verá valor.
- **O que será compartilhado:** liste apenas os dados mínimos em linguagem simples.
- **Sem esta ferramenta:** explique a alternativa que já funciona.
- **Acesso:** informe se é público, exige conta ou pode ter limitações de plano.

Para Quizlet, use linguagem equivalente a:

> Os tópicos prontos contêm conceitos que funcionam bem como flashcards. Ao conectar o Quizlet, serão criados conjuntos interativos. Sem conexão, os mesmos cartões continuam disponíveis no GitHub.

Quando a conexão for útil agora e ainda não estiver disponível, a resposta de chat pode apresentar o controle de conexão. Não escreva um pedido técnico longo e não bloqueie o uso da alternativa local.

## Ferramentas que não foram escolhidas

Não crie uma lista extensa de recusas. Resuma apenas decisões que poderiam gerar dúvida:

> Não incluímos uma ferramenta adicional de hábitos porque o plano já possui tarefas e revisões suficientes. Essa decisão pode ser revista depois.

## Detalhes operacionais

<details>
<summary>Ver contrato técnico de integrações</summary>

Esta seção existe para o agente, revisão e auditoria. Ela não deve dominar a experiência de quem estuda.

Para cada capacidade, registre:

- provider;
- decision: `selected`, `recommended`, `declined` ou `unavailable`;
- preflight: `required_for_selected_publication`, `optional_probe` ou `not_enabled`;
- authority boundary;
- provider-independent fallback;
- minimum data;
- connection-offer eligibility;
- return command when applicable.

GitHub permanece responsável por currículo, conteúdo, avaliação e progresso verificado. Apenas um backend de tarefas mantém o estado de execução. Todoist pode ser principal ou lembrete auxiliar, nunca um segundo estado concorrente. Mermaid permanece a representação visual versionada. Airtable, quando usado, é uma projeção `github_to_airtable`.

Uma oferta de conexão exige clique explícito. Exibir o controle não comprova autorização e não permite escritas externas por si só. Provedores recusados, evitados, proibidos, irrelevantes ou já conectados não devem ser sugeridos.

Para Quizlet, a oferta é elegível somente quando existe ao menos um deck Markdown/TSV aprovado. O comando natural é:

`Conectei o Quizlet. Crie meus flashcards.`

O alias técnico continua aceito:

`Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.`

Quando o conector cria, mas não edita conjuntos, use uma nova versão após mudança de conteúdo e preserve o registro anterior como `superseded`.

</details>

## Regras por tipo de recurso

### Pesquisa e fontes

Use Consensus para apoiar pesquisas empíricas quando fizer sentido, mas registre sempre a fonte original no módulo. Para tecnologia, produtos, APIs e padrões, prefira documentação oficial e fontes primárias. Siga `docs/content-quality-and-sources.md`.

### Flashcards

Use Quizlet quando houver material útil para recuperação ativa. Mantenha sempre os decks Markdown e TSV. Pontuação formativa não conclui uma etapa.

### Tarefas

Trello é adequado para trilhas com várias etapas, links e checklists. Todoist pode ser mais simples. O cartão deve falar com a pessoa, não reproduzir estado técnico.

### Agenda e lembretes

Use Reclaim quando a rotina varia; Google ou Outlook Calendar para blocos fixos. Nenhuma presença em calendário comprova aprendizagem.

### Vídeos, cursos e outras formas de aprender

YouTube, aulas universitárias, Coursera, edX, Udemy, Khan Academy e outros catálogos podem complementar o módulo. Selecione a aula, seção, exercício ou timestamp exato, explique por que ajuda e ofereça alternativa gratuita quando houver custo potencial.

### Entregáveis e visualizações

Google Drive ou outro workspace pode guardar entregáveis. Mermaid continua suficiente para compreender o conteúdo. Ferramentas externas não devem ser a única representação necessária.

## Estado e idempotência

Registre recursos externos com identificador seguro, URL, tópico, versão, limite de autoridade e estado de sincronização em `state/integrations.json`. Não armazene tokens, credenciais, submissões brutas ou detalhes OAuth.
