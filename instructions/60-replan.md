# Replan

Recalculate schedule projections when availability, deadline or actual velocity changes. Preserve completed evidence and topic dependencies. Add, remove or split topics only when the goal, diagnostic evidence or mastery results justify the change.

Document material curriculum changes in `study/roadmap.md` with date, reason and impact.

Re-evaluate `study/integrations.md` only when the changed course structure, availability, learner preference, provider access or repeated evidence creates a concrete new capability need. Do not rotate providers merely because another app exists.

Examples of justified integration changes:

- switch Trello to Todoist when a replanned path becomes short and simple;
- add reminder-only Todoist when spaced review becomes important;
- select Reclaim when schedule variability becomes the main blocker;
- add Habitify when consistency, rather than understanding, is repeatedly failing;
- add Quizlet when later topics introduce substantial atomic recall material;
- remove an unavailable or paid-only optional provider and retain its fallback;
- enable Airtable when the learner needs cross-course analytics, while keeping `github_to_airtable` and no mastery authority.

Any task-backend change must migrate or reconcile the authoritative execution state and leave only one authoritative backend. Preserve safe identifiers in `state/integrations.json`, archive or mark superseded resources, and never infer mastery from the old or new external provider.

External integration changes do not silently rewrite approved objectives, mastery criteria or assessment evidence. Apply the same draft PR, internal review, CI and safe-merge policy used for curriculum changes when repository contracts change.

Complete the phase using `instructions/phase-completion.md`. Summarize only what materially changed and why, link the updated roadmap, integration plan or pull request, and provide one exact command for returning to progress tracking or reviewing a changed topic.
