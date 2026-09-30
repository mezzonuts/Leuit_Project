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

### Stage 4: CI BUILD + AUTO-RETRY
Push triggers GitHub Actions workflow automatically.

**Auto-retry loop (max 5 iterations):**
```
1. Wait 120 seconds (let CI start + run)
2. Check: gh run list --limit 1 --json conclusion
3. If conclusion == "success" → go to Stage 5
4. If conclusion == "failure" →
   a. Get failed step: gh run view <id> --log-failed | tail -50
   b. Diagnose error (lint, mypy, test)
   c. Fix the code
   d. git add -A && git commit --amend --no-edit && git push --force-with-lease
   e. Go to step 1 (wait 120s again)
5. If conclusion == "in_progress" → wait 60s, check again
6. If still failing after 5 iterations → STOP, report to user
```

**Key rules:**
- Never skip a failing CI — always fix before proceeding
- Use `--force-with-lease` (not `--force`) for safety
- Log each iteration: what failed, what was fixed

### Stage 5: TEST GATE
After CI passes, verify quality gates:
- **Lint**: ESLint (frontend) + Ruff (backend) — 0 errors
- **TypeCheck**: TypeScript strict + mypy — 0 errors
- **Unit Tests**: Vitest + pytest — all pass
- **Coverage**: ≥ 80% on new code

If any gate fails → go back to Stage 4 auto-retry loop.

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

### Stage 10: NEXT PLAN + SPRINT TRANSITION
When current sprint day complete (all tasks done, CI green, PR merged):
1. Update `.kilo/PLAN.md` — mark current day as ✅ done
2. Read next day's deliverables from PLAN.md
3. Create new branch: `feat/day<N>-<scope>`
4. Write new plan: `.kilo/plans/<timestamp>-<next-topic>.md`
5. Begin Stage 1 (PLAN) for next day
6. Auto-repeat until sprint complete (Day 14)

**Sprint transition:**
- End of Sprint 1 (Day 7) → update PLAN.md, create Sprint 2 plan
- End of Sprint 2 (Day 14) → generate `RELEASE_REPORT.md`, notify user

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
