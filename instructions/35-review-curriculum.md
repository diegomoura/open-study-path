# Internal curriculum review checklist

Run this checklist automatically inside initial generation and every later content-materialization operation. Do not ask the owner to send a separate review command.

## Scope

Review against:

- approved intake and diagnostic evidence;
- `instructions/30-generate-path.md`;
- `instructions/57-materialize-next-content.md` when materializing later content;
- `docs/mermaid-visual-learning.md`;
- topic, module, rubric and Issue Form templates;
- configured availability, granularity, visual-learning and content-generation strategy;
- verified assessment evidence when future content is being adapted.

Do not publish external tasks during curriculum review.

## Review checklist

Confirm that:

1. the roadmap contains the complete approved topic graph;
2. the roadmap includes a Mermaid diagram of the actual topic dependencies rather than a generic lifecycle diagram;
3. every prerequisite exists and the graph is acyclic;
4. each topic represents one coherent, independently assessable capability;
5. topics are not oversized and are not fragmented into trivial administrative units;
6. each topic defines three to seven focused activities, normally 10–25 minutes each;
7. topic effort is normally 45–90 minutes, and a topic above 120 minutes is split when it contains separable capabilities;
8. every topic contract has a valid `content_status` of `planned` or `materialized`;
9. every materialized topic has a complete module, rubric and discoverable Issue Form;
10. planned topics do not have broken links or claim nonexistent detailed content;
11. every materialized module teaches the content rather than merely listing actions;
12. modules contain a granular execution plan, prerequisite retrieval, explanations, worked examples, misconceptions, guided practice, independent practice and active recall;
13. every materialized module contains at least the configured minimum number of fenced Mermaid diagrams;
14. each diagram represents a meaningful relationship, decision, sequence, state, timeline, comparison, data flow or architecture rather than decorative boxes;
15. each diagram is introduced and followed by an explanation of what the learner should notice and what the model omits;
16. diagram types fit the subject and use Mermaid syntax that renders in GitHub without unsupported features or raw HTML;
17. complex technical modules use additional diagrams when one view would mix architecture, runtime interaction and state changes excessively;
18. each assessment has five substantive prompts and a rubric totaling 100 points;
19. rubrics define a passing score, critical misconceptions and focused recovery rules;
20. Issue Forms contain the standard labels, deterministic topic marker and command `Finalizei o TOPIC-000. Avalie minhas respostas.`;
21. the initial materialized set follows the configured full-upfront thresholds or rolling-window size in deterministic topological order;
22. later materialization preserves approved objectives, prerequisites, deliverables, effort and mastery criteria;
23. adaptations from assessment evidence affect examples, emphasis, visual models and practice without silently changing the approved curriculum structure;
24. total effort and schedule projection remain consistent with availability;
25. scope is explicitly introductory when it does not satisfy the complete long-term goal;
26. required resources name a specific work and canonical locator;
27. no external tasks or integrations are created during curriculum generation or review.

Reject a module as incomplete when it could be replaced by a short checklist without losing meaningful teaching content. Also reject a required visual section that contains a generic diagram unrelated to the topic or a Mermaid block without explanatory prose. Correct problems directly on the proposal branch.

## Allowed diffs

Initial generation may change the instance marker, roadmap, every topic contract and only the modules, rubrics and forms selected by the initial content window.

Later materialization must remain limited to the selected topic contracts, their modules, rubrics and forms, plus roadmap materialization status.

## Automatic review and merge policy

Read `workflow.curriculum_merge_policy` from `.open-study-path/instance.yml`. If missing, use `manual`.

- `manual`: finish review, report findings and leave the PR open.
- `agent_review_then_merge`: correct the branch, run required checks, self-review the final diff, set any required approved or materialized status, rerun checks, mark ready and merge when no unresolved pedagogical decision remains.

Do not attempt to formally approve a PR authored by the same account. Contract verification, final diff review and successful CI constitute operational review.

Leave the PR open only when goal, structure, effort, resource precision, assessment meaning, visual representation or a structural adaptation genuinely requires owner input, or when CI/scope validation fails.

When owner input is required, annotate the PR and use:

`Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

After successful merge, use:

`Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`

Never ask the owner to perform the entire review or merge merely because a pull request exists.
