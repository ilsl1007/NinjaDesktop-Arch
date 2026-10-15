#!/usr/bin/env python3
"""Repair the debtap conversion of NinjaDesktop 1.0.6 amd64, without root."""
from pathlib import Path
import gzip
import subprocess
import sys
import tempfile

if len(sys.argv) != 2:
    raise SystemExit('Usage: python3 repair-ninjadesktop.py INPUT.pkg.tar.zst')
source = Path(sys.argv[1]).resolve()
output = source.with_name('ninjadesktop-electron-1.0.6-2-x86_64.pkg.tar.zst')
if output.exists():
    raise SystemExit(f'Output already exists; refusing to overwrite: {output}')

with tempfile.TemporaryDirectory(prefix='ninjadesktop-repair-') as directory:
    root = Path(directory)
    subprocess.run(['bsdtar', '-xf', str(source), '-C', directory], check=True)
    info = root / '.PKGINFO'
    data = info.read_text()
    for expected in ('pkgname = ninjadesktop-electron\n', 'pkgver = 1.0.6-1\n', 'arch = x86_64\n'):
        if expected not in data:
            raise SystemExit(f'Unexpected input package; missing: {expected.strip()}')
    data = data.replace('pkgver = 1.0.6-1\n', 'pkgver = 1.0.6-2\n')
    data = data.replace('depend = gtk\n', '')
    data = data.replace('license = \n', 'license = UNLICENSED\n')
    if 'depend = libsecret\n' not in data:
        data += 'depend = libsecret\n'
    info.write_text(data)

    install = root / '.INSTALL'
    data = install.read_text()
    replacements = {
        '\tand once every installed postrm keeps\n':
            '\t# and once every installed postrm keeps\n',
        '[ -n "$TARGET_HOME" ] || \n':
            '[ -n "$TARGET_HOME" ] || return 0\n',
        '[ -f "$TARGET_HOME/.config/ninjadesktop/appconfig.yaml" ] || [ -d "$TARGET_HOME/.local/share/ninjadesktop" ] || \n':
            '[ -f "$TARGET_HOME/.config/ninjadesktop/appconfig.yaml" ] || [ -d "$TARGET_HOME/.local/share/ninjadesktop" ] || return 0\n',
    }
    for old, new in replacements.items():
        if data.count(old) == 1:
            data = data.replace(old, new)
        elif new not in data:
            raise SystemExit('Unexpected .INSTALL contents; no output package written.')
    install.write_text(data)
    subprocess.run(['bash', '-n', str(install)], check=True)

    manifest = subprocess.run([
        'bsdtar', '-cf', '-', '--format=mtree',
        '--options=!all,use-set,type,uid,gid,mode,time,size,md5,sha256,link',
        '--uid', '0', '--gid', '0', '.PKGINFO', '.INSTALL', 'opt', 'usr',
    ], cwd=root, check=True, stdout=subprocess.PIPE).stdout
    (root / '.MTREE').write_bytes(gzip.compress(manifest))
    subprocess.run([
        'bsdtar', '--zstd', '-cf', str(output), '--uid', '0', '--gid', '0',
        '.PKGINFO', '.INSTALL', '.MTREE', 'opt', 'usr',
    ], cwd=root, check=True)
print(output)
