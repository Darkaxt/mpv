"""Fetch only the exact sources approved by the NuvioDV native lock."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

LOCK = Path(__file__).with_name("sources.json")


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def clone(url, destination):
    lock = json.loads(LOCK.read_text())
    commit = lock["sources"][url]  # Unknown sources must fail, never float.
    target = Path(destination)
    if target.exists():
        raise RuntimeError(f"Source directory already exists: {target}")
    run("git", "init", str(target))
    run("git", "-C", str(target), "remote", "add", "origin", url)
    fetch = ["git", "-C", str(target), "fetch", "--filter=blob:none"]
    # Full ancestry is needed to establish inclusion of the OpenGL leak fix.
    if "libplacebo" not in url:
        fetch += ["--depth=1"]
    run(*fetch, "origin", commit)
    run("git", "-C", str(target), "checkout", "--detach", commit)
    run("git", "-C", str(target), "submodule", "update", "--init", "--recursive",
        "--depth=1")
    if "libplacebo" in url:
        run("git", "-C", str(target), "merge-base", "--is-ancestor",
            lock["libplacebo_fix"], "HEAD")


def patch(destination):
    """Apply exactly the hashed libplacebo patch set recorded in the lock."""
    lock = json.loads(LOCK.read_text())
    directory = LOCK.parent / "patches" / "libplacebo"
    present = sorted(p.name for p in directory.glob("*.patch"))
    if present != sorted(lock.get("libplacebo_patches", {})):
        raise RuntimeError(f"Patch set differs from lock: {present}")
    for name, digest in sorted(lock["libplacebo_patches"].items()):
        path = directory / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Patch hash mismatch: {name}")
        run("git", "-C", str(destination), "apply", "--ignore-space-change",
            str(path.resolve()))


if __name__ == "__main__":
    if sys.argv[1] == "clone":
        clone(*sys.argv[2:])
    elif sys.argv[1] == "patch":
        patch(*sys.argv[2:])
    else:
        raise SystemExit("usage: sources.py clone URL DESTINATION | patch DESTINATION")
