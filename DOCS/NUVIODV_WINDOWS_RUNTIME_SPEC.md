# NuvioDV Windows Dolby Vision runtime

Authorization: the 2026-11-08 request to import Dolby Vision support into
`Darkaxt/mpv` and update its README. AnimeJaNai and SVP integration are separate
subsequent features. This specification covers a usable native Windows release,
not promotion into a Nuvio application release.

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
  this request does not implement the next feature or promote a new app runtime.
- DV5: Explain the Windows/Android difference and actual capabilities in README.
  Windows uses FFmpeg/libplacebo; it does not need the Android wrapper or a
  separately linked libdovi. Keep the three-day native maintenance coverage.

## Execution and reconciliation

| Stage | Status | Requirements / acceptance | Evidence and remaining work |
| --- | --- | --- | --- |
| Owned Dolby Vision build and verification | ACTIVE | DV1-DV3, DV5: complete pinned pipeline, accurate README, Windows runtime verification | Implement and run the build and runtime checks. |
| Native release and delivery verification | NOT STARTED | DV4: normal release, independently retrieved and verified artifact; final reconciliation | Requires the first stage to pass. |

Current advancement blockers: build/runtime verification and publication have
not yet occurred. No tracked deferrals within this bounded request.

Build diagnosis: initial run `42526378064` stopped at Meson's compiler sanity
check because Wine inherited GitHub's differently owned home directory. The
container now supplies an owned `/tmp/nuviodv-wine` prefix, as required by the
upstream full-build workflow. No native compilation or memory failure occurred.

## Build and rollback policy

Build on GitHub-hosted infrastructure, Windows x64 outputs only. No local WSL
or Gradle build is required. Use two compiler workers. Pin the cross-build image
by digest; explicitly pin source-built dependencies. Record the resolved image,
tool versions, configured dependencies and full build logs in the artifact.

NuvioDesktopDV continues to use DLL SHA-256
`04e4d27dc385dc18ddd93fbe69c75e635b864f3c6ec53a9122df54c2f7842f4a`.
NuvioMobileDV continues to use its existing Android AAR. Neither is changed by
native release publication. Candidate failure therefore needs no app rollback.
