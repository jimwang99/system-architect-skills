#!/usr/bin/env bash
# Keep rendering reproducible by using only a project-local or explicitly installed CLI.
set -euo pipefail

usage() {
  echo "usage: render.sh INPUT.json5 [OUTPUT_BASE] [--png]" >&2
}

if [[ $# -lt 1 || $# -gt 3 ]]; then
  usage
  exit 2
fi

input=$1
shift
output=${input%.*}
if [[ $# -gt 0 && $1 != "--png" ]]; then
  output=$1
  shift
fi
png=false
if [[ $# -gt 0 ]]; then
  if [[ $1 != "--png" ]]; then
    usage
    exit 2
  fi
  png=true
  shift
fi
if [[ $# -ne 0 ]]; then
  usage
  exit 2
fi
if [[ ! -f $input ]]; then
  echo "input not found: $input" >&2
  exit 2
fi

renderer=""
flavor=""
if [[ -n ${WAVEDROM_BIN:-} ]]; then
  renderer=$WAVEDROM_BIN
  flavor=${WAVEDROM_FLAVOR:-wavedrom}
elif [[ -x node_modules/.bin/wavedrom ]]; then
  renderer=node_modules/.bin/wavedrom
  flavor=wavedrom
elif command -v wavedrom >/dev/null 2>&1; then
  renderer=$(command -v wavedrom)
  flavor=wavedrom
elif [[ -x node_modules/.bin/wavedrom-cli ]]; then
  renderer=node_modules/.bin/wavedrom-cli
  flavor=wavedrom-cli
elif command -v wavedrom-cli >/dev/null 2>&1; then
  renderer=$(command -v wavedrom-cli)
  flavor=wavedrom-cli
else
  echo "WaveDrom CLI not found. Install it in the project with: npm install --save-dev wavedrom" >&2
  exit 2
fi

svg=${output}.svg
temporary_svg=$(mktemp "${svg}.tmp.XXXXXX")
cleanup() {
  rm -f "$temporary_svg"
}
trap cleanup EXIT
if [[ $flavor == "wavedrom-cli" ]]; then
  "$renderer" -i "$input" -s "$temporary_svg"
else
  "$renderer" --input "$input" > "$temporary_svg"
fi
if [[ ! -s $temporary_svg ]]; then
  echo "renderer did not create a non-empty SVG" >&2
  exit 1
fi
mv "$temporary_svg" "$svg"
trap - EXIT
echo "wrote $svg"

if [[ $png == true ]]; then
  if ! python -c 'import cairosvg' >/dev/null 2>&1; then
    echo "PNG needs CairoSVG and the native Cairo library. Run through uv with CairoSVG after installing Cairo." >&2
    exit 2
  fi
  python -c 'import cairosvg, sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], scale=2)' "$svg" "${output}.png"
  echo "wrote ${output}.png"
fi
