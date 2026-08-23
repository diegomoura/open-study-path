# Open Study Path

Template open source para criar trilhas de estudo personalizadas com ChatGPT e GitHub.

> Este repositório é o template. Cada pessoa cria um repositório próprio a partir dele para guardar sua trilha, aulas, avaliações e progresso.

## O que a experiência entrega

Uma trilha possui:

- um mapa completo do caminho de aprendizagem;
- etapas pequenas, com objetivo e tempo sugerido;
- aulas autocontidas com explicações, exemplos, prática e diagramas;
- slides visuais em PDF para revisar cada aula pronta;
- fontes verificáveis e formas alternativas de aprender;
- flashcards quando ajudam;
- avaliações com feedback e revisão focada;
- integração opcional com tarefas, agenda, Quizlet e outras ferramentas.

As próximas aulas podem ser preparadas conforme a pessoa avança. Isso permite adaptar exemplos, fontes e prática a partir das avaliações anteriores.

## Conteúdo com fontes

Cada aula pronta deve mostrar:

- de onde vieram as ideias principais;
- quais partes são síntese ou adaptação pedagógica;
- fontes primárias, oficiais, acadêmicas ou técnicas;
- artigos, livros, papers, TCCs ou dissertações quando pertinentes;
- vídeos, aulas abertas, podcasts, demonstrações ou cursos quando acrescentarem valor;
- capítulo, seção, página, versão, aula, exercício ou timestamp preciso.

Uma resposta de plugin ou um resultado de busca não é uma fonte final. O módulo registra o documento original e explica como ele foi usado. Recursos pagos nunca são o único caminho.

Veja `docs/content-quality-and-sources.md`.

## Revisão independente

Tudo o que uma instância gera ou altera passa por um papel revisor antes de a operação ser considerada concluída.

Há revisores especializados para configuração, intake, diagnóstico, currículo, publicação, avaliação, progresso, replanejamento e migração. A autoria e a revisão acontecem em passes separados, mesmo quando o mesmo runtime executa os dois.

A revisão procura contradições entre o pedido, os artefatos produzidos, o estado persistido e as ferramentas externas. Cada aprovação registra os arquivos exatos revisados e suas versões em `state/reviews/`. Mudanças sem revisão, cobertura parcial, aprovação antiga ou achado bloqueante impedem o merge.

A revisão de aulas continua mais profunda: cada resultado prometido precisa ser realmente ensinado e avaliado, com evidência versionada em `state/content-reviews/`. Depois disso, uma revisão separada verifica se os slides resumem fielmente a aula, cobrem os mesmos resultados e continuam legíveis.

Veja `docs/review-framework.md` e `docs/study-slides.md`.

## Linguagem voltada para quem estuda

O GitHub continua usando PRs, CI e arquivos de estado internamente, mas a conversa principal não precisa parecer um relatório de engenharia.

Depois de uma operação bem-sucedida, a pessoa recebe:

1. o que ficou pronto;
2. o link necessário agora;
3. o próximo passo;
4. uma frase curta para continuar.

Números de PR, hashes, branches, jobs de CI e classificações internas aparecem somente quando solicitados ou quando explicam um bloqueio.

Veja `docs/learner-facing-language.md`.

## Começar uma nova trilha

1. Use este template para criar um repositório próprio.
2. Aguarde a ação **Prepare ChatGPT Project Instructions** concluir. Ela preenche automaticamente o nome exato do novo repositório.
3. Abra `templates/chatgpt-project-instructions.md` no repositório novo e confirme que a linha **Instance** já contém `owner/repositório`.
4. Crie um Projeto dedicado no ChatGPT.
5. Conecte o GitHub e autorize o repositório da trilha.
6. Copie o conteúdo já preparado de `templates/chatgpt-project-instructions.md` para as Instruções do Projeto, sem editar o identificador.
7. Abra o primeiro chat e envie:

```text
Configure este repositório como uma nova trilha de estudos usando o formulário do GitHub.
```

Se o arquivo ainda mostrar `OWNER/REPOSITORY`, execute manualmente a ação **Prepare ChatGPT Project Instructions** na aba Actions. A substituição manual continua disponível apenas como alternativa.

O agente cuida internamente dos arquivos, validações e limites da primeira operação. Ao terminar, ele devolve o link do formulário.

Depois de preencher:

```text
Preenchi o formulário. Pode continuar.
```

Os comandos seguintes também são naturais:

```text
Vamos fazer meu diagnóstico.
Crie minha trilha de estudos.
Organize minha trilha nas ferramentas que escolhemos.
Terminei <título da aula>. Avalie minhas respostas.
```

Comandos técnicos antigos continuam aceitos como aliases, mas não precisam ser ensinados à pessoa.

### Alternativa: pipeline automatizado via GitHub Actions

Existe um segundo caminho, ainda em piloto, pra quem já quer despachar cada fase como uma chamada real à API da Claude em vez de uma conversa manual: adicionar sua própria `ANTHROPIC_API_KEY` como Secret do repositório e rodar a Action **Agent pilot**. Veja `docs/claude-agent-setup.md` para o passo a passo e `docs/claude-agent-pilot.md` para o que já foi validado em cada fase e quais restrições ainda existem. Os dois caminhos podem ser usados na mesma instância; nenhum dos dois é obrigatório.

## Ciclo de aprendizagem

```mermaid
flowchart LR
    I[Conte o que quer aprender] --> D[Diagnóstico curto]
    D --> R[Trilha personalizada]
    R --> A[Aulas e slides prontos]
    A --> P[Prática e avaliação]
    P -->|Concluiu| N[Próximas aulas]
    P -->|Precisa revisar| V[Revisão focada]
    V --> P
    N --> A
```

O mapa completo é criado desde o início. Em trilhas maiores, apenas as primeiras aulas ficam prontas de imediato. As demais são preparadas automaticamente quando os pré-requisitos são concluídos.

## Estrutura da trilha

- `study/roadmap.md` — visão completa e sequência;
- `study/topics/` — visão resumida de cada etapa;
- `study/modules/` — aulas completas;
- `study/slides/` — fontes internas e PDFs dos slides;
- `study/flashcards/` — prática local em Markdown e TSV;
- `study/assessments/` — rubricas;
- `.github/ISSUE_TEMPLATE/` — formulários de entrada e avaliação;
- `study/integrations.md` — ferramentas que podem ajudar;
- `state/reviews/` — revisões independentes das operações;
- `state/content-reviews/` — revisão semântica das aulas materializadas;
- `state/slide-reviews/` — revisão semântica dos slides;
- `state/` — registros técnicos de progresso e integrações.

## Aprendizagem visual

O roadmap mostra as dependências reais em Mermaid. Cada aula pronta possui ao menos um diagrama útil e explicado. Diagramas podem representar decisões, sequências, estados, relações, arquitetura, dados ou cronologia.

Depois da revisão da aula, o template produz uma apresentação resumida em HTML semântico, revisa o conteúdo visual e gera automaticamente um PDF 16:9. O HTML é apenas a base de renderização; a pessoa recebe o PDF na aula e na ferramenta de tarefas.

Veja `docs/mermaid-visual-learning.md` e `docs/study-slides.md`.

## Integrações por necessidade

Ferramentas externas são escolhidas pelo valor que oferecem, não por estarem disponíveis.

| Necessidade | Possível ferramenta | Alternativa local |
| --- | --- | --- |
| Flashcards | Quizlet | Markdown e TSV |
| Tarefas | Trello ou Todoist | GitHub ou Markdown |
| Agenda | Reclaim, Google ou Outlook | projeção semanal |
| Pesquisa acadêmica | Consensus | fontes originais e web |
| Diagramas externos | Whimsical | Mermaid |
| Entregáveis | Google Drive | arquivos do repositório |
| Analytics | Airtable | arquivos de estado |

Só uma ferramenta de tarefas mantém o acompanhamento principal. Flashcards, agenda, hábitos e cursos ajudam, mas não concluem uma etapa.

Os recursos externos são indexados em `state/integrations.json` para evitar duplicações. Veja `docs/integration-capabilities.md`.

## Avaliação

Cada aula pronta possui um formulário com cinco questões e uma rubrica de 100 pontos. A pessoa responde com o próprio raciocínio, recebe feedback e, quando necessário, uma revisão focada.

O comando recomendado usa o título da aula:

```text
Terminei Agência sem garantia. Avalie minhas respostas.
```

O agente localiza a submissão correta sem exigir o número da issue na situação normal.

## Princípios

- a aula ensina; não é uma lista de links;
- os slides resumem a aula aprovada sem criar um segundo conteúdo;
- as fontes são verificadas e explicadas;
- exemplos e atividades são personalizados sem expor dados desnecessários;
- toda operação gerada passa por revisão independente;
- ferramentas opcionais nunca bloqueiam o caminho principal;
- conteúdo, slides e avaliações ficam versionados no GitHub;
- detalhes técnicos ficam disponíveis sem ocupar a conversa principal;
- nenhuma credencial ou submissão bruta é versionada.
