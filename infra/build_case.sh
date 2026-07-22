#!/usr/bin/env bash
#
# Build one gallery case, run it, and generate its media.
#
#   infra/build_case.sh <case-dir> [profile]
#
# profile defaults to "ci" (fast, for preview media). Use "hero" for the
# high-resolution run. The environment must provide samurai (find_package)
# and the python post-processing stack; on a dev machine this is the
# samurai-gallery micromamba environment.
set -euo pipefail

CASE_DIR=$(cd "$1" && pwd)
PROFILE=${2:-ci}
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Activate the dedicated environment when running interactively. In CI the
# environment is already active, so skip if samurai's config is reachable.
if [ -z "${GALLERY_NO_ACTIVATE:-}" ]; then
    micromamba activate samurai-gallery 2>/dev/null || true
fi

echo ">> case:    $CASE_DIR"
echo ">> profile: $PROFILE"

eval "$(python "$ROOT/infra/case_meta.py" "$CASE_DIR/case.yaml" "$PROFILE")"

BUILD_DIR="$CASE_DIR/build"
OUT_DIR="$CASE_DIR/.output"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo ">> configuring and building target '$TARGET'"
cmake -S "$CASE_DIR" -B "$BUILD_DIR" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="${CONDA_PREFIX:-}" >/dev/null
cmake --build "$BUILD_DIR" --target "$TARGET"

echo ">> running simulation"
# shellcheck disable=SC2086
"$BUILD_DIR/$TARGET" $ARGS \
    --path "$OUT_DIR" \
    --filename "$OUTPUT_PREFIX" \
    --nfiles "$NFILES"

echo ">> generating media"
( cd "$CASE_DIR" && PYTHONPATH="$ROOT/infra" python postprocess.py "$OUT_DIR" )

echo ">> done. media written to $CASE_DIR"
ls -1 "$CASE_DIR"/*.png "$CASE_DIR"/*.mp4 2>/dev/null || true
