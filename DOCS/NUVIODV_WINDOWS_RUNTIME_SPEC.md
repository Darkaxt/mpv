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

| Stage | Status | Requirements / acceptance | Evidence and remaining work |
| --- | --- | --- | --- |
| Owned Dolby Vision build and verification | COMPLETE | DV1-DV3, DV5: complete pinned pipeline, accurate README, Windows runtime verification | Run `42529472063` succeeded at `b473072ac2e9a36d595dda9a3d071e8fccb74448`. Windows client API 2.6 loaded the DLL; GPU-next/D3D11 WARP rendered SDR and DV Profiles 5/8.1 with the expected color matrices. Inspected rendered frames and independently downloaded artifact/checksum. Native contracts passed with one Wine lifetime skip. |
| Android native mpv update and AAR qualification | COMPLETE | DV6 and Android library R1-R7: compatible pinned native stack and exact public ARM64 artifact | Run `42532012258` passed at library source `84c7e40cb83ba66918edf4ce811b4a177b742c79`. Independently downloaded AAR SHA-256 `e8f5e4063a2db82a78c84350d8170ec7951a301488248b82b1bae9a4779bf02a` matches CI. Wrapper compatibility, all ARM64 ELF hashes/dependencies and both libdovi exports pass independent inspection. |
| NuvioMobileDV native integration and verification | ACTIVE | DV7 and mobile maintenance specification: exact AAR -> complete mobile verification and release preparation | Consume the exact qualified AAR, advance the fork counter/Android code and pass required contracts/full Android verification without changing unrelated app behavior. |
| Native and mobile release delivery verification | NOT STARTED | DV4, DV7: normal native release and signed mobile release, independently retrieved and verified; final reconciliation | Requires prior implementation stages to pass. |

Current-stage advancement blockers: mobile AAR integration, version/code advance
and required application verification remain. Final publication belongs to its
named delivery stage. No tracked deferrals within the current stage.

Qualified Windows candidate: DLL SHA-256
`ee27b3ca2b621a23a5d16c074767ee13fd81bc2cc215bf695cc085981e4591db`;
archive SHA-256
`a4ed90b0f7a890b2f8be642c00b4a34ba1b4ec8d9e1a013b836c0b368691a8e8`.
Read back Windows report and workflow success, compared independently retrieved
archive hash, and visually inspected the Profile 5/8.1 screenshots. Native public
release remains assigned to the final delivery stage. No app DLL pin changed.

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

Build on GitHub-hosted infrastructure, Windows x64 outputs only. No local WSL
or Gradle build is required. Use two compiler workers. Pin the cross-build image
by digest; explicitly pin source-built dependencies. Record the resolved image,
tool versions, configured dependencies and full build logs in the artifact.

NuvioDesktopDV continues to use DLL SHA-256
`04e4d27dc385dc18ddd93fbe69c75e635b864f3c6ec53a9122df54c2f7842f4a`.
NuvioMobileDV keeps its existing AAR until the newly authorized Android candidate
passes native and application qualification. Windows native release publication
does not change either app by itself. Preserve the prior AAR pin until promotion.
