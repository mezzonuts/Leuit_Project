# Orchestrator: LEUIT Dev Lifecycle Agent

## Purpose
Automate full dev cycle: plan → code → commit → build → test → deploy → monitor → next plan.

---

## Lifecycle Stages

### Stage 1: PLAN
- Read `.kilo/PLAN.md` identify current sprint day
- Create sub-branch `staging`
- Break tasks into wave-by-wave plan file-level dependency mapping
- Write plan to `.kilo/plans/<timestamp>-<topic>.md`
- Dispatch parallel agent workers independent tasks

### Stage 2: CODE
For each task in plan:
1. Dispatch `general` agent full file context + exact diff spec
2. Agent reads target file → applies changes → reads back to verify
3. Agent posts RESULT to board
4. When wave completes → verify all files → launch next wave

### Stage 3: COMMIT
```bash
git add -A
git commit -m "feat(<scope>): <description>"
git push origin <branch>
```

### Stage 4: CI BUILD
- Push triggers GitHub Actions workflow automatically
- Monitor workflow: `gh run watch <run-id>`
- If fails → fix, amend commit, force-push

### Stage 5: TEST
CI runs automatically:
- **Lint**: ESLint (frontend) + Ruff (backend) — 0 errors
- **TypeCheck**: TypeScript strict + mypy — 0 errors
- **Unit Tests**: Vitest + pytest — all pass
- **Coverage**: ≥ 80% on new code

If tests fail:
1. Read CI logs
2. Fix issues
3. Amend commit + force-push
4. Re-watch CI

### Stage 6: CREATE PR
```bash
gh pr create --base staging --head <branch> \
  --title "feat(<scope>): <description>" \
  --body "<summary + changes + test results>"
```

### Stage 7: MERGE PR
After CI passes on PR:
```bash
gh pr merge <number> --squash --auto --delete-branch
```

### Stage 8: DEPLOY
Current: Binary artifacts on GitHub Releases (manual download)
Future: Auto-deploy distribution server

### Stage 9: MONITOR
Post-release:
- Check GitHub Issues for bug reports
- Monitor crash reports (if telemetry added)
- Track license activation metrics

### Stage 10: NEXT PLAN
When current sprint day complete:
1. Update `.kilo/PLAN.md` — mark day as done
2. Review next day's deliverables
3. Create new branch if needed
4. Repeat Stage 1

---

## Board Communication Protocol

| Participant | Role |
|---|---|
| **main** | Reads PLAN, creates waves, dispatches workers, integrates results |
| **worker** | Reads assignment board, executes, posts RESULT |
| **ALL** | Team-wide announcements only |

### Message Types
- **INFO** — Share findings, context, blockers
- **ASK** — Request decision from coordinator
- **RESULT** — Completed work output
- **HOLD** — Temporary blocker (resolved independently)
- **VETO** — Critical issue blocking merge

### Flow
1. main posts task board file list + spec
2. Worker reads board → executes → posts RESULT
3. main reads RESULTS before launching dependent wave
4. If HOLD → main pauses task, continues others
5. If VETO → main stops, escalates to user

---

## Branch Strategy
```
main → staging → feat/<scope>
```
- PR targets `staging`
- Squash merge
- Delete feature branch after merge

---

## Quality Gates (every PR to staging)

| Gate | Tool | Threshold |
|------|------|-----------|
| Lint | ESLint + Ruff | 0 errors |
| TypeCheck | TypeScript strict + mypy | 0 errors |
| Unit Test | Vitest + pytest | All pass |
| Coverage | pytest-cov / vitest | ≥ 80% new code |
| Security | No hardcoded secrets | Manual review |
| Build | pnpm build + pyinstaller | Artifacts generated |

---

## Trigger Commands

| User Says | Action |
|---|---|
| "lanjut hari N" | Start Sprint Day N implementation |
| "fix CI" | Diagnose + fix CI failures |
| "submit PR" | Create PR for current branch |
| "next plan" | Generate next day's plan |
| "review" | Run full quality gate check |
