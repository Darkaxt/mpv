"""Exercise the delivered DLL on real Windows, including GPU-next DV mapping."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import urllib.request
import zipfile

FIXTURES = {
    '5': ('glass-blowing2-dolby-vision-profile-5-frag.mp4',
          'd21fc3938a813b6ce25efe890074b23d966a5828c9a3d33de7e8591a25dd2036'),
    '8': ('glass-blowing2-dolby-vision-profile-8-1-frag.mp4',
          '2cbedc36cf1ec2fdaaa54d26942ff93faeda4d4b2baf9fd25ee74bfebc15287e'),
}
CHROMIUM = '42f97fae10fbc8754f31dee18264a99d3124b93f'


class Event(C.Structure):
    _fields_ = [('event_id', C.c_int), ('error', C.c_int),
                ('reply_userdata', C.c_uint64), ('data', C.c_void_p)]


class Log(C.Structure):
    _fields_ = [('prefix', C.c_char_p), ('level', C.c_char_p),
                ('text', C.c_char_p), ('log_level', C.c_int)]


def check(result):
    if result < 0:
        raise RuntimeError(f'libmpv error {result}')
    return result


def verify(archive, backend='warp'):
    archive = archive.resolve()
    directory = archive.parent
    extracted = directory / 'runtime-verification'
    with zipfile.ZipFile(archive) as package:
        package.extractall(extracted)
    runtime = extracted / 'nuviodv-windows-x64'
    manifest = json.loads((runtime / 'manifest.json').read_text())
    dll = runtime / 'libmpv-2.dll'
    dll_directory = os.add_dll_directory(str(runtime))
    mpv = C.CDLL(str(dll))
    mpv.mpv_client_api_version.restype = C.c_ulong
    mpv.mpv_create.restype = C.c_void_p
    mpv.mpv_set_option_string.argtypes = [C.c_void_p, C.c_char_p, C.c_char_p]
    mpv.mpv_initialize.argtypes = [C.c_void_p]
    mpv.mpv_request_log_messages.argtypes = [C.c_void_p, C.c_char_p]
    mpv.mpv_command.argtypes = [C.c_void_p, C.POINTER(C.c_char_p)]
    mpv.mpv_wait_event.argtypes = [C.c_void_p, C.c_double]
    mpv.mpv_wait_event.restype = C.POINTER(Event)
    mpv.mpv_get_property_string.argtypes = [C.c_void_p, C.c_char_p]
    mpv.mpv_get_property_string.restype = C.c_void_p
    mpv.mpv_free.argtypes = [C.c_void_p]
    mpv.mpv_terminate_destroy.argtypes = [C.c_void_p]
    api = mpv.mpv_client_api_version()
    if api >> 16 != 2:
        raise RuntimeError(f'Unexpected client API: {api}')

    def command(handle, *args):
        encoded = [str(arg).encode() for arg in args] + [None]
        check(mpv.mpv_command(handle, (C.c_char_p * len(encoded))(*encoded)))

    def get(handle, name):
        ptr = mpv.mpv_get_property_string(handle, name.encode())
        if not ptr:
            return None
        try:
            return C.string_at(ptr).decode()
        finally:
            mpv.mpv_free(ptr)

    fixtures = extracted / 'fixtures'
    fixtures.mkdir()
    sdr = fixtures / 'sdr.ppm'
    sdr.write_bytes(b'P6\n64 64\n255\n' + bytes(
        component for y in range(64) for x in range(64)
        for component in (x * 4, y * 4, (x + y) * 2)))
    cases = [('sdr', sdr)]
    for profile, (name, expected) in FIXTURES.items():
        target = fixtures / name
        url = f'https://raw.githubusercontent.com/chromium/chromium/{CHROMIUM}/media/test/data/{name}'
        urllib.request.urlretrieve(url, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Fixture integrity failed: {name}')
        cases.append((profile, target))
    report = {'mpv_source': manifest['mpv_source'], 'api_version': api,
              'dll_sha256': hashlib.sha256(dll.read_bytes()).hexdigest(),
              'backend': backend, 'cases': []}
    for profile, sample in cases:
        handle = mpv.mpv_create()
        if not handle:
            raise RuntimeError('mpv_create failed')
        logs = []
        try:
            options = {'config': 'no', 'vo': 'gpu-next', 'gpu-api': 'd3d11',
                       'gpu-context': 'd3d11', 'd3d11-warp': 'yes' if backend == 'warp' else 'no',
                       'hwdec': 'no', 'ao': 'null', 'pause': 'yes',
                       'keep-open': 'yes', 'force-window': 'yes', 'osc': 'no',
                       'input-default-bindings': 'no', 'load-scripts': 'no',
                       'target-prim': 'bt.709', 'target-trc': 'srgb'}
            for key, value in options.items():
                check(mpv.mpv_set_option_string(handle, key.encode(), value.encode()))
            check(mpv.mpv_request_log_messages(handle, b'v'))
            check(mpv.mpv_initialize(handle))
            command(handle, 'loadfile', sample)
            while True:
                # Wait for a real render event; no elapsed-time success heuristic.
                event = mpv.mpv_wait_event(handle, -1).contents
                check(event.error)
                if event.event_id == 2:
                    entry = C.cast(event.data, C.POINTER(Log)).contents
                    logs.append((entry.prefix + b': ' + entry.text).decode(errors='replace'))
                elif event.event_id == 21:  # PLAYBACK_RESTART after first rendered frame
                    matrix = get(handle, 'video-params/colormatrix')
                    vo = get(handle, 'current-vo')
                    count = int(get(handle, 'track-list/count') or 0)
                    found_profile = next((get(handle, f'track-list/{i}/dolby-vision-profile')
                        for i in range(count) if get(handle, f'track-list/{i}/type') == 'video'), None)
                    if vo != 'gpu-next':
                        raise RuntimeError(f'Unexpected video output: {vo}')
                    if profile != 'sdr' and (found_profile != profile or matrix != 'dolbyvision'):
                        raise RuntimeError(f'DV was not mapped: profile={found_profile}, matrix={matrix}')
                    screenshot = directory / f'{backend}-{profile}.png'
                    command(handle, 'screenshot-to-file', screenshot, 'video')
                    png = screenshot.read_bytes()
                    if (png[:8] != b'\x89PNG\r\n\x1a\n' or png[12:16] != b'IHDR'
                            or len(png) < 24 or not all(struct.unpack('>II', png[16:24]))):
                        raise RuntimeError('Rendered screenshot is not a valid nonempty PNG')
                    report['cases'].append({'profile': profile, 'detected_profile': found_profile,
                        'matrix': matrix, 'vo': vo, 'screenshot_sha256': hashlib.sha256(screenshot.read_bytes()).hexdigest()})
                    break
                elif event.event_id in (1, 7):
                    raise RuntimeError(f'Playback ended before the first render: {event.event_id}')
        finally:
            mpv.mpv_terminate_destroy(handle)
            (directory / f'{backend}-{profile}.log').write_text(''.join(logs), encoding='utf-8')
    (directory / f'verification-{backend}.json').write_text(json.dumps(report, indent=2) + '\n')
    # Every delivered zip: the runtime and, when built, its separate debug symbols.
    sums = [f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
            for path in sorted(archive.parent.glob('nuviodv-windows-x64*.zip'))]
    (directory / 'SHA256SUMS').write_text(''.join(sums))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    verify(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else 'warp')
