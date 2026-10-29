#!/usr/bin/env bash
# Runs the newest Matugen installed instead of whichever comes first in PATH.
# The shell's own launchers put ~/.local/bin and ~/.cargo/bin ahead of /usr/bin,
# so a stale user build can shadow an up-to-date system package.
#
# Source it to get a `matugen` function (resolved once, on first call), or run it
# directly with Matugen's arguments. Builds without --source-color-index (pre-4.0)
# get the call with that option dropped; 4.x needs it to skip its colour prompt.

MATUGEN_BIN=""
MATUGEN_HAS_SOURCE_INDEX=""

_matugen_version_gt() {
    local -a a b
    local i
    IFS=. read -ra a <<< "$1"
    IFS=. read -ra b <<< "$2"
    for ((i = 0; i < ${#a[@]} || i < ${#b[@]}; i++)); do
        ((10#${a[i]:-0} > 10#${b[i]:-0})) && return 0
        ((10#${a[i]:-0} < 10#${b[i]:-0})) && return 1
    done
    return 1
}

matugen_resolve() {
    [[ -n "$MATUGEN_BIN" ]] && return

    local candidate real out version best_version=""
    local -A seen=()
    while IFS= read -r candidate; do
        [[ -x "$candidate" ]] || continue
        real=$(readlink -f -- "$candidate") || real="$candidate"
        [[ "$real" == "$(readlink -f "${BASH_SOURCE[0]}")" ]] && continue
        [[ -v seen["$real"] ]] && continue
        seen["$real"]=1

        out=$("$candidate" --version 2>/dev/null)
        version=0
        [[ "$out" =~ ([0-9]+(\.[0-9]+)+) ]] && version="${BASH_REMATCH[1]}"
        if [[ -z "$MATUGEN_BIN" ]] || _matugen_version_gt "$version" "$best_version"; then
            MATUGEN_BIN="$candidate"
            best_version="$version"
        fi
    done < <(type -aP matugen 2>/dev/null
        printf '%s\n' /usr/bin/matugen /usr/local/bin/matugen "$HOME/.local/bin/matugen" "$HOME/.cargo/bin/matugen")

    MATUGEN_HAS_SOURCE_INDEX=0
    if [[ -z "$MATUGEN_BIN" ]]; then
        MATUGEN_BIN="matugen"
    elif "$MATUGEN_BIN" image --help 2>&1 | grep -q -- "--source-color-index"; then
        MATUGEN_HAS_SOURCE_INDEX=1
    fi
}

_matugen_filter_args() {
    _matugen_args=()
    local has_source_index=0
    local is_image_cmd=0
    local arg
    for arg in "$@"; do
        if [[ "$arg" == "image" ]]; then
            is_image_cmd=1
        elif [[ "$arg" == "--source-color-index" || "$arg" == --source-color-index=* ]]; then
            has_source_index=1
        fi
    done

    while (($#)); do
        if [[ "$MATUGEN_HAS_SOURCE_INDEX" != 1 ]]; then
            case "$1" in
                --source-color-index) shift; (($#)) && shift; continue ;;
                --source-color-index=*) shift; continue ;;
            esac
        fi
        _matugen_args+=("$1")
        shift
    done

    # In Matugen 4.x, running `image` without --source-color-index prompts interactively,
    # hanging non-interactive scripts and background processes. Ensure a default index.
    if [[ "$MATUGEN_HAS_SOURCE_INDEX" == 1 && "$is_image_cmd" == 1 && "$has_source_index" == 0 ]]; then
        _matugen_args=(--source-color-index 0 "${_matugen_args[@]}")
    fi
}

matugen() {
    matugen_resolve
    _matugen_filter_args "$@"
    command "$MATUGEN_BIN" "${_matugen_args[@]}"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    matugen_resolve
    _matugen_filter_args "$@"
    exec "$MATUGEN_BIN" "${_matugen_args[@]}"
fi
