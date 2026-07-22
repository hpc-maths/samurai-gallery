#!/usr/bin/env bash
#
# Ensure a given samurai version is built and installed, once, into a
# per-ref prefix.
#
#   infra/ensure_samurai.sh <repo> <ref> <prefix>
#
#   repo    samurai git repository: 'owner/name' or a full clone URL
#   ref     git ref (tag, commit or branch) to build
#   prefix  install prefix; the caller adds it to CMAKE_PREFIX_PATH
#
# Idempotent: if <prefix> already holds <ref> (recorded in <prefix>/.samurai-ref)
# nothing is rebuilt, so cases sharing a ref reuse a single install. Must run in
# an environment providing the samurai build toolchain and dependencies
# (the samurai-gallery env); those are picked up from $CONDA_PREFIX.
set -euo pipefail

REPO="$1"
REF="$2"
PREFIX="$3"

# Accept 'owner/name' shorthand as well as full URLs / local paths.
case "$REPO" in
    *://*|git@*|/*|.*) URL="$REPO" ;;
    *) URL="https://github.com/${REPO}.git" ;;
esac

MARKER="$PREFIX/.samurai-ref"
# A core header that must be present for the install to be usable. Guards against
# a previously cached but incomplete install (e.g. config written, headers not):
# such a prefix is treated as a miss and rebuilt rather than trusted.
SENTINEL="$PREFIX/include/samurai/algorithm.hpp"
if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$REF" ] && [ -f "$SENTINEL" ]; then
    echo ">> samurai $REF already installed at $PREFIX"
    exit 0
fi

echo ">> building samurai $REF from $URL"
SRC=$(mktemp -d)
trap 'rm -rf "$SRC"' EXIT

git clone --filter=blob:none "$URL" "$SRC" >/dev/null 2>&1
git -C "$SRC" checkout --detach "$REF" >/dev/null 2>&1

BUILD=$(mktemp -d)
trap 'rm -rf "$SRC" "$BUILD"' EXIT

# Deps (xtensor, hdf5, ...) come from the active env; install into the per-ref
# prefix so several samurai versions can coexist.
rm -rf "$PREFIX"
cmake -S "$SRC" -B "$BUILD" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_PREFIX_PATH="${CONDA_PREFIX:-}" \
    -DBUILD_DEMOS=OFF -DBUILD_TESTS=OFF >/dev/null
cmake --install "$BUILD" >/dev/null

# Fail loudly on an incomplete install rather than caching a broken prefix and
# only discovering it when a case fails to find samurai's headers.
if [ ! -f "$SENTINEL" ]; then
    echo "!! samurai install at $PREFIX is missing headers ($SENTINEL)" >&2
    exit 1
fi

echo "$REF" > "$MARKER"
echo ">> samurai $REF installed at $PREFIX"
