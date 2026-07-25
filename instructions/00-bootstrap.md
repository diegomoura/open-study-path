# Bootstrap an instance

Bootstrap is allowed only in a fork or repository created from this template.

1. Read `AGENTS.md`, `.open-study-path/template.yml`, `templates/instance.yml`, `instructions/manifest.yml` and the ChatGPT Project Instructions when available.
2. Resolve the exact target as `OWNER/REPOSITORY` from the Project Instructions or the owner's explicit message. Do not rely only on the ChatGPT Project name or description.
3. Confirm the target is accessible and is not the canonical template repository.
4. If `.open-study-path/instance.yml` is absent, copy `templates/instance.yml`, replace `OWNER/REPOSITORY`, set the initialization timestamp and preserve its workflow defaults.
5. New instances must start with `workflow.guided: true` and `workflow.intake_merge_policy: auto_when_unambiguous` unless the owner explicitly selects another supported policy.
6. If an instance marker already exists, verify its `repository` value matches the current target before writing anything. Do not overwrite an existing workflow policy silently.
7. Copy the example configuration and state templates to their instance paths.
8. Leave all learner fields unconfigured. Do not import a submission during bootstrap.
9. Continue to `instructions/05-configure-intake.md` unless the owner explicitly asks to postpone intake configuration.
10. Stop when the selected intake method is ready. Do not import answers, generate a curriculum, publish tasks or create study integrations during setup.
11. Complete the phase using `instructions/phase-completion.md`, including the exact next action for the selected intake provider.

The ChatGPT Project Instructions provide the initial repository pointer. After bootstrap, `.open-study-path/instance.yml` is the persistent repository and workflow source of truth.

Never overwrite an existing instance without comparing changes. Work on a feature branch and prefer a pull request.