---
title: Synth Term — fork hardening and rename
status: draft
owner: zephyr (warp session)
created: 2026-11-19
---

# Synth Term — fork hardening and rename

## Summary

Synth Warp becomes **Synth Term** (exe `synth-term`, CLI `sterm`, scheme `synthterm://`, app id
`io.github.synthet.term`). It also gets fork tooling that keeps it stable on top of upstream
`warpdotdev/warp`. The fork keeps its merge-based "unwire, don't delete" sync (owner decision,
2026-11-19). It adds a machine-checked feature registry, identity guards, frozen fork specs, a pinned
upstream baseline with a sync report, and a local presubmit fork check, so a merge can't silently
undo a fork change and the fork doesn't depend on GitHub CI.

## Users / stakeholders

- The owner, who runs Synth Term beside official Warp on Windows, macOS and Linux.
- Agents on zephyr, tridentx and strix, who merge upstream and change fork features.

## Product scenario

Today, an upstream merge can revert fork behavior with no conflict marker, and nothing flags it until
someone sees it in the UI. Fork identifiers still equal upstream's in places: the Windows mutex, named
pipe and URL scheme, App Paths, and the Inno AppId plus an uninstaller that deletes upstream's data
folders. So Synth Warp can lock against or overwrite another `warp-oss` build. About 220 Rust files
still show "Warp" to users. After this epic, every fork change is registered and guarded, a sync
starts from a report that lists the risky files, the product has its own name and identity, and the
guards run locally in one command.

## Non-goals

- Converting the fork to a patch series or overlay. The owner chose merge-based sync.
- Renaming internal crate, module or type names (`warp_core`, `Channel::Oss` strings excepted where
  they leak into identifiers). Keeping them is what keeps merges small.
- Porting features from other forks in this epic. T-12 only proposes candidates for the owner to pick.
- New GitHub workflows. Checks run locally, and existing CI may call the same scripts.
- Publishing, tagging or merging release PR #16.

## User stories

- As a fork maintainer, I want a merge that drops a fork change to fail a local check, so regressions
  are caught before push.
- As a fork maintainer, I want a sync report before merging upstream, so I know which fork features
  are at risk.
- As a user, I want Synth Term to run next to official Warp and other Warp forks without stealing
  their windows, URL scheme or data.
- As a user, I want the app to say Synth Term, not Warp, everywhere except factual upstream
  attribution.
- As a user upgrading from Synth Warp, I want my settings and history kept.

## Acceptance criteria

- **AC-1**: The fork shall list every fork behavior in `fork/features.toml` with code markers, guard
  tests and a reapply recipe, checked by `scripts/ci/check_fork_features.py`.
- **AC-2**: When `check_fork_features.py --upstream <ref>` runs, the fork shall report every file that
  diverges from that upstream ref and that no registered feature claims.
- **AC-3**: When `script/fork-check` runs on a developer machine, the fork shall run the registry check,
  the boundary check and the guard tests, and shall exit non-zero if any fails, without network or
  GitHub access.
- **AC-4**: The fork shall record the last merged upstream commit and date in `fork/upstream.toml`.
- **AC-5**: When `scripts/fork/sync_report.py` runs against a fetched upstream ref, the fork shall write a
  report listing the upstream commits since the pin, the registered features whose files those
  commits touch, and the predicted conflicted files.
- **AC-6**: A fork spec whose front matter says `status: frozen` shall be changed only by adding a
  superseding spec. `check_fork_features.py` shall fail when a frozen spec's recorded hash no longer
  matches its content.
- **AC-7**: If the Windows single-instance mutex, URI named pipe, URL scheme, App Paths key, installer
  AppId, installer registry root or Linux desktop id equals the upstream value, then a guard test
  shall fail.
- **AC-8**: The OSS GUI build shall use the mutex, pipe, scheme `synthterm`, App Paths `synth-term.exe`
  and an installer AppId that are all fork-owned.
- **AC-9**: If the Inno uninstaller runs, then it shall delete only fork-owned folders.
- **AC-10**: The OSS build shall produce the binary `synth-term` (Windows `synth-term.exe`) with bundle and
  app id `io.github.synthet.term` on Windows, macOS and Linux.
- **AC-11**: When Synth Term first starts on a machine that has Synth Warp data and no Synth Term data,
  it shall copy the Synth Warp settings and history into the Synth Term data folder and leave the
  originals unchanged.
- **AC-12**: The OSS build shall show "Synth Term" instead of "Warp" or "Synth Warp" in window titles,
  About, onboarding, settings, lifecycle prompts, notifications and the TUI zero state, except the
  strings the branding audit lists as factual upstream references.
- **AC-13**: The OSS build shall show Synth Term logo assets wherever it showed a Warp logo.
- **AC-14**: While `warp_inc_links_enabled()` is false, the OSS build shall show no docs.warp.dev or
  github.com/warpdotdev link, except attribution.
- **AC-15**: While Warp Drive is unavailable, the OSS build shall show no Warp Drive surface.
- **AC-16**: When `deploy.ps1` stages a build, it shall record the source commit in the install, and
  shall fail if `LICENSE-AGPL`, `LICENSE-MIT`, the fork notice or `THIRD_PARTY_LICENSES.txt` is missing.
- **AC-17**: The fork shall document its sync model, registry, frozen specs, presubmit check and identity
  rules in `docs/architecture/synth-fork.md`.

## Assumptions and dependencies

- The three local branches (`feat/fork-feature-registry`, `feat/agent-page-trim`,
  `feat/fork-guard-tests`) are the basis for AC-1 and AC-2. They are 10 commits behind master and need
  a rebase plus verification on tridentx, because zephyr runs out of memory on the `warp` test crate.
- Strix's branding audit (branch `docs/warp-ui-branding-audit`) is the inventory for AC-12 to AC-15.
- The Synth Term masters already exist in `assets/branding/synth-term/`.
- Upstream is fetched by URL (`git fetch https://github.com/warpdotdev/warp.git master`), which keeps
  `.git/config` untouched.

## Open questions

- **OPEN QUESTION 1 (data dir):** copy Synth Warp data into the `synthet.term` folder on first start
  (AC-11, recommended), or keep the old data folder name forever?
- **OPEN QUESTION 2 (Inno installer):** keep it as a supported shipping path, with identities fixed
  (recommended, since README calls it the shipping path), or retire it in favor of `deploy.ps1`?
- **OPEN QUESTION 3 (channel naming):** derive mutex and pipe names from a fork product constant
  (recommended, small diff), or rename `Channel::Oss` itself (large merge surface)?

Sources: fork practices from the Gram, Zedless, warp-lite and Synth Zed projects (identity swap,
unwire-don't-delete, pinned upstream baseline, reviewed sync reports, per-release source links).
