# PulseIQ Phase 4 Complete - additive completion workspace

This workspace is additive to the committed Phase 4 release candidate. It does not replace existing report generation, report outputs, API, lineage, tests or board pack.

## Task 18 foundations
- Data-driven, fail-closed role/metric/dimension authorization.
- Demo identity resolver reading the supplied user registry.
- Trusted hierarchy loader.
- Privacy decision helper that withholds results when group size or threshold is missing.

## Required source files
Place the official Task 18 demo_users.csv in config/. Populate metric_permissions.csv from the official metric dictionary and approved policy. Populate department_team_hierarchy.csv from the authoritative organization mapping.

Templates are supplied. They contain no invented users, team mappings, metric grants or thresholds.

## Current limits
Production identity remains fail-closed until a verified SSO/OIDC adapter and trusted claim validation are implemented. The existing Render blueprint is not a verified deployment. The scheduled report workflow is not a warehouse refresh. Never expose development mode publicly.
