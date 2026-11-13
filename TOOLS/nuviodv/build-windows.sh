#!/usr/bin/env bash
# Owned Dolby Vision baseline; reuse mpv's full static Windows CI build.
set -euo pipefail
: "${FFBUILD_PREFIX:?Use the pinned FFmpeg-Builds container from sources.json}"
# checkout's Node action and this container shell use different home/config
# bindings. Trust only this explicitly checked-out source, before version probes.
git config --global --add safe.directory "$PWD"
export NUVIODV_SOURCE_LOCK=1 NUVIODV_BUILD_JOBS=2
export CMAKE_BUILD_PARALLEL_LEVEL=2 CARGO_BUILD_JOBS=2 MAKEFLAGS=-j2
export CARGO_NET_OFFLINE=false
# Separate GNU debug files for libmpv (and the static libplacebo inside it).
export NUVIODV_DEBUG_SYMBOLS=1

python3 TOOLS/nuviodv/sources.py clone https://github.com/haasn/libplacebo.git libplacebo
# Windows/NVIDIA Vulkan presentation fixes from the-database/mpv-winbuild
# (see TOOLS/nuviodv/patches/libplacebo/PROVENANCE.md); AnimeJaNai uses Vulkan.
python3 TOOLS/nuviodv/sources.py patch libplacebo
meson setup libplacebo/build libplacebo --cross-file=/cross.meson \
    --prefix="$FFBUILD_PREFIX" --buildtype=release -Ddebug=true --default-library=static \
    -Dvulkan=enabled -Dopengl=enabled -Dd3d11=enabled \
    -Dvk-proc-addr=enabled \
    -Dvulkan-registry="$FFBUILD_PREFIX/share/vulkan/registry/vk.xml" \
    -Dshaderc=enabled -Dglslang=disabled -Dlcms=enabled -Dxxhash=enabled \
    -Ddemos=false -Dtests=false -Dbench=false -Dfuzz=false
meson compile -C libplacebo/build -j 2
meson install -C libplacebo/build
# Needed by the statically linked C++ shader generation code, as in the image recipe.
echo 'Libs.private: -lstdc++' >> "$FFBUILD_PREFIX/lib/pkgconfig/libplacebo.pc"

bash ci/build-mingw64-full.sh
meson test -C build --num-processes 2 --print-errorlogs
python3 TOOLS/nuviodv/package.py
