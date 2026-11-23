import os
from pathlib import Path
import shutil
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DeployTxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'scripts').mkdir()
        (self.root/'site').mkdir()
        shutil.copy2(ROOT/'scripts/deploy_tx.sh', self.root/'scripts/deploy_tx.sh')
        (self.root/'build.sh').write_text('echo build >> "$EVENTS"\n')
        for args in [('init', '-q'), ('config', 'user.email', 'test@example.com'), ('config', 'user.name', 'Test'), ('add', '.'), ('commit', '-qm', 'initial')]:
            subprocess.run(['git', *args], cwd=self.root, check=True)
        self.commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.root, text=True).strip()
        bin_dir = self.root/'bin'
        bin_dir.mkdir()
        (bin_dir/'ssh').write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
command=sys.argv[-1]
with open(os.environ['EVENTS'],'a') as f: f.write('ssh '+command+'\\n')
if '.deploy-commit' in command and 'cat ' in command:
 print(os.environ.get('DEPLOYED_COMMIT',''))
''')
        (bin_dir/'rsync').write_text('#!/bin/sh\necho rsync >> "$EVENTS"\nexit "${RSYNC_EXIT:-0}"\n')
        for p in bin_dir.iterdir():
            p.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(bin_dir)+os.pathsep+os.environ['PATH'], 'EVENTS':str(self.root/'events')}

    def run_deploy(self, deployed='', fail_upload=False):
        env = {**self.env, 'DEPLOYED_COMMIT':deployed, 'RSYNC_EXIT':'1' if fail_upload else '0'}
        result = subprocess.run(['bash','scripts/deploy_tx.sh'], cwd=self.root, env=env, capture_output=True, text=True)
        return result, (self.root/'events').read_text()

    def test_same_commit_skips_build_upload_and_activation(self):
        result, events = self.run_deploy(self.commit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('build\n', events)
        self.assertNotIn('rsync\n', events)
        self.assertNotIn('find /var/www/cxwiki/releases', events)
        self.assertEqual(events.count('ssh '), 1)
        self.assertIn('跳过', result.stdout)

    def test_first_deployment_records_commit_only_after_upload(self):
        result, events = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('build\n', events)
        self.assertIn(self.commit, events)
        self.assertLess(events.index('rsync\n'), events.index('mv -Tf'))
        self.assertIn('.deploy-commit', events[events.index('rsync\n'):])

    def test_different_commit_deploys(self):
        result, events = self.run_deploy('a'*40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('rsync\n', events)

    def test_failed_upload_does_not_mark_or_activate_release(self):
        result, events = self.run_deploy(fail_upload=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('mv -Tf', events)
        self.assertNotIn('find /var/www/cxwiki/releases', events)
        self.assertNotIn(self.commit, events)

    def test_cleanup_keeps_active_release_and_unrelated_files(self):
        result, events = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(events.index('mv -Tf'), events.index('find /var/www/cxwiki/releases'))
        command = next(line[4:] for line in events.splitlines() if 'find /var/www/cxwiki/releases' in line)
        active = re.search(r"= '(/var/www/cxwiki/releases/[^']+)'", command).group(1)
        remote = self.root/'remote'
        active_path = remote/'releases'/Path(active).name
        active_path.mkdir(parents=True)
        (active_path/'index.html').write_text('active')
        for name in ['old1', 'old2']:
            old = remote/'releases'/name
            old.mkdir()
            (old/'index.html').write_text('old')
        (remote/'current').symlink_to(active_path)
        (remote/'auth-config').write_text('keep')
        command = command.replace('/var/www/cxwiki', str(remote)).replace('sudo -n ', '')
        subprocess.run(['bash', '-c', command], check=True)
        self.assertEqual(list((remote/'releases').iterdir()), [active_path])
        self.assertEqual((remote/'current/index.html').read_text(), 'active')
        self.assertTrue((remote/'auth-config').exists())

if __name__ == '__main__':
    unittest.main()
