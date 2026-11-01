#!/usr/bin/env python3
"""Reject incompatible local IPKs and a Btrfs build lacking Zstd support."""
import io
from pathlib import Path
import tarfile

repo = Path(__file__).resolve().parents[1]
seen = set()
for path in (repo / 'imagebuilder/packages').glob('*.ipk'):
    with tarfile.open(path, 'r:gz') as package:
        control_member = next(m for m in package if m.name.removeprefix('./') == 'control.tar.gz')
        with tarfile.open(fileobj=io.BytesIO(package.extractfile(control_member).read()), mode='r:gz') as control:
            member = next(m for m in control if m.name.removeprefix('./') == 'control')
            fields = dict(line.split(': ', 1) for line in control.extractfile(member).read().decode().splitlines() if ': ' in line and not line.startswith(' '))
    name = fields['Package']
    if name in seen:
        raise SystemExit('Duplicate local package: ' + name)
    seen.add(name)
    if fields['Architecture'] not in ('all', 'aarch64_generic'):
        raise SystemExit('Wrong package architecture: ' + str(path))
    if name == 'btrfs-progs':
        if 'libzstd' not in fields.get('Depends', '') or 'n1zstd' not in fields['Version']:
            raise SystemExit('Custom Btrfs package must include Zstd')
expected = {'btrfs-progs', 'luci-app-openclash', 'luci-app-amlogic', 'luci-i18n-amlogic-zh-cn',
            'luci-theme-vantage', 'luci-app-vantage', 'luci-i18n-vantage-zh-cn', 'luci-i18n-vantage-theme-zh-cn'}
if seen != expected:
    raise SystemExit('Unexpected/missing local packages: ' + str(seen ^ expected))
print('Local IPK architecture, package set and Btrfs Zstd checks passed.')
