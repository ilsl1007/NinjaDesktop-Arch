#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

repair_tmp=$(mktemp -d)
trap 'rm -rf -- "$repair_tmp"' EXIT

python3 - /usr/bin/debtap "$repair_tmp/debtap" <<'PY'
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text()
replacements = {
    "grep -E '*.files?(.[[:digit:]]{3})'":
        r"grep -E '\.files(\.[[:digit:]]{3})?$'",
    "$(pacman -Qi base 2> /dev/null | grep ^Depends":
        "$(LC_ALL=C pacman -Qi base 2> /dev/null | grep ^Depends",
}
for old, new in replacements.items():
    if source.count(old) == 1:
        source = source.replace(old, new)
    elif new not in source:
        raise SystemExit('Unexpected debtap version; no system files changed.')
pathlib.Path(sys.argv[2]).write_text(source)
PY

bash -n "$repair_tmp/debtap"
pactree -lu base | sed 's/[<>=].*$//' | sort -u > "$repair_tmp/extended-base-packages-list"
test -s "$repair_tmp/extended-base-packages-list"
grep -qx glibc "$repair_tmp/extended-base-packages-list"

ls /var/cache/pkgfile | grep -E '\.files(\.[[:digit:]]{3})?$' >/dev/null
for cache in debian-main-packages-files debian-non-free-packages-files debian-contrib-packages-files ubuntu-packages-files aur-packages virtual-packages; do
    test -s "/var/cache/debtap/$cache"
done

if [[ $EUID != 0 ]]; then
    printf 'Validation passed. Apply with: sudo bash %q\n' "$(realpath "$0")"
    exit 0
fi

if [[ ! -e /usr/bin/debtap.before-cache-fix ]]; then
    cp -p /usr/bin/debtap /usr/bin/debtap.before-cache-fix
fi
install -m 755 "$repair_tmp/debtap" /usr/bin/debtap
install -m 644 "$repair_tmp/extended-base-packages-list" /var/cache/debtap/extended-base-packages-list
echo 'debtap repaired; existing download caches retained.'
