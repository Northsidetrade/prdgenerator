Here is the **detailed Agile Backlog** for the **Automated PRD Generator MVP**, structured by **Epics and User Stories**, each with:

- **SSCS-compliant scoring** based on **Fibonacci values** (1, 2, 3 only — no story exceeds 3)
- **Clear Acceptance Criteria**
- **TDD/BDD tags**
- **Sprint assignments**

---

# 📦 Epics & Backlog (SSCS Scored)

---

## 💡 EPIC 1: Project Setup & Core Backend

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| BE-01 | Backend Scaffold | Scaffold FastAPI project, CI, linting, testing tools | 2 | Sprint 1 | TDD, Infra |
| BE-02 | Supabase Schema | Set up tables: `users`, `projects`, `prds`, `templates` | 3 | Sprint 1 | DB, TDD |
| BE-03 | OpenAI Integration | Add ability to call OpenAI API via Python SDK | 2 | Sprint 1 | AI, API |
| BE-04 | Claude Integration | Add ability to call Claude API via `anthropic` | 2 | Sprint 1 | AI, API |
| BE-05 | PRD Prompt Engine | Compose prompt from user + template data | 3 | Sprint 1 | AI, TDD |
| BE-06 | Save PRD in DB | Store generated content with project ID, user ID | 2 | Sprint 1 | DB, BDD |
| BE-07 | Generate PRD API | POST `/generate-prd` accepting prompt, returning draft | 3 | Sprint 1 | API, TDD |
| BE-08 | Unit Tests (Sprint 1) | Write tests for all core services (mocked model calls) | 2 | Sprint 1 | Test, TDD |
| BE-09 | BDD Test Suite Init | Write BDD scenarios: success, invalid input, timeout | 3 | Sprint 1 | Test, BDD |

---

## 🧠 EPIC 2: PRD Formatting & Export

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| FE-01 | Markdown Renderer | Format PRD output into SSCS markdown template | 3 | Sprint 2 | Format, TDD |
| FE-02 | JSON Renderer | Provide equivalent JSON schema format | 2 | Sprint 2 | Format, TDD |
| FE-03 | Export Controller | Implement `/export/:project_id` endpoint | 2 | Sprint 2 | API, TDD |
| FE-04 | Download Button | Add UI button to download PRD (Markdown/JSON) | 2 | Sprint 2 | UI, Test |
| FE-05 | Export Format Toggle | UI toggle between preview formats | 1 | Sprint 2 | UI, BDD |
| FE-06 | Export Tests | TDD coverage for rendering and edge cases | 2 | Sprint 2 | Test, TDD |
| FE-07 | BDD for Export Flow | Scenarios for UI → API → file download | 3 | Sprint 2 | Test, BDD |

---

## 🧩 EPIC 3: Prompt Templates

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| TM-01 | Create Templates Table | Add CRUD for `prompt_templates` | 2 | Sprint 3 | DB, BDD |
| TM-02 | Seed 3 Default Templates | CRUD App, AI Assistant, SaaS App | 1 | Sprint 3 | Data, Dev |
| TM-03 | Template Selector UI | Dropdown on UI to select template | 2 | Sprint 3 | UI, Test |
| TM-04 | Template Injection | Replace placeholder tokens in prompt | 2 | Sprint 3 | Logic, AI |
| TM-05 | Template Unit Tests | Validate format substitutions and usage | 2 | Sprint 3 | TDD |

---

## 🔐 EPIC 4: Auth & User Projects

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| AU-01 | Supabase Auth | Implement login/signup | 2 | Sprint 3 | Auth, BDD |
| AU-02 | Auth-Protected Routes | Lock generate/view endpoints to logged-in users | 1 | Sprint 3 | Auth |
| AU-03 | Project History UI | View list of projects + view details | 3 | Sprint 3 | UI, DB |
| AU-04 | BDD for Auth Flow | Login → Generate → View History | 2 | Sprint 3 | BDD |

---

## 🎨 EPIC 5: Frontend Input Form

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| UI-01 | Prompt Form UI | Minimal input form (title, idea description) | 2 | Sprint 3 | UI, Test |
| UI-02 | Submission UX | Submit button, loading state, error handling | 1 | Sprint 3 | UX |
| UI-03 | Markdown Preview | Preview PRD live in editor | 3 | Sprint 3 | UI, Format |
| UI-04 | Unit Tests (UI) | Render tests, state tests, API mock tests | 2 | Sprint 3 | TDD |

---

## 🧪 EPIC 6: QA, Docs, Deploy

| Story ID | Title | Description | Score | Sprint | Tags |
|----------|-------|-------------|-------|--------|------|
| QA-01 | Manual QA Pass | Full end-to-end test before release | 2 | Sprint 3 | QA |
| QA-02 | README & Docs | Write setup, API, and UI docs | 2 | Sprint 3 | Docs |
| QA-03 | Deploy to Vercel + Railway | First working MVP deploy | 2 | Sprint 3 | Infra |
| QA-04 | BDD Regression Suite | Ensure no regressions across modules | 2 | Sprint 3 | BDD |

---

# ✅ Summary Table

| Sprint | Story Count | Estimated Points | Focus |
|--------|-------------|------------------|-------|
| Sprint 1 | 9 | 22 pts | Backend, AI, Data, API |
| Sprint 2 | 7 | 18 pts | Formatting, Export, Integration |
| Sprint 3 | 17 | 35 pts | UI, Auth, Templates, QA |

Total Points (All Sprints): **75**  
All stories scored ≤ 3 per **SSCS rules**

---

