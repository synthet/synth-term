# GitHub Actions (synthet/warp)

This fork keeps a **single** workflow: [`ci.yml`](./ci.yml) (`Warp CI`). It runs on
`github.repository_owner == 'synthet'` using GitHub-hosted runners (`ubuntu-latest`,
`macos-14`).

Upstream Warp workflows (release cutting, repo-sync, Oz/docubot automation, Docker Hub
agent-dev image, warpdotdev/docs dispatch, etc.) are **not** carried in this fork. They
depended on Warp-internal secrets, Namespace runners, GCP, and `warpdotdev/*` reusable
workflows. Removing them avoids skipped scheduled runs, failing `update-*-local` jobs, and
noisy `notify-docs` / `publish-agent-dev-image` failures on every `master` push.

## What runs when

| Trigger | Jobs |
|---|---|
| Push to `master`, PR | Linux fmt + clippy, miscellaneous checks, wasm fmt + clippy, release-flag compile checks (Linux, Windows, wasm), Linux unit tests (no `integration` crate), DB migration check when the schema changes |
| Manual run (`workflow_dispatch`) | Everything above, plus macOS jobs, Windows tests and clippy, the `integration` crate with the shell matrix (bash, fish, zsh, PowerShell), and doc tests |

Why the split (2026-11-14 audit of runs #20–#33, none of which finished green):

- macOS jobs were never assigned a runner and were cancelled within a second.
- Linux test compilation was killed after ~14 minutes on the 16 GB `ubuntu-latest` runner. The
  test job now frees disk space, adds 12 GB of swap, caps parallel rustc jobs at 2, and skips
  building the `integration` crate.
- Windows test compilation took ~33 minutes and hit the job timeout; Windows clippy hit its
  20-minute timeout. Windows compile breakage is still caught by the release-flag check.

Removed because they only work for Warp Inc.: GCP login and the SSH integration tests (Warp's
test VM), trunk.io result uploads (Warp's account), the `agent_mode_evals` compile check (feeds
`warpdotdev/agent-mode-evals`), and the disabled remote-server job.

When merging `warpdotdev/warp` `master`, expect `.github/workflows/` to gain upstream files
again. Reconcile by keeping `ci.yml` fork overrides (owner + runners, no repo-sync lint) and
deleting reintroduced upstream-only workflows unless you intentionally adopt them.
