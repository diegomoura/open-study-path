# Capability-based integration preflight

Run this preflight inside the `publish` phase before any external write.

## Inputs

Read:

- `study.config.yml`;
- approved `study/integrations.md`;
- `state/integrations.json`;
- exact repository identity from `.open-study-path/instance.yml`.

Do not infer enabled providers from a global app catalog. A provider is relevant only when selected by the approved plan or needed as its fallback.

## Classify capabilities

Classify every capability as one of:

- `required_for_selected_publication` — its provider must be available before the atomic required publication set begins;
- `optional_probe` — try a harmless read, but failure immediately selects the documented fallback and does not block;
- `not_enabled` — no probe and no write.

GitHub access is always required.

The authoritative external task backend is required when the selected plan expects tasks outside Markdown. A provider explicitly promoted to required by the owner is also required. By default, research, flashcards, reminders, scheduling, habits, external visuals, artifact workspaces, analytics, course discovery and notifications are optional.

## Provider resolution

Resolve the concrete providers configured for each capability:

- task manager: Trello, Todoist, GitHub Issues or Markdown;
- reminders: Todoist, calendar or none;
- scheduling: Reclaim, Google Calendar, Outlook Calendar or none;
- research: Consensus, web or none;
- formative practice: Quizlet, Ace Quiz Maker, local flashcards or none;
- habits: Habitify or none;
- external visuals: Whimsical, Miro, Lucid, Figma or none;
- artifacts: Google Drive, Notion, SharePoint, Dropbox or none;
- analytics: Airtable or none;
- notifications: Gmail, Outlook email, chat or none.

A value of `auto` must already have a documented recommendation and fallback in `study/integrations.md`. Resolve it before writes and persist the actual provider used in `study.config.yml` or `state/integrations.json`.

## Verify actual access

A provider name, installed app, visible tool definition or learner statement does not prove that the current ChatGPT Project is authorized.

For every relevant external provider, execute one harmless minimal read-only operation supported by its connector. Examples:

- GitHub: read the instance marker or repository metadata;
- Trello: list a small number of boards;
- Todoist: list a small number of projects or tasks;
- Reclaim, Google Calendar or Outlook Calendar: read availability, calendars or a bounded event window;
- Quizlet: list or read a saved set when supported;
- Consensus: run a minimal non-writing availability search only when research use is pending;
- Habitify: read a small habit list;
- Whimsical or another visual provider: list a small number of workspaces or files;
- Google Drive or alternatives: list a small number of files;
- Airtable: list accessible bases or schema metadata;
- Gmail or Outlook email: list labels, folders or profile metadata.

Use only operations actually exposed by the connected plugin. Never request API keys, tokens or passwords.

## Required-provider atomicity

Complete every required probe before creating any required external resource.

When one or more required providers are unavailable:

1. create no resource in the required publication set;
2. do not partially publish through other required providers;
3. optional probes may be skipped because required publication is paused;
4. name only the unavailable required providers;
5. tell the owner to connect or authorize those apps in the current ChatGPT Project;
6. provide the exact return command below:

`Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.`

The return command does not prove access. Run the read-only probes again.

## Optional-provider fallback

When an optional provider is unavailable, unauthorized, unsupported, paid-only for the needed action or outside the learner's account policy:

1. create no resource in that provider;
2. mark the provider `unavailable` with the reason category in `state/integrations.json`, without storing sensitive error details;
3. activate the approved fallback;
4. continue the publication operation;
5. report the fallback briefly at completion.

Examples:

- Quizlet unavailable → link local TSV/Markdown flashcards;
- Consensus unavailable → retain primary sources, official documentation and web research;
- Reclaim unavailable → use approved Google/Outlook Calendar fallback or no schedule;
- Habitify unavailable → keep habits in the task backend or module checklist;
- Whimsical unavailable → use Mermaid only;
- Drive unavailable → use repository artifacts;
- Airtable unavailable → use repository state and omit the dashboard;
- email unavailable → report in chat.

Optional failure must never block generation, study, assessment, recovery or mastery.

## Free-tier policy

When `integration_preferences.free_tier_only` or a capability's `free_tier_only` is true:

- do not probe by performing a paid write;
- do not assume current plan entitlements from documentation or memory;
- use only capabilities confirmed by harmless reads or safe attempted operations;
- avoid requiring upgrades;
- select the documented free fallback when the needed feature is unavailable.

## Idempotency before writes

Before creating resources, inspect exact records in `state/integrations.json` and search the connected provider for matching resources. Reuse or update valid resources rather than creating duplicates.

Match on capability, provider, external type, topic ID, content version and stable course identifier. An interrupted publication must report what was actually created or updated. Never claim atomic rollback when the provider does not support it.

## Continue after probes

When required probes pass, do not send an intermediate “connections verified” response. Continue directly with required publication and optional provider probes.

## Blocked response

Use a brief response equivalent to:

> Resultado: publicação pausada antes de qualquer criação externa obrigatória.
>
> Atenção: não foi possível verificar a conexão com `<providers>`. Conecte ou autorize esses apps no Projeto do ChatGPT.
>
> Depois, envie:
>
> `Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.`

Do not list unavailable optional providers in the blocked response; they use fallbacks and will be summarized after successful core publication.
