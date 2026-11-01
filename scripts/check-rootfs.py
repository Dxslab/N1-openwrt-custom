#!/usr/bin/env python3
"""Inspect the built archive without running target-architecture executables."""
import sys
import tarfile

if len(sys.argv) != 2:
    raise SystemExit('Expected exactly one rootfs.tar.gz archive')
required = {
    'etc/config/network', 'etc/uci-defaults/99zz-n1-settings',
    'etc/sysctl.d/99-n1-ipv4.conf', 'etc/openclash/core/clash_meta',
    'etc/init.d/openclash', 'etc/init.d/ttyd', 'etc/init.d/firewall',
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
    core = members['etc/openclash/core/clash_meta']
    if not core.mode & 0o111:
        raise SystemExit('Mihomo core is not executable')
print('Rootfs checks passed: network settings, proxy core, UI services and storage tools present.')
