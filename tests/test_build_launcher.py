"""Check launcher setup/reuse behavior without installing system packages."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAKE_PYTHON = '''#!/usr/bin/env bash
set -eu
[[ -z "${PYTHONPATH:-}" && -z "${PYTHONHOME:-}" ]] || exit 42
printf '%s|%s\\n' "$PWD" "$*" >> "$LAUNCHER_TEST_LOG"
if [[ "${1:-}" == -m && "${2:-}" == venv ]]; then
    mkdir -p "$3/bin"
    cp "$0" "$3/bin/python"
elif [[ "${1:-}" == -m && "${2:-}" == pip && "${3:-}" == install ]]; then
    [[ "${FAIL_INSTALL:-0}" == 0 ]] || exit 23
    touch "$LAUNCHER_TEST_INSTALLED"
elif [[ "${1:-}" == - ]]; then
    cat >/dev/null
    [[ -f "$LAUNCHER_TEST_INSTALLED" ]]
fi
'''


class LauncherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cxwiki launcher ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copy2(ROOT / 'build.sh', self.root / 'build.sh')
        (self.root / 'scripts').mkdir()
        for n in ['build_blog.py', 'check_blog.py', 'check_wiki.py']:
            (self.root / 'scripts' / n).touch()
        (self.root / 'requirements.txt').write_text('mistune==3.1.2\nPyYAML>=6.0,<7\n')
        self.python = self.root / 'fake-python'
        self.python.write_text(FAKE_PYTHON)
        self.python.chmod(0o755)
        self.log = self.root / 'calls'
        self.env = dict(os.environ, CXWIKI_PYTHON=str(self.python),
                        LAUNCHER_TEST_LOG=str(self.log),
                        LAUNCHER_TEST_INSTALLED=str(self.root / 'installed'))

    def run_launcher(self, *args, **env):
        return subprocess.run(['bash', str(self.root / 'build.sh'), *args],
                              cwd='/tmp', env=dict(self.env, **env),
                              capture_output=True, text=True)

    def test_setup_then_reuse_and_changed_requirements(self):
        for _ in range(2):
            result = self.run_launcher()
            self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.log.read_text()
        self.assertEqual(calls.count('-m venv '), 1)
        self.assertEqual(calls.count('-m pip install '), 1)
        self.assertEqual(calls.count('scripts/build_blog.py'), 2)
        self.assertEqual(calls.count('scripts/check_blog.py'), 2)
        with (self.root / 'requirements.txt').open('a') as f:
            f.write('# changed dependency specification\n')
        self.assertEqual(self.run_launcher().returncode, 0)
        self.assertEqual(self.log.read_text().count('-m pip install '), 2)

    def test_failed_install_does_not_mark_setup_complete(self):
        result = self.run_launcher(FAIL_INSTALL='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('scripts/build_blog.py', self.log.read_text())
        result = self.run_launcher()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().count('-m pip install '), 2)

    def test_missing_dependency_is_reinstalled(self):
        self.assertEqual(self.run_launcher().returncode, 0)
        (self.root / 'installed').unlink()
        self.assertEqual(self.run_launcher().returncode, 0)
        self.assertEqual(self.log.read_text().count('-m pip install '), 2)

    def test_sourced_python_environment_does_not_leak(self):
        result = self.run_launcher(PYTHONPATH='/opt/ros/unrelated',
                                   PYTHONHOME='/unrelated-python')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preview_serves_site_on_localhost(self):
        result = self.run_launcher('--serve', '--port', '8081')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('-m http.server 8081 --bind 127.0.0.1 --directory ' +
                      str(self.root / 'site'), self.log.read_text())

    def test_help_and_invalid_port_have_no_side_effects(self):
        self.assertEqual(self.run_launcher('--help').returncode, 0)
        self.assertNotEqual(self.run_launcher('--port', 'not-a-port').returncode, 0)
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
