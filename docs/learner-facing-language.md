# Linguagem voltada para quem estuda

Este contrato separa a experiência humana da operação técnica. Pull requests, CI, branches, hashes, estados internos e classificações de integração continuam existindo para segurança e auditoria, mas não devem dominar a conversa com quem está criando ou seguindo uma trilha.

## Três vozes diferentes

1. **Voz da pessoa:** objetivos, preferências, respostas, dúvidas e decisões.
2. **Voz da experiência de estudo:** explica o que está pronto, por que importa e o que fazer agora.
3. **Voz técnica:** registra PR, validação, merge, IDs externos, sincronização e detalhes de diagnóstico.

A voz técnica fica no GitHub, nos arquivos de estado ou em uma seção técnica solicitada. A resposta principal usa a voz da experiência de estudo.

## Quatro perguntas da resposta principal

Uma resposta de fase bem-sucedida deve responder somente ao que for útil agora:

1. **O que ficou pronto?**
2. **Onde encontro o que preciso?**
3. **Qual é o próximo passo?**
4. **Existe algo que realmente exige minha atenção?**

Se uma informação não ajuda a responder uma dessas perguntas, ela normalmente não pertence à resposta principal.

## Uma interface não é um inventário

Trello, Todoist, GitHub Issues ou outra ferramenta de tarefas devem funcionar como uma porta de entrada curta para o estudo, não como uma listagem de todos os arquivos produzidos pelo sistema.

Para cada capacidade, mostre um único recurso principal:

- uma aula;
- uma prática disponível agora;
- uma avaliação.

Quando uma integração externa foi criada com sucesso, ela é o recurso principal daquela capacidade no cartão. Exemplo: se o conjunto do Quizlet existe, o cartão mostra **Praticar no Quizlet** e não repete o deck Markdown e o TSV.

As alternativas locais continuam dentro da aula e do repositório. Elas aparecem no cartão somente quando a integração principal está indisponível, quando importação é a ação desejada ou quando a pessoa pede alternativas.

Não use como navegação principal:

- contratos internos em `study/topics/`;
- rubricas YAML em `study/assessments/`;
- arquivos de estado;
- índices de sincronização;
- nomes de formulários sem link direto.

Resuma no próprio cartão o objetivo, o tempo, o entregável e os critérios de conclusão que a pessoa realmente precisa conhecer.

## A aula começa pela aprendizagem

Arquivos em `study/modules/` são páginas destinadas à pessoa que estuda. Eles devem começar pelo título e pela orientação da aula, sem uma tabela de frontmatter YAML com `topic_id`, versão, duração, contagem de diagramas ou caminhos de arquivos.

Esses metadados permanecem no contrato interno correspondente em `study/topics/`, onde podem ser usados por geração, validação, avaliação e integrações. Comentários HTML ocultos podem orientar o agente, mas não devem criar ruído visível na página.

A regra é simples:

- **contrato da etapa:** identidade e operação;
- **aula:** ensino e prática;
- **cartão:** próximo passo.

## O que não deve aparecer por padrão após sucesso

Não destaque:

- número ou estado do PR;
- hash de commit ou merge;
- nome de branch;
- quantidade de commits, arquivos, adições ou exclusões;
- nomes de jobs, validadores ou logs do CI;
- frases como “aprovado pelo agente e pelo CI”;
- `materialized`, `planned`, `adaptive_rolling_window`, `optional_probe`, `required_for_selected_publication` ou `source_of_truth`;
- detalhes de idempotência e sincronização;
- explicações sobre como a issue foi localizada;
- links para contratos internos ou rubricas detalhadas quando um resumo no cartão é suficiente.

Esses dados continuam disponíveis quando a pessoa pede detalhes técnicos, quando uma decisão está bloqueada ou quando uma falha precisa de ação.

## Tradução de termos internos

| Termo interno | Linguagem para a pessoa |
| --- | --- |
| materialized | aula pronta |
| planned | aula futura |
| active rolling window | próximas aulas que já estão sendo preparadas |
| mastery | conclusão comprovada pela avaliação |
| authoritative backend | ferramenta principal de acompanhamento |
| fallback | alternativa disponível |
| preflight | verificação de conexão |
| provider unavailable | ferramenta não conectada ou indisponível |
| synchronization | atualização dos links e tarefas |

Use o título da aula em vez do ID sempre que o ID não for necessário para localizar um recurso.

## Comandos naturais

O agente deve aceitar comandos técnicos antigos por compatibilidade, mas apresentar comandos naturais por padrão:

- `Preenchi o formulário. Pode continuar.`
- `Vamos fazer meu diagnóstico.`
- `Crie minha trilha de estudos.`
- `Organize minha trilha nas ferramentas que escolhemos.`
- `Conectei o Quizlet. Crie meus flashcards.`
- `Terminei <título da aula>. Avalie minhas respostas.`
- `Terminei a revisão de <título da aula>.`

O agente resolve internamente repositório, issue, tópico, fase, validações e artefatos necessários.

## Respostas de sucesso

Exemplo:

> **Sua trilha está pronta.**
>
> As duas primeiras aulas já estão disponíveis. Comece por **Agência sem garantia**.
>
> [Abrir a primeira aula]
>
> Quando terminar, envie a avaliação e escreva: **“Terminei Agência sem garantia. Avalie minhas respostas.”**

## Quando mostrar detalhes técnicos

Mostre detalhes técnicos somente quando:

- a pessoa pedir;
- houver mais de uma opção que precise ser escolhida;
- uma validação falhar e a pessoa puder agir;
- uma conexão obrigatória estiver ausente;
- uma decisão pedagógica ou de privacidade estiver pendente;
- for necessário apontar um PR específico para comentários.

Mesmo nesses casos, comece pelo impacto humano e coloque o detalhe técnico depois.

## Tom

- fale diretamente com “você”;
- prefira verbos de ação concretos;
- evite linguagem de marketing e elogios automáticos;
- não repita avisos técnicos em toda aula;
- explique limites apenas no ponto em que eles ajudam uma decisão;
- personalize exemplos, motivos e próximos passos a partir do intake e do diagnóstico;
- não exponha dados pessoais desnecessários para parecer mais pessoal.