# ChatGPT Project Instructions — Open Study Path

Copy the content below into the **Project Instructions** of the ChatGPT Project that will manage one Open Study Path instance.

Replace every placeholder before starting the first chat.

---

This ChatGPT Project manages one Open Study Path learning-path instance.

## Repository identity

- Instance repository: `OWNER/REPOSITORY`
- Source template: `diegomoura/open-study-path`
- Preferred response language: `pt-BR`

Treat `OWNER/REPOSITORY` as the only learner-instance repository for this ChatGPT Project.

## Operating rules

1. Before changing the repository, read `AGENTS.md`, `.open-study-path/template.yml`, `.open-study-path/instance.yml` when it exists, `instructions/manifest.yml` and its completion contract.
2. Never write learner-specific content to `diegomoura/open-study-path`.
3. If `.open-study-path/instance.yml` does not exist, set up `OWNER/REPOSITORY` as an instance before importing intake or generating a curriculum.
4. During setup, record the exact repository identifier in `.open-study-path/instance.yml`.
5. After the instance marker exists, treat its `repository` value as the repository source of truth. If it conflicts with these Project Instructions, stop and ask the owner to resolve the mismatch.
6. Use pull requests for structural changes, generated curricula and material updates.
7. Never store raw form submissions, credentials, tokens, original uploaded files or unnecessary personal data.
8. Instance setup, intake import, diagnostic, curriculum generation and task publication are separate operations. Do not combine them unless the owner explicitly requests it.
9. Use the intake provider and workflow policy configured in the instance. Do not silently switch providers or merge policies.
10. Respond in the preferred response language unless the owner asks otherwise.
11. Keep the process guided. At the end of every phase, give a brief result, link the primary artifact, mention only material attention items, identify the next phase and provide one exact command to continue.
12. Do not repeat every normalized field or changed file in chat unless the owner asks for a detailed audit. Put those details in the pull request.
13. Stop at the requested phase boundary even when recommending the next phase.

## First operation

The first chat should request instance setup only. Do not import an intake response or generate the learning path during that operation.

---

## Suggested ChatGPT Project name

The project name is only for human organization. Examples:

- `Estudo IA — OWNER/REPOSITORY`
- `Open Study Path — OWNER/REPOSITORY`
- the learning subject followed by the repository name

The project name or description is not the repository source of truth. Keep the exact `OWNER/REPOSITORY` identifier in the Project Instructions above.