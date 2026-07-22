#!/usr/bin/env bash
#
# Re-render a case's media from its existing .output frames, without
# rebuilding or re-running the simulation.
#
#   infra/render_media.sh <case-dir>
#
# Useful after tweaking a postprocess.py or the shared renderer. Runs in the
# samurai-gallery environment (which owns the rendering stack).
set -euo pipefail

CASE_DIR=$(cd "$1" && pwd)
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MAMBA_ROOT="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"
BASE_PATH="$PATH"

activate() {
    local prefix="$MAMBA_ROOT/envs/$1"
    export CONDA_PREFIX="$prefix"
    export PATH="$prefix/bin:$BASE_PATH"
    if [ -d "$prefix/etc/conda/activate.d" ]; then
        set +eu
        for s in "$prefix"/etc/conda/activate.d/*.sh; do [ -f "$s" ] && . "$s"; done
        set -eu
    fi
}

activate samurai-gallery
eval "$(python "$ROOT/infra/case_meta.py" "$CASE_DIR/case.yaml" ci)"

FRAMES_DIR="$CASE_DIR/.output"
[ -n "$OUTPUT_SUBDIR" ] && FRAMES_DIR="$CASE_DIR/.output/$OUTPUT_SUBDIR"

if [ ! -d "$FRAMES_DIR" ]; then
    echo "!! no frames at $FRAMES_DIR - run infra/build_case.sh first" >&2
    exit 1
fi

echo ">> re-rendering $(basename "$CASE_DIR")"
( cd "$CASE_DIR" && PYTHONPATH="$ROOT/infra" python postprocess.py "$FRAMES_DIR" )
