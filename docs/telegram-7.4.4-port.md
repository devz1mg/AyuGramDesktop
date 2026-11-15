# AyuGram on Telegram Desktop 7.4.4

This is an unofficial development port, not an official AyuGram release.

## Source

- AyuGram baseline: `0f2a31bb4` (`dev`, based on Telegram Desktop 7.2.9).
- Upstream target: the stable Telegram Desktop tag `v7.4.4`, not `master`.
- Integration branch: `update/telegram-7.4.4`.
- The fork's default branch is left unchanged.
- `Telegram/lib_ui` and `Telegram/codegen` use pinned commits from companion forks in the same GitHub account. These commits merge the upstream library versions while retaining the AyuGram patches.
- The AyuGram TL generator and ICU fork are retained.

Clone the integration branch with all submodules:

```sh
git clone --recursive --branch update/telegram-7.4.4 https://github.com/devz1mg/AyuGramDesktop.git
```

## Windows builds on GitHub

The `AyuGram Windows x64 Debug` workflow runs on pushes to `update/**`:

https://github.com/devz1mg/AyuGramDesktop/actions/workflows/build-windows.yml

It uses a public Windows runner, MSVC 14.44, Windows SDK 10.0.26100.0, static Qt 6, and a single x64 Debug configuration. Dependency preparation uses the repository's own scripts. This does not install a compiler or Qt on the user's PC.

A successful run uploads an `AyuGram-windows-x64-Qt6-Debug-<commit>` artifact containing `AyuGram.exe`, its runtime modules, and `SHA256SUMS.txt`. Download and extract the complete archive; do not extract the executable alone. Artifacts expire after seven days. A failed run uploads available diagnostics instead, not a working application.

The binary is unsigned and intended for testing. The workflow checks the PE architecture and attempts startup with an empty, isolated profile. That smoke test does not verify account login or every AyuGram feature.

## Updates and account safety

Automatic updates are disabled by default and explicitly disabled in CI. The old AyuGram RSA/v1 update path cannot be carried into Telegram's v2-only updater unchanged. Do not enable updates without configuring and auditing a fork-specific signing and distribution system: Telegram's official update packages are not AyuGram packages.

Crash reporting is disabled for these development builds. No release-signing secrets or account session files are used by the workflow. The API configuration follows the values already published in AyuGram's build documentation; test-only API credentials are not used.

The source port and CI setup do not modify an installed client or existing account data. For manual runtime testing, use a separate working directory and do not point an unverified build at the only copy of an existing profile. Full runtime and feature testing must be reported separately from successful compilation.
