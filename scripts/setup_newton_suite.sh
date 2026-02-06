#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH=${1:-}
if [[ -z "${TARGET_PATH}" ]]; then
  echo "Usage: $0 /path/to/newton-suite" >&2
  exit 1
fi

SOURCE_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

PROJECTS=(
  "realTinyTalk"
  "adan"
  "adan_portable"
  "newton_agent"
  "statsy"
)

mkdir -p "${TARGET_PATH}"

if [[ -d "${TARGET_PATH}/.git" ]]; then
  echo "Target already looks like a git repo: ${TARGET_PATH}" >&2
  exit 1
fi

for project in "${PROJECTS[@]}"; do
  if [[ ! -d "${SOURCE_ROOT}/${project}" ]]; then
    echo "Missing project directory: ${SOURCE_ROOT}/${project}" >&2
    exit 1
  fi
  rsync -a --delete "${SOURCE_ROOT}/${project}/" "${TARGET_PATH}/${project}/"
done

cp "${SOURCE_ROOT}/docs/newton_suite/README.md" "${TARGET_PATH}/README.md"

(
  cd "${TARGET_PATH}"
  git init
  git add .
  git status --short
)