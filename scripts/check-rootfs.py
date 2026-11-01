#!/usr/bin/env python3
"""Inspect the built archive without running target-architecture executables."""
import sys
import tarfile
import re
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('Expected exactly one rootfs.tar.gz archive')
required = {
    'etc/config/network', 'etc/uci-defaults/99zz-n1-settings',
    'etc/sysctl.d/99-n1-ipv4.conf', 'etc/openclash/core/clash_meta',
    'etc/init.d/openclash', 'etc/init.d/ttyd', 'etc/init.d/firewall',
    'etc/config/amlogic',
    'usr/share/luci/menu.d/luci-app-amlogic.json',
    'usr/share/rpcd/ucode/luci.amlogic',
    'usr/share/amlogic/amlogic_check_firmware.sh',
    'usr/share/amlogic/amlogic_check_kernel.sh',
    'usr/share/luci/menu.d/luci-app-vantage.json',
    'usr/share/rpcd/ucode/luci.vantage',
    'usr/lib/lua/luci/i18n/vantage.zh-cn.lmo',
    'usr/lib/lua/luci/i18n/vantage-theme.zh-cn.lmo',
}
with tarfile.open(sys.argv[1], 'r:gz') as archive:
    members = {member.name.removeprefix('./'): member for member in archive.getmembers()}
    missing = required - members.keys()
    if missing:
        raise SystemExit('Rootfs missing files: ' + ', '.join(sorted(missing)))
    for tool in ('btrfs', 'parted', 'lsblk', 'uuidgen'):
        if not any(f'{directory}/{tool}' in members for directory in ('bin', 'sbin', 'usr/bin', 'usr/sbin')):
            raise SystemExit(f'Rootfs missing maintenance tool: {tool}')
    network = archive.extractfile(members['etc/config/network']).read().decode()
    if "option ipaddr '192.168.1.2'" not in network:
        raise SystemExit('Wrong LAN address')
    defaults = archive.extractfile(members['etc/uci-defaults/99zz-n1-settings']).read().decode()
    if "set luci.main.mediaurlbase='/luci-static/vantage'" not in defaults:
        raise SystemExit('Vantage is not configured as the default theme')
    if not any(name.startswith('www/luci-static/vantage/') for name in members):
        raise SystemExit('Missing Vantage theme assets')
    btrfs = next(members[f'{directory}/btrfs'] for directory in ('usr/bin', 'sbin', 'usr/sbin', 'bin') if f'{directory}/btrfs' in members)
    if b'libzstd.so' not in archive.extractfile(btrfs).read():
        raise SystemExit('Btrfs binary lacks the required Zstd library dependency')
    core = members['etc/openclash/core/clash_meta']
    if not core.mode & 0o111:
        raise SystemExit('Mihomo core is not executable')
    amlogic = archive.extractfile(members['etc/config/amlogic']).read().decode()
    for value in ('https://github.com/Dxslab/N1-openwrt-custom', 'N1-', 'kernel_flippy'):
        if value not in amlogic:
            raise SystemExit(f'Amlogic update configuration missing {value}')
    # Verify actual installed packages as well as Kconfig selections.
    status_name = next((name for name in ('usr/lib/opkg/status', 'lib/opkg/status') if name in members), None)
    if not status_name:
        raise SystemExit('Missing opkg installed-package status')
    status = archive.extractfile(members[status_name]).read().decode()
    installed = set(re.findall(r'^Package: (\S+)\s*$', status, re.MULTILINE))
    requested = {line.strip() for line in (Path(__file__).resolve().parents[1] / 'configs/packages.txt').read_text().splitlines()
                 if line.strip() and not line.lstrip().startswith(('#', '-'))}
    missing_packages = requested - installed
    if missing_packages:
        raise SystemExit('Rootfs missing requested packages: ' + ', '.join(sorted(missing_packages)))
    allowed_apps = {'luci-app-openclash', 'luci-app-ttyd', 'luci-app-amlogic',
                    'luci-app-firewall', 'luci-app-package-manager', 'luci-app-opkg', 'luci-app-vantage'}
    extra = sorted(name for name in installed if name.startswith('luci-app-') and name not in allowed_apps)
    if extra:
        raise SystemExit('Unexpected installed LuCI applications: ' + ', '.join(extra))
print('Rootfs checks passed: all requested packages, Vantage/dashboard Chinese translations, default theme, proxy core and Btrfs Zstd present.')
