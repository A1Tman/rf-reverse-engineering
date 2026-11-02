#!/usr/bin/env python3
"""Check local documentation links and explicitly marked offline CLI examples."""

import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = re.compile(r'^<!-- offline-smoke -->\r?\n```bash\r?\n(.*?)^```\s*$', re.M | re.S)
CLI_PATHS = {
    'gazco-fireplace/code/controller.py',
    'sonte-smart-film/code/sonte_controller.py',
    'sonte-smart-film/code/sonte_button1_transparent.py',
    'sonte-smart-film/code/sonte_button2_opaque.py',
    *(f'gazco-fireplace/code/scripts/gazco_{name}.py' for name in ('on', 'off', 'up', 'down')),
}
RUN_OFFLINE = '''
import importlib.abc
import runpy
import sys
from pathlib import Path
class NoRadio(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('rflib', 'usb', 'serial'):
            raise ImportError('Radio access is forbidden in documentation examples')
sys.meta_path.insert(0, NoRadio())
sys.argv = sys.argv[1:]
# Match Python's normal script-directory import path while retaining the
# isolated interpreter and the explicit radio-import guard.
sys.path.insert(0, str(Path(sys.argv[0]).parent))
runpy.run_path(sys.argv[0], run_name='__main__')
'''


def main():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    checked = set()
    example_count = 0
    documents = 0
    for relative in paths:
        path = ROOT / relative
        if path.suffix != '.md' or not path.is_file():
            continue
        documents += 1
        text = path.read_text(encoding='utf-8')
        for line_number, line in enumerate(text.splitlines(), 1):
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)', line):
                url = urlsplit(target.strip('<>'))
                if url.scheme or url.netloc or not url.path:
                    continue
                if not (path.parent / unquote(url.path)).exists():
                    raise ValueError(f'{relative}:{line_number}: missing local link {target}')
        for match in EXAMPLES.finditer(text):
            for line in match.group(1).splitlines():
                args = shlex.split(line, comments=True)
                if not args:
                    continue
                if (len(args) < 3 or args[0] != 'python' or args[1] not in CLI_PATHS
                        or args[-1] not in ('--dry-run', '--help')):
                    raise ValueError(f'{relative}: unsupported offline example: {line}')
                example_count += 1
                command = tuple(args[1:])
                if command in checked:
                    continue
                result = subprocess.run(
                    [sys.executable, '-I', '-c', RUN_OFFLINE, str(ROOT / args[1]), *args[2:]],
                    cwd=ROOT, capture_output=True, text=True, timeout=10,
                )
                if result.returncode:
                    raise RuntimeError(f'{relative}: example failed: {line}\n{result.stdout}\n{result.stderr}')
                checked.add(command)
    if not example_count:
        raise ValueError('No marked offline examples found')
    print(f'Checked links in {documents} documents and {example_count} offline examples '
          f'({len(checked)} distinct commands), with radio imports blocked.')


if __name__ == '__main__':
    main()
