Here's a **detailed UML Class Diagram (Data Model)** for the **Automated PRD Generator**, based on the PRD you requested.

---

## 🧩 UML Class Diagram (Textual Representation)

```plaintext
+--------------------+
|      User          |
+--------------------+
| - id: UUID         |
| - name: String     |
| - email: String    |
| - created_at: Date |
+--------------------+
| +generatePRD()     |
| +viewProjects()    |
+--------------------+
           |
           | 1
           |----------------------+
                                   \
                                    \*
                                +----------------------+
                                |      Project         |
                                +----------------------+
                                | - id: UUID           |
                                | - user_id: UUID      |
                                | - title: String      |
                                | - input_prompt: Text |
                                | - created_at: Date   |
                                +----------------------+
                                | +generatePRD()       |
                                | +exportMarkdown()    |
                                | +exportJSON()        |
                                +----------------------+
                                         |
                                         | 1
                                         |--------------+
                                                         \
                                                          \*
                                           +-----------------------------+
                                           |      PRDDocument            |
                                           +-----------------------------+
                                           | - id: UUID                  |
                                           | - project_id: UUID          |
                                           | - format: Enum (MD/JSON)    |
                                           | - content: Text             |
                                           | - created_at: Date          |
                                           +-----------------------------+
                                           | +download()                 |
                                           | +viewPreview()              |
                                           +-----------------------------+

+----------------------------+
|        LLMProvider         |
+----------------------------+
| - id: UUID                 |
| - name: String             |
| - provider_type: String    |
| - version: String          |
| - endpoint_url: String     |
+----------------------------+
| +callModel(prompt)         |
+----------------------------+

+----------------------------+
|       PromptTemplate       |
+----------------------------+
| - id: UUID                 |
| - title: String            |
| - description: Text        |
| - template_body: Text      |
| - model_hint: String       |
+----------------------------+
| +render(input_data)        |
+----------------------------+

```

---

## 🧠 Class Breakdown

### `User`
- Represents a system user.
- Can own many projects.

### `Project`
- Stores each user's idea with an input prompt and metadata.
- Has many `PRDDocument` entries (Markdown, JSON, revisions).

### `PRDDocument`
- Represents the actual generated PRD file.
- Includes format, content, and export methods.

### `LLMProvider`
- Abstract representation of any supported model provider (OpenAI, Claude, Ollama).
- Used to call the backend model for PRD generation.

### `PromptTemplate`
- Holds reusable templates used to standardize prompt structures.
- Useful for scaffolding TDD/BDD PRD types quickly.

---

## 🧮 Enum Definitions

```plaintext
Enum Format:
- MARKDOWN
- JSON
- HTML (future)
```

---

## 🔒 Notes on Relationships

- `User` 1—* `Project`
- `Project` 1—* `PRDDocument`
- `LLMProvider` is independent but used during project PRD generation
- `PromptTemplate` may be globally shared or personalized per user in future versions

---
