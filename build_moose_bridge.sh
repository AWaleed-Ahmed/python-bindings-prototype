#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOOSE_DIR="${ROOT_DIR}/third_party/MOOSE"
MOOSE_BUILD_DIR="${MOOSE_DIR}/build"
BRIDGE_SRC_DIR="${ROOT_DIR}/src/moose_bridge"
BRIDGE_BUILD_DIR="${ROOT_DIR}/build/moose_bridge"

if [[ ! -d "${MOOSE_DIR}" ]]; then
  echo "Missing ${MOOSE_DIR}. Clone BRL-CAD/MOOSE first."
  exit 1
fi

echo "[1/4] Building BRL-CAD/MOOSE"
cmake -S "${MOOSE_DIR}" -B "${MOOSE_BUILD_DIR}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DZLIB_STATIC_LIBRARY=/usr/lib/x86_64-linux-gnu/libz.so \
  -DZLIB_LIBRARY=/usr/lib/x86_64-linux-gnu/libz.so
cmake --build "${MOOSE_BUILD_DIR}" -j

echo "[2/4] Building C bridge"
cmake -S "${BRIDGE_SRC_DIR}" -B "${BRIDGE_BUILD_DIR}" \
  -DMOOSE_ROOT="${MOOSE_DIR}" \
  -DMOOSE_BUILD="${MOOSE_BUILD_DIR}" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "${BRIDGE_BUILD_DIR}" -j

echo "[3/4] Bridge built at: ${BRIDGE_BUILD_DIR}/libbrlcad_moose_bridge.so"

echo "[4/4] To use from Python:"
echo "export BRLCAD_MOOSE_BRIDGE_PATH=${BRIDGE_BUILD_DIR}/libbrlcad_moose_bridge.so"
echo "export BRLCAD_BACKEND=moose_rt3"
