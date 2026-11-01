#!/usr/bin/env python3
"""Fail before a long compile if required settings disappear in defconfig."""
import pathlib
import sys

config = pathlib.Path(sys.argv[1]).read_text()
selected = {line.split('=', 1)[0] for line in config.splitlines() if line.endswith('=y')}
required = {
    'CONFIG_TARGET_armsr', 'CONFIG_TARGET_armsr_armv8',
    'CONFIG_TARGET_ROOTFS_TARGZ', 'CONFIG_PACKAGE_luci-app-openclash',
    'CONFIG_PACKAGE_luci-app-ttyd', 'CONFIG_PACKAGE_firewall4',
    'CONFIG_PACKAGE_dnsmasq-full', 'CONFIG_PACKAGE_ip-full',
    'CONFIG_PACKAGE_btrfs-progs', 'CONFIG_PACKAGE_dosfstools',
    'CONFIG_PACKAGE_lsblk', 'CONFIG_PACKAGE_parted', 'CONFIG_PACKAGE_uuidgen',
    'CONFIG_PACKAGE_bash', 'CONFIG_PACKAGE_ruby-yaml',
    'CONFIG_PACKAGE_perl', 'CONFIG_PACKAGE_tar', 'CONFIG_PACKAGE_kmod-tun',
    'CONFIG_PACKAGE_kmod-nft-tproxy', 'CONFIG_PACKAGE_kmod-inet-diag',
}
missing = sorted(required - selected)
if missing:
    raise SystemExit('Required config selections missing: ' + ', '.join(missing))
allowed_apps = {
    'CONFIG_PACKAGE_luci-app-openclash', 'CONFIG_PACKAGE_luci-app-ttyd',
    'CONFIG_PACKAGE_luci-app-firewall', 'CONFIG_PACKAGE_luci-app-package-manager',
    'CONFIG_PACKAGE_luci-app-opkg',
}
extra = sorted(s for s in selected if s.startswith('CONFIG_PACKAGE_luci-app-') and s not in allowed_apps)
if extra:
    raise SystemExit('Unexpected LuCI applications: ' + ', '.join(extra))
print('Configuration checks passed. LuCI applications:')
for entry in sorted(selected & allowed_apps):
    print(' ', entry.removeprefix('CONFIG_PACKAGE_'))
