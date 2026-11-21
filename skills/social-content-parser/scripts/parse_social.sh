#!/usr/bin/env sh
set -eu

if command -v node >/dev/null 2>&1; then
  DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  exec node "$DIR/parse_social.mjs" "$@"
fi

echo "Node is required for social-content-parser." >&2
exit 1
