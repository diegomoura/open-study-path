# Intake

Read the latest approved response from the configured provider. For Jotform, use form `262053811445048` unless the fork owner changes it. Extract only facts required for planning, remove unnecessary personal data, and save a normalized summary to `state/intake-summary.json`. Never commit the raw submission.

Map intake fields into `study.config.yml` and visibly mark assumptions. Stop generation only when a missing fact would materially change the curriculum; otherwise use conservative defaults.
