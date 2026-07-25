# Integration preflight for task publication

Run this preflight inside the `publish` phase before any external write.

## Determine required connections

Read `study.config.yml` and derive only the connections required by the configured providers:

- `integrations.task_manager.provider: trello` requires Trello;
- `integrations.task_manager.provider: github_issues` requires access to the instance repository through GitHub;
- `integrations.task_manager.provider: markdown` requires no external connection;
- `integrations.calendar.provider: google_calendar` with `enabled: true` requires Google Calendar;
- `integrations.notifications.provider: gmail` with `email_enabled: true` requires Gmail;
- providers set to `none`, `chat` or disabled do not require an external connection.

Do not test integrations that are not enabled in the instance.

## Verify actual access

A provider name in `study.config.yml`, an installed app, or an available tool definition does not prove that the current ChatGPT Project is authorized.

For every required external provider, execute one harmless read-only operation through its connector. Examples include listing a small number of Trello boards, reading Google Calendar colors or a minimal event search, listing Gmail labels, or reading the instance repository through GitHub.

Treat missing tools, authorization requests, permission errors and failed read operations as an unavailable connection. Never request API keys, tokens or passwords in chat.

## Atomic preflight

Complete the connection preflight before creating any board, card, issue, event, email or integration-state write.

When one or more required connections are unavailable:

1. create no external resources;
2. do not partially publish through the providers that are connected;
3. name only the unavailable providers;
4. tell the owner to connect or authorize those apps in the current ChatGPT Project;
5. provide the exact return command below, replacing `<providers>` with the missing provider names:

`Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação das tarefas sem alterar o currículo.`

The return command does not prove access. Run the read-only probes again. If a connection is still unavailable, report only the providers that still fail.

The original publication request plus the return command authorize continuation of the same publication operation. Do not request another confirmation after all required probes pass.

When every required connection is available, do not send an intermediate “connections verified” response. Continue directly with the configured publication adapters.

## Idempotency before writes

Before creating resources, search for identifiers already stored in `state/integrations.json` when it exists and look for exact matching resources in the connected providers. Reuse valid existing boards, projects, lists, cards, events or task artifacts rather than creating duplicates.

A failed or interrupted publication must report which resources were actually created. Never claim atomic rollback when an external provider does not support it.

## Blocked response

Use a brief response equivalent to:

> Resultado: publicação pausada antes de qualquer criação externa.
>
> Atenção: não foi possível verificar a conexão com `<providers>`. Conecte ou autorize esses apps no Projeto do ChatGPT.
>
> Depois, envie:
>
> `Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação das tarefas sem alterar o currículo.`

Do not include a success artifact or claim that integrations were configured while the probes are failing.
