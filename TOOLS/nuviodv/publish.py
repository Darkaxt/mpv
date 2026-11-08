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
files += sorted(directory.glob('warp-*.png')) + sorted(directory.glob('warp-*.log'))
subprocess.run(['gh', 'release', 'create', tag, '--repo', 'Darkaxt/mpv',
                '--target', report['mpv_source'], '--title', 'NuvioDV Windows libmpv — Dolby Vision baseline 1',
                '--notes-file', str(notes), '--latest', *map(str, files)], check=True)
