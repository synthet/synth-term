# Tasks: Synth Term — fork hardening and rename

Spec: [spec.md](spec.md). One task is one PR. Heavy `warp`-crate test builds run on tridentx, because zephyr runs out of memory on them.

## Traceability matrix

| AC | Tasks | Verification |
|----|-------|--------------|
| AC-1 | T-1 | python -I scripts/ci/check_fork_features.py |
| AC-2 | T-1 | python -I scripts/ci/check_fork_features.py --upstream FETCH_HEAD |
| AC-3 | T-2 | script/fork-check |
| AC-18 | T-2 | script/fork-check exits non-zero after removing one SYNTH-FORK marker |
| AC-4 | T-3 | python -I scripts/ci/check_fork_features.py |
| AC-5 | T-3 | python -I scripts/fork/sync_report.py --upstream FETCH_HEAD |
| AC-6 | T-4 | python -m pytest scripts/ci/tests -q |
| AC-19 | T-4 | python -m pytest scripts/ci/tests -q (edited-frozen-spec fixture) |
| AC-7 | T-5 | python -I scripts/ci/check_fork_identity.py (reads state.rs, single_instance_manager.rs, deploy.ps1, *.iss, *.desktop) |
| AC-8 | T-5, T-6 | cargo nextest run -p warp_core -E 'test(identity)'; deploy.ps1 -WhatIf |
| AC-9 | T-6 | iscc dry compile + review of [UninstallDelete] |
| AC-10 | T-7 | deploy.ps1 -WhatIf; script/macos/bundle and script/linux/bundle dry runs |
| AC-11 | T-7 | cargo nextest run -p warp_core -E 'test(migrate)' |
| AC-12 | T-8, T-9 | branding scan script + about_page/onboarding tests |
| AC-13 | T-10 | asset reference test |
| AC-14 | T-11 | links guard test + boundary baseline |
| AC-15 | T-11 | drive gating tests |
| AC-16 | T-13 | deploy.ps1 then the recorded commit file in the install |
| AC-20 | T-13 | deploy.ps1 -WhatIf with a missing-notice fixture |
| AC-17 | T-14 | wiki lint / link check |

## Task table

| ID | Task | Owner role | Files / areas | Depends on | ACs | Verification |
|----|------|------------|---------------|------------|-----|--------------|
| T-1 | Land the fork feature registry and boundary guard: rebase feat/fork-feature-registry, feat/agent-page-trim and feat/fork-guard-tests onto master, refresh claims for the 10 new master commits, verify on tridentx | fork-tooling | fork/features.toml, fork/boundary-baseline.txt, scripts/ci/check_fork_features.py, scripts/ci/check_fork_boundary.py, .claude/skills/sync-upstream-fork | - | AC-1, AC-2 | python -I scripts/ci/check_fork_features.py; nextest guard filter on tridentx |
| T-2 | Add a local, network-free script/fork-check that runs the registry check, the boundary check and the guard-test filter, and call it from script/presubmit | fork-tooling | script/fork-check, script/presubmit, fork/guard_filter.txt | T-1 | AC-3, AC-18 | script/fork-check exits 0 on master and non-zero after removing one SYNTH-FORK marker |
| T-3 | Pin the upstream baseline in fork/upstream.toml and add scripts/fork/sync_report.py: upstream commits since the pin, registered features touched, git merge-tree predicted conflicts; wire it into the sync-upstream-fork skill step 1 | fork-tooling | fork/upstream.toml, scripts/fork/sync_report.py, scripts/fork/tests/, .claude/skills/sync-upstream-fork/SKILL.md | T-1 | AC-4, AC-5 | python -m pytest scripts/fork/tests -q; report against a fetched FETCH_HEAD |
| T-4 | Frozen fork specs: front matter status draft/frozen plus a content hash; check_fork_features.py fails on an edited frozen spec; document "supersede, don't edit" | fork-tooling | specs/SYNTH-*/, scripts/ci/check_fork_features.py, scripts/ci/tests/ | T-1 | AC-6, AC-19 | python -m pytest scripts/ci/tests -q |
| T-5 | Identity guard first (red): scripts/ci/check_fork_identity.py compares the identifiers in source, scripts, installers and .desktop files with the upstream values; then a fork product-identity constant that derives the mutex, pipe, URL scheme and App Paths names | app-windows | scripts/ci/check_fork_identity.py, crates/warp_core/src/channel/state.rs, crates/warp_core/src/identity.rs (new), app/src/app_services/windows/single_instance_manager.rs, app/src/app_services/windows/registry.rs, fork/features.toml | T-1 | AC-7, AC-8 | python -I scripts/ci/check_fork_identity.py; cargo nextest run -p warp_core -E 'test(identity)' |
| T-6 | Windows installer and deploy identities: fork-owned Inno AppId, registry root, verbs and shortcut AUMID; UninstallDelete limited to fork folders; deploy.ps1 stops writing App Paths\warp-oss.exe and cleans its own old entries | app-windows | script/windows/windows-installer.iss, script/windows/tui-installer.iss, script/windows/deploy.ps1, script/windows/bundle.ps1 | T-5 | AC-8, AC-9 | deploy.ps1 -WhatIf; review of [UninstallDelete] and [Registry] |
| T-7 | Binary and app id rename: synth-term exe, sterm CLI, io.github.synthet.term on Windows/macOS/Linux bundles and .desktop file; one-time copy of Synth Warp data into the new data folder | app-core | app/Cargo.toml, app/src/bin/oss.rs, crates/warp_core/src/app_id.rs, crates/warp_core/src/paths.rs, script/macos/bundle, script/linux/bundle, app/channels/oss/*.desktop, docs/technical/app-id.md | T-5 | AC-10, AC-11 | cargo nextest run -p warp_core -E 'test(migrate) or test(app_id)'; deploy.ps1 -WhatIf |
| T-8 | Product-name strings, app chrome, lifecycle, About, onboarding and settings: Warp and Synth Warp become Synth Term per the branding audit, keeping factual upstream references | app-ui | app/src/root_view.rs, app/src/settings_view/, crates/onboarding/, app/src/app_menus.rs, app/src/workspace/ | T-7 | AC-12 | about_page and onboarding tests; branding scan |
| T-9 | Product-name strings, AI, agent, CLI-agent plugin prompts and TUI zero state (Warp Agent becomes Agent, Warpify becomes Shell integration) | app-ui | app/src/terminal/input.rs, app/src/terminal/cli_agent_sessions/, app/src/ai/, crates/warp_tui/ | T-7 | AC-12 | tui render-to-lines tests; branding scan |
| T-10 | Logo assets: redraw warp-drive, warp-2, warp-3, warp-logo-* and warp.svg from assets/branding/synth-term masters; fix the Icon::Warp/WarpDrive swap; TUI ASCII mark; delete dead warp-loading frames | app-ui | app/assets/, crates/warpui icons map, crates/warp_tui | T-1 | AC-13 | asset reference test; visual check |
| T-11 | Links and Drive policy bugs from the branding audit: route docs.warp.dev links through one gated helper, remove hardcoded warpdotdev issue links, gate every Drive surface on Drive availability, gate the welcome-slide login and TUI credit fallback | app-ui | app/src/util/links.rs, app/src/terminal/shell_terminated_banner.rs, app/src/ai/blocklist/, app/src/drive/, app/src/settings_view/ | T-1 | AC-14, AC-15 | links and drive guard tests; check_fork_boundary.py |
| T-12 | Survey other forks' features (Zap, warp-lite, man-brain local agent, oh-my-warp, Gram and Zedless practices): verify each claim in its source, check overlap with upstream BYOM, and present a pick table to the owner. No porting | research | docs/reports/fork-feature-candidates.md | - | - | owner pick recorded |
| T-13 | Release compliance in deploy.ps1: write the source commit into the install, fail when LICENSE-AGPL, LICENSE-MIT, the fork notice or THIRD_PARTY_LICENSES.txt is missing | release | script/windows/deploy.ps1, script/windows/prepare_bundled_resources.ps1 | - | AC-16, AC-20 | deploy.ps1 -WhatIf; missing-file fixture |
| T-14 | Document the fork development model in synth-fork.md: merge sync plus registry, frozen specs, fork-check, sync report, identity rules; update README and CANONICAL_SOURCES | docs | docs/architecture/synth-fork.md, README.md, docs/CANONICAL_SOURCES.md | T-2, T-3, T-4, T-7 | AC-17 | wiki-lint |

## Execution order

1. Foundation: T-1, then T-2, T-3 and T-4 in parallel.
2. Identity: T-5, then T-6 and T-7 in parallel.
3. Branding: T-8, T-9 (after T-7), T-10, T-11 (after T-1), parallel-safe across files.
4. Independent now: T-12 (research) and T-13 (after the paused deploy build resumes and finishes).
5. Close: T-14.

## Definition of done

- script/fork-check is green on master.
- Guard tests pass on tridentx.
- deploy.ps1 -WhatIf lists only fork-owned identities.
- check_fork_boundary.py shows no new upstream-brand literals beyond the reviewed baseline.
