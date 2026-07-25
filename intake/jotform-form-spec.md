# Jotform intake specification

This document defines the reusable onboarding form for an Open Study Path instance.

## Ownership rule

Each fork owner should create or duplicate the form in their own Jotform account and store that form ID only in their instance's `study.config.yml`. The canonical template must not hardcode a learner form ID.

The maintainer reference form used while developing the template is:

- https://form.jotform.com/262053811445048

It is a reference implementation, not the default data store for every fork.

## Required questions

- Topic or skill to learn.
- Detailed objective.
- Current level: no knowledge, beginner, intermediate or advanced.
- Preferred content language.
- Available hours per week, validated as a positive number.
- Task manager: GitHub Issues, Trello or Markdown only.
- Consent to save normalized planning data without raw submissions or unnecessary personal data.

## Optional questions

- Name of the learning path.
- Concrete desired outcome.
- Motivation.
- Prior knowledge and experience.
- Deadline.
- Preferred days and periods.
- Learning formats.
- Theory/practice balance.
- Assessment style.
- Accessibility needs or restrictions.
- Google Calendar integration.
- Email summaries.
- Additional notes.
- Reference text or URLs.
- One or more file uploads.

## Optional attachments

File uploads must always be optional. Useful examples include a job description, résumé, PDF, syllabus, image or text file.

The agent should:

1. read an attachment only when it materially affects the plan;
2. avoid committing the original file;
3. save only safe metadata, a summary or a source reference;
4. continue without attachments when the written answers are sufficient.

## Submission selection

A submission is approved when the user explicitly identifies it or asks the agent to use the latest submission. The agent must not silently combine multiple submissions.

## Normalization

The form response is input, not the source of truth. The instance stores a minimized representation in `study.config.yml` and `state/intake-summary.json`. Raw responses and personal identifiers are not persisted by default.
