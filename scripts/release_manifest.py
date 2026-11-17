#!/usr/bin/env python3
"""Versioned, verifiable release bundle for the current C172 viewer (Phase 8).

The bundle is every tracked file the Phase 8 viewer needs to run offline, plus
its data, documentation and editable .blend. This script writes
08_realistic_digital_twin/release-manifest.json (version, sha256 and size of
every bundle file) and keeps the version consistent across package.json, the
top heading of RELEASES.md and the manifest.

  python3 scripts/release_manifest.py                  # regenerate the manifest
  python3 scripts/release_manifest.py --check          # CI: manifest and version current
  python3 scripts/release_manifest.py --check --tag v8.0.0   # release: tag matches version
  python3 scripts/release_manifest.py --sums FILE      # write bundle checksums (sha256sum -c format)

Stdlib only. Files are listed from `git ls-files`, so untracked local files
never enter a release.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = '08_realistic_digital_twin/release-manifest.json'
ENTRY_POINT = '08_realistic_digital_twin/index.html'
# Runtime viewer, its data and docs, and the shared simulation it imports
# (js/*.js re-export ../../shared/js). docs/renders are CI baselines, not part of the bundle.
BUNDLE = (
    '08_realistic_digital_twin/index.html',
    '08_realistic_digital_twin/phase8_manifest.json',
    '08_realistic_digital_twin/README.md',
    '08_realistic_digital_twin/README_AR.md',
    '08_realistic_digital_twin/css/',
    '08_realistic_digital_twin/js/',
    '08_realistic_digital_twin/vendor/',
    '08_realistic_digital_twin/models/',
    '08_realistic_digital_twin/assets/',
    '08_realistic_digital_twin/data/',
    '08_realistic_digital_twin/docs/gallery.html',
    '08_realistic_digital_twin/docs/gallery/',
    ':(glob)08_realistic_digital_twin/docs/*.md',
    'shared/',
)
# Files the viewer cannot start without; a bundle missing any of them is broken.
REQUIRED = (
    ENTRY_POINT,
    '08_realistic_digital_twin/js/app.js',
    '08_realistic_digital_twin/models/C172N_realistic_high.glb',
    '08_realistic_digital_twin/models/C172N_realistic_medium.glb',
    '08_realistic_digital_twin/models/C172N_realistic_low.glb',
    '08_realistic_digital_twin/assets/hdri/sky.hdr',
    '08_realistic_digital_twin/data/instruments.json',
    '08_realistic_digital_twin/data/parts_catalog.json',
    'shared/js/sim.js',
)
SEMVER = re.compile(r'^\d+\.\d+\.\d+$')
RELEASE_HEADING = re.compile(r'^## v(\S+)\s*$', re.M)


def bundle_paths(root=ROOT):
    out = subprocess.run(['git', 'ls-files', '-z', '--', *BUNDLE], cwd=root, check=True,
                         capture_output=True).stdout.decode('utf-8')
    return sorted(p for p in out.split('\0') if p and p != MANIFEST)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def package_version(root=ROOT):
    return json.loads((root / 'package.json').read_text(encoding='utf-8')).get('version')


def build_manifest(version, root=ROOT):
    files = [{'path': p, 'size': (root / p).stat().st_size, 'sha256': sha256(root / p)} for p in bundle_paths(root)]
    return {
        'schema_version': 1,
        'name': 'flygaca-c172-digital-twin',
        'version': version,
        'phase': 8,
        'entry_point': ENTRY_POINT,
        'note': 'Pin to git tag v' + str(version) + '; GitHub Pages serves main and may be newer. '
                'Verify with: python3 scripts/release_manifest.py --check',
        'file_count': len(files),
        'total_bytes': sum(f['size'] for f in files),
        'files': files,
    }


def render(manifest):
    return json.dumps(manifest, indent=1, ensure_ascii=False) + '\n'


def version_errors(pkg_version, releases_text, manifest_version=None, tag=None):
    errors = []
    if not isinstance(pkg_version, str) or not SEMVER.match(pkg_version):
        return [f'package.json version must be MAJOR.MINOR.PATCH, found {pkg_version!r}']
    headings = RELEASE_HEADING.findall(releases_text)
    if not headings:
        errors.append('RELEASES.md has no "## vX.Y.Z" release heading')
    elif headings[0] != pkg_version:
        errors.append(f'RELEASES.md top release is v{headings[0]} but package.json is {pkg_version}')
    if len(headings) != len(set(headings)):
        errors.append('RELEASES.md repeats a release heading')
    if manifest_version is not None and manifest_version != pkg_version:
        errors.append(f'{MANIFEST} is for {manifest_version} but package.json is {pkg_version}')
    if tag is not None and tag != 'v' + pkg_version:
        errors.append(f'tag {tag!r} does not match package.json version v{pkg_version}')
    return errors


def manifest_diff(committed, current):
    """Human-readable differences between two manifests' file lists."""
    old = {f['path']: f for f in committed.get('files', [])}
    new = {f['path']: f for f in current.get('files', [])}
    lines = [f'added: {p}' for p in sorted(new.keys() - old.keys())]
    lines += [f'removed: {p}' for p in sorted(old.keys() - new.keys())]
    lines += [f'changed: {p}' for p in sorted(old.keys() & new.keys())
              if (old[p]['sha256'], old[p]['size']) != (new[p]['sha256'], new[p]['size'])]
    return lines


def check(root=ROOT, tag=None):
    version = package_version(root)
    path = root / MANIFEST
    committed = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
    errors = version_errors(version, (root / 'RELEASES.md').read_text(encoding='utf-8'),
                            committed.get('version') if committed else None, tag)
    current = build_manifest(version, root)
    present = {f['path'] for f in current['files']}
    errors += [f'bundle is missing required file {p}' for p in REQUIRED if p not in present]
    if committed is None:
        errors.append(f'{MANIFEST} is missing; run python3 scripts/release_manifest.py')
    elif render(committed) != render(current):
        diff = manifest_diff(committed, current)
        errors.append(f'{MANIFEST} is stale ({len(diff)} file differences); run python3 scripts/release_manifest.py')
        errors += ['  ' + line for line in diff[:20]]
    return errors, current


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='fail if the manifest or version is stale')
    parser.add_argument('--tag', help='with --check: fail unless this tag is v<package.json version>')
    parser.add_argument('--sums', type=Path, help='write bundle checksums in sha256sum -c format')
    args = parser.parse_args()
    if args.tag and not args.check:
        parser.error('--tag needs --check')
    if args.check:
        errors, current = check(tag=args.tag)
    else:
        version = package_version()
        errors = [e for e in version_errors(version, (ROOT / 'RELEASES.md').read_text(encoding='utf-8'))]
        current = build_manifest(version)
        if not errors:
            (ROOT / MANIFEST).write_text(render(current), encoding='utf-8')
    if args.sums and not errors:
        args.sums.write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in current['files']), encoding='utf-8')
    for error in errors:
        print(error, file=sys.stderr)
    print(json.dumps({'version': current['version'], 'files': current['file_count'],
                      'total_bytes': current['total_bytes'], 'ok': not errors}))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
