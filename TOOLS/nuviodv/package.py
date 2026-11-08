"""Package the owned native runtime and its source/build evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


def output(*args):
    return subprocess.check_output(args, text=True).strip()


root = Path.cwd()
lock = json.loads((root / 'TOOLS/nuviodv/sources.json').read_text())
package = root / 'nuviodv-windows-x64'
package.mkdir()
for name in ('artifact', 'artifact-libmpv'):
    shutil.copytree(root / name, package, dirs_exist_ok=True)
shutil.copy(root / 'README.md', package)
shutil.copy(root / 'Copyright', package)
shutil.copy(root / 'TOOLS/nuviodv/sources.json', package)
evidence = package / 'build-evidence'
evidence.mkdir()
shutil.copy(root / 'build/meson-logs/testlog.txt', evidence)
shutil.copy(root / 'build/meson-info/intro-buildoptions.json', evidence)
shutil.copy(root / 'build/meson-info/intro-dependencies.json', evidence)
shutil.copy(root / 'ffmpeg/ffbuild/config.log', evidence / 'ffmpeg-config.log')
licenses = package / 'dependency-licenses'
licenses.mkdir()
for name in ('ffmpeg', 'libplacebo', 'LuaJIT', 'libsixel', 'libarchive',
             'uchardet', 'subrandr', 'cppwinrt-2.0.250303.1', 'windows-rs',
             'subprojects/mujs'):
    source = root / name
    for path in source.iterdir():
        if path.is_file() and path.name.upper().startswith(('LICENSE', 'COPYING', 'COPYRIGHT')):
            target = licenses / name.replace('/', '-')
            target.mkdir(exist_ok=True)
            shutil.copy(path, target)
manifest = {
    'release': lock['release'],
    'mpv_source': output('git', 'rev-parse', 'HEAD'),
    'dependency_lock': lock,
    'pkg_config': output('pkg-config', '--modversion', 'libavcodec', 'libavutil', 'libplacebo'),
    'compiler': output('sh', '-c', '$CC --version'),
    'submodules': {name: output('git', '-C', name, 'submodule', 'status', '--recursive')
                   for name in ('libplacebo', 'ffmpeg', 'subrandr')},
    'qualification': 'Native Windows GPU-next smoke tests are recorded separately; no app promotion.',
}
(package / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
shutil.make_archive(str(root / 'nuviodv-windows-x64'), 'zip', root, package.name)
print(json.dumps(manifest, indent=2))
