# Bootstrap an instance

Bootstrap is allowed only in a fork or repository created from this template.

Read and apply `instructions/02-setup-execution.md` before inspecting or changing the target repository.

1. Read `AGENTS.md`, `.open-study-path/template.yml`, `.open-study-path/instance.yml` when present, `templates/instance.yml`, `instructions/manifest.yml` and the ChatGPT Project Instructions when available.
2. Resolve the exact target as `OWNER/REPOSITORY` from the prepared Project Instructions or the owner's explicit message. The normal template-created flow renders `templates/chatgpt-project-instructions.md` automatically through GitHub Actions. Do not rely only on the ChatGPT Project name or description.
3. Confirm the target is accessible and is not the canonical template repository.
4. Determine repository mode from the sentinel files, not repository size, search results or an incomplete local checkout. If `.open-study-path/template.yml` exists, the repository is not empty and its inherited infrastructure must be preserved.
5. If the instructions still contain the literal placeholder `OWNER/REPOSITORY`, stop before writing and ask the owner to run **Prepare ChatGPT Project Instructions** or provide the exact repository identifier explicitly.
6. Before writing generated setup artifacts, create one feature branch for the complete setup operation. Never write setup artifacts directly to the default branch.
7. If `.open-study-path/instance.yml` is absent, copy `templates/instance.yml`, replace `OWNER/REPOSITORY`, set the initialization timestamp and preserve its workflow defaults. Keep `.open-study-path/template.yml`; instance mode is represented by both markers, with the instance marker taking precedence.
8. New instances must start with `workflow.guided: true` and `workflow.intake_merge_policy: auto_when_unambiguous` unless the owner explicitly selects another supported policy.
9. If an instance marker already exists, verify its `repository` value matches the current target before writing anything. Do not overwrite an existing workflow policy silently.
10. Copy `study.config.example.yml` to `study.config.yml` and copy the state templates to their instance paths.
11. Copy `templates/integrations-state.json` to `state/integrations.json`, replace `OWNER/REPOSITORY`, and keep its resources empty. This file is only an idempotency index; it is not a second source of learning truth.
12. Leave all learner fields and provider selections unconfigured or `auto`. Do not import a submission, recommend providers or create external resources during bootstrap.
13. Continue to `instructions/05-configure-intake.md` unless the owner explicitly asks to postpone intake configuration.
14. Stop when the selected intake method is ready. Do not import answers, generate a curriculum, publish tasks or create study integrations during setup.
15. Assemble all outputs and the approved setup review on the same feature branch. Open exactly one pull request only after the complete setup head exists; intermediate commits must never be treated as a completed setup.
16. Validate the complete setup diff and satisfy the merge gate in `instructions/02-setup-execution.md` before merging or reporting success.
17. Complete the phase using `instructions/phase-completion.md`, including the exact next action for the selected intake provider.

The prepared ChatGPT Project Instructions provide the initial repository pointer. After bootstrap, `.open-study-path/instance.yml` is the persistent repository and workflow source of truth. `study.config.yml` stores learner and capability preferences. `state/integrations.json` stores only safe external identifiers and synchronization metadata.

Never overwrite an existing instance without comparing changes. Setup must use one feature branch and one pull request for the complete first-chat operation.
