#!/bin/sh
# Build a real release sdist, copy it alongside PKGBUILD and record its checksum.
set -eu
cd "$(dirname "$0")/../.."
python -m build --sdist --no-isolation
python - <<'PY'
from pathlib import Path
import hashlib
import shutil
archive = Path('dist/nekoinfo-2.0.0.tar.gz')
target = Path('packaging/arch') / archive.name
shutil.copyfile(archive, target)
recipe = target.parent / 'PKGBUILD'
lines = recipe.read_text().splitlines()
checksum = hashlib.sha256(target.read_bytes()).hexdigest()
recipe.write_text('\n'.join("sha256sums=('" + checksum + "')" if line.startswith('sha256sums=') else line for line in lines) + '\n')
print(target, checksum)
PY
