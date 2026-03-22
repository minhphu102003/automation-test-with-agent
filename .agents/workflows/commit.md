---
description: Automatically stage, commit with a Conventional Commit message, and push to origin.
---

Follow these steps to commit and push changes:

1. Stage all changes:
// turbo
`git add .`

2. Review the staged changes:
`git diff --cached`

3. Generate a commit message following the Conventional Commits specification (e.g., `feat: ...`, `fix: ...`, `refactor: ...`).
   - Use `feat:` for new features (like new tests).
   - Use `refactor:` for reorganization.
   - Use `docs:` for README updates.

4. Commit the changes:
// turbo
`git commit -m "<generated_message>"`

5. Push to the remote repository:
// turbo
`git push origin head`
