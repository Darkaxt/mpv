#!/usr/bin/env bash
#
# Static mpv and libmpv builds on top of the FFmpeg-Builds container images
# (ghcr.io/ffmpeg-builds/ffmpeg-builds/<target>-<variant>, see
# https://github.com/FFmpeg-Builds/FFmpeg-Builds). The image ships the cross toolchain,
# a matching /cross.meson and every FFmpeg dependency as static library in
# $FFBUILD_PREFIX. OpenSSL is rebuilt without permanent DLL pinning for libmpv,
# along with FFmpeg and the things FFmpeg does not need. Run from the mpv tree:
#
#   docker run --rm -v "$PWD:/mpv" -w /mpv \
#       ghcr.io/ffmpeg-builds/ffmpeg-builds/win64-gpl:latest ./ci/build-mingw64-full.sh
#
# The mpv binaries end up in artifact/, the libmpv package in artifact-libmpv/.
set -euo pipefail

: "${FFBUILD_PREFIX:?not running in a FFmpeg-Builds image}"
: "${VARIANT:?not running in a FFmpeg-Builds image}"

. ./ci/build-common.sh

# The dependency headers are not ours to fix, keep --werror to mpv's own code.
CFLAGS="${CFLAGS/-I${FFBUILD_PREFIX}\/include/-isystem${FFBUILD_PREFIX}/include}"
CXXFLAGS="${CXXFLAGS/-I${FFBUILD_PREFIX}\/include/-isystem${FFBUILD_PREFIX}/include}"

gpl=false
[[ $VARIANT == gpl* ]] && gpl=true

clone_source() {
    local url=$1 destination=$2
    shift 2
    if [[ -n "${NUVIODV_SOURCE_LOCK:-}" ]]; then
        python3 TOOLS/nuviodv/sources.py clone "$url" "$destination"
    else
        git clone --depth=1 --recursive --shallow-submodules "$@" "$url" "$destination"
    fi
}
jobs=${NUVIODV_BUILD_JOBS:-$(nproc)}
group() { echo "::group::$1"; }
endgroup() { echo "::endgroup::"; }

group "Building unloadable OpenSSL"
# The image's static OpenSSL pins its containing DLL during curl_global_init.
# Preserve its version and features, but allow libmpv to unload after cleanup.
openssl_ver=$(PKG_CONFIG_PATH="$FFBUILD_PREFIX/lib/pkgconfig" pkg-config --modversion openssl)
clone_source https://github.com/openssl/openssl.git openssl -b "openssl-$openssl_ver"
pushd openssl
# The source must be exactly the image's OpenSSL release (a pinned lock may lag the image).
source_ver=$(. ./VERSION.dat && echo "$MAJOR.$MINOR.$PATCH")
[[ $source_ver == "$openssl_ver" ]] || {
    echo "OpenSSL source $source_ver does not match image OpenSSL $openssl_ver" >&2; exit 1; }
openssl_target=mingw64
[[ $FFBUILD_TOOLCHAIN == aarch64-* ]] && openssl_target=mingwarm64
CC="${CC/${FFBUILD_CROSS_PREFIX}/}" CXX="${CXX/${FFBUILD_CROSS_PREFIX}/}" \
AR="${AR/${FFBUILD_CROSS_PREFIX}/}" RANLIB="${RANLIB/${FFBUILD_CROSS_PREFIX}/}" \
CFLAGS="$CFLAGS -fno-strict-aliasing" \
./Configure "$openssl_target" --cross-compile-prefix="$FFBUILD_CROSS_PREFIX" \
            --prefix="$FFBUILD_PREFIX" --libdir=lib threads zlib no-shared no-pinshared \
            no-tests no-apps no-legacy no-ssl3 enable-camellia enable-ec enable-srp
make -j"$jobs" build_sw
make install_sw
popd
endgroup

group "Building FFmpeg"
clone_source https://github.com/FFmpeg/FFmpeg.git ffmpeg
pushd ffmpeg
# rav1e and librsvg bring their own Rust runtime, which clashes with subrandr's.
./configure --prefix="$FFBUILD_PREFIX" --pkg-config-flags="--static" \
            $FFBUILD_TARGET_FLAGS $FF_CONFIGURE \
            --extra-cflags="$FF_CFLAGS" --extra-cxxflags="$FF_CXXFLAGS" \
            --extra-libs="$FF_LIBS" --extra-ldflags="$FF_LDFLAGS" \
            --extra-ldexeflags="$FF_LDEXEFLAGS" \
            --cc="$CC" --cxx="$CXX" --ar="$AR" --ranlib="$RANLIB" --nm="$NM" \
            --enable-static --disable-shared --disable-{doc,programs} \
            --disable-{librav1e,librsvg,openal} || { cat ffbuild/config.log; exit 1; }
make -j"$jobs"
make install
popd
endgroup

group "Building LuaJIT"
clone_source https://github.com/LuaJIT/LuaJIT.git LuaJIT -b v2.1
pushd LuaJIT
# Strip -ldl, not needed for Windows.
sed -i "/^Libs\.private/d" etc/luajit.pc
# FILE_T and INSTALL_DEP are only needed to glue install target.
make TARGET_SYS=Windows PREFIX="$FFBUILD_PREFIX" HOST_CC="$HOST_CC" \
     CFLAGS="$HOST_CFLAGS" CROSS="$FFBUILD_CROSS_PREFIX" TARGET_CFLAGS="$CFLAGS" \
     BUILDMODE=static XCFLAGS=-DLUAJIT_ENABLE_LUA52COMPAT FILE_T=luajit.exe \
     INSTALL_DEP=src/luajit.exe amalg
# LuaJIT's install goal also invokes a build. Independent top-level goals race
# under MAKEFLAGS=-j2, including simultaneous writes to host/minilua.o.
make TARGET_SYS=Windows PREFIX="$FFBUILD_PREFIX" HOST_CC="$HOST_CC" \
     CFLAGS="$HOST_CFLAGS" CROSS="$FFBUILD_CROSS_PREFIX" TARGET_CFLAGS="$CFLAGS" \
     BUILDMODE=static XCFLAGS=-DLUAJIT_ENABLE_LUA52COMPAT FILE_T=luajit.exe \
     INSTALL_DEP=src/luajit.exe install
popd
endgroup

group "Building libsixel"
clone_source https://github.com/saitoha/libsixel.git libsixel
pushd libsixel
./configure --prefix="$FFBUILD_PREFIX" --host="$FFBUILD_TOOLCHAIN" --disable-shared \
            --disable-{img2sixel,sixel2png,python} --without-{jpeg,libcurl,png}
make -j"$jobs"
make install
popd
endgroup

group "Building libarchive"
clone_source https://github.com/libarchive/libarchive.git libarchive
mkdir -p libarchive/build
pushd libarchive/build
cmake -GNinja -DCMAKE_TOOLCHAIN_FILE="$FFBUILD_CMAKE_TOOLCHAIN" \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$FFBUILD_PREFIX" \
      -DBUILD_SHARED_LIBS=OFF -DENABLE_{CAT,CPIO,TAR,TEST,UNZIP}=OFF \
      -DENABLE_{LIBXML2,OPENSSL,PCRE2POSIX}=OFF ..
ninja -j"$jobs" install
popd
endgroup

group "Building uchardet"
clone_source https://gitlab.freedesktop.org/uchardet/uchardet.git uchardet -b v0.0.8
mkdir -p uchardet/build
pushd uchardet/build
cmake -GNinja -DCMAKE_TOOLCHAIN_FILE="$FFBUILD_CMAKE_TOOLCHAIN" \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$FFBUILD_PREFIX" \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      -DBUILD_SHARED_LIBS=OFF -DBUILD_BINARY=OFF ..
ninja -j"$jobs" install
popd
endgroup

group "Building subrandr"
build_subrandr "$FFBUILD_PREFIX" --target "$FFBUILD_RUST_TARGET" \
               --static-library true --shared-library false
endgroup

group "Building cppwinrt"
# win32-smtc needs the C++/WinRT projection headers, generated from the
# Windows metadata that windows-rs carries.
cppwinrt_ver=2.0.250303.1
windows_rs_ver=73
if [[ -n "${NUVIODV_SOURCE_LOCK:-}" ]]; then
    clone_source https://github.com/microsoft/cppwinrt.git "cppwinrt-$cppwinrt_ver"
    clone_source https://github.com/microsoft/windows-rs.git windows-rs
else
    wget -q "https://github.com/microsoft/cppwinrt/archive/${cppwinrt_ver}.tar.gz" -O - | tar -xz
    git clone --depth=1 --filter=blob:none --sparse -b "$windows_rs_ver" \
        https://github.com/microsoft/windows-rs.git
    git -C windows-rs sparse-checkout set crates/libs/bindgen/default
fi
mkdir -p "cppwinrt-$cppwinrt_ver/build"
pushd "cppwinrt-$cppwinrt_ver/build"
CFLAGS="$HOST_CFLAGS" CXXFLAGS="$HOST_CXXFLAGS" LDFLAGS= \
    cmake -GNinja -DCMAKE_CXX_COMPILER="$HOST_CXX" -DCMAKE_BUILD_TYPE=Release \
          -DCPPWINRT_BUILD_VERSION="$cppwinrt_ver" ..
ninja -j"$jobs" cppwinrt
./cppwinrt -input ../../windows-rs/crates/libs/bindgen/default \
           -output "$FFBUILD_PREFIX/include"
popd
endgroup

group "Building mpv"
mkdir -p subprojects
if [[ -n "${NUVIODV_SOURCE_LOCK:-}" ]]; then
    clone_source https://github.com/ArtifexSoftware/mujs.git subprojects/mujs
    cp TOOLS/nuviodv/mujs-meson.build subprojects/mujs/meson.build
else
    meson wrap install mujs
fi
meson subprojects download

mpv_args=(
    --cross-file /cross.meson $common_args
    --buildtype=release
    --prefer-static
    --default-library=shared
    # With --prefer-static meson searches for libiconv only in the compiler's
    # own directories, so pass it in the link args.
    # https://github.com/mesonbuild/meson/issues/10172
    -Dc_link_args="$FF_LIBS -L$FFBUILD_PREFIX/lib -liconv"
    -Dcpp_link_args="$FF_LIBS -L$FFBUILD_PREFIX/lib -liconv"
    -Dgpl=$gpl
    --force-fallback-for=mujs
    -Dmujs:werror=false
    -Dmujs:default_library=static
    -Dlua=luajit
    -D{amf,d3d11,iconv,javascript,lcms2,libarchive,libbluray,libcurl}=enabled
    -D{sdl2-audio,sdl2-gamepad,sdl2-video}=enabled
    -D{shaderc,sixel,spirv-cross,subrandr,uchardet,vapoursynth,vulkan}=enabled
    -D{win32-smtc,zimg}=enabled
)
if $gpl; then
    # Only the GPL image carries the dependencies of the GPL features.
    mpv_args+=(-D{dvda,dvdnav,rubberband}=enabled -Dajn-mvtools=true)
fi
meson setup build "${mpv_args[@]}"
meson compile -C build -j "$jobs"
endgroup

group "Packaging"
license=LICENSE.LGPL
if $gpl; then
    license=LICENSE.GPL
fi
mkdir -p artifact artifact-libmpv/include/mpv
cp -p build/mpv.{exe,com} etc/mpv-*.bat "$license" artifact/
cp -p build/libmpv*.dll build/libmpv*.dll.a "$license" artifact-libmpv/
cp -p include/mpv/*.h artifact-libmpv/include/mpv/
if [[ -f build/video/filter/mvtools/ajn-mvtools.dll ]]; then
    cp -p build/video/filter/mvtools/ajn-mvtools.dll artifact-libmpv/
    mkdir -p artifact-libmpv/licenses/ajn-mvtools
    cp -p video/filter/mvtools/{LICENSE,UPSTREAM.md} artifact-libmpv/licenses/ajn-mvtools/
fi
cp -p "$FFBUILD_PREFIX"/share/java/libbluray-*.jar artifact/
cp -p "$FFBUILD_PREFIX"/share/java/libbluray-*.jar artifact-libmpv/
"${FFBUILD_CROSS_PREFIX}strip" artifact/mpv.{exe,com} artifact-libmpv/libmpv*.dll
[[ -f artifact-libmpv/ajn-mvtools.dll ]] && "${FFBUILD_CROSS_PREFIX}strip" artifact-libmpv/ajn-mvtools.dll
ls -l artifact artifact-libmpv
endgroup
