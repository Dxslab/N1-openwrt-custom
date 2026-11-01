#!/usr/bin/env python3
"""Fetch pinned release assets, verifying cached files as well as new downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--skip-sdk', action='store_true')
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
lock = json.loads((repo / 'configs/prebuilt-lock.json').read_text())
destination = repo / 'downloads'
destination.mkdir(exist_ok=True)
assets = [lock['imagebuilder'], *lock['packages']]
if not args.skip_sdk:
    assets.append(lock['sdk'])
for asset in assets:
    path = destination / asset['name']
    def valid():
        if not path.is_file():
            return False
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest() == asset['sha256']
    if not valid():
        temporary = path.with_suffix(path.suffix + '.part')
        for attempt in range(3):
            try:
                request = urllib.request.Request(asset['url'], headers={'User-Agent': 'N1-firmware-builder'})
                with urllib.request.urlopen(request, timeout=120) as source, temporary.open('wb') as output:
                    shutil.copyfileobj(source, output)
                temporary.replace(path)
                if not valid():
                    path.unlink()
                    raise ValueError('SHA256 mismatch: ' + asset['name'])
                break
            except Exception:
                temporary.unlink(missing_ok=True)
                if attempt == 2:
                    raise
                time.sleep(3)
    print('Verified:', asset['name'], flush=True)
