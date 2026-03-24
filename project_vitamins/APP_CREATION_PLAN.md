# VitaminSHE App Creation Plan

## Scope
This scaffold separates responsibilities across focused Django apps:

- `core`: public landing pages, navigation, shared context helpers.
- `accounts`: sign up, login, profile, password reset, role rules.
- `dashboard`: personalized overview after authentication.
- `tracking`: vitamin intake logs, symptom logs, reminders, trends.
- `recommendations`: food/supplement recommendations from tracked data.
- `resources`: educational articles, FAQ, reference content.
- `locator`: clinics/labs map lookup and nearby search flows.

## Build Sequence
1. `accounts`
2. `tracking`
3. `dashboard`
4. `recommendations`
5. `resources`
6. `locator`
7. `core` polish and shared UX pass

## First Models To Add
- `accounts`: custom user profile and preference metadata.
- `tracking`: daily intake entry, symptom entry, reminder schedule.
- `recommendations`: recommendation rule and recommendation result.
- `resources`: category and article/resource item.
- `locator`: clinic record and saved clinic links for users.

## Initial Integration Tasks
1. Replace app placeholder `HttpResponse` views with class-based views.
2. Add per-app templates in `templates/<app_name>/`.
3. Connect forms, model validation, and tests for each app.
4. Add auth gating for dashboard/tracking/recommendation routes.
5. Introduce API endpoints if mobile integration is needed.
