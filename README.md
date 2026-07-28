# Open Study Path

Template open source para criar trilhas de estudo personalizadas com ChatGPT e GitHub.

> Este repositório é o template. Cada pessoa cria um repositório próprio a partir dele para guardar sua trilha, aulas, avaliações e progresso.

## O que a experiência entrega

Uma trilha possui:

- um mapa completo do caminho de aprendizagem;
- etapas pequenas, com objetivo e tempo sugerido;
- aulas autocontidas com explicações, exemplos, prática e diagramas;
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
2. Crie um Projeto dedicado no ChatGPT.
3. Conecte o GitHub e autorize o repositório da trilha.
4. Copie `templates/chatgpt-project-instructions.md` para as Instruções do Projeto.
5. Substitua `OWNER/REPOSITORY` pelo identificador exato.
6. Abra o primeiro chat e envie:

```text
Configure este repositório como uma nova trilha de estudos usando o formulário do GitHub.
```

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

## Ciclo de aprendizagem

```mermaid
flowchart LR
    I[Conte o que quer aprender] --> D[Diagnóstico curto]
    D --> R[Trilha personalizada]
    R --> A[Aulas prontas]
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
- `study/flashcards/` — prática local em Markdown e TSV;
- `study/assessments/` — rubricas;
- `.github/ISSUE_TEMPLATE/` — formulários de entrada e avaliação;
- `study/integrations.md` — ferramentas que podem ajudar;
- `state/` — registros técnicos de progresso e integrações.

## Aprendizagem visual

O roadmap mostra as dependências reais em Mermaid. Cada aula pronta possui ao menos um diagrama útil e explicado. Diagramas podem representar decisões, sequências, estados, relações, arquitetura, dados ou cronologia.

Veja `docs/mermaid-visual-learning.md`.

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
- as fontes são verificadas e explicadas;
- exemplos e atividades são personalizados sem expor dados desnecessários;
- ferramentas opcionais nunca bloqueiam o caminho principal;
- conteúdo e avaliações ficam versionados no GitHub;
- detalhes técnicos ficam disponíveis sem ocupar a conversa principal;
- nenhuma credencial ou submissão bruta é versionada.
