#!/usr/bin/env bash
# Build only the Zstd-enabled maintenance tool using the official prebuilt SDK.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$repo/sdk" "$repo/local-packages"
sdk_archive=$(python3 -c 'import json; print(json.load(open("configs/prebuilt-lock.json"))["sdk"]["name"])')
tar --zstd -xf "$repo/downloads/$sdk_archive" -C "$repo/sdk" --strip-components=1
cd "$repo/sdk"
# Keep the SDK's release-matched feeds, including its base feed.
./scripts/feeds update -a
./scripts/feeds install btrfs-progs
package_makefile=feeds/packages/utils/btrfs-progs/Makefile
test -f "$package_makefile"
# A higher release ensures the local build wins over the official r1 package.
sed -i 's/^PKG_RELEASE:=1$/PKG_RELEASE:=2.n1zstd/' "$package_makefile"
grep -qx 'PKG_RELEASE:=2.n1zstd' "$package_makefile"
cat > .config <<'EOF'
CONFIG_ALL=n
CONFIG_ALL_NONSHARED=n
CONFIG_ALL_KMODS=n
CONFIG_PACKAGE_btrfs-progs=y
CONFIG_BTRFS_PROGS_ZSTD=y
EOF
make defconfig
grep -qx 'CONFIG_BTRFS_PROGS_ZSTD=y' .config
make package/feeds/packages/btrfs-progs/compile -j2 V=s
mapfile -t packages < <(find bin/packages -name 'btrfs-progs_*.ipk' -type f)
test "${#packages[@]}" -eq 1
cp "${packages[0]}" "$repo/local-packages/"
mkdir -p "$repo/artifacts"
cp .config "$repo/artifacts/btrfs-sdk.config"
cp feeds.conf.default "$repo/artifacts/btrfs-sdk-feeds.conf"
for feed in base packages luci routing telephony; do
    printf '%s: ' "$feed"
    git -C "feeds/$feed" rev-parse HEAD
done > "$repo/artifacts/btrfs-sdk-revisions.txt"
