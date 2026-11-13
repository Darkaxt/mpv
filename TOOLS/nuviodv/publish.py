"""Publish only after Windows qualification has completed successfully."""
import json
from pathlib import Path
import subprocess
import sys

directory = Path(sys.argv[1])
lock = json.loads(Path(__file__).with_name('sources.json').read_text())
report = json.loads((directory / 'verification-warp.json').read_text())
tag = lock['release']
notes = directory / 'release-notes.md'
animejanai = '-ajn.' in tag
if animejanai:
    notes.write_text(f'''Owned Windows x64 AnimeJaNai-capable libmpv from `{report['mpv_source']}`.

Built from Darkaxt/mpv branch `nuviodv-animejanai` (the-database/mpv with the owned
NuvioDV tooling merged) with pinned OpenSSL, FFmpeg and libplacebo, the OpenGL
sync-object leak correction and the vendored Windows/NVIDIA Vulkan presentation
patches. Includes `vf=animejanai`, VapourSynth support and the optional GPL
`ajn-mvtools.dll`, and the WASAPI explicit audio-session and device-role options.
Windows libmpv API and GPU-next SDR/Profile 5/Profile 8.1 rendering verified with
software decoding and D3D11 WARP. Separate GNU debug files for the stripped DLLs are
in `nuviodv-windows-x64-symbols.zip` when that asset is present.

Qualification candidate only: not promoted into Nuvio. The AnimeJaNai inference
library, TensorRT runtime and models are not part of this package.
''')
else:
    notes.write_text(f'''Owned Windows x64 Dolby Vision baseline from `{report['mpv_source']}`.

Built from Darkaxt/mpv with pinned FFmpeg and libplacebo, including the OpenGL
sync-object leak correction. Windows libmpv API and GPU-next SDR/Profile 5/Profile
8.1 rendering verified with software decoding and D3D11 WARP. Screenshots, runtime
logs, dependency lock, build evidence and checksums accompany the package.

This native release does not replace Nuvio's installed DLL. AnimeJaNai and SVP
integration follow separately. Native Dolby Vision display signaling, full Profile
7 FEL and long-playback compatibility are not certified by this smoke test.
''')
files = [directory / 'nuviodv-windows-x64.zip', directory / 'SHA256SUMS',
         directory / 'verification-warp.json']
files += sorted(directory.glob('nuviodv-windows-x64-symbols.zip'))
files += sorted(directory.glob('warp-*.png')) + sorted(directory.glob('warp-*.log'))
subprocess.run(['gh', 'release', 'create', tag, '--repo', 'Darkaxt/mpv',
                '--target', report['mpv_source'], '--title', f'NuvioDV Windows libmpv — {tag}',
                '--notes-file', str(notes),
                '--latest=false' if animejanai else '--latest', *map(str, files)], check=True)
