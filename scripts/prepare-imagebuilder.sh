#!/usr/bin/env bash
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo"
archive=$(python3 -c 'import json; print(json.load(open("configs/prebuilt-lock.json"))["imagebuilder"]["name"])')
mkdir -p imagebuilder/packages imagebuilder/files
tar --zstd -xf "downloads/$archive" -C imagebuilder --strip-components=1
cp downloads/*.ipk local-packages/*.ipk imagebuilder/packages/
cp -a files/. imagebuilder/files/
chmod 0755 imagebuilder/files/etc/uci-defaults/99zz-n1-settings
grep -qx 'CONFIG_TARGET_ROOTFS_TARGZ=y' imagebuilder/.config
python3 scripts/check-prebuilt.py
