# TASK 1 — Implement Test Mode Backend

## Purpose
In the course of the session, we will implement self-contained end-to-end (E2E) testing using Playwright. To achieve this, we first need to decouple our backend from the live Azure Cosmos DB service. This task focuses on implementing a "Test Mode" that uses an in-memory repository instead of the real database. This allows tests to run locally and reliably without network dependencies or cloud costs.

**Note:** This task is strictly about setting up the application to run with the test storage. We will implement the actual Playwright tests in a later task.

## Objective & Desired Outcome
You need to modify the backend to support a "test mode". When this mode is active:
1. The application should use an **In-Memory Repository** implementation for data storage instead of connecting to Cosmos DB.
2. The application should be startable locally in this mode without Azure credentials.
3. The existing Cosmos DB implementation should remain intact for production use.

Specifically, this involves:
- Creating an interface/abstraction for your data access layer.
- Moving the current Cosmos DB logic into a concrete implementation of that interface.
- Creating a new In-Memory implementation (e.g., using a Python dictionary or list).
- Using an environment variable (e.g., `TEST_MODE=true` or `REPOSITORY_TYPE=memory`) to switch implementations at runtime.

## Ways to Complete This Task
You are free to use any method you prefer to reach the goal, depending on your comfort level:

- **Pro-Code**: Use your preferred coding style. You can manually refactor the code, abstract the repository pattern, and implement the in-memory store. Use Copilot Inline Suggestions (`Ctrl+I` / `Cmd+I`) to generate the boilerplate for the new classes.
- **Assisted**: Use Copilot Chat (`Ctrl+Alt+I` / `Cmd+Alt+I`) to ask for a plan ("How do I refactor this FastAPI app to use the Repository pattern?") or specific code snippets.
- **Autonomous (Agent Mode)**: Use Copilot's Agent Mode to plan and implement the changes across multiple files automatically.

## Follow-Along Instructions
If you have less coding experience or want to see the Agent in action, use the following steps:

1. Open **Copilot Edits** (Agent Mode).
2. In the model picker, select **Claude Sonnet 4.5**.
3. Input the following prompt exactly:

    > I want to implement self-contained end-to-end testing using Playwright. For that, implement a “test mode” backend storage option (in-memory repository) so tests don’t depend on Cosmos and start the app locally. Ignore the actual e2e testing for now.

4. **Review**: The Agent will analyze your workspace (`backend/src/`) and propose a plan. It will likely suggest creating a `Repository` abstract base class and two subclasses (`CosmosRepository`, `InMemoryRepository`).
5. **Approve**: Click to apply the edits.
6. **Verify**: Once finished, the Agent should tell you how to run the app in test mode. Try starting the backend (e.g., `cd backend && TEST_MODE=true python src/main.py` or similar command provided by the agent) and check if it runs without errors.

## Expected Outcome
- The `backend/src` folder contains an abstraction for repositories.
- There is an implementation for Cosmos DB (preserving existing logic).
- There is a new implementation for In-Memory storage.
- The app can start locally using the In-Memory storage.
