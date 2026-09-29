# Fix CI Annotations

## Problem
GitHub Actions CI shows 3 warnings:
1. "Some specified paths were not resolved, unable to cache dependencies"
2. "Node.js 20 is deprecated"
3. "ubuntu-latest label will migrate to Ubuntu 26"

## Root Causes
1. `cache-dependency-path: frontend/pnpm-lock.yaml` - pnpm lockfile lives at repo root `pnpm-lock.yaml`, not inside `frontend/`
2. `NODE_VERSION: '20'` - GitHub runners deprecated Node 20, now force Node 24
3. Informational only - ubuntu-latest will migrate Oct 2026, no action needed

## Changes Required

### File: `.github/workflows/ci.yml`

| Line | Current Value | New Value | Reason |
|------|--------------|-----------|--------|
| 10 | `NODE_VERSION: '20'` | `NODE_VERSION: '22'` | Node 20 deprecated, upgrade to LTS 22 |
| 33 | `cache-dependency-path: frontend/pnpm-lock.yaml` | `cache-dependency-path: pnpm-lock.yaml` | Lockfile is at repo root |
| 84 | `cache-dependency-path: frontend/pnpm-lock.yaml` | `cache-dependency-path: pnpm-lock.yaml` | Same fix |
| 140 | `cache-dependency-path: frontend/pnpm-lock.yaml` | `cache-dependency-path: pnpm-lock.yaml` | Same fix |

## Validation
- Push changes to `chore/fix-ci-annotations` branch
- Create PR to `main`
- Verify CI runs without cache/Node warnings