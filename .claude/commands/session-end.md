# /session-end

Run this at the end of every working session on the POD-and-Affiliate project.

## Steps

1. **Review what changed this session**
   - Check `git diff HEAD` and `git status` for any uncommitted changes
   - Summarise what was built, fixed, or verified

2. **Update `CLAUDE.md` — Current status section**
   - Replace the existing "Current status" block with today's date and a fresh summary of:
     - What is now done and confirmed working
     - What still needs verifying (not assumed, actually tested)
   - Update "Next steps" to reflect current state — remove completed items, reorder if priorities shifted

3. **Update `BACKLOG.md`**
   - Tick off any completed backlog items
   - Add any new ideas or tasks that came up during the session
   - Update the Decisions log if any architectural or tooling decisions were made

4. **Update project memory**
   - Read `C:\Users\nickc\.claude\projects\c--Users-nickc-Documents-POD-and-Affiliate\memory\project_pod_overview.md`
   - Update the "Pending setup steps" list to reflect current state
   - Write any non-obvious decisions or context that won't be obvious from the code

5. **Commit all session changes to git**
   - Stage all modified tracked files: `CLAUDE.md`, `BACKLOG.md`, and any code changes from this session
   - Do not stage `.env` or any file in `.gitignore`
   - Commit with a message in the format: `session: <date> — <one-line summary of what changed>`
   - Example: `session: 2026-05-20 — verified Gemini pipeline, updated backlog and CLAUDE.md`
   - Report the commit hash to the user

6. **Apply a git tag if a milestone was reached this session** (see versioning scheme in `CLAUDE.md`)
   - Check whether this session crossed one of the defined milestones (see `CLAUDE.md` versioning section)
   - If yes, apply the corresponding tag: `git tag v0.x.0 -m "description"`
   - If no milestone was reached, skip — do not tag every session, only milestones
   - Report the tag applied (or confirm none was needed)

7. **Produce a session summary** — output to the user:
   - What was done this session (bullet list)
   - What is unresolved or untested
   - The single most important next action for the next session
