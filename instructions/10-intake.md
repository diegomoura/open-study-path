# Intake

Run this phase only in instance mode.

Read the latest approved response from the provider configured in the instance's `study.config.yml`. Never use a form ID or submission belonging to the canonical template unless the maintainer is explicitly testing the template.

For Jotform:

- use the form ID configured by the instance owner;
- select the latest approved submission rather than assuming every submission is ready;
- treat file uploads as optional;
- read attached files only when their contents materially affect the plan;
- do not commit raw submissions or uploaded files.

Required planning facts are the subject, detailed objective, current level, preferred language and weekly availability. Desired outcome, motivation, deadline, preferred days or periods, accessibility needs, notes, text references, URLs and attachments are optional.

Map approved intake into `study.config.yml` and `state/intake-summary.json`. Mark assumptions visibly. Missing optional answers must not block generation; derive conservative defaults only when necessary and record them as assumptions.