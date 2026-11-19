# Synth Warp

**Synth Warp** is a commercial-free, local-first fork of [Warp](https://github.com/warpdotdev/warp)’s open-source client.

Synth Warp is an independent open-source fork of Warp, originally developed by Denver Technologies, Inc. It is not affiliated with or endorsed by Warp.

It keeps the terminal and local tooling, and removes billing, upgrades, credits, referrals, Warp Drive cloud sync, and hosted Warp AI/credit flows. Use external CLI agents (Claude Code, Codex, Gemini CLI, and others) or BYOK where the client supports them.

## What this fork is

- Local-first terminal / agentic IDE client
- No Stripe billing, plan upgrades, credit packs, or referral UI
- No Warp Drive cloud sync or hosted Warp-credit AI surfaces
- Runs without a Warp account for local use
- Licensed under the same terms as upstream: **AGPL v3** for the app, **MIT** for `warpui` / `warpui_core`

## What this fork is not

Warp’s server, Drive backend, and hosted agent inference are **not** in this repository and are not recreated here. Synth Warp does not unlock paid Warp cloud services against Warp’s servers.

## Building

```bash
./script/bootstrap   # platform-specific setup
./script/build       # resumable compile (re-run after OOM or interrupt)
./script/run         # build and run Synth Warp
./script/presubmit   # fmt, clippy, and tests
```

On Windows, `.\script\windows\build.ps1` (or `.\script\build.cmd`) sets up MSVC and retries with fewer jobs after a crash. Incremental artifacts in `target\` are reused unless you pass `-Clean` / `--clean`.

See [AGENTS.md](AGENTS.md) for the engineering guide and [docs/](docs/README.md) for design notes, including the [Zed × Warp hybrid](docs/zed-warp/README.md).

## Licensing

- UI framework crates (`warpui_core`, `warpui`): [MIT](LICENSE-MIT)
- Everything else in this repository: [AGPL v3](LICENSE-AGPL)

Distributing modified builds requires complying with AGPL (including source availability for network-used modifications).

The license summary shipped with the app, including the no-warranty and non-affiliation statements, is [legal/synth-warp-notice.md](legal/synth-warp-notice.md).

## Trademarks

"Warp" and the Warp logo are trademarks of their owner. This fork uses the name only to identify the upstream project; the open-source licenses do not grant trademark rights.

## Upstream

Forked from [warpdotdev/warp](https://github.com/warpdotdev/warp), the original project by Denver Technologies, Inc.
