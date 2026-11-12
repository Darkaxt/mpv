# NuvioDV Windows Dolby Vision runtime

Authorization: the 2026-11-08 request to import Dolby Vision support into
`Darkaxt/mpv` and update its README, followed by the user's instruction to update
Android mpv for consumption by Nuvio. AnimeJaNai and SVP integration are separate
subsequent features. Windows app-runtime promotion remains outside this request;
Android library and NuvioMobileDV integration are now explicitly included.

## Requirements

- DV1: Build Windows x64 mpv and libmpv from this fork. Retain upstream history
  and reuse the upstream full MinGW build, with immutable build inputs.
- DV2: Retain FFmpeg's Dolby Vision RPU parsing and libplacebo's reshaping,
  tone mapping and GPU-next rendering. Pin the existing known-good FFmpeg
  `9a861e9687d30e657d59521817cad18405995983`. Current mpv requires libplacebo
  API 387, exceeding the old Windows pin's API 377, so use libplacebo
  `9fabf6d5057c40089afb020017c6347002b07308`. Verify ancestry of libplacebo
  sync-object leak fix `c93aa134ab62365ce1177efff99b8e1e66a818e7`.
- DV3: Verify the actual Windows library's public API and SDR / Dolby Vision
  Profile 5 / Profile 8 playback through GPU-next on Windows. Hardware display
  signaling, full Profile 7 FEL reconstruction and long-playback compatibility
  are not established by these short native tests and must not be claimed.
- DV4: Publish a normal native release with DLL, CLI, public headers/import
  library, licenses, exact source/dependency manifest, checksums and build/test
  evidence. Independently retrieve the published package and verify its hash,
  contents and DLL API. Preserve the installed Nuvio runtime's existing pin;
  this request does not implement the next feature or promote a Windows app
  runtime. Android application delivery follows DV6-DV7 below.
- DV5: Explain the Windows/Android difference and actual capabilities in README.
  Windows uses FFmpeg/libplacebo; it does not need the Android wrapper or a
  separately linked libdovi. Keep the three-day native maintenance coverage.
- DV6 (added by direct user steering): Update the Android native mpv revision,
  reconcile the dependencies and carried Dolby Vision patches required by that
  revision, and verify the ARM64 release AAR under the Android library's
  `docs/NUVIO_LIBRARY_FORK_SPEC.md`. Preserve the 0.1.12 wrapper API, independent
  libplacebo leak correction and unrelated dependency pins where compatible.
- DV7: Consume that exact verified AAR in NuvioMobileDV, update runtime provenance
  and fork version/code, pass the mobile maintenance specification's required
  contracts/Android checks, and deliver a normal signed Android release. Verify
  the published APK and native payload. Do not silently claim device playback
  validation or access an Android endpoint without its managed workflow.

## Execution and reconciliation

### 2026-11-11 scheduled maintenance

Authorization: the recurring three-day maintenance instruction covers Android,
Desktop, Windows native mpv and the Android library, with normal releases and
independent artifact verification. Inspected upstream tips: Android `4135f96cd`,
Desktop `37ce07d35`, native mpv `bcde6b93cc`. All four checkouts were clean.
Android library has zero missing upstream commits and successful AAR run
`42532012258`; its existing qualified pin is retained without rebuilding.

| Maintenance stage | Status | Required acceptance / remaining work |
| --- | --- | --- |
| Android sync and normal delivery | COMPLETE | Source `e261d52ac` contains inspected upstream `4135f96cd`. Normal release `v0.6.12-nuviodv.1` / `12261` passes full Linux tests, signed build and authentication checks in run `43089796486`. Independent public APK SHA-256 `0ca27acd37c6d9eaceb83cd58956946b437ec34b244e2fa9e216c4de08179f8e`, signer/identity/updater and all ten pinned native libraries pass. Sync `43084002957` attempt 2 is a verified no-op. Mobile specification records complete failure/correction evidence; no test shadows or download production changes remain. |
| Desktop sync, Windows release and local upgrade | BLOCKED | Source `868730fb1736b184768a02952667a6514ad93701` integrates inspected upstream; full local tests/MSI and fork contracts passed. External GitHub orchestration inconsistency after incident `dvy0t3mvh1lg`: original run `43096139223` reports queued / attempt 1 with zero jobs, attempt 1 independently reports completed / startup_failure, and supported cancellation refuses because it considers the run completed. GitHub declared its backlog drained at 21:21 UTC; this is not a duration-based queue classification. No public `.5` release exists. Preserve the same identity and inspect for a consistent terminal/running state before supported recovery; never dispatch a duplicate. Independent public MSI verification, broker installation and installed/configuration/profile checks remain unmet. Installed `1.1.3504` is preserved. |
| Windows native sync and qualified release | COMPLETE | Normal release `nuviodv-windows-dv.2` from `6b4a48dfff89306a091f6d16e23c5aa888e2727f`, run `43101201701`, passes pinned native build/contracts and real Windows GPU-next SDR/P5/P8.1 checks. Independently retrieved ZIP `c7d406eacf434bfd07f81c9e5c73710aa12099548c4db0f4e03f5f00553d9148` and all public asset hashes match. DLL `df30ec9b4c458c778640e0aee93e46a8f0636abb981fb6d442e5aeef8149562d` loads API 2.6 locally; source/dependency lock, licenses, build/runtime evidence and DV frames inspected. Exact temporary DLL extraction cleaned after loader process exit. No app pin changed. |
| Issue delta triage and final reconciliation | COMPLETE | All four pushed source branches contain their inspected upstream tips; Android sync/release and unchanged Android AAR workflow are healthy, native DV 2 normal release is independently verified. Full paginated issue delta and baseline comments yield no newly actionable native-player evidence. Desktop's external blocker is recorded without claiming release/install completion. Reviewed cleanup `3ae4bd06e9b6685a3cf003e9344cdd69` applied 45 exact spent members / 394510230 bytes; native DLL extraction transaction `a5ed0c7f232902e6069c6e5b107920dd` applied 2 / 161483776 bytes after loader exit. Only six exact pending-Desktop recovery inputs remain in the documented E: recovery folder; no task D: scratch remains. |

Desktop resumed after reported service recovery, then its conflicting run/attempt
states and rejected cancellation established a concrete external orchestration
blocker. Original managed monitor identity is session `10797`, workflow
`43096139223`; no build was cancelled. Native qualification completed in original
run `43101201701`. No tracked deferral or ACTIVE implementation stage remains;
Desktop remains BLOCKED, so the overall requested maintenance is incomplete.

Final independent reconciliation: Android `5fd2caa9c` contains inspected upstream
`4135f96cd`; Desktop application source `868730fb1` (later evidence-only docs)
contains `37ce07d35`; native source `6b4a48dfff` (later evidence-only docs) contains
`bcde6b93cc`; Android wrapper `27bde9f7` is unchanged and zero behind FortunasXP.
Origin branch readbacks match the corresponding local commits. Android signed
normal release `v0.6.12-nuviodv.1` targets `e261d52ac`; native normal release
`nuviodv-windows-dv.2` targets `6b4a48dfff`; both have independently checked public
assets. Native packaged test evidence has zero failures and one known Wine-only
skip; the separate real Windows SDR/P5/P8.1 runtime gate passed. No app pin was
promoted. Local Gradle gates acquired the shared Windows mutex, used initial
3 GiB Gradle/Kotlin heaps, two workers/no parallel projects and one test fork,
reported no memory failure and verified whole-tree exit. No local WSL ran.

Resume Desktop by inspecting run `43096139223` plus its attempt endpoint until
GitHub's conflicting states reconcile. The accepted rerun must not be duplicated;
supported recovery requires a consistent terminal state or the existing actual
job result. Then verify normal `.5` release/tag/source, independently download
its exact public MSI, inspect version/configuration/checksums, install through
the elevation broker and verify installed/public JAR equality and preserved
profiles. Installed MSI remains `1.1.3504`; no administrator request was submitted
because a public replacement does not exist. Only the identity-checked local
`gh run watch` process was stopped when the external API blocker was established;
the GitHub workflow was not cancelled. Pending helper/baseline inputs at
`E:\Temp\nuviodv-maintenance-20261111-recovery` are retained for this exact consumer
and must be removed transactionally after delivery finishes. The Desktop parity
specification records the same recovery contract. No new feature stage passed.
Only one maintenance stage may be ACTIVE.
The completed baseline delivery below remains historical evidence.

Native source reconciliation: normal merge of inspected upstream `bcde6b93cc`
adds 27 commits, including Windows playback timer handling and archive stream
position fixes. Its Meson change replaces `ntdll` with `winmm`; it does not raise
the FFmpeg/libplacebo requirements. Upstream's cross-image rename only changes
the reusable build script's documentation. The owned workflow retains the exact
previous image digest and every source pin, including libplacebo leak-fix ancestry.
Candidate tag advances to `nuviodv-windows-dv.2`; the publisher now derives its
title from that tag rather than falsely naming every release baseline 1.
The complete pinned native build and real Windows SDR/P5/P8.1 qualification remain
mandatory before publication. No application AAR/DLL promotion is authorized by
this native source merge.

| Stage | Status | Requirements / acceptance | Evidence and remaining work |
| --- | --- | --- | --- |
| Owned Dolby Vision build and verification | COMPLETE | DV1-DV3, DV5: complete pinned pipeline, accurate README, Windows runtime verification | Run `42529472063` succeeded at `b473072ac2e9a36d595dda9a3d071e8fccb74448`. Windows client API 2.6 loaded the DLL; GPU-next/D3D11 WARP rendered SDR and DV Profiles 5/8.1 with the expected color matrices. Inspected rendered frames and independently downloaded artifact/checksum. Native contracts passed with one Wine lifetime skip. |
| Android native mpv update and AAR qualification | COMPLETE | DV6 and Android library R1-R7: compatible pinned native stack and exact public ARM64 artifact | Run `42532012258` passed at library source `84c7e40cb83ba66918edf4ce811b4a177b742c79`. Independently downloaded AAR SHA-256 `e8f5e4063a2db82a78c84350d8170ec7951a301488248b82b1bae9a4779bf02a` matches CI. Wrapper compatibility, all ARM64 ELF hashes/dependencies and both libdovi exports pass independent inspection. |
| NuvioMobileDV native integration and verification | COMPLETE | DV7 and mobile maintenance specification: exact AAR -> complete mobile verification and release preparation | Vendored qualified AAR `e8f5e406...`, shared checksum gates in sync/release, version `0.6.10-nuviodv.2` / `12259`. Contracts, focused player tests and full debug APK passed under mutex ticket `009a8bd351384cb6917a797357760a92`, with 3 GiB shared in-process Kotlin/Gradle heap, two workers/no parallel projects and verified daemon exit. Actual APK metadata/native payload verified. |
| Native and mobile release delivery verification | COMPLETE | DV4, DV7: normal native release and signed mobile release, independently retrieved and verified; final reconciliation | Normal Windows release `nuviodv-windows-dv.1` targets `b473072ac2e9a36d595dda9a3d071e8fccb74448`. Normal Android release `v0.6.10-nuviodv.2`, code `12259`, targets `82c8dada01798eabf6111a9f473e794cc3ee0163`; release run `42535938912` passed. Both public packages independently downloaded and verified as detailed below. DV1-DV7 satisfied; no blocker or deferral remains. |

Blockers and tracked deferrals: none. Final reconciliation satisfies DV1-DV7.
Device playback validation is not claimed by these builds.

Qualified Windows candidate: DLL SHA-256
`ee27b3ca2b621a23a5d16c074767ee13fd81bc2cc215bf695cc085981e4591db`;
archive SHA-256
`a4ed90b0f7a890b2f8be642c00b4a34ba1b4ec8d9e1a013b836c0b368691a8e8`.
Read back Windows report and workflow success, compared independently retrieved
archive hash, and visually inspected the Profile 5/8.1 screenshots. Normal public
release `nuviodv-windows-dv.1` targets native source `b473072ac2e9a36d595dda9a3d071e8fccb74448`.
Its public ZIP was independently retrieved: checksum, dependency/source manifest,
required CLI/DLL/header/license/build-evidence entries and loaded client API 2.6
all match. GitHub reports neither draft nor prerelease. No app DLL pin changed.

Build diagnosis: initial run `42526378064` stopped at Meson's compiler sanity
check because Wine inherited GitHub's differently owned home directory. The
container now supplies an owned `/tmp/nuviodv-wine` prefix, as required by the
upstream full-build workflow. No native compilation or memory failure occurred.

Run `42526614255` built libplacebo and FFmpeg, then exposed LuaJIT's independent
`amalg install` goals racing under the two-worker MAKEFLAGS setting: duplicate
host compiler invocations produced an invalid host/minilua object. The recipe
now completes `amalg` before invoking `install`, retaining two compiler workers.
This was a build-order failure, not a memory failure.

Verification-script diagnosis: encoding the exact 64x64 SDR fixture as PNG
produces a valid 206-byte file, below the original arbitrary 500-byte check.
Validate PNG signature/IHDR/nonzero dimensions instead. The workflow accepts an
existing build-run ID so verifier-only corrections exercise the same built DLL
without recompiling the native stack; provenance remains in its manifest.

Run `42527782064` completed native compilation and the executed Meson contracts
(16 passed, one libmpv lifetime test skipped by Wine). Packaging then failed
because the container shell did not inherit checkout's Git safe-directory
configuration. Configure the exact owned checkout before all version/provenance
probes. Failure artifacts now retain compiled CLI/DLL/header outputs plus build
metadata, rather than only logs, enabling package recovery without recompilation.
That completed runner did not upload its binaries, so those outputs cannot be
retrieved; the corrected source requires a new build. No memory failure occurred.

## Build and rollback policy

Build Windows native outputs on GitHub-hosted infrastructure, x64 only. No local
WSL is required. Android application verification uses the managed Windows Gradle
gate recorded above. Use two native compiler workers. Pin the cross-build image
by digest; explicitly pin source-built dependencies. Record the resolved image,
tool versions, configured dependencies and full build logs in the artifact.

NuvioDesktopDV continues to use DLL SHA-256
`04e4d27dc385dc18ddd93fbe69c75e635b864f3c6ec53a9122df54c2f7842f4a`.
NuvioMobileDV's qualified replacement AAR is committed at application source
`82c8dada01798eabf6111a9f473e794cc3ee0163`; normal signed release run `42535938912`
passed. The independently retrieved public APK for `v0.6.10-nuviodv.2` has SHA-256
`3daaf2c07f29eb7e6e0c535a7b2625f9083707a81592f19c2447a48209362e29`.
Verified package `com.darkaxt.nuviodv`, label `NuvioDV`, code `12259`, ARM64-only
native code, valid v2 signature with the existing signer, and updater reference
`Darkaxt/NuvioMobileDV`. All ten AAR native libraries, including the C++ runtime,
match the published APK byte-for-byte; libmpv SHA-256 is
`1c5bf5e2256b3a20fb41617cbd5d47b017d821c512f8dc850d88e617c1d0f8f8`.
CI's generated authenticated runtime configuration checks passed. The prior
AAR remains recoverable in Git history. Rollback publishes it with a higher
Android version code, preserving app data. Windows native publication does not
change the Desktop app by itself.
