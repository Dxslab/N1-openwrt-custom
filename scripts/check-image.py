#!/usr/bin/env python3
"""Validate the N1 MBR and Btrfs size, then read gzip to EOF for its CRC."""
import gzip
import pathlib
import struct
import sys

path = pathlib.Path(sys.argv[1])
opener = gzip.open if path.suffix == '.gz' else open
with opener(path, 'rb') as image:
    header = image.read(512)
    if len(header) != 512 or header[510:512] != b'\x55\xaa':
        raise SystemExit('Invalid MBR signature')
    partitions = []
    for index in range(4):
        entry = header[446 + index * 16:462 + index * 16]
        kind = entry[4]
        start, sectors = struct.unpack_from('<II', entry, 8)
        if sectors:
            partitions.append((index + 1, start * 512, sectors * 512, kind))
    ordered = sorted(partitions, key=lambda part: part[1])
    if len(ordered) != 2 or [part[0] for part in ordered] != [1, 2]:
        raise SystemExit(f'Expected the packager\'s two-partition USB image, got {partitions}')
    if ordered[0][1] < 512 or ordered[0][1] + ordered[0][2] > ordered[1][1]:
        raise SystemExit('Invalid or overlapping partitions')
    _, start, capacity, kind = ordered[1]
    if kind != 0x83:
        raise SystemExit(f'Unexpected root partition type: {kind}')
    image.seek(start + 65536)
    superblock = image.read(4096)
    if len(superblock) != 4096 or superblock[64:72] != b'_BHRfS_M':
        raise SystemExit('Expected a Btrfs root filesystem')
    fs_size = struct.unpack_from('<Q', superblock, 112)[0]
    if fs_size <= 0 or fs_size > capacity:
        raise SystemExit(f'Filesystem size {fs_size} exceeds partition capacity {capacity}')
    while image.read(1024 * 1024):
        pass
    length = image.tell()
    if any(offset + size > length for _, offset, size, _ in ordered):
        raise SystemExit('A partition extends beyond the image')
print(f'Image: {path.name}')
for number, offset, capacity, kind in ordered:
    print(f'Partition {number}: offset={offset}, bytes={capacity}, type=0x{kind:02x}')
print(f'Btrfs filesystem bytes: {fs_size}')
print(f'Uncompressed image bytes: {length}')
print('PASS: MBR, partition bounds, Btrfs size and full archive read.')
print('This is a structural check, not a hardware boot test. Test USB boot before eMMC installation.')
