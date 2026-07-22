#!/usr/bin/env bash
#
# Build one gallery case, run it, and generate its media.
#
#   infra/build_case.sh <case-dir> [profile]
#
# profile defaults to "ci" (fast, for preview media). Use "hero" for the
# high-resolution run.
#
# A case builds either from its own CMakeLists.txt (default) or, for
# "engine" cases (case.yaml declares `engine.source`), from an external
# CMake project such as samurai-euler. Build+run happen in the case's `env`
# (default samurai-gallery); media post-processing always runs in
# samurai-gallery (it owns the rendering stack).
set -euo pipefail

CASE_DIR=$(cd "$1" && pwd)
PROFILE=${2:-ci}
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

BASE_PATH="$PATH"
MAMBA_ROOT="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"

# Where per-ref samurai installs and engine checkouts are cached, so cases
# sharing a ref (and successive CI runs) reuse a single build.
CACHE_ROOT="${SAMURAI_GALLERY_CACHE:-$HOME/.cache/samurai-gallery}"
SAMURAI_INSTALL_ROOT="${SAMURAI_INSTALL_ROOT:-$CACHE_ROOT/installs}"
ENGINE_SRC_ROOT="${ENGINE_SRC_ROOT:-$CACHE_ROOT/engines}"

# Turn a git repo/ref into a filesystem-safe token.
sanitize() { printf '%s' "$1" | tr '/:@ ' '____'; }

# Deterministic environment activation (works inside a non-interactive script,
# where the `micromamba` shell function may be unavailable). Switches cleanly
# between environments so an engine case can build/run in one env and render in
# another.
activate() {
    local env="$1"
    local prefix="$MAMBA_ROOT/envs/$env"
    if [ ! -d "$prefix" ]; then
        echo "!! environment '$env' not found at $prefix" >&2
        return 1
    fi
    export CONDA_PREFIX="$prefix"
    export PATH="$prefix/bin:$BASE_PATH"
    # Pick up compiler/env variables (CC, CXX, flags, ...). conda activate.d
    # scripts are not written for `set -eu`, so relax it while sourcing.
    if [ -d "$prefix/etc/conda/activate.d" ]; then
        set +eu
        for s in "$prefix"/etc/conda/activate.d/*.sh; do
            [ -f "$s" ] && . "$s"
        done
        set -eu
    fi
}

# Read case metadata (needs python + pyyaml from the gallery env).
activate samurai-gallery
eval "$(python "$ROOT/infra/case_meta.py" "$CASE_DIR/case.yaml" "$PROFILE")"

echo ">> case:    $CASE_DIR"
echo ">> profile: $PROFILE (env: $ENV)"

# ---- cache lookup --------------------------------------------------------
# Skip compile+run+render when nothing that affects the media has changed:
# the samurai/engine version, the case sources, and the shared figure engine
# and scripts are hashed into a content-addressed key (see infra/cache.py).
# Escape hatches: GALLERY_NO_CACHE=1 bypasses the cache entirely;
# GALLERY_CACHE_REFRESH=1 forces a rebuild but still repopulates the store.
CACHE_DIR="${GALLERY_CACHE_DIR:-$ROOT/.cache/media}"
MEDIA_FILES=(thumbnail-dark.png thumbnail-light.png preview-dark.mp4 preview-light.mp4)

entry_complete() {
    local entry="$1"
    [ -d "$entry" ] || return 1
    local f
    for f in "${MEDIA_FILES[@]}"; do
        [ -f "$entry/$f" ] || return 1
    done
    return 0
}

CACHE_KEY=""
CACHE_ENTRY=""
if [ "${GALLERY_NO_CACHE:-0}" != "1" ]; then
    CACHE_KEY=$(python "$ROOT/infra/cache.py" key "$CASE_DIR" "$PROFILE")
    CACHE_ENTRY="$CACHE_DIR/$CACHE_KEY"
    if [ "${GALLERY_CACHE_REFRESH:-0}" != "1" ] && entry_complete "$CACHE_ENTRY"; then
        echo ">> cache hit ($CACHE_KEY) - restoring media, skipping build/run/render"
        for f in "${MEDIA_FILES[@]}"; do
            cp "$CACHE_ENTRY/$f" "$CASE_DIR/$f"
        done
        ls -1 "$CASE_DIR"/*.png "$CASE_DIR"/*.mp4 2>/dev/null || true
        exit 0
    fi
    echo ">> cache miss ($CACHE_KEY)"
fi

OUT_DIR="$CASE_DIR/.output"
rm -rf "$OUT_DIR" "$CASE_DIR/build"
mkdir -p "$OUT_DIR"

# ---- build + run (in the case's env) -------------------------------------
if [ -n "$IS_ENGINE" ]; then
    # Clone the engine project at the tested ref (cached per repo+ref).
    ENGINE_SRC="$ENGINE_SRC_ROOT/$(sanitize "$ENGINE_REPO")-$(sanitize "$ENGINE_REF")"
    case "$ENGINE_REPO" in
        *://*|git@*|/*|.*) ENGINE_URL="$ENGINE_REPO" ;;
        *) ENGINE_URL="https://github.com/${ENGINE_REPO}.git" ;;
    esac
    if [ "$(cat "$ENGINE_SRC/.engine-ref" 2>/dev/null || true)" != "$ENGINE_REF" ]; then
        echo ">> cloning engine $ENGINE_REPO@$ENGINE_REF"
        rm -rf "$ENGINE_SRC"
        git clone --filter=blob:none "$ENGINE_URL" "$ENGINE_SRC" >/dev/null 2>&1
        git -C "$ENGINE_SRC" checkout --detach "$ENGINE_REF" >/dev/null 2>&1
        echo "$ENGINE_REF" > "$ENGINE_SRC/.engine-ref"
    fi

    # Create the engine environment from the checkout if it is missing.
    if [ ! -d "$MAMBA_ROOT/envs/$ENV" ]; then
        echo ">> creating engine env '$ENV' from $ENGINE_SRC/conda/environment.yml"
        micromamba create -y -n "$ENV" -f "$ENGINE_SRC/conda/environment.yml"
    fi

    activate "$ENV"
    BUILD_DIR="$CASE_DIR/build-engine"
    echo ">> building engine target '$TARGET' from $ENGINE_SRC"
    cmake -S "$ENGINE_SRC" -B "$BUILD_DIR" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_PREFIX_PATH="${CONDA_PREFIX:-}" >/dev/null
    cmake --build "$BUILD_DIR" --target "$TARGET" -j4
    EXE=$(find "$BUILD_DIR" -name "$TARGET" -type f -perm -111 | head -1)
else
    # Build samurai at the tested ref (cached per ref), then the case against it.
    activate "$ENV"
    SAMURAI_PREFIX="$SAMURAI_INSTALL_ROOT/$(sanitize "$SAMURAI_REF")"
    bash "$ROOT/infra/ensure_samurai.sh" "$SAMURAI_REPO" "$SAMURAI_REF" "$SAMURAI_PREFIX"

    BUILD_DIR="$CASE_DIR/build"
    echo ">> configuring and building target '$TARGET' (samurai $SAMURAI_REF)"
    # samurai's exported CMake target does not always advertise its own include
    # directory (the installed samurai::samurai omits INTERFACE_INCLUDE_DIRECTORIES),
    # so add the per-ref prefix include explicitly. Harmless when the target does
    # export it. -isystem keeps samurai's headers out of the case's warnings.
    cmake -S "$CASE_DIR" -B "$BUILD_DIR" -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_PREFIX_PATH="$SAMURAI_PREFIX;${CONDA_PREFIX:-}" \
        -DCMAKE_CXX_FLAGS="-isystem $SAMURAI_PREFIX/include" >/dev/null
    cmake --build "$BUILD_DIR" --target "$TARGET"
    EXE="$BUILD_DIR/$TARGET"
fi

echo ">> running simulation"
# Run inside OUT_DIR so executables that write to a fixed subdirectory
# (e.g. samurai-euler's "results") land under the case output dir.
# shellcheck disable=SC2086
if [ -n "$IS_ENGINE" ]; then
    # Engine executables link MPI and call MPI_Init even for a single rank. On
    # cloud CI runners UCX otherwise probes an RDMA/verbs NIC that is not usable
    # (e.g. Azure "mana": "uct_iface_open(ud_verbs/...) failed"), aborting
    # intermittently. Restrict UCX to TCP/shared-memory transports so MPI_Init
    # always succeeds regardless of the host's network hardware.
    export UCX_TLS="${UCX_TLS:-tcp,self,sm}"
    # Engine executables own their output naming; only --nfiles is common.
    ( cd "$OUT_DIR" && "$EXE" $ARGS --nfiles "$NFILES" )
else
    ( cd "$OUT_DIR" && "$EXE" $ARGS \
        --path "$OUT_DIR" \
        --filename "$OUTPUT_PREFIX" \
        --nfiles "$NFILES" )
fi

FRAMES_DIR="$OUT_DIR"
[ -n "$OUTPUT_SUBDIR" ] && FRAMES_DIR="$OUT_DIR/$OUTPUT_SUBDIR"

# ---- render media (always in samurai-gallery) ----------------------------
activate samurai-gallery
echo ">> generating media"
( cd "$CASE_DIR" && PYTHONPATH="$ROOT/infra" python postprocess.py "$FRAMES_DIR" )

echo ">> done. media written to $CASE_DIR"
ls -1 "$CASE_DIR"/*.png "$CASE_DIR"/*.mp4 2>/dev/null || true

# ---- populate cache ------------------------------------------------------
if [ "${GALLERY_NO_CACHE:-0}" != "1" ] && [ -n "$CACHE_ENTRY" ]; then
    mkdir -p "$CACHE_ENTRY"
    for f in "${MEDIA_FILES[@]}"; do
        [ -f "$CASE_DIR/$f" ] && cp "$CASE_DIR/$f" "$CACHE_ENTRY/$f"
    done
    python "$ROOT/infra/cache.py" manifest "$CASE_DIR" "$PROFILE" > "$CACHE_ENTRY/manifest.json"
    echo ">> cached media under $CACHE_ENTRY"
fi
