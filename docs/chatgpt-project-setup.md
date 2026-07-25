# Set up a ChatGPT Project for an Open Study Path instance

A ChatGPT Project is the recommended workspace for conversations that manage one Open Study Path repository.

## Why store the repository in Project Instructions

Connecting GitHub gives ChatGPT access to authorized repositories, but the project still needs an explicit repository target. Store the exact `OWNER/REPOSITORY` identifier in the ChatGPT Project Instructions so every chat starts with the same target.

The project name and description are useful for human organization, but they are not reliable machine-readable configuration. They may include the repository name, but the exact identifier belongs in Project Instructions.

After instance setup, `.open-study-path/instance.yml` becomes the persistent repository source of truth.

```mermaid
flowchart LR
    T[Create repository from template] --> P[Create ChatGPT Project]
    P --> I[Add OWNER/REPOSITORY to Project Instructions]
    I --> C[Open first chat]
    C --> B[Bootstrap Open Study Path instance]
    B --> M[Write repository to instance marker]
    M --> S[Configure intake provider]
```

## Setup steps

1. Create a repository from `diegomoura/open-study-path` by using the GitHub template or forking it.
2. Create a new ChatGPT Project dedicated to that learning path.
3. Connect GitHub to ChatGPT and authorize access to the new repository.
4. Connect Jotform, Trello, Google Calendar or Gmail only when those integrations will be used.
5. Copy `templates/chatgpt-project-instructions.md` into the ChatGPT Project Instructions.
6. Replace `OWNER/REPOSITORY` with the exact repository identifier.
7. Optionally name the ChatGPT Project after the learning subject and repository.
8. Open the first chat and send the setup prompt below.

## First-chat prompt

```text
Use the repository defined in this project's instructions.

Set it up as an Open Study Path instance and ask me which intake provider to use.
Do not import a submission, generate the curriculum or publish tasks yet.
```

## Identity resolution rules

During the first setup, the repository target comes from the ChatGPT Project Instructions or an explicit repository identifier in the user's message.

The agent must verify that the accessible repository matches that identifier before writing files. It then records the exact value in `.open-study-path/instance.yml`.

After the instance marker exists:

- `.open-study-path/instance.yml` is the repository source of truth;
- the ChatGPT Project Instructions remain the bootstrap and conversation context;
- a mismatch between the two must stop write operations until the owner resolves it;
- the project title and description never override either source.

## One project per instance

Use one ChatGPT Project per Open Study Path instance. This prevents conversations, attachments, integration identifiers and instructions from being mixed between unrelated learning paths.

A single repository should also represent one active learner instance unless the repository intentionally implements a multi-learner extension.