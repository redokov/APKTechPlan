#!/usr/bin/env python3
"""Single source of truth for the 1C:Enterprise 8.5 platform path (bin dir).

The platform is updated frequently on this machine, so scripts must NOT
hardcode a specific 8.5.4.x build. Resolution order:

  1. CLI option --v8path <path-to-bin>  (highest priority)
  2. Environment variable APK_V8_PATH   (full path to the 'bin' directory)
  3. Auto-detect: the newest C:\\Program Files\\1cv8\\8.5.<x>.<y>\\bin
     directory that actually contains 1cv8.exe. Candidates are sorted by
     the parsed version numbers (not by mtime). Dirs with a gutted bin
     (missing 1cv8.exe) are skipped.

Usage from other scripts (same directory):
    import v8conf
    V8  = v8conf.v8_exe()            # ...\\bin\\1cv8.exe
    V8C = v8conf.v8c_exe()           # ...\\bin\\1cv8c.exe
    BIN = v8conf.resolve_v8path()    # ...\\bin

To honour a --v8path CLI option in your own script:
    BIN = v8conf.resolve_v8path(v8conf.cli_v8path(prune=True))
(prune=True removes the --v8path tokens from sys.argv so positional
argument parsing in the calling script stays intact).

All failures raise V8PathError with an actionable message (English, ASCII).
"""
import os
import re
import sys

# Install roots to scan during auto-detect.
SEARCH_ROOTS = (
    r"C:\Program Files\1cv8",
    r"C:\Program Files (x86)\1cv8",
)

# Exact 4-number version directory: 8.5.4.2028
_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$")

ENV_VAR = "APK_V8_PATH"
CLI_OPTION = "--v8path"


class V8PathError(RuntimeError):
    """Raised when no usable platform bin directory can be resolved."""


def _version_key(dirname):
    """Parse '8.5.4.2028' into a sortable tuple, or None if not a version."""
    m = _VERSION_RE.match(os.path.basename(os.path.normpath(dirname)))
    if not m:
        return None
    return tuple(int(g) for g in m.groups())


def autodetect():
    """Newest 8.5.* install whose bin\\1cv8.exe exists, or None."""
    candidates = []
    for root in SEARCH_ROOTS:
        if not os.path.isdir(root):
            continue
        try:
            entries = os.listdir(root)
        except OSError:
            continue
        for name in entries:
            if not name.startswith("8.5."):
                continue
            ver = _version_key(os.path.join(root, name))
            if ver is None:
                continue
            bin_dir = os.path.join(root, name, "bin")
            if os.path.isfile(os.path.join(bin_dir, "1cv8.exe")):
                candidates.append((ver, bin_dir))
    if not candidates:
        return None
    return max(candidates)[1]


def resolve_v8path(cli_value=None):
    """Resolve the platform bin dir: CLI --v8path > APK_V8_PATH > autodetect."""
    for cand in (cli_value, os.environ.get(ENV_VAR)):
        if not cand:
            continue
        cand = os.path.normpath(os.path.expandvars(cand))
        if not os.path.isfile(os.path.join(cand, "1cv8.exe")):
            raise V8PathError(
                "Override path %r (from %s) does not contain 1cv8.exe. "
                "Point it at the platform 'bin' directory or unset it."
                % (cand, CLI_OPTION if cand == cli_value else ENV_VAR))
        return cand
    auto = autodetect()
    if auto is None:
        raise V8PathError(
            "No 1C 8.5.x platform found: no C:\\Program Files\\1cv8\\8.5.*\\bin "
            "directory with an existing 1cv8.exe. Install the platform or set "
            "%s / pass %s <path-to-bin> explicitly." % (ENV_VAR, CLI_OPTION))
    return auto


def v8_exe(cli_value=None):
    """Full path to 1cv8.exe."""
    return os.path.join(resolve_v8path(cli_value), "1cv8.exe")


def v8c_exe(cli_value=None):
    """Full path to the thin client 1cv8c.exe."""
    return os.path.join(resolve_v8path(cli_value), "1cv8c.exe")


def cli_v8path(argv=None, prune=False):
    """Extract '--v8path VALUE' (or '--v8path=VALUE') from argv.

    argv defaults to sys.argv (full list, including argv[0] which is
    skipped). With prune=True the matched tokens are removed from sys.argv
    in place so positional parsing in the caller is unaffected.
    Returns None when the option is absent.
    """
    if argv is None:
        argv = sys.argv
    value = None
    out = [argv[0]]
    i = 1
    while i < len(argv):
        tok = argv[i]
        if tok == CLI_OPTION and i + 1 < len(argv):
            value = argv[i + 1]
            i += 2
        elif tok.startswith(CLI_OPTION + "="):
            value = tok.split("=", 1)[1]
            i += 1
        else:
            out.append(tok)
            i += 1
    if prune and value is not None:
        sys.argv[:] = out
    return value


def _selftest():
    """Offline sanity checks for path resolution logic."""
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print("[selftest] ok: %s %s" % (name, detail))
        else:
            failures.append(name)
            print("[selftest] FAIL: %s %s" % (name, detail))

    # version parsing
    check("version-key", _version_key(r"C:\x\8.5.4.2028") == (8, 5, 4, 2028))
    check("version-key-rejects-non-version",
          _version_key(r"C:\x\8.5.4") is None)
    # cli parsing
    check("cli-space-form",
          cli_v8path(["p", "--v8path", r"C:\v8\bin"]) == r"C:\v8\bin")
    check("cli-eq-form",
          cli_v8path(["p", "--v8path=" + r"C:\v8\bin"]) == r"C:\v8\bin")
    check("cli-absent", cli_v8path(["p", "feature.file"]) is None)
    saved = list(sys.argv)
    try:
        sys.argv[:] = ["p", "--v8path", r"C:\v8\bin", "feature.file", "600"]
        val = cli_v8path(prune=True)
        check("cli-prune", val == r"C:\v8\bin" and sys.argv == ["p", "feature.file", "600"],
              "argv=%s" % sys.argv)
    finally:
        sys.argv[:] = saved
    # override validation (nonexistent path must raise)
    try:
        resolve_v8path(r"C:\definitely\not\a\real\v8\bin")
        check("override-missing-raises", False)
    except V8PathError:
        check("override-missing-raises", True)
    # real resolution on this machine
    try:
        bin_dir = resolve_v8path()
        check("resolve", os.path.isfile(os.path.join(bin_dir, "1cv8.exe")),
              "-> %s" % bin_dir)
        check("v8c-exe", os.path.isfile(v8c_exe()))
    except V8PathError as e:
        check("resolve", False, str(e))
    # env override round-trip
    saved_env = os.environ.get(ENV_VAR)
    try:
        real_bin = autodetect()
        if real_bin:
            os.environ[ENV_VAR] = real_bin
            check("env-override", resolve_v8path() == real_bin)
        else:
            check("env-override", True, "(skipped: nothing to autodetect)")
    finally:
        if saved_env is None:
            os.environ.pop(ENV_VAR, None)
        else:
            os.environ[ENV_VAR] = saved_env

    if failures:
        print("[selftest] FAILURES: %s" % ", ".join(failures))
        return 1
    print("[selftest] v8conf: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(_selftest())
