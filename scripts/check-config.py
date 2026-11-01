#!/usr/bin/env python3
"""Fail before a long compile if required settings disappear in defconfig."""
import pathlib
import re
import sys

config = pathlib.Path(sys.argv[1]).read_text()
selected = {line.split('=', 1)[0] for line in config.splitlines() if line.endswith('=y')}
required = {
    'CONFIG_TARGET_armsr', 'CONFIG_TARGET_armsr_armv8',
    'CONFIG_TARGET_ROOTFS_TARGZ', 'CONFIG_PACKAGE_luci-app-openclash',
    'CONFIG_PACKAGE_luci-app-ttyd', 'CONFIG_PACKAGE_firewall4',
    'CONFIG_PACKAGE_luci-app-amlogic', 'CONFIG_PACKAGE_rpcd-mod-ucode',
    'CONFIG_PACKAGE_jq', 'CONFIG_PACKAGE_pv',
    'CONFIG_PACKAGE_dnsmasq-full', 'CONFIG_PACKAGE_ip-full',
    'CONFIG_PACKAGE_btrfs-progs', 'CONFIG_PACKAGE_dosfstools',
    'CONFIG_PACKAGE_lsblk', 'CONFIG_PACKAGE_parted', 'CONFIG_PACKAGE_uuidgen',
    'CONFIG_PACKAGE_bash', 'CONFIG_PACKAGE_ruby-yaml',
    'CONFIG_PACKAGE_perl', 'CONFIG_PACKAGE_tar', 'CONFIG_PACKAGE_kmod-tun',
    'CONFIG_PACKAGE_kmod-nft-tproxy', 'CONFIG_PACKAGE_kmod-inet-diag',
    'CONFIG_TARGET_armsr_armv8_DEVICE_generic',
}
maintenance_packages = {
    'perl', 'perl-http-date', 'perlbase-file', 'perlbase-getopt',
    'perlbase-time', 'perlbase-unicode', 'perlbase-utf8',
    'blkid', 'fdisk', 'lsblk', 'parted', 'attr', 'btrfs-progs',
    'chattr', 'dosfstools', 'e2fsprogs', 'f2fs-tools', 'f2fsck',
    'lsattr', 'mkf2fs', 'xfs-fsck', 'xfs-mkfs', 'bsdtar', 'pigz',
    'bash', 'gawk', 'getopt', 'losetup', 'tar', 'uuidgen',
}
required.update('CONFIG_PACKAGE_' + name for name in maintenance_packages)
required.add('CONFIG_BTRFS_PROGS_ZSTD')
missing = sorted(required - selected)
if missing:
    raise SystemExit('Required config selections missing: ' + ', '.join(missing))
allowed_apps = {
    'CONFIG_PACKAGE_luci-app-openclash', 'CONFIG_PACKAGE_luci-app-ttyd',
    'CONFIG_PACKAGE_luci-app-firewall', 'CONFIG_PACKAGE_luci-app-package-manager',
    'CONFIG_PACKAGE_luci-app-opkg',
    'CONFIG_PACKAGE_luci-app-amlogic',
}
if len(sys.argv) != 3:
    raise SystemExit('Usage: check-config.py .config tmp/.packageinfo')
package_info = pathlib.Path(sys.argv[2]).read_text()
actual_apps = {
    'CONFIG_PACKAGE_' + name
    for name in re.findall(r'^Package: (\S+)\s*$', package_info, re.MULTILINE)
    if name.startswith('luci-app-')
}
if 'CONFIG_PACKAGE_luci-app-openclash' not in actual_apps:
    raise SystemExit('Package metadata does not contain the OpenClash package')
# INCLUDE_* options may default to y even when their parent package is absent.
# Match only real Package: records, not all CONFIG_PACKAGE_luci-app-* keys.
extra = sorted((selected & actual_apps) - allowed_apps)
if extra:
    raise SystemExit('Unexpected LuCI applications: ' + ', '.join(extra))
print('Configuration checks passed. LuCI applications:')
for entry in sorted(selected & allowed_apps):
    print(' ', entry.removeprefix('CONFIG_PACKAGE_'))
