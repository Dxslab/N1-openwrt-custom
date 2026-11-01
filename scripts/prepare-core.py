#!/usr/bin/env python3
"""Download a pinned official Mihomo ARM64 release and verify its digest."""
import gzip
import hashlib
import pathlib
import struct
import sys
import urllib.request

version, expected, destination = sys.argv[1:]
url = f'https://github.com/MetaCubeX/mihomo/releases/download/{version}/mihomo-linux-arm64-{version}.gz'
request = urllib.request.Request(url, headers={'User-Agent': 'N1-custom-firmware-build'})
with urllib.request.urlopen(request, timeout=120) as response:
    archive = response.read()
actual = hashlib.sha256(archive).hexdigest()
if actual != expected:
    raise SystemExit(f'Mihomo archive checksum mismatch: {actual}')
binary = gzip.decompress(archive)
if binary[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', binary, 18)[0] != 183:
    raise SystemExit('Expected a little-endian AArch64 ELF executable')
target = pathlib.Path(destination)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(binary)
target.chmod(0o755)
print(f'Installed verified {version} ARM64 core: {len(binary)} bytes')
