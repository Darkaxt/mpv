common_args="--werror \
-Dlibmpv=true \
-Dtests=true \
"

export CFLAGS="$CFLAGS -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=3"

build_subrandr() {
    if [[ -n "${NUVIODV_SOURCE_LOCK:-}" ]]; then
        python3 TOOLS/nuviodv/sources.py clone https://github.com/afishhh/subrandr.git subrandr
    else
        git clone --depth=1 https://github.com/afishhh/subrandr.git
    fi
    pushd subrandr
    cargo xtask install --prefix "$@"
    popd
}
