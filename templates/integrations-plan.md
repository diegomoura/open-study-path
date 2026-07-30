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
| Acompanhar as etapas | substituir | substituir | sim/não | GitHub Issues ou roadmap no repositório |
| Praticar flashcards | substituir | substituir | não | flashcards no GitHub |
| Reservar tempo | substituir | substituir | não | agenda manual ou nenhuma agenda |
| Receber resumos | substituir | substituir | não | chat |

Não mostre nesta tabela termos internos como `selected`, `optional_probe`, `required_for_selected_publication`, `not_enabled`, `authority` ou `sync_status`.

## Preferência de conexão

Explique em linguagem simples se a pessoa aceita sugestões contextuais de conexão ou prefere permanecer sem outras contas.

Quando `integration_preferences.account_connections` for `no_external_accounts`, registre no bloco técnico:

`account_connections: no_external_accounts`

Nesse modo, não selecione nem recomende provedores que exigem outra conta, não torne ofertas de conexão elegíveis e use GitHub Issues ou Markdown do repositório, flashcards locais, Mermaid, arquivos do GitHub, fontes primárias/web e chat.

## Como cada ferramenta será usada

Crie uma seção para cada ferramenta selecionada ou recomendada. Uma preferência explícita do formulário nunca pode desaparecer nem ser movida para “Ferramentas que não foram escolhidas”. Quando ainda faltar uma decisão operacional, mantenha a ferramenta como selecionada e explique claramente o que falta configurar.

### <Ferramenta> — <benefício principal>

- **Por que faz sentido para você:** use sinais concretos do objetivo, diagnóstico, restrições de tempo ou formato de aprendizagem.
- **Como será usada:** descreva a operação real nesta trilha.
- **Quando entra em cena:** diga em que momento a pessoa verá valor.
- **O que será compartilhado:** liste apenas os dados mínimos em linguagem simples.
- **Sem esta ferramenta:** explique a alternativa que já funciona.
- **Acesso:** informe se é público, exige conta ou pode ter limitações de plano.

Para Quizlet, use linguagem equivalente a:

> Os tópicos prontos contêm conceitos que funcionam bem como flashcards. Ao conectar o Quizlet, serão criados conjuntos interativos. Sem conexão, os mesmos cartões continuam disponíveis no GitHub.

Quando a conexão for útil agora, estiver permitida e ainda não estiver disponível, a resposta de chat deve apresentar o controle de conexão ou registrar honestamente que ele está indisponível. Não escreva um pedido técnico longo e não bloqueie o uso da alternativa local.

Para Gmail ou Outlook selecionado, use linguagem equivalente a:

> Você escolheu receber resumos por e-mail. Antes de ativar os envios, será definida uma política simples: somente quando solicitado, após cada avaliação, semanalmente ou mensalmente. A escolha do provedor não pode ser descartada por falta dessa frequência.

## Ferramentas que não foram escolhidas

Não crie uma lista extensa de recusas. Resuma apenas decisões que poderiam gerar dúvida. Nunca inclua aqui um provedor explicitamente selecionado no formulário ou em `study.config.yml`.

> Não incluímos uma ferramenta adicional de hábitos porque o plano já possui tarefas e revisões suficientes. Essa decisão pode ser revista depois.

## Detalhes operacionais

<details>
<summary>Ver contrato técnico de integrações</summary>

Esta seção existe para o agente, revisão e auditoria. Ela não deve dominar a experiência de quem estuda.

Registre primeiro:

- account_connections: `ask_per_provider` ou `no_external_accounts`;
- task fallback order: `trello`, `github_issues`, `markdown`, ajustado pela preferência da pessoa;
- integration constraints preservadas do intake.

Para cada capacidade selecionada ou recomendada, registre:

- provider;
- decision: `selected`, `recommended`, `declined` ou `unavailable`;
- preflight: `required_for_selected_publication`, `optional_probe` ou `not_enabled`;
- authority boundary;
- provider-independent fallback;
- minimum data;
- connection-offer eligibility;
- return command when applicable;
- required configuration still missing, when applicable;
- expected terminal disposition in `state/integrations.json`.

GitHub permanece responsável por currículo, conteúdo, avaliação e progresso verificado. Apenas um backend de tarefas mantém o estado de execução. Todoist pode ser principal ou lembrete auxiliar, nunca um segundo estado concorrente. Mermaid permanece a representação visual versionada. Airtable, quando usado, é uma projeção `github_to_airtable`.

Uma oferta de conexão exige clique explícito. Exibir o controle não comprova autorização e não permite escritas externas por si só. Provedores recusados, restringidos, irrelevantes, já conectados ou proibidos por `no_external_accounts` não devem ser sugeridos.

Para Quizlet, a oferta é elegível somente quando existe ao menos um deck Markdown/TSV aprovado e conexões externas estão permitidas. O comando natural é:

`Conectei o Quizlet. Crie meus flashcards.`

Quando o conector cria, mas não edita conjuntos, use uma nova versão após mudança de conteúdo e preserve o registro anterior como `superseded`.

Para notificações por e-mail selecionadas, registre:

- provider: `gmail` ou `outlook_email`;
- decision: `selected`;
- preflight: `optional_probe`;
- delivery policy quando definida;
- `pending_configuration` quando a frequência ainda não foi escolhida;
- alternativa em chat quando o provedor estiver indisponível.

</details>

## Regras por tipo de recurso

### Pesquisa e fontes

Use Consensus para apoiar pesquisas empíricas quando fizer sentido, mas registre sempre a fonte original no módulo. Para tecnologia, produtos, APIs e padrões, prefira documentação oficial e fontes primárias. Siga `docs/content-quality-and-sources.md`.

### Flashcards

Use Quizlet quando houver material útil para recuperação ativa e conexões estiverem permitidas. Mantenha sempre os decks Markdown e TSV. Pontuação formativa não conclui uma etapa. Quando houver decks aprovados e o Quizlet não estiver conectado, a publicação deve apresentar a oferta uma vez ou registrar `unavailable`; não use estados inventados como adiamento implícito.

### Tarefas

Trello é adequado para trilhas com várias etapas, links e checklists. GitHub Issues é o primeiro fallback operacional. Todoist pode ser mais simples. Markdown do repositório é o último fallback interno quando não deve haver outro backend. O cartão ou registro deve falar com a pessoa, não reproduzir estado técnico.

### Agenda e lembretes

Use Reclaim quando a rotina varia; Google ou Outlook Calendar para blocos fixos. Nenhuma presença em calendário comprova aprendizagem. Colete detalhes mínimos somente quando a ativação for realmente solicitada.

### Resumos por e-mail

Gmail e Outlook só enviam resumos configurados. A seleção do provedor deve permanecer visível no plano e no estado. Sem política de entrega, marque a capacidade como `pending_configuration`; não conclua a publicação como se a escolha não existisse.

### Vídeos, cursos e outras formas de aprender

YouTube, aulas universitárias, Coursera, edX, Udemy, Khan Academy e outros catálogos podem complementar o módulo. Selecione a aula, seção, exercício ou timestamp exato, explique por que ajuda e ofereça alternativa gratuita quando houver custo potencial.

### Entregáveis e visualizações

Google Drive ou outro workspace pode guardar entregáveis. Mermaid continua suficiente para compreender o conteúdo. Ferramentas externas não devem ser a única representação necessária.

## Estado e idempotência

Registre recursos externos com identificador seguro, URL, tópico, versão, limite de autoridade e estado de sincronização em `state/integrations.json`. Não armazene tokens, credenciais, submissões brutas ou detalhes OAuth.

Cada capacidade esperada deve ter `resolution_status: resolved` ou `action_required`. O bloco superior `resolution` deve listar exatamente as capacidades pendentes. `sync.status: success` é inválido enquanto houver uma escolha selecionada sem desfecho.
