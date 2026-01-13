# TASK 0 — Create Copilot Instructions

## Purpose
GitHub Copilot works best when a repo includes clear, project-specific guidance about coding style, architecture, tooling, and conventions. This task asks you to create a **Copilot instructions** file so that Copilot (and other contributors) can generate code that matches this project’s patterns.

## Steps
### Manual setup
1. Create a new file at `.github/copilot-instructions.md`.
2. In `.github/copilot-instructions.md`, add guidance covering at least:
   - **Project overview**: one-paragraph description of what the app does (frontend + backend + infra).
   - **Tech stack**: key languages/frameworks (e.g., Vite/React frontend, Python backend, Bicep infra).
   - **Repo structure**: what lives in `frontend/`, `backend/`, and `infra/`.
   - **Coding conventions**:
     - TypeScript/React style preferences (component patterns, naming, hooks usage)
     - Python style preferences (formatting/linting, typing, modules layout)
     - Error handling and logging conventions
   - **Testing & validation**: how to run unit tests/lint/typecheck (or state “not yet available” if missing).
   - **PR expectations**: small focused diffs, update docs when behavior changes, add/adjust tests when applicable.
   - **Do/Don’t rules**: anything the repo should avoid (e.g., don’t commit secrets, don’t change infra defaults without discussion).
3. Keep the instructions **specific and actionable**. Prefer concrete commands and file locations over generic advice.
4. Verify that the file is **easy to scan** and uses headings/bullets.

### Automatic setup (VS Code)
1. Open **Copilot Chat** in VS Code.
2. In the chat view, click the **gear icon**.
3. Click **Generate chat instructions**.
4. Ensure the generated instructions are saved at `.github/copilot-instructions.md`.
   - If VS Code generates the file in a different location, move/copy the contents so the final file lives at `.github/copilot-instructions.md`.
5. Double-check (and edit) the generated content using the **Manual setup** guidance above.

## Expected Outcome
- A new file exists: `.github/copilot-instructions.md`.
- The file clearly explains how Copilot should behave in this repository (style, structure, testing, and constraints).
- A new contributor can read it and understand where to make changes, how to validate them, and what conventions to follow.
- An answer is included in `.github/task-0/copilot-instructions.md`. You can compare it with your result or activate it by moving it to the root of `.github/`.

**Note:** Keep the instructions updated as the project evolves; treat it as living documentation.
