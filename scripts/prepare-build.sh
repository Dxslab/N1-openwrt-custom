#!/usr/bin/env bash
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo/openwrt"
cp "$repo/configs/feeds.conf" feeds.conf.default
./scripts/feeds update -a
./scripts/feeds install -a

# Prefer the explicitly pinned OpenClash checkout over any feed version.
for feed in packages luci routing; do
    candidate="package/feeds/$feed/luci-app-openclash"
    if [[ -L "$candidate" ]]; then
        rm "$candidate"
    elif [[ -e "$candidate" ]]; then
        echo "Unexpected non-symlink package: $candidate" >&2
        exit 1
    fi
done
mkdir -p package/custom
cp -a "$repo/openclash-source/luci-app-openclash" package/custom/
mkdir -p files
cp -a "$repo/files/." files/
chmod 0755 files/etc/uci-defaults/99zz-n1-settings
cp "$repo/configs/n1.config" .config
make defconfig
python3 "$repo/scripts/check-config.py" .config
